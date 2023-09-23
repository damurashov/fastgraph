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
    outline_selected_thickness = 6


class _CanvasProperties:
    allow_overlapping_node_creation = False
    """
    If allowed, clicking on a node will create a new one. Warning: with this
    option set to True, the behavior is undefined.
    """


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

    def get_closest_object_identifiers_at(self, x, y):
        """
        See `find_closest` in Tkiter documentation. Used in event processing.
        """
        return self.find_closest(x, y)

    def select_node(self, node_id):
        """
        Redraws a specified node as selected
        """
        self.itemconfig(node_id, outline=self._node_properties.outline_selected_color,
            width=self._node_properties.outline_selected_thickness)
        fastgraph.logging.info(Canvas._LOG_CONTEXT,
            f"on_node_clicked: selected node id={node_id}")

    def on_node_left_button_clicked(self, event, node_id):
        fastgraph.logging.debug(Canvas._LOG_CONTEXT, f"on_node_clicked: {event} node id={node_id}")

        # Draw the node as selected
        self.select_node(node_id)
        fastgraph.logging.info(Canvas._LOG_CONTEXT,
            f"on_node_clicked: selected node id={node_id} at {event.x, event.y}")

    def get_objects_at(self, x, y, width=1, height=1):
        """
        Returns overlapping objects at a given coordinate. Used for collision
        detection.
        """
        overlapping_objects = self.find_overlapping(x, y, x + width, y + height)

        return overlapping_objects

    def add_node_at(self, x, y):
        node_bounding_rectangle = ((x, y),
            (x + self._node_properties.size_pixels, y + self._node_properties.size_pixels))
        node = self.create_oval(node_bounding_rectangle, fill=self._node_properties.color)

        # Capture the context in a function, so we won't have to search for the node ID using geometrical match
        def __on_node_left_button_clicked_context(event):
            """
            Side effect: if the click "goes through", stacked nodes will
            probably be selected.
            """
            self.on_node_left_button_clicked(event, node)

        self.tag_bind(node, _Tkinter.MOUSE_BUTTON_LEFT, __on_node_left_button_clicked_context)
        fastgraph.logging.info(Canvas._LOG_CONTEXT, f"add_node_at: new node at ({x}, {y}) id={node}")

    def on_left_button_clicked_canvas(self, event):
        """
        Gets invoked each time user clicks on a canvas. Depending on the current
        `self._mode`, the appropriate handler is invoked.
        """
        fastgraph.logging.debug(Canvas._LOG_CONTEXT, f"got event {event}")

        if self._mode == _CanvasMode.DRAWING:
            overlapping_objects = self.get_objects_at(event.x, event.y)
            fastgraph.logging.debug(Canvas._LOG_CONTEXT,
                f"overlapping ojects at {(event.x, event.y)}: {overlapping_objects}")

            if len(overlapping_objects) != 0:
                fastgraph.logging.warning(Canvas._LOG_CONTEXT, f"Got overlapping objects at {(event.x, event.y)}")

            if len(overlapping_objects) == 0 or self._properies.allow_overlapping_node_creation:
                self.add_node_at(event.x, event.y)
            else:
                fastgraph.logging.info(Canvas._LOG_CONTEXT,
                    f"Found collision at {(event.x, event.y)}. Creating collided nodes is not allowed. Skipping")


class InteractiveTest(unittest.TestCase):

    def test_use_canvas(self):
        root = tkinter.Tk()
        canvas = Canvas(root, width=400, height=300, bg="white")
        canvas.pack(fill=tkinter.BOTH, expand=True)
        canvas.set_drawing_mode()
        root.mainloop()
