import qtx
import trio
import triq
from izpdf_qt.pageview2 import PageModel, REDView
from izutil.eventbus import Signal
import tempfile


class PdfPageModel(PageModel):
    def __init__(self, pdf_page):
        super().__init__()
        self._pdf_page = pdf_page
        self._cropbox = pdf_page.crop_box

    def cropbox(self):
        return self._cropbox

    async def render_at(self, scale):
        with tempfile.NamedTemporaryFile() as f:
            await trio.to_thread.run_sync(self._pdf_page.render, f.name, scale)
            image =  qtx.QImage(f.name)
            return image


if __name__ == '__main__':
    import os
    from red import RED_Document
    from redwidgets.unhandled_error_presenter import UnhandledErrorPresenter
    from redwidgets.dialogs import Dialogs

    class DummyModel:
        changed = Signal()

        def __init__(self):
            self._image = qtx.QImage('/home/mike/tmp/repo2/pdfium/pdfium_red/test_002.ppm')
            sz = self._image.size()
            self._cropbox = 0, 0, sz.width(), sz.height()

        def cropbox(self):
            return self._cropbox

        async def render_at(self, scale):
            await trio.sleep(0.3)
            return self._image

    def draw_rect(scene):
        rect = qtx.QGraphicsRectItem(qtx.QRectF(0., 0., 100, 200))
        scene.addItem(rect)

    fname = os.path.expanduser('~/REDSync/testResources/izguts/9783642049415.pdf')
    doc = RED_Document(fname)
    assert len(doc) > 0

    app = qtx.QApplication([])

    dialogs = Dialogs()
    uep = UnhandledErrorPresenter(None, dialogs)

    main = qtx.QMainWindow()
    main._toolbar = qtx.QToolBar(main)
    main.addToolBar(main._toolbar)

    exit_action = qtx.QAction('Exit')
    exit_action.triggered.connect(triq.exit)
    main._toolbar.addAction(exit_action)

    view = REDView(parent=main, upside_down=True)
    main.setCentralWidget(view)
    main.__view = view

    view.model = PdfPageModel(doc[0])
    view.pageno = 0

    prev_page_action = qtx.QAction('<')
    def prev_page():
        if view.pageno > 0:
            view.pageno -= 1
            view.model = PdfPageModel(doc[view.pageno])
            draw_rect(view.scene())
    prev_page_action.triggered.connect(prev_page)
    main._toolbar.addAction(prev_page_action)

    next_page_action = qtx.QAction('>')
    def next_page():
        if view.pageno < len(doc) - 1:
            view.pageno += 1
            view.model = PdfPageModel(doc[view.pageno])
            draw_rect(view.scene())
    next_page_action.triggered.connect(next_page)
    main._toolbar.addAction(next_page_action)

    zoom_in_action = qtx.QAction('Zoom In')
    def zoom_in():
        view.scale = view.scale * 1.2
    zoom_in_action.triggered.connect(zoom_in)
    main._toolbar.addAction(zoom_in_action)

    zoom_out_action = qtx.QAction('Zoom Out')
    def zoom_out():
        view.scale = view.scale / 1.2
    zoom_out_action.triggered.connect(zoom_out)
    main._toolbar.addAction(zoom_out_action)

    rotate_right_action = qtx.QAction('Rotate Right')
    def rotate_right():
        view.rotation = (view.rotation + 1) % 4
    rotate_right_action.triggered.connect(rotate_right)
    main._toolbar.addAction(rotate_right_action)

    rotate_left_action = qtx.QAction('Rotate Left')
    def rotate_left():
        view.rotation = (view.rotation + 3) % 4
    rotate_left_action.triggered.connect(rotate_left)
    main._toolbar.addAction(rotate_left_action)

    draw_rect(view.scene())

    main.show()

    triq.run(app)
