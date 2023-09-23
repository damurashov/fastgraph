import fastgraph.logging
import tkinter
import tkinter.ttk
import unittest


_LOG_CONTEXT = "canvas"


class _Tkinter:
    MOUSE_BUTTON_LEFT = "<Button-1>"
    MOUSE_BUTTON_LEFT_RELEASED = "<ButtonRelease-1>"
    COLOR_BLACK = "black"
    COLOR_WHITE = "white"
    COLOR_RED = "red"


class _CanvasMode:
    """
    See `Canvas
    """
    VIEWING = 0
    DRAWING = 1


class _CanvasNodeProperties:
    size_pixels = 20
    color = _Tkinter.COLOR_BLACK
    outline_selected_color = _Tkinter.COLOR_RED
    outline_selected_thicknesss = 2


class _CanvasProperties:
    allow_overlapping_node_creation = False


class Canvas(tkinter.Canvas):
    _LOG_CONTEXT = f"fastgraph.{_LOG_CONTEXT}.Canvas"

    def __init__(self, *args, **kwargs):
        tkinter.Canvas.__init__(self, *args, **kwargs)
        # Set default mode
        self._mode = _CanvasMode.VIEWING

        # Set default node properties
        self._node_properties = _CanvasNodeProperties()

        # Bind left mouse click
        self.bind(_Tkinter.MOUSE_BUTTON_LEFT, self.on_left_button_clicked_canvas)

        # Create default _CanvasNodeProperties
        self._properies = _CanvasProperties()

    def set_drawing_mode(self):
        """
        The canvas gets switched into drawing mode: a user may draw nodes
        """
        self._mode = _CanvasMode.DRAWING

    def on_node_clicked(self, event):
        fastgraph.logging.debug(Canvas._LOG_CONTEXT, f"on_node_clicked: {event}")

    def get_objects_at(self, x, y, width=1, height=1):
        """
        Returns overlapping objects at a given coordinate
        """
        overlapping_objects = self.find_overlapping(x, y, x + width, y + height)

        return overlapping_objects

    def add_node_at(self, x, y):
        node_bounding_rectangle = ((x, y), (x + self._node_properties.size_pixels, y + self._node_properties.size_pixels))
        node = self.create_oval(node_bounding_rectangle, fill=self._node_properties.color)
        self.tag_bind(node, _Tkinter.MOUSE_BUTTON_LEFT, self.on_node_clicked)
        fastgraph.logging.info(Canvas._LOG_CONTEXT, f"add_node_at: new node at ({x}, {y}) id={node}")

    def on_left_button_clicked_canvas(self, event):
        """
        Gets invoked each time user clicks on a canvas. Depending on the current
        `self._mode`, the appropriate handler is invoked.
        """
        fastgraph.logging.debug(Canvas._LOG_CONTEXT, f"got event {event}")

        if self._mode == _CanvasMode.DRAWING:
            overlapping_objects = self.get_objects_at(event.x, event.y)

            if len(overlapping_objects) == 0 or self._properies.allow_overlapping_node_creation:
                self.add_node_at(event.x, event.y)
            else:
                fastgraph.logging.info(Canvas._LOG_CONTEXT, f"Found collision at {(event.x, event.y)}. Creating collided nodes is not allowed. Skipping")


class InteractiveTest(unittest.TestCase):

    def test_use_canvas(self):
        root = tkinter.Tk()
        canvas = Canvas(root, width=400, height=300, bg="white")
        canvas.pack(fill=tkinter.BOTH, expand=True)
        canvas.set_drawing_mode()
        root.mainloop()
