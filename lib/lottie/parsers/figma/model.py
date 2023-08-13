import dataclasses
from ...objects.layers import MatteMode
from ...objects.helpers import BlendMode
from ...utils.color import Color
from ...objects.shapes import LineJoin, LineCap
from ...nvector import NVector


@dataclasses.dataclass
class Transform:
    m00: float = 1.0
    m01: float = 0.0
    m02: float = 0.0
    m10: float = 0.0
    m11: float = 1.0
    m12: float = 0.0


@dataclasses.dataclass(order=True, unsafe_hash=True, frozen=True)
class Id:
    session_id: int
    local_id: int


class FigmaNode:
    def __init__(self):
        self.name = ""
        self.mask = False
        self.mask_type = MatteMode.Alpha
        self.id = None
        self.parent = None
        self.transform = Transform()
        self.visible = True
        self.opacity = 1
        self.blend_mode = BlendMode.Normal


class Document(FigmaNode):
    pass


class Canvas(FigmaNode):
    def __init__(self):
        super().__init__()
        self.background_color = Color()
        self.background_opacity = 1
        self.background_enabled = True


class Shape(FigmaNode):
    def __init__(self):
        super().__init__()
        self.locked = True
        self.dash_pattern = []
        self.stroke_weight = 1
        self.corner_radius = 0
        self.stroke_cap = LineCap.Butt
        self.stroke_join = LineCap.Miter
        self.fill_paints = []
        self.stroke_paints = []
        self.miter_limit = 4


class Frame(Shape):
    pass


class Symbol(Frame):
    pass


class Instance(Shape):
    def __init__(self):
        super().__init__()
        self.symbol_id = None
        self.symbol_overrides = []



class Ellipse(Shape):
    def __init__(self):
        super().__init__()
        self.size = NVector(0, 0)


class RoundedRectangle(Shape):
    def __init__(self):
        super().__init__()
        self.size = NVector(0, 0)
        self.rectangle_top_left_corner_radius = 0
        self.rectangle_top_right_corner_radius = 0
        self.rectangle_bottom_left_corner_radius = 0
        self.rectangle_bottom_right_corner_radius = 0
        self.rectangle_corner_radii_independent = False
        self.rectangle_corner_tool_independent = False


class Star(Shape):
    def __init__(self):
        super().__init__()
        self.size = NVector(0, 0)
        self.count = 3
        self.star_inner_scale = 0.5


class Text(Shape):
    pass


class Vector(Shape):
    def __init__(self):
        super().__init__()
        self.size = NVector(0, 0)


class BooleanOperation(Shape):
    pass


class Section(Shape):
    pass
