
try:
    from .so import so, FPDF_RECT, FPDF_MATRIX
except OSError:
    print('Failed to load shared library')
    class DummySO:
        def __getattr__(self, name):
            raise RuntimeError('dynamic library failed to load')
    so = DummySO()
    FPDF_RECT = None
    FPDF_MATRIX = None

