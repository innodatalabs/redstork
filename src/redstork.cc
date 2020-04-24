#include <stdio.h>
#include "public/fpdfview.h"
#include "public/cpp/fpdf_scopers.h"
#include "fpdfsdk/cpdfsdk_helpers.h"
#include "core/fpdfapi/parser/cpdf_document.h"
#include "core/fpdfapi/page/cpdf_page.h"
#include "core/fpdfapi/page/cpdf_pageobject.h"
#include "core/fpdfapi/page/cpdf_textobject.h"
#include "core/fpdfapi/page/cpdf_imageobject.h"
#include "core/fpdfapi/page/cpdf_image.h"
#include "core/fpdfapi/page/cpdf_formobject.h"
#include "core/fpdfapi/page/cpdf_form.h"
#include "core/fpdfapi/font/cpdf_font.h"
#include "constants/page_object.h"
#include "core/fpdfapi/parser/cpdf_array.h"
#include "core/fpdfapi/parser/cpdf_stream.h"
#include "core/fpdfapi/parser/cpdf_stream_acc.h"
#include "core/fpdfapi/edit/cpdf_creator.h"


FPDF_EXPORT extern "C" const char *FPDF_ErrorCodeToString(long err) {
  switch (err) {
    case FPDF_ERR_SUCCESS:
      return "Success";
    case FPDF_ERR_UNKNOWN:
      return "Unknown error";
    case FPDF_ERR_FILE:
      return "File not found or could not be opened";
    case FPDF_ERR_FORMAT:
      return "File not in PDF format or corrupted";
    case FPDF_ERR_PASSWORD:
      return "Password required or incorrect password";
    case FPDF_ERR_SECURITY:
      return "Unsupported security scheme";
    case FPDF_ERR_PAGE:
      return "Page not found or content error";
    default:
      return "Unexpected error (not in the list of possible FPDF errors!)";
  }
}

FPDF_EXPORT extern "C" const char* RED_LastError() {
  unsigned long err = FPDF_GetLastError();
  return FPDF_ErrorCodeToString(err);
}

FPDF_EXPORT extern "C" void RED_InitLibrary(void) {
    FPDF_LIBRARY_CONFIG config;
    config.version = 2;
    config.m_pUserFontPaths = nullptr;
    config.m_pIsolate = nullptr;
    config.m_v8EmbedderSlot = 0;

    FPDF_InitLibraryWithConfig(&config);
}

FPDF_EXPORT extern "C" void RED_DestroyLibrary(void) {
    FPDF_DestroyLibrary();
}

FPDF_EXPORT extern "C" FPDF_DOCUMENT RED_LoadDocument(char const *path, const char *pass) {
    return FPDF_LoadDocument(path, pass);
}

FPDF_EXPORT extern "C" int REDPage_GetPageRotation(FPDF_PAGE page) {
    CPDF_Page* pPage = CPDFPageFromFPDFPage(page);

    return pPage->GetPageRotation();
}

static CPDF_Object* GetPageAttr(CPDF_Page const *page, const ByteString& name) {
  CPDF_Dictionary* pPageDict = page->GetDict();
  std::set<CPDF_Dictionary*> visited;
  while (1) {
    visited.insert(pPageDict);
    if (CPDF_Object* pObj = pPageDict->GetDirectObjectFor(name))
      return pObj;

    pPageDict = pPageDict->GetDictFor(pdfium::page_object::kParent);
    if (!pPageDict || pdfium::ContainsKey(visited, pPageDict))
      break;
  }
  return nullptr;
}

static CFX_FloatRect GetBox(CPDF_Page const *page, const ByteString& name) {
  CFX_FloatRect box;
  CPDF_Array* pBox = ToArray(GetPageAttr(page, name));
  if (pBox) {
    box = pBox->GetRect();
    box.Normalize();
  }
  return box;
}


FPDF_EXPORT extern "C" int REDPage_GetMediaBox(FPDF_PAGE page, FS_RECTF *rect) {
    CPDF_Page const *pPage = CPDFPageFromFPDFPage(page);

    auto mediabox = GetBox(pPage, pdfium::page_object::kMediaBox);
    if (mediabox.IsEmpty())
      mediabox = CFX_FloatRect(0, 0, 612, 792);

    rect->left = mediabox.left;
    rect->top  = mediabox.top;
    rect->right = mediabox.right;
    rect->bottom = mediabox.bottom;

    return true;
}

FPDF_EXPORT extern "C" int REDPage_GetCropBox(FPDF_PAGE page, FS_RECTF *rect) {
    CPDF_Page const *pPage = CPDFPageFromFPDFPage(page);

    auto mediabox = GetBox(pPage, pdfium::page_object::kMediaBox);
    if (mediabox.IsEmpty())
      mediabox = CFX_FloatRect(0, 0, 612, 792);

    auto cropbox = GetBox(pPage, pdfium::page_object::kCropBox);
    if (cropbox.IsEmpty())
      cropbox = mediabox;

    cropbox.Intersect(mediabox);

    rect->left = cropbox.left;
    rect->top  = cropbox.top;
    rect->right = cropbox.right;
    rect->bottom = cropbox.bottom;

    return true;
}


FPDF_EXPORT extern "C" int REDPage_GetPageObjectCount(FPDF_PAGE page) {
    CPDF_Page* pPage = CPDFPageFromFPDFPage(page);
    pPage->ParseContent();
    return pPage->GetPageObjectCount();
}

FPDF_EXPORT extern "C" CPDF_PageObject * REDPage_GetPageObjectByIndex(FPDF_PAGE page, int index) {
    CPDF_Page* pPage = CPDFPageFromFPDFPage(page);
    return pPage->GetPageObjectByIndex(index);
}

FPDF_EXPORT extern "C" int REDPageObject_GetType(CPDF_PageObject *pObj) {
    return pObj->GetType();
}

FPDF_EXPORT extern "C" void REDPageObject_GetRect(CPDF_PageObject *pObj, FS_RECTF *r) {
    auto rect = pObj->GetRect();
    r->left = rect.Left();
    r->top = rect.Top();
    r->right = rect.Right();
    r->bottom = rect.Bottom();
}

FPDF_EXPORT extern "C" int REDTextObject_CountItems(CPDF_TextObject *pObj) {
    return pObj->CountItems();
}

FPDF_EXPORT extern "C" float REDTextObject_GetFontSize(CPDF_TextObject *pObj) {
    return pObj->GetFontSize();
}

FPDF_EXPORT extern "C" CPDF_Font * REDTextObject_GetFont(CPDF_TextObject *pObj) {
    return pObj->GetFont().Leak();
}

FPDF_EXPORT extern "C" int REDTextObject_GetTextMatrix(CPDF_TextObject *pObj, FS_MATRIX *pMatrix) {
  CFX_Matrix m = pObj->GetTextMatrix();
  pMatrix->a = m.a;
  pMatrix->b = m.b;
  pMatrix->c = m.c;
  pMatrix->d = m.d;
  pMatrix->e = m.e;
  pMatrix->f = m.f;
  return 1;
}

FPDF_EXPORT extern "C" int REDTextObject_GetItemCount(CPDF_TextObject *pObj) {
  return pObj->CountItems();
}

FPDF_EXPORT extern "C" void REDTextObject_GetItemInfo(CPDF_TextObject *pObj, unsigned int index, CPDF_TextObjectItem *pItem) {
  pObj->GetItemInfo(index, pItem);
}

FPDF_EXPORT extern "C" void REDFont_Destroy(CPDF_Font *p) {
    RetainPtr<CPDF_Font> font;

    font.Unleak(p);
}

FPDF_EXPORT extern "C" unsigned long REDFont_GetName(CPDF_Font *font, char *buf, unsigned long buflen) {
  ByteString basefont = font->GetBaseFontName();
  unsigned long length = basefont.GetLength();
  if (buf && buflen >= length + 1) {
    memcpy(buf, basefont.c_str(), length + 1);
  }

  return length;
}

FPDF_EXPORT extern "C" int REDFont_GetFlags(CPDF_Font *font) {
  return font->GetFontFlags();
}

FPDF_EXPORT extern "C" int REDFont_GetWeight(CPDF_Font *font) {
  return font->GetFontWeight();
}

FPDF_EXPORT extern "C" bool REDFont_GetId(CPDF_Font *font, unsigned int *pObjNum, unsigned int *pGenNum) {
  auto pFontDict = font->GetFontDict();

  if (pFontDict == nullptr) return false;

  *pObjNum = pFontDict->GetObjNum();
  *pGenNum = pFontDict->GetGenNum();

  return true;
}

FPDF_EXPORT extern "C" bool REDFont_IsVertical(CPDF_Font *pFont) {
    return pFont->IsVertWriting();
}

FPDF_EXPORT extern "C" int REDFont_UnicodeFromCharCode(CPDF_Font *pFont, int code, void *buf, unsigned buflen) {
  auto out = pFont->UnicodeFromCharCode(code).ToUTF8();
  unsigned long length = out.GetLength();
  if (buf && buflen >= length + 1) {
    memcpy(buf, out.c_str(), length + 1);
  }

  return length;
}

FPDF_EXPORT extern "C" unsigned int REDImageObject_GetPixelWidth(CPDF_ImageObject *pObj) {
  return pObj->GetImage()->GetPixelWidth();
}

FPDF_EXPORT extern "C" unsigned int REDImageObject_GetPixelHeight(CPDF_ImageObject *pObj) {
  return pObj->GetImage()->GetPixelHeight();
}

#ifdef PNG_SUPPORT
int WritePng(const char* file_name,
    void* buffer,
    int stride,
    int width,
    int height) {

  auto input =
      pdfium::make_span(static_cast<uint8_t*>(buffer), stride * height);
  std::vector<uint8_t> png_encoding =
      image_diff_png::EncodeBGRAPNG(input, width, height, stride, /*discard_transparency=*/ false);
  if (png_encoding.empty()) {
    return false;
  }

  FILE* fp = fopen(file_name, "wb");
  if (!fp) {
    return false;
  }

  size_t bytes_written =
      fwrite(&png_encoding.front(), 1, png_encoding.size(), fp);
  if (bytes_written != png_encoding.size()) {
    fclose(fp);
    return false;
  }
  fclose(fp);
  return true;
}
#endif

bool WritePpm(const char* file_name,
    void* buffer_void,
    int stride,
    int width,
    int height) {

  int out_len = width * height;
  if (out_len > INT_MAX / 3)
    return false;

  out_len *= 3;

  FILE* fp = fopen(file_name, "wb");
  if (!fp)
    return false;

  fprintf(fp, "P6\n# PDFium/RED render\n%d %d\n255\n", width, height);
  // Source data is B, G, R, unused.
  // Dest data is R, G, B.
  const uint8_t* buffer = reinterpret_cast<const uint8_t*>(buffer_void);
  std::vector<uint8_t> result(out_len);
  for (int h = 0; h < height; ++h) {
    const uint8_t* src_line = buffer + (stride * h);
    uint8_t* dest_line = result.data() + (width * h * 3);
    for (int w = 0; w < width; ++w) {
      // R
      dest_line[w * 3] = src_line[(w * 4) + 2];
      // G
      dest_line[(w * 3) + 1] = src_line[(w * 4) + 1];
      // B
      dest_line[(w * 3) + 2] = src_line[w * 4];
    }
  }
  if (fwrite(result.data(), out_len, 1, fp) != 1) {
    fclose(fp);
    return false;
  }

  fclose(fp);
  return true;
}

#define FORMAT_PNG (0)
#define FORMAT_PPM (1)
FPDF_EXPORT extern "C" bool REDPage_Render(FPDF_PAGE page, char const *file_name, int format, float scale) {
  auto width = static_cast<int>(FPDF_GetPageWidthF(page) * scale);
  auto height = static_cast<int>(FPDF_GetPageHeightF(page) * scale);

  ScopedFPDFBitmap bitmap(FPDFBitmap_Create(width, height, 0));
  if (!bitmap) {
    return false;
  }

  FPDFBitmap_FillRect(bitmap.get(), 0, 0, width, height, 0xFFFFFFFF);

  int flags = 0; // PageRenderFlagsFromOptions(options);
  FPDF_RenderPageBitmap(bitmap.get(), page, 0, 0, width, height, 0, flags);

  int stride = FPDFBitmap_GetStride(bitmap.get());
  void* buffer = FPDFBitmap_GetBuffer(bitmap.get());

  switch (format) {
#ifdef PNG_SUPPORT
    case FORMAT_PNG:
      if (!WritePng(file_name, buffer, stride, width, height) ) {
        return false;
      }
      break;
#endif

    case FORMAT_PPM:
      if (!WritePpm(file_name, buffer, stride, width, height)) {
        return false;
      }
      break;

    default:
      return false;
  }

  return true;
}

#define FORMAT_PNG (0)
#define FORMAT_PPM (1)
FPDF_EXPORT extern "C" bool REDPage_RenderRect(FPDF_PAGE page, char const *file_name, int format, float scale, const FS_MATRIX *matrix, const FS_RECTF *rect) {
  FS_RECTF clip;
  if (rect == nullptr) {
    REDPage_GetCropBox(page, &clip);
  } else {
    clip = *rect;
  }
  auto width = static_cast<int>((clip.right-clip.left));
  auto height = static_cast<int>((clip.bottom-clip.top));

  ScopedFPDFBitmap bitmap(FPDFBitmap_Create(width, height, 0));
  if (!bitmap) {
    return false;
  }

  FPDFBitmap_FillRect(bitmap.get(), 0, 0, width, height, 0xFFFFFFFF);

  FPDF_RenderPageBitmapWithMatrix(bitmap.get(), page, matrix, &clip, FPDF_LCD_TEXT);

  int stride = FPDFBitmap_GetStride(bitmap.get());
  void* buffer = FPDFBitmap_GetBuffer(bitmap.get());

  switch (format) {
#ifdef PNG_SUPPORT
    case FORMAT_PNG:
      if (!WritePng(file_name, buffer, stride, width, height) ) {
        return false;
      }
      break;
#endif

    case FORMAT_PPM:
      if (!WritePpm(file_name, buffer, stride, width, height)) {
        return false;
      }
      break;

    default:
      return false;
  }

  return true;
}

FPDF_EXPORT extern "C" unsigned int REDDoc_GetMetaTextKeyCount(FPDF_DOCUMENT document) {
  CPDF_Document* pDoc = CPDFDocumentFromFPDFDocument(document);
  if (!pDoc)
    return 0;

  const CPDF_Dictionary* pInfo = pDoc->GetInfo();
  if (!pInfo)
    return 0;

  return pInfo->GetKeys().size();
}

FPDF_EXPORT extern "C" const char * REDDoc_GetMetaTextKeyAt(FPDF_DOCUMENT document, unsigned int index) {
  CPDF_Document* pDoc = CPDFDocumentFromFPDFDocument(document);
  if (!pDoc)
    return nullptr;

  const CPDF_Dictionary* pInfo = pDoc->GetInfo();
  if (!pInfo)
    return nullptr;

  const auto keys = pInfo->GetKeys();

  if (index < 0 || index >= keys.size()) {
    return nullptr;
  }

  return keys[index].c_str();
}


FPDF_EXPORT extern "C" unsigned int REDFormObject_GetObjectCount(CPDF_FormObject const *pFormObj) {
  return pFormObj->form()->GetPageObjectCount();
}

FPDF_EXPORT extern "C" CPDF_PageObject *REDFormObject_GetObjectAt(CPDF_FormObject const *pFormObj, unsigned int index) {
  return pFormObj->form()->GetPageObjectByIndex(index);
}

FPDF_EXPORT extern "C" bool REDFormObject_GetFormMatrix(CPDF_FormObject const *pFormObj, FS_MATRIX *m) {
  CFX_Matrix matrix = pFormObj->form_matrix();

  m->a = matrix.a;
  m->b = matrix.b;
  m->c = matrix.c;
  m->d = matrix.d;
  m->e = matrix.e;
  m->f = matrix.f;

  return true;
}

FPDF_EXPORT extern "C" const void *REDFont_LoadGlyph(CPDF_Font *font, int char_code) {
  auto pCfxFont = font->GetFont();
  bool bVert = false;
  unsigned int glyph_index = font->GlyphFromCharCode(char_code, &bVert);
  const CFX_PathData *pPathData = pCfxFont->LoadGlyphPath(glyph_index, 0);
  return pPathData;
}

FPDF_EXPORT extern "C" int REDGlyph_Size(const CFX_PathData *path) {
  return path->GetPoints().size();
}

typedef struct {
  float x;
  float y;
  unsigned char type;
  bool close;
} RED_PATH_POINT;

FPDF_EXPORT extern "C" void REDGlyph_Get(const CFX_PathData *path, int index, RED_PATH_POINT *p) {
  auto pPoint = path->GetPoints()[index];
  *p = * ((RED_PATH_POINT*) &pPoint);
}

FPDF_EXPORT extern "C" const void *REDFont_LoadUnicodeMap(CPDF_Font *font) {
  auto pDict = font->GetFontDict();
  if (pDict == nullptr) {
    return nullptr;
  }

  auto pStream = pDict->GetStreamFor("ToUnicode");
  if (pStream == nullptr) {
    return nullptr;
  }

  auto pAcc = pdfium::MakeRetain<CPDF_StreamAcc>(pStream);
  pAcc->LoadAllDataFiltered();
  auto span = pAcc->GetSpan();

  unsigned int size = span.size();
  unsigned char *data = span.data();
  unsigned char *buffer = (unsigned char *) malloc(size + 1);
  if (buffer == nullptr) {
    fprintf(stderr, "Failed to allocate\n");
    return nullptr;
  }

  memcpy(buffer, data, size);
  buffer[size] = '\0';

  return buffer;
}

FPDF_EXPORT extern "C" bool REDFont_WriteUnicodeMap(CPDF_Font *font, unsigned char *buffer, size_t len) {
  auto pDict = font->GetFontDict();
  if (pDict == nullptr) {
    return false;
  }

  auto pStream = pDict->GetStreamFor("ToUnicode");
  if (pStream == nullptr) {
    return false;
  }

  auto span = pdfium::span<const uint8_t>(buffer, len);
  pStream->SetDataAndRemoveFilter(span);
  return true;
}

FPDF_EXPORT extern "C" void REDFont_DestroyUnicodeMap(unsigned char *buffer) {
  free(buffer);
}

class FileWriter : public IFX_RetainableWriteStream {
public:
  FileWriter(const char *filename) : m_fp(nullptr) {
  }

  bool Open(const char *filename) {
    Close();
    m_fp = fopen(filename, "wb");
    return m_fp != nullptr;
  }

  void Close() {
    if (m_fp != nullptr) {
      fclose(m_fp);
    }
  }

  ~FileWriter() {
    Close();
  }

  virtual bool WriteBlock(const void* pData, size_t size) {
    size_t num = fwrite(pData, 1, size, m_fp);
    return num == size;
  }
  virtual bool WriteString(ByteStringView str) {
    return WriteBlock(str.unterminated_c_str(), str.GetLength());
  }

private:
  FILE *m_fp;
};

FPDF_EXPORT extern "C" int REDDoc_Save(FPDF_DOCUMENT document, char const *filename) {
  CPDF_Document* pDoc = CPDFDocumentFromFPDFDocument(document);
  if (!pDoc)
    return 0;

  auto buffer_io = RetainPtr<FileWriter>(new FileWriter(filename));
  if (!buffer_io->Open(filename)) {
    return false;
  }

  CPDF_Creator creator(pDoc, buffer_io);

  return creator.Create(0);
}
