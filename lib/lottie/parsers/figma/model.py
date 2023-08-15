import re
import math
import dataclasses
import PIL.Image

from . import schema
from .file import FigmaFile


class Converter:
    def to_figma_file(self, nodes):
        self.file = FigmaFile()
        self.file.schema = FigmaFile.default_schema()
        self.message = schema.Message(
            type=schema.MessageType.NODE_CHANGES,
            sessionID=0,
            ackID=0,
            nodeChanges=[],
            blobs=[]
        )
        self.file.data = self.message
        self.node_ids = {}
        self.next_global_id = 0
        self.file.thumbnail = PIL.Image.new("RGBA", (512, 512))

        for node in nodes:
            self.add_node(node)

        return self.file

    def guid(self, node: "FigmaNode"):
        guid = self.node_ids.get(id(node), None)
        if guid is not None:
            return guid

        if node.parent is None:
            session = 0
        else:
            parent = self.guid(node.parent)
            session = parent.localID

        local = self.next_global_id
        self.next_global_id += 1

        guid = schema.GUID(session, local)
        self.node_ids[id(node)] = guid
        return guid

    def add_node(self, node):
        nc = schema.NodeChange(
            guid=self.guid(node),
            phase=schema.NodePhase.CREATED,
            type=getattr(schema.NodeType, re.sub("([a-z])([A-Z])", r"\1_\2", type(node).__name__).upper()),
        )

        if node.parent:
            nc.parentIndex = schema.ParentIndex(
                guid=self.guid(node.parent),
                position="!"
            )

        for pname, pval in vars(node).items():
            if pname not in ("children", "parent"):
                setattr(nc, pname, pval)

        self.message.nodeChanges.append(nc)

        for child in node.children:
            self.add_node(child)


def identity_transform():
    return schema.Matrix(
        m00=1.0,
        m01=0.0,
        m02=0.0,
        m10=0.0,
        m11=1.0,
        m12=0.0,
    )


class FigmaNode:
    def __init__(self):
        self.parent = None
        self.children = []

        self.name = ""
        self.mask = False
        self.maskType = schema.MaskType.ALPHA
        self.blendMode = schema.BlendMode.PASS_THROUGH
        self.transform = identity_transform()
        self.visible = True
        self.opacity = 1

    def add_child(self, node):
        node.parent = self
        self.children.append(node)
        return node


class Document(FigmaNode):
    def __init__(self):
        super().__init__()
        self.maskIsOutline = False
        self.documentColorProfile = schema.DocumentColorProfile.SRGB

    def to_figma_file(self):
        c = Converter()
        return c.to_figma_file([self])


class Canvas(FigmaNode):
    def __init__(self):
        super().__init__()
        self.maskIsOutline = False
        self.backgroundColor = schema.Color(
            FigmaFile.default_gray_value,
            FigmaFile.default_gray_value,
            FigmaFile.default_gray_value,
            1
        )
        self.backgroundOpacity = 1
        self.backgroundEnabled = True


class Drawable(FigmaNode):
    def __init__(self):
        super().__init__()
        self.locked = True
        self.dashPattern = []
        self.strokeWeight = 1
        self.cornerRadius = 0
        self.strokeAlign = schema.StrokeAlign.INSIDE
        self.strokeCap = schema.StrokeCap.NONE
        self.strokeJoin = schema.StrokeJoin.MITER
        self.fillPaints = []
        self.strokePaints = []
        self.miterLimit = 4


class Frame(Drawable):
    pass


class Symbol(Frame):
    pass


class Instance(Drawable):
    def __init__(self):
        super().__init__()
        self.symbolId = None
        self.symbolOverrides = []


class Shape(Drawable):
    def __init__(self):
        super().__init__()
        self.size = schema.Vector(0, 0)


class Ellipse(Shape):
    def __init__(self):
        super().__init__()
        self.arcData = schema.ArcData(
            startingAngle=0,
            endingAngle=2 * math.pi,
            innerRadius=0
        )


class Line(Shape):
   pass


class RoundedRectangle(Shape):
    def __init__(self):
        super().__init__()
        self.rectangleTopLeftCornerRadius = 0
        self.rectangleTopRightCornerRadius = 0
        self.rectangleBottomLeftCornerRadius = 0
        self.rectangleBottomRightCornerRadius = 0
        self.rectangleCornerRadiiIndependent = False
        self.rectangleCornerToolIndependent = False


class RegularPolygon(Shape):
    def __init__(self):
        super().__init__()
        self.count = 3


class Star(Shape):
    def __init__(self):
        super().__init__()
        self.count = 3
        self.starInnerScale = 0.5


class Text(Shape):
    pass


class Vector(Shape):
    pass


class BooleanOperation(Shape):
    pass


class Section(Shape):
    pass


def SolidPaint(color, opacity=1):
    return schema.Paint(
        type=schema.PaintType.SOLID,
        color=color,
        opacity=opacity,
        visible=True,
        blendMode=schema.BlendMode.NORMAL
    )
