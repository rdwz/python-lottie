import math

from . import model, schema, enum_mapping
from ... import objects
from ...nvector import NVector
from ...utils.transform import TransformMatrix
from ...utils.color import Color
from ...utils.binstream import BinStream, Endian


def transform_to_lottie(obj: schema.Matrix, transform=None):
    if transform is None:
        transform = objects.helpers.Transform()

    matrix = None

    if obj is not None:
        matrix = TransformMatrix()
        matrix.a = obj.m00
        matrix.b = obj.m10
        matrix.c = obj.m01
        matrix.d = obj.m11
        matrix.tx = obj.m02
        matrix.ty = obj.m12
        structure = matrix.extract_transform()
        transform.position.value = structure["translation"]
        transform.rotation.value = structure["angle"] * 180 / math.pi
        transform.scale.value = structure["scale"] * 100

    return transform, matrix


class NodeItem:
    def __init__(self, map: "NodeMap", figma: "schema.NodeChange"):
        self.figma = figma
        self.lottie = None
        self.parent = None
        self.children = []
        self.map = map

    @property
    def type(self):
        return self.figma.type


class NodeMap:
    def __init__(self, schema):
        self.nodes = {}
        self.blobs = []
        self.document = None
        self.schema = schema

    def node(self, id: schema.GUID, add_missing=True):
        id = self.id(id)
        node = self.nodes.get(id)

        if node is None and add_missing:
            self.nodes[id] = node = NodeItem(self, None)

        return node

    def id(self, id: schema.GUID):
        return (id.sessionID, id.localID)

    def add_node(self, node: schema.NodeChange):
        item = self.node(node.guid)
        item.figma = node
        return item

    def process_change(self, node: schema.NodeChange):
        item = self.add_node(node)
        if item.figma.parentIndex:
            item.parent = self.node(item.figma.parentIndex.guid, False)
            if item.parent:
                item.parent.children.append(item)
        return item

    def process_message(self, message: schema.Message):
        if message.nodeChanges is not None:
            for node in message.nodeChanges:
                item = self.process_change(node)
                if node.type == self.schema.NodeType.DOCUMENT:
                    self.document = item

        if message.blobs:
            for blob in message.blobs:
                self.blobs.append(blob.bytes)


def message_to_lottie(message, kiwi_schema=schema):
    nodes = NodeMap(kiwi_schema)
    nodes.process_message(message)
    if not nodes.document:
        return objects.animation.Animation()
    return document_to_lottie(nodes.document)


def document_to_lottie(node: NodeItem):
    anim = objects.animation.Animation()
    parsed_main = False

    for canvas in node.children:
        if canvas.type != node.map.schema.NodeType.CANVAS or canvas.figma.name == "Internal Only Canvas":
            continue

        if not parsed_main:
            canvas_to_comp(canvas, anim)
            parsed_main = True
        else:
            comp = objects.composition.Composition()
            anim.assets.append(comp)
            canvas_to_comp(canvas, comp)

    return anim


def canvas_to_comp(canvas: NodeItem, comp: objects.composition.Composition):
    comp.name = canvas.figma.name
    canvas.lottie = comp

    adj = objects.layers.NullLayer()
    adj.name = "Page adjustment"
    adj.index = 0
    comp.add_layer(adj)
    bounding_points = []

    for child in reversed(canvas.children):
        figma_to_lottie_layer(child, comp, adj.index, bounding_points)

    if bounding_points:
        bb = objects.shapes.BoundingBox()
        for p in bounding_points:
            bb.include(p.x, p.y)

        comp.width = math.ceil(bb.width)
        comp.height = math.ceil(bb.height)
        adj.transform.position.value = NVector(-bb.x1, -bb.y1)


def figma_to_lottie_layer(node: NodeItem, comp: objects.composition.Composition, parent_index, bounding_points):
    NodeType = node.map.schema.NodeType

    match node.type:
        case NodeType.TEXT:
            layer = objects.layers.TextLayer()
            # TODO
        case NodeType.MEDIA:
            layer = objects.layers.ImageLayer()
            # TODO
        case _:
            shape = figma_to_lottie_shape(node, bounding_points)
            if shape is None:
                return None
            layer = objects.layers.ShapeLayer()
            layer.shapes.append(shape)

    layer.name = node.figma.name
    node.lottie = layer
    layer.index = len(comp.layers)
    comp.add_layer(layer)
    layer.parent_index = parent_index
    for child in node.children:
        figma_to_lottie_layer(child, comp, layer.index, bounding_points)

    return layer


def figma_to_lottie_shape(node: NodeItem, bounding_points):
    NodeType = node.map.schema.NodeType
    points = []

    match node.type:
        case NodeType.ELLIPSE:
            shape = ellipse_to_lottie(node)
        case NodeType.CANVAS:
            shape = canvas_to_group(node, points)
        case NodeType.VECTOR:
            shape = vector_shape_to_lottie(node)
        case NodeType.RECTANGLE | NodeType.ROUNDED_RECTANGLE | NodeType.SECTION:
            shape = rect_to_lottie(node)
        # TODO
        # case NodeType.STAR:
            # shape = star_to_lottie(node)
        # case NodeType.BOOLEAN_OPERATION:
            # shape = boolean_to_lottie(node)
        # case NodeType.REGULAR_POLYGON:
            # shape = polygon_to_lottie(node)
        # case NodeType.LINE:
            # shape = line_to_lottie(node)
        case _:
            shape = None

    if shape is None:
        return None

    shape.name = node.figma.name

    if not isinstance(shape, objects.shapes.Group):
        group = objects.shapes.Group()
        group.add_shape(shape)
        shape_style_to_lottie(node, group)
        shape = group
        shape.name = node.figma.name
        points = [
            NVector(0, 0),
            NVector(node.figma.size.x, 0),
            NVector(node.figma.size.x, node.figma.size.y),
            NVector(0, node.figma.size.y)
        ]

    if node.figma.blendMode is not None:
        shape.blend_mode = enum_mapping.blend_mode.to_lottie(node.figma.blendMode)

    matrix = transform_to_lottie(node.figma.transform, shape.transform)[1]
    for point in points:
        bounding_points.append(matrix.apply(point))

    node.lottie = shape
    return shape


def color_to_lottie(color: schema.Color):
    if color is None:
        return Color(), 0
    return Color(color.r, color.g, color.b, 1), color.a


def shape_style_to_lottie(node: NodeItem, group: objects.shapes.Group):
    if node.figma.fillPaints:
        for paint in node.figma.fillPaints:
            match paint.type:
                case node.map.schema.PaintType.GRADIENT_LINEAR:
                    shape = objects.shapes.GradientFill()
                    # TODO
                case node.map.schema.PaintType.GRADIENT_RADIAL:
                    shape = objects.shapes.GradientFill()
                    # TODO
                case node.map.schema.PaintType.SOLID:
                    shape = objects.shapes.Fill()
                    shape.color.value, shape.opacity.value = color_to_lottie(paint.color)
                    shape.opacity.value *= 100
                case _:
                    continue

            if paint.opacity is not None:
                shape.opacity.value *= paint.opacity

            shape.blend_mode = enum_mapping.blend_mode.to_lottie(paint.blendMode)
            group.add_shape(shape)

    if node.figma.strokePaints:
        for paint in node.figma.fillPaints:
            match paint.type:
                case node.map.schema.PaintType.GRADIENT_LINEAR:
                    shape = objects.shapes.GradientStroke()
                    # TODO
                case node.map.schema.PaintType.GRADIENT_RADIAL:
                    shape = objects.shapes.GradientStroke()
                    # TODO
                case node.map.schema.PaintType.SOLID:
                    shape = objects.shapes.Stroke()
                    shape.color.value, shape.opacity.value = color_to_lottie(paint.color)
                    shape.opacity.value *= 100
                case _:
                    continue

            if paint.opacity is not None:
                shape.opacity.value *= paint.opacity

            shape.blend_mode = enum_mapping.blend_mode.to_lottie(paint.blendMode)
            group.add_shape(shape)

            shape.line_cap = enum_mapping.line_cap.to_lottie(node.figma.strokeCap)
            shape.line_join = enum_mapping.line_join.to_lottie(node.figma.strokeJoin)
            shape.width.value = node.figma.strokeWeight or 0


def vector_to_lottie(value: schema.Vector):
    return NVector(value.x, value.y)


def ellipse_to_lottie(node: NodeItem):
    shape = objects.shapes.Ellipse()
    shape.size.value = vector_to_lottie(node.figma.size)
    shape.position.value = shape.size.value / 2
    return shape


def rect_to_lottie(node: NodeItem):
    shape = objects.shapes.Rect()
    shape.size.value = vector_to_lottie(node.figma.size)
    shape.position.value = shape.size.value / 2
    return shape


def blob_to_bezier(blob: bytes):
    bez = objects.bezier.Bezier()
    f = BinStream(blob, Endian.Little)

    point_count = f.read_uint32()
    seg_count = f.read_uint32()
    f.skip(4)
    bez.closed = seg_count == point_count
    bez.node_types = ""

    for i in range(point_count):
        mirror = f.read_uint32()
        if mirror == 1:
            bez.node_types += "s"
        elif mirror == 2:
            bez.node_types += "z"
        else:
            bez.node_types += "c"

        x = f.read_float32()
        y = f.read_float32()
        bez.add_point(NVector(x, y))

    for i in range(seg_count):
        f.skip(4)

        p = f.read_uint32()
        x = f.read_float32()
        y = f.read_float32()
        bez.out_tangents[p] = NVector(x, y)

        p = f.read_uint32()
        x = f.read_float32()
        y = f.read_float32()
        bez.in_tangents[p] = NVector(x, y)

    return bez

def vector_shape_to_lottie(node: NodeItem):
    shape = objects.shapes.Path()

    if node.figma.vectorData and node.figma.vectorData.vectorNetworkBlob is not None:
        blob = node.map.blobs[node.figma.vectorData.vectorNetworkBlob]
        shape.shape.value = blob_to_bezier(blob)

    return shape


def canvas_to_group(node: NodeItem, bounding_points):
    group = objects.shapes.Group()

    for child in reversed(node.children):
        shape = figma_to_lottie_shape(child, bounding_points)
        if shape:
            group.add_shape(shape)

    return group
