import re
import math
import enum
import struct
import dataclasses
import PIL.Image

from . import schema
from .file import FigmaFile
from ...objects import bezier


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
        nc = node.to_node_change(self)

        self.message.nodeChanges.append(nc)

        for child in node.children:
            self.add_node(child)

    def blob(self, data):
        blob = schema.Blob(bytes=data)
        id = len(self.message.blobs)
        self.message.blobs.append(blob)
        return id


def identity_transform():
    return schema.Matrix(
        m00=1.0,
        m01=0.0,
        m02=0.0,
        m10=0.0,
        m11=1.0,
        m12=0.0,
    )


def translated(matrix, x, y):
    matrix = dataclasses.replace(matrix)
    matrix.m02 += x
    matrix.m12 += y


def camel_to_caps(text):
    return re.sub("([a-z])([A-Z])", r"\1_\2", text).upper()


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
        if node is None:
            return None
        node.parent = self
        self.children.append(node)
        return node

    def node_change_type(self):
        return camel_to_caps(type(self).__name__)

    def node_change_ignore(self):
        return ("children", "parent")

    def to_node_change(self, converter):
        nc = schema.NodeChange(
            guid=converter.guid(self),
            phase=schema.NodePhase.CREATED,
            type=getattr(schema.NodeType, self.node_change_type()),
        )

        if self.parent:
            nc.parentIndex = schema.ParentIndex(
                guid=converter.guid(self.parent),
                position="!"
            )

        for pname, pval in vars(self).items():
            if pname not in self.node_change_ignore():
                setattr(nc, pname, pval)

        return nc


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
        self.locked = False
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
    def __init__(self):
        super().__init__()
        self.bezier = Bezier()

    def node_change_ignore(self):
        return super().node_change_ignore() + ("bezier", "size")

    def to_node_change(self, converter):
        nc = super().to_node_change(converter)

        nc.vectorData = schema.VectorData(
            vectorNetworkBlob=converter.blob(self.bezier.to_blob())
        )

        if self.bezier.points:
            p = self.bezier.points[0].vertex

            nc.transform = translated(nc.transform, p.x, p.y)

            minp = schema.Vector(p.x, p.y)
            maxp = schema.Vector(p.x, p.y)
            for p in self.bezier.points:
                if p.vertex.x < minp.x:
                    minp.x = p.vertex.x
                if p.vertex.y < minp.y:
                    minp.y = p.vertex.y
                if p.vertex.x > maxp.x:
                    maxp.x = p.vertex.x
                if p.vertex.y > maxp.y:
                    maxp.y = p.vertex.y

            if nc.size and nc.size.x == 0 and nc.size.y == 0:
                nc.size = schema.Vector(maxp.x - minp.x, maxp.y - minp.y)

            nc.vectorData.normalizedSize = nc.size

        return nc


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


class BezierTangentMirror(enum.Enum):
    NoMirror = 0
    Angle = 1
    AngleLength = 2


class BezierPoint(bezier.BezierPoint):
    def __init__(self, vertex, in_tangent=None, out_tangent=None):
        super().__init__(vertex, in_tangent, out_tangent)
        self.mirror = BezierTangentMirror.NoMirror


class Bezier:
    def __init__(self):
        self.points = []
        self.closed = False

    def add_point(self, vertex, in_tangent=None, out_tangent=None):
        p = BezierPoint(vertex, in_tangent, out_tangent)
        self.points.append(p)
        return p

    def close(self):
        self.closed = True

    def to_blob(self):
        data = b''

        data += struct.pack("<i", len(self.points))
        n_segs = len(self.points)
        if not self.closed:
            n_segs -= 1
        data += struct.pack("<i", n_segs)
        data += struct.pack("<i", 0)

        if len(self.points) > 0:
            delta = self.points[0].vertex

            for p in self.points:
                data += struct.pack("<i", p.mirror.value)
                data += struct.pack("<f", p.vertex.x - delta.x)
                data += struct.pack("<f", p.vertex.y - delta.y)

            for segment_index in range(n_segs):
                data += struct.pack("<i", 0)

                data += struct.pack("<i", segment_index)
                p = self.points[segment_index]
                data += struct.pack("<f", p.out_tangent.x)
                data += struct.pack("<f", p.out_tangent.y)

                segment_index = (segment_index + 1) % len(self.points)
                data += struct.pack("<i", segment_index)
                p = self.points[segment_index]
                data += struct.pack("<f", p.in_tangent.x)
                data += struct.pack("<f", p.in_tangent.y)

        return data
