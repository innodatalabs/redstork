#include "redstork.h"
#include "redstork_version.h"

#include <stdio.h>

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
#include "core/fpdfapi/parser/cpdf_string.h"
#include "core/fpdfapi/edit/cpdf_creator.h"
#include "core/fpdftext/cpdf_textpage.h"
//#include "third_party/base/stl_util.h"


// inline const CFX_Path *CFXPathDataFromFPDFPathData(FPDF_PATH data) {
//   return reinterpret_cast<const CFX_Path*>(data);
// }

// inline FPDF_PATHDATA FPDFPathDataFromCFXPathData(const CFX_PathData *pData) {
//   return reinterpret_cast<FPDF_PATHDATA>(pData);
// }

FPDF_EXPORT extern "C" const char * FPDF_CALLCONV FPDF_ErrorCodeToString(long err) {
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

FPDF_EXPORT extern "C" const char* FPDF_CALLCONV RED_LastError() {
  unsigned long err = FPDF_GetLastError();
  return FPDF_ErrorCodeToString(err);
}

FPDF_EXPORT extern "C" void FPDF_CALLCONV RED_InitLibrary(void) {
    FPDF_LIBRARY_CONFIG config;
    config.version = 2;
    config.m_pUserFontPaths = nullptr;
    config.m_pIsolate = nullptr;
    config.m_v8EmbedderSlot = 0;

    FPDF_InitLibraryWithConfig(&config);
}

FPDF_EXPORT extern "C" FPDF_CALLCONV int REDTextObject_CountItems(FPDF_PAGEOBJECT textObj) {
  CPDF_PageObject *pPageObj = CPDFPageObjectFromFPDFPageObject(textObj);
  CPDF_TextObject *pTextObj = pPageObj->AsText();
  return pTextObj->CountItems();
}

FPDF_EXPORT extern "C" FPDF_CALLCONV FPDF_FONT REDTextObject_GetFont(FPDF_PAGEOBJECT textObj) {
  CPDF_PageObject *pPageObj = CPDFPageObjectFromFPDFPageObject(textObj);
  CPDF_TextObject *pTextObj = pPageObj->AsText();
  return FPDFFontFromCPDFFont(pTextObj->GetFont().Leak());
}

FPDF_EXPORT extern "C" int FPDF_CALLCONV REDTextObject_GetTextMatrix(FPDF_PAGEOBJECT textObj, FS_MATRIX *pMatrix) {
  CPDF_PageObject *pPageObj = CPDFPageObjectFromFPDFPageObject(textObj);
  CPDF_TextObject *pTextObj = pPageObj->AsText();
  CFX_Matrix m = pTextObj->GetTextMatrix();
  pMatrix->a = m.a;
  pMatrix->b = m.b;
  pMatrix->c = m.c;
  pMatrix->d = m.d;
  pMatrix->e = m.e;
  pMatrix->f = m.f;
  return 1;
}

FPDF_EXPORT extern "C" int FPDF_CALLCONV REDTextObject_GetItemInfo(FPDF_PAGEOBJECT textObj, unsigned int index, FPDF_TEXT_OBJECT_ITEM *pItem) {
  CPDF_PageObject *pPageObj = CPDFPageObjectFromFPDFPageObject(textObj);
  CPDF_TextObject *pTextObj = pPageObj->AsText();
  CPDF_TextObject::Item item = pTextObj->GetItemInfo(index);

  pItem->charCode = item.m_CharCode;
  pItem->originX  = item.m_Origin.x;
  pItem->originY  = item.m_Origin.y;

  return 1;
}

FPDF_EXPORT extern "C" int FPDF_CALLCONV REDText_GetCharCode(FPDF_TEXTPAGE text_page, unsigned int index, unsigned int *pCode) {
  CPDF_TextPage* textpage = CPDFTextPageFromFPDFTextPage(text_page);
  if (index < 0 || static_cast<size_t>(index) >= textpage->size()) {
    return 0;
  }
  const CPDF_TextPage::CharInfo& charinfo = textpage->GetCharInfo(index);
  *pCode = charinfo.char_code();

  return 1;
}

FPDF_EXPORT extern "C" unsigned long FPDF_CALLCONV REDFont_GetName(FPDF_FONT font, char *buf, unsigned long buflen) {
  CPDF_Font *pFont = CPDFFontFromFPDFFont(font);
  ByteString basefont = pFont->GetBaseFontName();
  unsigned long length = basefont.GetLength();
  if (buf && buflen >= length + 1) {
    memcpy(buf, basefont.c_str(), length + 1);
  }

  return length;
}

FPDF_EXPORT extern "C" int FPDF_CALLCONV REDFont_GetFlags(FPDF_FONT font) {
  CPDF_Font *pFont = CPDFFontFromFPDFFont(font);
  return pFont->GetFontFlags();
}

FPDF_EXPORT extern "C" int FPDF_CALLCONV REDFont_GetWeight(FPDF_FONT font) {
  CPDF_Font *pFont = CPDFFontFromFPDFFont(font);
  return pFont->GetFontWeight();
}

FPDF_EXPORT extern "C" int FPDF_CALLCONV REDFont_GetId(FPDF_FONT font, unsigned int *pObjNum, unsigned int *pGenNum) {
  CPDF_Font *pFont = CPDFFontFromFPDFFont(font);
  auto pFontDict = pFont->GetFontDict();

  if (pFontDict == nullptr) return 0;

  *pObjNum = pFontDict->GetObjNum();
  *pGenNum = pFontDict->GetGenNum();

  return 1;
}

FPDF_EXPORT extern "C" int FPDF_CALLCONV REDFont_IsVertical(FPDF_FONT font) {
    CPDF_Font *pFont = CPDFFontFromFPDFFont(font);
    return pFont->IsVertWriting();
}

FPDF_EXPORT extern "C" int FPDF_CALLCONV REDFont_UnicodeFromCharCode(FPDF_FONT font, int code, void *buf, unsigned buflen) {
  CPDF_Font *pFont = CPDFFontFromFPDFFont(font);
  auto out = pFont->UnicodeFromCharCode(code).ToUTF8();
  unsigned long length = out.GetLength();
  if (buf && buflen >= length + 1) {
    memcpy(buf, out.c_str(), length + 1);
  }

  return length;
}

FPDF_EXPORT extern "C" unsigned int FPDF_CALLCONV REDImageObject_GetPixelWidth(FPDF_PAGEOBJECT imageObj) {
  CPDF_PageObject *pPageObj = CPDFPageObjectFromFPDFPageObject(imageObj);
  CPDF_ImageObject *pImageObj = pPageObj->AsImage();
  return pImageObj->GetImage()->GetPixelWidth();
}

FPDF_EXPORT extern "C" unsigned int FPDF_CALLCONV REDImageObject_GetPixelHeight(FPDF_PAGEOBJECT imageObj) {
  CPDF_PageObject *pPageObj = CPDFPageObjectFromFPDFPageObject(imageObj);
  CPDF_ImageObject *pImageObj = pPageObj->AsImage();
  return pImageObj->GetImage()->GetPixelHeight();
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
FPDF_EXPORT extern "C" int FPDF_CALLCONV REDPage_Render(FPDF_PAGE page, char const *file_name, int format, float scale) {
  auto width = static_cast<int>(FPDF_GetPageWidthF(page) * scale);
  auto height = static_cast<int>(FPDF_GetPageHeightF(page) * scale);

  ScopedFPDFBitmap bitmap(FPDFBitmap_Create(width, height, 0));
  if (!bitmap) {
    return 0;
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
        return 0;
      }
      break;
#endif

    case FORMAT_PPM:
      if (!WritePpm(file_name, buffer, stride, width, height)) {
        return 0;
      }
      break;

    default:
      return 0;
  }

  return 1;
}

#define FORMAT_PNG (0)
#define FORMAT_PPM (1)
FPDF_EXPORT extern "C" int FPDF_CALLCONV REDPage_RenderRect(FPDF_PAGE page, char const *file_name, int format, float scale, const FS_MATRIX *matrix, const FS_RECTF *rect) {
  FS_RECTF clip;
  if (rect == nullptr) {
    return false;
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
        return 0;
      }
      break;
#endif

    case FORMAT_PPM:
      if (!WritePpm(file_name, buffer, stride, width, height)) {
        return 0;
      }
      break;

    default:
      return 0;
  }

  return 1;
}

FPDF_EXPORT extern "C" int FPDF_CALLCONV REDPage_RenderRect_Buffer(
  FPDF_PAGE page, float scale, const FS_MATRIX *matrix, const FS_RECTF *rect, unsigned char *buffer, int len
  ) {
  FS_RECTF clip;
  if (rect == nullptr) {
    return false;
  } else {
    clip = *rect;
  }
  auto width = static_cast<int>((clip.right-clip.left));
  auto height = static_cast<int>((clip.bottom-clip.top));

  if (len < width*height*4){
    return 0;
  }

  // use external buffer
  FPDF_BITMAP bitmap = FPDFBitmap_CreateEx(width, height, FPDFBitmap_BGRx, buffer, width*4);
  if (!bitmap) {
    return 0;
  }

  FPDFBitmap_FillRect(bitmap, 0, 0, width, height, 0xFFFFFFFF);

  FPDF_RenderPageBitmapWithMatrix(bitmap, page, matrix, &clip, FPDF_LCD_TEXT | FPDF_ANNOT);

  return 1;
}

FPDF_EXPORT extern "C" unsigned int FPDF_CALLCONV REDDoc_GetMetaTextKeyCount(FPDF_DOCUMENT document) {
  CPDF_Document* pDoc = CPDFDocumentFromFPDFDocument(document);
  if (!pDoc)
    return 0;

  const CPDF_Dictionary* pInfo = pDoc->GetInfo();
  if (!pInfo)
    return 0;

  return pInfo->GetKeys().size();
}

FPDF_EXPORT extern "C" const char * FPDF_CALLCONV REDDoc_GetMetaTextKeyAt(FPDF_DOCUMENT document, unsigned int index) {
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

FPDF_EXPORT extern "C" int FPDF_CALLCONV REDDoc_SetMetaItem(FPDF_DOCUMENT document, const char *key, const char *value) {
  CPDF_Document* pDoc = CPDFDocumentFromFPDFDocument(document);
  if (!pDoc)
    return 0;

  CPDF_Dictionary* pInfo = pDoc->GetInfo();
  if (!pInfo)
    return 0;

  auto bkey = ByteString(key);

  if (value == nullptr) {
    pInfo->SetFor(bkey, (RetainPtr<CPDF_Object>) nullptr);  // deletes this key
  } else {
    pInfo->SetNewFor<CPDF_String>(bkey, value);
  }
  return 1;
}


FPDF_EXPORT extern "C" unsigned int FPDF_CALLCONV REDFormObject_GetObjectCount(FPDF_PAGEOBJECT formObj) {
  CPDF_PageObject *pPageObj = CPDFPageObjectFromFPDFPageObject(formObj);
  CPDF_FormObject *pFormObj = pPageObj->AsForm();
  return pFormObj->form()->GetPageObjectCount();
}

FPDF_EXPORT extern "C" FPDF_PAGEOBJECT FPDF_CALLCONV REDFormObject_GetObjectAt(FPDF_PAGEOBJECT formObj, unsigned int index) {
  CPDF_PageObject *pPageObj = CPDFPageObjectFromFPDFPageObject(formObj);
  CPDF_FormObject *pFormObj = pPageObj->AsForm();
  CPDF_PageObject *pInner = pFormObj->form()->GetPageObjectByIndex(index);
  return FPDFPageObjectFromCPDFPageObject(pInner);
}

FPDF_EXPORT extern "C" int FPDF_CALLCONV REDFormObject_GetFormMatrix(FPDF_PAGEOBJECT formObj, FS_MATRIX *m) {
  CPDF_PageObject *pPageObj = CPDFPageObjectFromFPDFPageObject(formObj);
  CPDF_FormObject *pFormObj = pPageObj->AsForm();
  CFX_Matrix matrix = pFormObj->form_matrix();

  m->a = matrix.a;
  m->b = matrix.b;
  m->c = matrix.c;
  m->d = matrix.d;
  m->e = matrix.e;
  m->f = matrix.f;

  return 1;
}

FPDF_EXPORT extern "C" const void * FPDF_CALLCONV REDFont_LoadUnicodeMap(FPDF_FONT font) {
  CPDF_Font *pFont = CPDFFontFromFPDFFont(font);
  auto pDict = pFont->GetFontDict();
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
  const unsigned char *data = span.data();
  unsigned char *buffer = (unsigned char *) malloc(size + 1);
  if (buffer == nullptr) {
    fprintf(stderr, "Failed to allocate\n");
    return nullptr;
  }

  memcpy(buffer, data, size);
  buffer[size] = '\0';

  return buffer;
}

FPDF_EXPORT extern "C" int FPDF_CALLCONV REDFont_WriteUnicodeMap(FPDF_FONT font, unsigned char *buffer, size_t len) {
  CPDF_Font *pFont = CPDFFontFromFPDFFont(font);
  auto pDict = pFont->GetMutableFontDict();
  if (pDict == nullptr) {
    return 0;
  }

  auto pStream = pDict->GetMutableStreamFor("ToUnicode");
  if (pStream == nullptr) {
    return 0;
  }

  auto span = pdfium::span<const uint8_t>(buffer, len);
  pStream->SetDataAndRemoveFilter(span);
  return 1;
}

FPDF_EXPORT extern "C" void FPDF_CALLCONV REDFont_DestroyUnicodeMap(unsigned char *buffer) {
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

  virtual bool WriteBlock(pdfium::span<const uint8_t> data) {
    size_t num = fwrite(data.data(), 1, data.size(), m_fp);
    return num == data.size();
  }
  virtual bool WriteString(ByteStringView str) {
    return WriteBlock(pdfium::make_span((const uint8_t *)(str.unterminated_c_str()), str.GetLength()));
  }

private:
  FILE *m_fp;
};

FPDF_EXPORT extern "C" int FPDF_CALLCONV REDDoc_Save(FPDF_DOCUMENT document, char const *filename) {
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

FPDF_EXPORT extern "C" const char *RED_GetVersion(void) {
  return REDSTORK_VERSION;
}