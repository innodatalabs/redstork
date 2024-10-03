#ifndef _REDSTORK_H
#define _REDSTORK_H

#include <stdio.h>
#include "public/fpdfview.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
  unsigned int charCode;
  float originX;
  float originY;
} FPDF_TEXT_OBJECT_ITEM;

typedef struct {
  float x;
  float y;
  unsigned char type;
  int close;
} FPDF_PATH_POINT;

typedef struct {
  void *dummy;
} const *FPDF_PATHDATA;

FPDF_EXPORT void FPDF_CALLCONV RED_InitLibrary(void);
FPDF_EXPORT int FPDF_CALLCONV REDTextObject_CountItems(FPDF_PAGEOBJECT pObj);
FPDF_EXPORT FPDF_FONT FPDF_CALLCONV REDTextObject_GetFont(FPDF_PAGEOBJECT pObj);
FPDF_EXPORT int FPDF_CALLCONV REDTextObject_GetItemInfo(FPDF_PAGEOBJECT pObj, unsigned int index, FPDF_TEXT_OBJECT_ITEM *pItem);
FPDF_EXPORT int FPDF_CALLCONV REDText_GetCharCode(FPDF_PAGEOBJECT textObj, unsigned int index, uint32_t *pCode);
FPDF_EXPORT unsigned long FPDF_CALLCONV REDFont_GetName(FPDF_FONT font, char *buf, unsigned long buflen);
FPDF_EXPORT int FPDF_CALLCONV REDFont_GetFlags(FPDF_FONT font);
FPDF_EXPORT int FPDF_CALLCONV REDFont_GetWeight(FPDF_FONT font);
FPDF_EXPORT int FPDF_CALLCONV REDFont_GetId(FPDF_FONT font, unsigned int *pObjNum, unsigned int *pGenNum);
FPDF_EXPORT int FPDF_CALLCONV REDFont_IsVertical(FPDF_FONT font);
FPDF_EXPORT int FPDF_CALLCONV REDFont_UnicodeFromCharCode(FPDF_FONT font, int code, void *buf, unsigned buflen);
FPDF_EXPORT unsigned int FPDF_CALLCONV REDImageObject_GetPixelWidth(FPDF_PAGEOBJECT  imageObj);
FPDF_EXPORT unsigned int FPDF_CALLCONV REDImageObject_GetPixelHeight(FPDF_PAGEOBJECT imageObj);

#define FORMAT_PNG (0)
#define FORMAT_PPM (1)

FPDF_EXPORT int FPDF_CALLCONV REDPage_Render(FPDF_PAGE page, char const *file_name, int format, float scale);
FPDF_EXPORT int FPDF_CALLCONV REDPage_RenderRect(FPDF_PAGE page, char const *file_name, int format, float scale, const FS_MATRIX *matrix, const FS_RECTF *rect);
FPDF_EXPORT int FPDF_CALLCONV REDPage_RenderRect_Buffer(
  FPDF_PAGE page, float scale, const FS_MATRIX *matrix, const FS_RECTF *rect, unsigned char *buffer, int len
  );

FPDF_EXPORT unsigned int FPDF_CALLCONV REDDoc_GetMetaTextKeyCount(FPDF_DOCUMENT document);
FPDF_EXPORT const char * FPDF_CALLCONV REDDoc_GetMetaTextKeyAt(FPDF_DOCUMENT document, unsigned int index);
FPDF_EXPORT int FPDF_CALLCONV REDDoc_SetMetaItem(FPDF_DOCUMENT document, const char *key, const char *value);
FPDF_EXPORT unsigned int FPDF_CALLCONV REDFormObject_GetObjectCount(FPDF_PAGEOBJECT pFormObj);
FPDF_EXPORT FPDF_PAGEOBJECT FPDF_CALLCONV REDFormObject_GetObjectAt(FPDF_PAGEOBJECT pFormObj, unsigned int index);
FPDF_EXPORT int FPDF_CALLCONV REDFormObject_GetFormMatrix(FPDF_PAGEOBJECT pFormObj, FS_MATRIX *m);
FPDF_EXPORT FPDF_PATHDATA FPDF_CALLCONV REDFont_LoadGlyph(FPDF_FONT font, int char_code);
FPDF_EXPORT int FPDF_CALLCONV REDGlyph_Size(FPDF_PATHDATA path);

FPDF_EXPORT void FPDF_CALLCONV REDGlyph_Get(FPDF_PATHDATA path, int index, FPDF_PATH_POINT *p);
FPDF_EXPORT int FPDF_CALLCONV REDGlyph_GetBounds(FPDF_PATHDATA path, FS_RECTF *out);
FPDF_EXPORT const void * FPDF_CALLCONV REDFont_LoadUnicodeMap(FPDF_FONT font);
FPDF_EXPORT int FPDF_CALLCONV REDFont_WriteUnicodeMap(FPDF_FONT font, unsigned char *buffer, size_t len);
FPDF_EXPORT void FPDF_CALLCONV REDFont_DestroyUnicodeMap(unsigned char *buffer);
FPDF_EXPORT int FPDF_CALLCONV REDDoc_Save(FPDF_DOCUMENT document, char const *filename);

#ifdef __cplusplus
}
#endif

#endif
