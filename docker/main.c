#include <stdio.h>
#include <stdlib.h>
#include <stdarg.h>
#include <dlfcn.h>

void fatal(const char *message, ...) {
    va_list args;
    va_start(args, message);
    vfprintf(stderr, message, args);
    va_end(args);
    exit(-1);
}

const char *filename = "/test/4F2E0N29.pdf";
// const char *filename = "/home/mike/REDSync/testResources/izguts/4F2E0N29.pdf";
const int pageno = 1;
const double bbox[] = {39.5, 695.6811999999999, 446.4780000000001, 718.9611};

int main(int argc, char** argv) {
    typedef long (*fptr)();
    fptr func;
    int rc;
    void *pdf;
    void *page;
    void *tp;
    unsigned short buffer[4096];

    void *handle = dlopen("/home/redstork/pdfium/out/libpdfium.so", RTLD_NOW);
    if (handle == NULL) {
        fatal(dlerror());
    }

    func = (fptr) dlsym(handle, "FPDF_InitLibrary");
    if (!func) {
        fatal(dlerror());
    }
    func(NULL);

    func = (fptr) dlsym(handle, "FPDF_LoadDocument");
    if (!func) {
        fatal(dlerror());
    }
    pdf = (void *) func(filename, NULL);
    if (pdf == NULL) {
        fatal("FPDF_LoadDocument failed: %s\n", filename);
    }
    func = (fptr) dlsym(handle, "FPDF_GetFileVersion");
    if (!func) {
        fatal(dlerror());
    }
    int version = 0;
    rc = func(pdf, &version);
    if (!rc) {
        fatal("FPDF_GetFileVersion failed: %s\n", filename);
    }
    printf("version = %d\n", version);
    func = (fptr) dlsym(handle, "FPDF_LoadPage");
    if (!func) {
        fatal(dlerror());
    }
    page = (void *) func(pdf, (int) (pageno - 1));
    if (page == NULL) {
        fatal("FPDF_LoadPage failed: %s %d\n", filename, pageno);
    }

    func = (fptr) dlsym(handle, "FPDFText_LoadPage");
    if (!func) {
        fatal(dlerror());
    }
    tp = (void *) func(page);
    if (tp == NULL) {
        fatal("FPDFText_LoadPage failed: %s %d\n", filename, pageno);
    }

    func = (fptr) dlsym(handle, "FPDFText_GetBoundedText");
    if (!func) {
        fatal(dlerror());
    }
    rc = func(tp, bbox[0], bbox[1], bbox[2], bbox[3], buffer, 4096);
    printf("rc = %d\n", rc);

    dlclose(handle);
    return 0;
}
