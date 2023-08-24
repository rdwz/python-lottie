import math

from . import model, schema, enum_mapping
from ... import objects
from ...nvector import NVector
from ...utils.transform import TransformMatrix
from ...utils.color import Color


def transform_to_lottie(obj: schema.Matrix, transform = None):
    if transform is None:
        transform = objects.helpers.Transform()

    if obj is not None:
        matrix = TransformMatrix()
        matrix.a = obj.m00
        matrix.b = obj.m10
        matrix.c = obj.m01
        matrix.d = obj.m11
        matrix.tx = obj.m12
        matrix.ty = obj.m02
        structure = matrix.extract_transform()
        transform.position.set(structure["translation"])
        transform.rotation.set(structure["angle"] * 180 / math.pi)
        transform.scale.set(structure["scale"] * 100)

    return transform


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
        self.blobs = {}
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
        item = self.node(node.id)
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
                if node.type == schema.NodeType.DOCUMENT:
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


def canvas_to_comp(canvas: NodeItem, comp: objects.composition.Composition):
    comp.name = canvas.figma.name
    canvas.lottie = comp

    for child in canvas:
        figma_to_lottie_layer(child, comp, None)


def figma_to_lottie_layer(node: NodeItem, comp: objects.composition.Composition, parent_index):
    NodeType = node.map.schema.NodeType

    match node.type:
        case NodeType.TEXT:
            layer = objects.layers.TextLayer()
            # TODO
        case NodeType.MEDIA:
            layer = objects.layers.ImageLayer()
            # TODO
        case _:
            shape = figma_to_lottie_shape(node)
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
        figma_to_lottie_layer(child, comp, layer.index)

    return layer


def figma_to_lottie_shape(node: NodeItem):
    NodeType = node.map.schema.NodeType

    match node.type:
        case NodeType.ELLIPSE:
            shape = ellipse_to_lottie(node)
        case NodeType.CANVAS:
            shape = canvas_to_group(node)
        case NodeType.VECTOR:
            shape = vector_to_lottie(node)
        case NodeType.STAR:
            shape = star_to_lottie(node)
        case NodeType.BOOLEAN_OPERATION:
            shape = boolean_to_lottie(node)
        case NodeType.RECTANGLE | NodeType.ROUNDED_RECTANGLE | NodeType.SECTION:
            shape = rect_to_lottie(node)
        case NodeType.REGULAR_POLYGON:
            shape = polygon_to_lottie(node)
        case NodeType.LINE:
            shape = line_to_lottie(node)
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

    if node.figma.blendMode is not None:
        shape.blend_mode = enum_mapping.blend_mode.to_lottie(node.figma.blendMode)
    transform_to_lottie(node.figma.transform, shape.transform)
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
