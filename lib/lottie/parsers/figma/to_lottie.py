import math
import bisect
import urllib.request

from . import model, schema, enum_mapping
from ... import objects
from ...nvector import NVector
from ...utils.transform import TransformMatrix
from ...utils.color import Color
from ...utils.binstream import BinStream, Endian


def transform_to_lottie(obj: schema.Matrix, transform=None):
    if transform is None:
        transform = objects.helpers.Transform()

    matrix = TransformMatrix()

    if obj is not None:
        transform.position.value = NVector(obj.m02, obj.m12)
        angle = math.asin(obj.m01)
        transform.rotation.value = -angle * 180 / math.pi
        matrix.rotate(angle)
        matrix.translate(transform.position.value)

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

    def add_to_parent(self, parent):
        self.parent = parent
        if parent:
            bisect.insort(parent.children, self, key=lambda it: it.figma.parentIndex.position)


class NodeMap:
    def __init__(self, schema):
        self.nodes = {}
        self.blobs = []
        self.document = None
        self.schema = schema
        self.animation = None
        self.pending_precomps = []
        self.pending_precomp_layers = []

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
            item.add_to_parent(self.node(item.figma.parentIndex.guid))
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

    def precomp_node(self, node: NodeItem):
        if not node.lottie:
            node.lottie = objects.assets.Precomp()
            node.lottie.id = "comp%s" % len(self.animation.assets)
            self.animation.assets.append(node.lottie)
        return node.lottie

    def process_pending(self):
        for node in self.pending_precomps:
            comp = self.precomp_node(node)
            node_to_comp(node, comp)
        self.pending_precomps = []

        for layer, guid in self.pending_precomp_layers:
            node = self.node(guid)
            comp = self.precomp_node(node)
            precomp_layer(layer, comp)
        self.pending_precomp_layers = []


def message_to_lottie(message, kiwi_schema=schema):
    nodes = NodeMap(kiwi_schema)
    nodes.process_message(message)
    if not nodes.document:
        return objects.animation.Animation()
    return document_to_lottie(nodes.document)


def document_to_lottie(node: NodeItem):
    anim = objects.animation.Animation()
    node.map.animation = anim
    parsed_main = False

    for canvas in node.children:
        if canvas.type == node.map.schema.NodeType.CANVAS:
            if canvas.figma.name == "Internal Only Canvas":
                continue

            if not parsed_main:
                node_to_comp(canvas, anim)
                parsed_main = True
            else:
                comp = node.map.precomp_node(canvas)
                node_to_comp(canvas, comp)

    node.map.process_pending()
    return anim


def node_to_comp(canvas: NodeItem, comp: objects.composition.Composition):
    comp.name = canvas.figma.name
    canvas.lottie = comp

    adj = objects.layers.NullLayer()
    adj.name = comp.name
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
    children = node.children

    match node.type:
        case NodeType.TEXT:
            layer = objects.layers.TextLayer()
            # TODO
        case NodeType.MEDIA:
            layer = objects.layers.ImageLayer()
            # TODO
        case NodeType.CANVAS | NodeType.FRAME:
            layer = objects.layers.NullLayer()
        case NodeType.SYMBOL:
            layer = objects.layers.PreCompLayer()
            node.map.pending_precomp_layers.append((layer, node.figma.guid))
            node.map.pending_precomps.append(node)
            children = []
        case NodeType.INSTANCE:
            layer = objects.layers.PreCompLayer()
            node.map.pending_precomp_layers.append((layer, node.figma.symbolData.symbolID))
        case _:
            shape = figma_to_lottie_shape(node)
            if shape is None:
                return None
            layer = objects.layers.ShapeLayer()
            layer.shapes.append(shape)

    layer.name = node.figma.name
    layer.index = len(comp.layers)
    comp.add_layer(layer)
    layer.parent_index = parent_index

    points = [
        NVector(0, 0),
        NVector(node.figma.size.x, 0),
        NVector(node.figma.size.x, node.figma.size.y),
        NVector(0, node.figma.size.y),
    ]

    for child in reversed(children):
        figma_to_lottie_layer(child, comp, layer.index, points)

    matrix = transform_to_lottie(node.figma.transform, layer.transform)[1]
    for point in points:
        bounding_points.append(matrix.apply(point))

    return layer


def figma_to_lottie_shape(node: NodeItem):
    NodeType = node.map.schema.NodeType

    match node.type:
        case NodeType.ELLIPSE:
            shape = ellipse_to_lottie(node)
        case NodeType.VECTOR:
            shape = vector_shape_to_lottie(node)
        case NodeType.RECTANGLE | NodeType.ROUNDED_RECTANGLE | NodeType.SECTION:
            shape = rect_to_lottie(node)
        case NodeType.REGULAR_POLYGON:
            shape = polystar_to_lottie(node, False)
        case NodeType.STAR:
            shape = polystar_to_lottie(node, True)
        case NodeType.LINE:
            shape = line_to_lottie(node)
        # TODO
        # case NodeType.BOOLEAN_OPERATION:
            # shape = boolean_to_lottie(node)
        case _:
            shape = None

    if shape is None:
        return None

    shape.name = node.figma.name

    group = objects.shapes.Group()
    group.add_shape(shape)
    shape_style_to_lottie(node, group)
    group.name = node.figma.name

    if node.figma.blendMode is not None:
        group.blend_mode = enum_mapping.blend_mode.to_lottie(node.figma.blendMode)

    return group


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
        dashes = None
        if node.figma.dashPattern:
            dashes = []
            DashType = objects.shapes.StrokeDashType
            dashes.append(objects.shapes.StrokeDash(0, DashType.Offset))
            for i, l in enumerate(node.figma.dashPattern):
                dashes.append(objects.shapes.StrokeDash(l, DashType.Gap if i % 2 else DashType.Dash))

        for paint in node.figma.strokePaints:
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
            shape.dashes = dashes


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


def polystar_to_lottie(node: NodeItem, star: bool):
    shape = objects.shapes.Star()
    shape.points.value = node.figma.count
    size = vector_to_lottie(node.figma.size)

    if size.x == size.y:
        shape.outer_radius.value = size.x / 2
        shape.position.value = size / 2
        ret_shape = shape
    else:
        shape.outer_radius.value = 50
        shape.name = node.figma.name
        group = objects.shapes.Group()
        group.add_shape(shape)
        group.transform.scale.value = size
        group.transform.position.value = size / 2
        ret_shape = group

    if star:
        shape.star_type = objects.shapes.StarType.Star
        shape.inner_radius.value = shape.outer_radius.value * node.figma.starInnerScale
    else:
        shape.star_type = objects.shapes.StarType.Polygon
        shape.inner_radius = shape.inner_roundness = None

    return ret_shape


def line_to_lottie(node: NodeItem):
    shape = objects.shapes.Path()
    shape.shape.value.add_point(NVector(0, 0))
    shape.shape.value.add_point(vector_to_lottie(node.figma.size))
    return shape


def precomp_layer(layer: objects.layers.PreCompLayer, comp: objects.assets.Precomp):
    layer.reference_id = comp.id
    layer.width = comp.width
    layer.height = comp.height
