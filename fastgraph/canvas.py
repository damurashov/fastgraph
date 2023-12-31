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

    fill_color = _Tkinter.COLOR_BLACK
    """ Fill color """

    outline_color_default = None
    outline_thickness_default = 0
    outline_color_selected = _Tkinter.COLOR_RED
    outline_thickness_selected = 6


class _CanvasEdgeProperties:
    fill_color_default = _Tkinter.COLOR_BLACK
    fill_color_selected = _Tkinter.COLOR_RED
    line_thickness = 6


class _CanvasProperties:
    allow_overlapping_node_creation = False
    """
    If allowed, clicking on a node will create a new one. Warning: with this
    option set to True, the behavior is undefined.
    """

    collision_area_scale_factor = 1.3
    """ The higher this value is, the wider the area around an existing node when no new nodes can be created"""

    auto_create_edge_between_2_selected_nodes = True

    allow_multigraph = False
    """ Allow multiple edges between the same nodes TODO """


class Canvas(tkinter.Canvas):
    _LOG_CONTEXT = f"fastgraph.{_LOG_CONTEXT}.Canvas"

    def __init__(self, *args, **kwargs):
        tkinter.Canvas.__init__(self, *args, **kwargs)
        # Set default mode
        self._mode = _CanvasMode.VIEWING

        # Set default node properties
        self._node_properties = _CanvasNodeProperties()

        # Create default _CanvasNodeProperties
        self._properies = _CanvasProperties()

        # Create default edge properties
        self._edge_properties = _CanvasEdgeProperties()

        # Bind left mouse click
        self.bind(_Tkinter.MOUSE_BUTTON_LEFT, self.on_canvas_left_button_clicked)

        # List of selected nodes. The order matters: it represents a sequence in which those have been selected
        self._selected_node_identifiers = list()

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

    def apply_node_style_selected(self, node_id):
        self.itemconfig(node_id, outline=self._node_properties.outline_color_selected,
            width=self._node_properties.outline_thickness_selected, fill=self._node_properties.fill_color)

    def apply_node_style_default(self, node_id):
        self.itemconfig(node_id, outline=self._node_properties.outline_color_default,
            width=self._node_properties.outline_thickness_default, fill=self._node_properties.fill_color)

    def is_node_selected(self, node_id):
        return node_id in self._selected_node_identifiers

    def unselect_node(self, node_id):
        """
        Redraws a specified node, removes it from the list of selected nodes
        """
        fastgraph.logging.info(Canvas._LOG_CONTEXT,
            f"Unselected node id={node_id} at {self.coords(node_id)}")
        self._selected_node_identifiers = list(filter(lambda i: i != node_id, self._selected_node_identifiers))
        self.apply_node_style_default(node_id)

    def select_node(self, node_id):
        """
        Redraws a specified node as selected
        """
        fastgraph.logging.info(Canvas._LOG_CONTEXT,
            f"Selected node id={node_id} at {self.coords(node_id)}")
        self._selected_node_identifiers.append(node_id)
        self.apply_node_style_selected(node_id)

    def unselect_all_nodes(self):
        while len(self._selected_node_identifiers) > 0:
            self.unselect_node(self._selected_node_identifiers[0])

        fastgraph.logging.info(Canvas._LOG_CONTEXT, "Unselected all nodes")

    def on_node_left_button_clicked(self, event, node_id):
        fastgraph.logging.debug(Canvas._LOG_CONTEXT, f"on_node_left_button_clicked: {event} node id={node_id}")

        if self._mode == _CanvasMode.DRAWING:
            # Draw the node as selected
            if self.is_node_selected(node_id):
                self.unselect_node(node_id)
            else:
                self.select_node(node_id)

            # 2 nodes have been selected in drawing mode. Create an edge between them
            if len(self._selected_node_identifiers) == 2 and self._properies.auto_create_edge_between_2_selected_nodes:
                self.add_edge(self._selected_node_identifiers[0], self._selected_node_identifiers[1])
                self.unselect_all_nodes()

    def get_objects_at(self, x, y, width=1, height=1):
        """
        Returns overlapping objects at a given coordinate. Used for collision
        detection.
        """
        overlapping_objects = self.find_overlapping(x, y, x + width, y + height)

        return overlapping_objects

    def get_colliding_objects_at(self, x, y):
        area_size_pixels = int(self._node_properties.size_pixels * self._properies.collision_area_scale_factor)

        # Get some space around the coordinates
        x = x - int(area_size_pixels / 2)
        y = y - int(area_size_pixels / 2)

        if x < 0:
            x = 0

        if y < 0:
            y = 0

        return self.get_objects_at(x, y, area_size_pixels, area_size_pixels)

    def add_node_at(self, x, y):
        """
        Creates a new node at provided coordinates. Returns the created node's id
        """

        # Center created node on cursor position
        starting_coordinate = [x - int(self._node_properties.size_pixels / 2),
            y - int(self._node_properties.size_pixels / 2)]

        if starting_coordinate[0] < 0:
            starting_coordinate[0] = 0

        if starting_coordinate[1] < 0:
            starting_coordinate[1] = 0

        node_bounding_rectangle = (tuple(starting_coordinate),
            (x + self._node_properties.size_pixels, y + self._node_properties.size_pixels))
        node_id = self.create_oval(node_bounding_rectangle, fill=self._node_properties.fill_color)
        self.apply_node_style_default(node_id)

        # Capture the context in a function, so we won't have to search for the node ID using geometrical match
        def __on_node_left_button_clicked_context(event):
            """
            Side effect: if the click "goes through", stacked nodes will
            probably be selected.
            """
            self.on_node_left_button_clicked(event, node_id)

        self.tag_bind(node_id, _Tkinter.MOUSE_BUTTON_LEFT, __on_node_left_button_clicked_context)
        fastgraph.logging.info(Canvas._LOG_CONTEXT, f"add_node_at: new node at ({x}, {y}) id={node_id}")

        return node_id

    def get_object_center_coordinates(self, object_id):
        coordinates = self.coords(object_id)
        x = int((coordinates[2] + coordinates[0]) / 2)
        y = int((coordinates[3] + coordinates[1]) / 2)

        return x, y

    def apply_edge_style_default(self, edge_id):
        self.itemconfig(edge_id, width=self._edge_properties.line_thickness,
            fill=self._edge_properties.fill_color_default)

    def apply_edge_style_selected(self, edge_id):
        pass  # TODO

    def on_edge_left_button_clicked(self, event, edge_id):
        pass  #TODO

    def add_edge(self, node_a_id, node_b_id):
        # Create and render the edge
        # TODO: prevent from creating existing nodes (see `allow_multigraph`)
        start_coordinates = self.get_object_center_coordinates(node_a_id)
        end_coordinates = self.get_object_center_coordinates(node_b_id)
        edge_id = self.create_line(start_coordinates, end_coordinates, width=self._edge_properties.line_thickness,
            fill=self._edge_properties.fill_color_default)
        self.apply_edge_style_default(edge_id)

        # Move the edge at the bottom of the stack, so each new node will be drawn upon it
        self.lower(edge_id)

        # Add hooks on user actions with the edge
        on_edge_left_button_clicked_context_capture = lambda event: self.on_edge_left_button_clicked(event, edge_id)  # A context-capturing lambda
        self.tag_bind(edge_id, _Tkinter.MOUSE_BUTTON_LEFT, on_edge_left_button_clicked_context_capture)
        fastgraph.logging.info(Canvas._LOG_CONTEXT,
            f"Added edge {edge_id} between nodes {(node_a_id, node_b_id)} start {start_coordinates} end {end_coordinates}")

        return edge_id

    def on_canvas_left_button_clicked(self, event):
        """
        Gets invoked each time user clicks on a canvas. Depending on the current
        `self._mode`, the appropriate handler is invoked.
        """
        fastgraph.logging.info(Canvas._LOG_CONTEXT, f"Left button click at {(event.x, event.y)}")

        if self._mode == _CanvasMode.DRAWING:
            overlapping_objects = self.get_colliding_objects_at(event.x, event.y)
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
