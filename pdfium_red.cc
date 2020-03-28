#include <stdio.h>
#include "public/fpdfview.h"
#include "fpdfsdk/cpdfsdk_helpers.h"
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

//     pPage->ParseContent();

//     auto count = 0;
//     for (const auto& pCurObj : *pPage) {
//         if (!pCurObj)
//             continue;

//         auto rect = pCurObj->GetRect();

//         fprintf(stderr, "Rect: %lf %lf %lf %lf\t", rect.Left(), rect.Top(), rect.Right(), rect.Bottom());

//         if (pCurObj->IsText()) {
//             auto pTextObj = pCurObj->AsText();
//             int numItems = pTextObj->CountItems();
//             fprintf(stderr, "TEXT %d\n", numItems);
//             RetainPtr<CPDF_Font> font(pTextObj->GetFont());
//             font.Leak();
//         } else if (pCurObj->IsPath()) {
//             fprintf(stderr, "PATH\n");
//         } else if (pCurObj->IsImage()) {
//             fprintf(stderr, "IMAGE\n");
//         } else if (pCurObj->IsShading()) {
//             fprintf(stderr, "SHADING\n");
//         } else if (pCurObj->IsForm()) {
//             fprintf(stderr, "FORM\n");
//         } else {
//             fprintf(stderr, "UNKNOWN type\n");
//         }

//         count += 1;
//     }
//     return count;
// }