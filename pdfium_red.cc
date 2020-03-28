#include <stdio.h>
#include "public/fpdfview.h"
#include "public/cpp/fpdf_scopers.h"
#include "fpdfsdk/cpdfsdk_helpers.h"
#include "core/fpdfapi/parser/cpdf_document.h"
#include "core/fpdfapi/page/cpdf_pageobject.h"
#include "core/fpdfapi/page/cpdf_textobject.h"
#include "core/fpdfapi/font/cpdf_font.h"

#define DLL_PUBLIC __attribute__ ((visibility ("default")))
#define DLL_LOCAL  __attribute__ ((visibility ("hidden")))


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

FPDF_EXPORT extern "C" void REDFont_Destroy(CPDF_Font *p) {
    RetainPtr<CPDF_Font> font;

    font.Unleak(p);
}

FPDF_EXPORT extern "C" unsigned long REDFont_GetName(CPDF_Font *font, char *buf, unsigned long buflen) {
  ByteString basefont = font->GetBaseFontName();
  unsigned long length = basefont.GetLength() + 1;
  if (buf && buflen >= length) {
    memcpy(buf, basefont.c_str(), length);
  }

  return length;
}

FPDF_EXPORT extern "C" int REDFont_GetFlags(CPDF_Font *font) {
  return font->GetFontFlags();
}

FPDF_EXPORT extern "C" int REDFont_GetWeight(CPDF_Font *font) {
  return font->GetFontWeight();
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
