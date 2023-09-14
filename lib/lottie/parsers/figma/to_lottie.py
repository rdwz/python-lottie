import io
import math
import json
import bisect
import base64
import urllib.request
import PIL.Image

from . import model, schema, enum_mapping
from .file import FigmaFile
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
        matrix.rotate(-angle)
        matrix.translate(transform.position.value)

    return transform, matrix


def transform_matrix(obj: schema.Matrix):
    matrix = TransformMatrix()
    matrix.a = obj.m00
    matrix.b = obj.m01
    matrix.c = obj.m10
    matrix.d = obj.m11
    matrix.tx = obj.m02
    matrix.ty = obj.m12
    return matrix


class NodeItem:
    def __init__(self, map: "NodeMap", figma: "schema.NodeChange"):
        self.figma = figma
        self.lottie = None
        self.parent = None
        self.children = []
        self.map = map
        self.animation_start = None
        self.interaction_index = None
        self.interaction_head = None
        self.interaction_rendered = False

    @property
    def type(self):
        return self.figma.type

    def add_to_parent(self, parent):
        self.parent = parent
        if parent:
            bisect.insort(parent.children, self, key=lambda it: it.figma.parentIndex.position)

    def child_dict(self, dict=None, handled=None):
        if dict is None:
            dict = {}
            handled = set()

        for child in self.children:
            name = child.figma.name
            if name:
                if name in handled:
                    dict.pop(name, None)
                else:
                    dict[name] = child
                    handled.add(name)

            child.child_dict(dict, handled)

        return dict


class NodeMap:
    def __init__(self, schema, file: FigmaFile):
        self.nodes = {}
        self.blobs = []
        self.document = None
        self.schema = schema
        self.animation: objects.animation.Animation = None
        self.pending_precomps = []
        self.pending_precomp_layers = []
        self.interaction_delay = 0.5
        self.paste_key = None
        self.images = {}
        self.pending_images = []
        self.file = file

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
        self.paste_key = message.pasteFileKey

        if message.nodeChanges is not None:

            # Assign interaction_index to all items that are the target of an interaction
            interaction_index = 0
            for node in message.nodeChanges:
                item = self.add_node(node)
                if node.prototypeInteractions:
                    if not item.interaction_index:
                        interaction_index += 1
                        item.interaction_index = interaction_index
                        item.interaction_head = interaction_index

                    for interaction in node.prototypeInteractions:
                        for action in interaction.actions:
                            if action.connectionType == self.schema.ConnectionType.INTERNAL_NODE:
                                target = self.node(action.transitionNodeID)
                                if interaction_index != target.interaction_index:
                                    target.interaction_head = None
                                target.interaction_index = interaction_index

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

        if self.pending_images:
            req_data = json.dumps({"sha1s": self.pending_images}).encode("ascii")
            query_url = "https://www.figma.com/file/%s/image/batch" % self.paste_key
            request = urllib.request.Request(query_url, req_data, {"Content-Type": "application/json"})
            response = urllib.request.urlopen(request)
            resp_data = json.loads(response.read())
            for hash, url in resp_data["meta"]["s3_urls"].items():
                asset = self.images[hash]
                asset.path = url
                if asset.width == 0:
                    img_data = urllib.request.urlopen(url).read()
                    img = PIL.Image.open(io.BytesIO(img_data))
                    asset.width = img.width
                    asset.height = img.height

            self.pending_images = []

    def image_asset(self, image: schema.Image):
        hex_hash = base64.b16encode(image.hash).lower().decode("ascii")

        if hex_hash in self.images:
            return self.images[hex_hash]

        asset = objects.assets.Image()
        asset.id = hex_hash
        asset.name = image.name or "Image"
        self.images[hex_hash] = asset
        self.animation.assets.append(asset)

        if hex_hash in self.file.assets:
            asset.load(self.file.assets[hex_hash])
        else:
            self.pending_images.append(hex_hash)
        return asset


def figma_file_to_lottie(file: FigmaFile):
    return message_to_lottie(file.data, file, file.schema.module)


def message_to_lottie(message: schema.Message, file: FigmaFile, kiwi_schema=schema):
    nodes = NodeMap(kiwi_schema, file)
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
    layers = LayerSpan.from_comp(comp)
    adj.index = layers.next_index()
    comp.add_layer(adj)
    adj.in_point = adj.out_point = None
    bounding_points = []

    for child in canvas.children:
        figma_to_lottie_layer(child, layers, adj.index, bounding_points, False)

    layers.flush()

    if bounding_points:
        bb = objects.shapes.BoundingBox()
        for p in bounding_points:
            bb.include(p.x, p.y)

        comp.width = math.ceil(bb.width)
        comp.height = math.ceil(bb.height)
        adj.transform.position.value = NVector(-bb.x1, -bb.y1)

    ip = None
    op = None
    for layer in comp.layers:
        if layer.in_point is not None:
            if ip is None:
                ip = layer.in_point
                op = layer.out_point
            else:
                if layer.in_point < ip:
                    ip = layer.in_point
                if layer.out_point < op:
                    op = layer.out_point

    if ip is None:
        ip = 0
        op = comp.frame_rate

    for layer in comp.layers:
        if layer.in_point is None:
            layer.in_point = ip
            layer.out_point = op

    comp.in_point = ip
    comp.out_point = op


class LayerManager:
    def __init__(self, comp: objects.composition.Composition):
        self.comp = comp
        self.layer_index = len(comp.layers) - 1

    def next_index(self):
        self.layer_index += 1
        return self.layer_index

    def span(self):
        return LayerSpan(self)


class LayerSpan:
    def __init__(self, manager: LayerManager):
        self.layers = []
        self.manager = manager

    def flush(self):
        self.manager.comp.layers += self.layers
        self.layers = []

    def add_over(self, layers: "LayerSpan"):
        self.layers = layers.layers + self.layers
        layers.layers = []

    def add_under(self, layers: "LayerSpan"):
        self.layers = self.layers + layers.layers
        layers.layers = []

    def add_layer(self, layer: objects.layers.Layer):
        if layer.index is None:
            layer.index = self.manager.next_index()
        self.layers.append(layer)

    def next_index(self):
        return self.manager.next_index()

    @classmethod
    def from_comp(cls, comp: objects.composition.Composition):
        return cls(LayerManager(comp))

    def span(self):
        return self.manager.span()


def figma_to_lottie_layer(node: NodeItem, layers: LayerSpan, parent_index, bounding_points, is_transition_target):
    # Created by something else
    if not is_transition_target and node.interaction_head != node.interaction_index:
        return

    NodeType = node.map.schema.NodeType
    children = node.children
    extra_layers = layers.span()

    match node.type:
        case NodeType.TEXT:
            layer = objects.layers.TextLayer()
            # TODO
        case NodeType.MEDIA:
            layer = objects.layers.ImageLayer()
            # TODO
        case NodeType.SYMBOL:
            layer = objects.layers.PreCompLayer()
            node.map.pending_precomp_layers.append((layer, node.figma.guid))
            node.map.pending_precomps.append(node)
            children = []
        case NodeType.INSTANCE:
            layer = objects.layers.PreCompLayer()
            node.map.pending_precomp_layers.append((layer, node.figma.symbolData.symbolID))
        case _:
            shape = figma_to_lottie_shape(node, extra_layers)
            if shape is None:
                return None
            layer = objects.layers.ShapeLayer()
            layer.shapes.append(shape)

    layer.in_point = layer.out_point = None  # Calculated later
    layer.name = node.figma.name
    layer.parent_index = parent_index
    layers.add_layer(layer)
    layers.add_under(extra_layers)
    node.lottie = layer

    points = [
        NVector(0, 0),
        NVector(node.figma.size.x, 0),
        NVector(node.figma.size.x, node.figma.size.y),
        NVector(0, node.figma.size.y),
    ]

    sub_layers = layers.span()

    for child in children:
        figma_to_lottie_layer(child, sub_layers, layer.index, points, False)

    if node.type == NodeType.FRAME:
        layers.add_over(sub_layers)
    else:
        layers.add_under(sub_layers)

    if is_transition_target:
        bounding_points += points
    else:
        matrix = transform_to_lottie(node.figma.transform, layer.transform)[1]
        for point in points:
            bounding_points.append(matrix.apply(point))

    if node.figma.prototypeInteractions:
        prototype_to_lottie(node, layer, layers)

    return layer


def shape_args(node: NodeItem):
    NodeType = node.map.schema.NodeType

    func = None
    type = None
    args = []

    match node.type:
        case NodeType.ELLIPSE:
            func = ellipse_to_lottie
            type = objects.shapes.Ellipse
        case NodeType.VECTOR:
            func = vector_shape_to_lottie
            type = objects.shapes.Path
        case NodeType.RECTANGLE | NodeType.ROUNDED_RECTANGLE | NodeType.SECTION | NodeType.FRAME:
            func = rect_to_lottie
            type = objects.shapes.Rect
        case NodeType.REGULAR_POLYGON:
            func = polystar_to_lottie
            type = objects.shapes.Star
            args = [False]
        case NodeType.STAR:
            func = polystar_to_lottie
            type = objects.shapes.Star
            args = [True]
        case NodeType.LINE:
            func = line_to_lottie
            type = objects.shapes.Path
        # TODO
        # case NodeType.BOOLEAN_OPERATION:
            # shape = boolean_to_lottie(node)
    return func, type, args


def figma_to_lottie_shape(node: NodeItem, extra_layers: LayerSpan):
    func, type, args = shape_args(node)

    if func is None:
        return None

    wrapper = ShapePropertyWriter(node, type())
    func(wrapper, *args)

    shape = wrapper.outer_shape()
    shape.name = node.figma.name

    group = objects.shapes.Group()
    group.add_shape(shape)
    shape_style_to_lottie(node, group, extra_layers)
    group.name = node.figma.name

    if node.figma.blendMode is not None:
        group.blend_mode = enum_mapping.blend_mode.to_lottie(node.figma.blendMode)

    return group


def color_to_lottie(color: schema.Color):
    if color is None:
        return Color(), 0
    return Color(color.r, color.g, color.b, 1), color.a


def gradient_stops_to_lottie(paint: schema.Paint):
    stops = []
    alpha_stops = []
    for stop in paint.stops:
        stops.append(stop.position)
        stops.append(stop.color.r)
        stops.append(stop.color.g)
        stops.append(stop.color.b)
        alpha_stops.append(stop.position)
        alpha_stops.append(stop.color.a)

    gradient = objects.properties.GradientColors()
    gradient.colors.value = stops + alpha_stops
    gradient.count = len(paint.stops)
    return gradient


def linear_gradient_to_lottie(paint: schema.Paint, shape: objects.shapes.Gradient):
    shape.gradient_type = objects.shapes.GradientType.Linear
    matrix = transform_matrix(paint.transform)
    p0 = NVector(0, 0)
    p1 = NVector(100, 0)
    shape.start_point.value = matrix.apply(p0)
    shape.end_point.value = matrix.apply(p1)
    shape.colors = gradient_stops_to_lottie(paint)


def radial_gradient_to_lottie(paint: schema.Paint, shape: objects.shapes.Gradient):
    shape.gradient_type = objects.shapes.GradientType.Radial
    # TODO parse transform and apply it to the points
    shape.start_point.value = NVector(0, 0)
    shape.end_point.value = NVector(100, 0)
    shape.colors = gradient_stops_to_lottie(paint)


def shape_style_to_lottie(node: NodeItem, group: objects.shapes.Group, extra_layers: LayerSpan):
    if node.figma.fillPaints:
        for paint in node.figma.fillPaints:
            match paint.type:
                case node.map.schema.PaintType.GRADIENT_LINEAR | node.map.schema.PaintType.GRADIENT_ANGULAR:
                    shape = objects.shapes.GradientFill()
                    linear_gradient_to_lottie(paint, shape)
                case node.map.schema.PaintType.GRADIENT_RADIAL | node.map.schema.PaintType.GRADIENT_DIAMOND:
                    shape = objects.shapes.GradientFill()
                    radial_gradient_to_lottie(paint, shape)
                case node.map.schema.PaintType.SOLID:
                    shape = objects.shapes.Fill()
                    shape.color.value, shape.opacity.value = color_to_lottie(paint.color)
                    shape.opacity.value *= 100
                case node.map.schema.PaintType.IMAGE:
                    image = node.map.image_asset(paint.image)
                    image.width = paint.originalImageWidth
                    image.height = paint.originalImageHeight
                    image_layer = objects.layers.ImageLayer()
                    extra_layers.add_layer(image_layer)
                    if paint.opacity is not None:
                        image_layer.transform.opacity.value = paint.opacity * 100
                    image_layer.blend_mode = enum_mapping.blend_mode.to_lottie(paint.blendMode)
                    transform_to_lottie(paint.transform, image_layer.transform)
                    image_layer.transform.rotation.value = paint.rotation
                    image_layer.hidden = not paint.visible
                    image_layer.name = image.name
                    image_layer.asset_id = image.id
                    continue
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
                    linear_gradient_to_lottie(node, shape)
                case node.map.schema.PaintType.GRADIENT_RADIAL:
                    shape = objects.shapes.GradientStroke()
                    radial_gradient_to_lottie(node, shape)
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


class AnimationArgs:
    def __init__(self):
        self.start_frame = self.end_frame = 0
        self.transition = None

    def set(self, property, value1, value2=None):
        if value2 is None:
            value2 = value1
            value1 = property.get_value(self.start_frame)
        property.add_keyframe(self.start_frame, value1, self.transition)
        property.add_keyframe(self.end_frame, value2)


class ShapePropertyWriter:
    def __init__(self, node: NodeItem, shape: objects.VisualObject, animation: AnimationArgs|None = None):
        self.node = node
        self.shape = shape
        self.animation = animation
        self.shape_wrapper = None

    def set(self, prop_name, value, shape=None):
        prop = getattr(shape or self.shape, prop_name)
        if self.animation is not None:
            self.animation.set(prop, value)
        else:
            prop.value = value

    def get(self, prop_name, shape=None):
        prop = getattr(shape or self.shape, prop_name)
        return prop.get_value(self.start_frame)

    @property
    def figma(self):
        return self.node.figma

    @property
    def map(self):
        return self.node.map

    def ensure_wrapper(self):
        if self.shape_wrapper:
            return self.shape_wrapper

        group = objects.shapes.Group()
        group.add_shape(self.shape)
        self.shape_wrapper = group
        return group

    def outer_shape(self):
        if self.shape_wrapper:
            return self.shape_wrapper
        return self.shape


def ellipse_to_lottie(node: ShapePropertyWriter):
    size = vector_to_lottie(node.figma.size)
    node.set("size", size)
    node.set("position", size / 2)


def rect_to_lottie(node: ShapePropertyWriter):
    ellipse_to_lottie(node)
    # TODO rounded corners


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


def vector_shape_to_lottie(node: ShapePropertyWriter):
    if node.figma.vectorData and node.figma.vectorData.vectorNetworkBlob is not None:
        blob = node.map.blobs[node.figma.vectorData.vectorNetworkBlob]
        node.set("shape", blob_to_bezier(blob))


def polystar_to_lottie(node: ShapePropertyWriter, star: bool):
    node.set("points", node.figma.count)
    size = vector_to_lottie(node.figma.size)

    if size.x == size.y:
        node.set("outer_radius", size.x / 2)
        node.set("position", size / 2)
    else:
        node.set("outer_radius", 50)
        node.shape.name = node.figma.name
        group = node.ensure_wrapper()
        node.set("scale", size, group.transform)
        node.set("position", size / 2, group.transform)

    if star:
        node.shape.star_type = objects.shapes.StarType.Star
        node.set("inner_radius", node.get("outer_radius") * node.figma.starInnerScale)
    else:
        node.shape.star_type = objects.shapes.StarType.Polygon
        node.shape.inner_radius = node.shape.inner_roundness = None


def line_to_lottie(node: ShapePropertyWriter):
    bez = objects.bezier.Bezier()
    bez.add_point(NVector(0, 0))
    bez.add_point(vector_to_lottie(node.figma.size))
    node.set("shape", bez)


def precomp_layer(layer: objects.layers.PreCompLayer, comp: objects.assets.Precomp):
    layer.reference_id = comp.id
    layer.width = comp.width
    layer.height = comp.height


def push_layer(layer, before, after, animation: AnimationArgs):
    start_pos = layer.transform.position.get_value(animation.start_frame)
    animation.set(layer.transform.position, start_pos + before, start_pos + after)


def prototype_to_lottie(node: NodeItem, layer: objects.layers.Layer, layers: LayerSpan):
    # Avoid loops
    if node.interaction_rendered:
        return
    node.interaction_rendered = True

    interactions = []
    InteractionType = node.map.schema.InteractionType
    TransitionType = node.map.schema.TransitionType
    interaction: node.map.schema.PrototypeInteraction = None
    action: node.map.schema.PrototypeAction = None
    if node.animation_start is None:
        node.animation_start = 0
    fps = node.map.animation.frame_rate

    for interaction in node.figma.prototypeInteractions:
        type = interaction.event.interactionType
        score = type.value
        if type == InteractionType.AFTER_TIMEOUT:
            score = -1
        elif type == InteractionType.NONE:
            score = 100

        interactions.append((score, interaction))

    first = True

    for _, interaction in sorted(interactions):

        delay = node.map.interaction_delay * fps
        if interaction.event.interactionType == InteractionType.AFTER_TIMEOUT:
            timeout = interaction.event.transitionTimeout
            if timeout is None:
                timeout = 0.8
            delay = timeout * fps

        for action in interaction.actions:
            if action.connectionType != node.map.schema.ConnectionType.INTERNAL_NODE:
                continue
            sub_layers = layers.span()
            next_node = node.map.node(action.transitionNodeID)
            animation = AnimationArgs()
            animation.start_frame = node.animation_start + delay
            animation.end_frame = action.transitionDuration * fps + animation.start_frame
            next_node.animation_start = animation.end_frame

            if layer.out_point is None or layer.out_point < animation.end_frame:
                layer.out_point = round(animation.end_frame)

            if layer.in_point is None or layer.in_point > animation.start_frame:
                layer.in_point = round(animation.start_frame)

            if TransitionType.SMART_ANIMATE and first:
                first = False
                animation.transition = objects.easing.Bezier(
                    NVector(
                        action.easingFunction[0],
                        action.easingFunction[1],
                    ),
                    NVector(
                        action.easingFunction[2],
                        action.easingFunction[3],
                    )
                )
                smart_animate(node, next_node, animation, sub_layers)
                layers.add_over(sub_layers)

                if next_node.figma.prototypeInteractions:
                    prototype_to_lottie(next_node, layer, layers)
                continue

            next_layer = figma_to_lottie_layer(next_node, sub_layers, layer.parent_index, [], True)
            next_layer.transform = objects.helpers.Transform()
            next_layer.transform.position.value = layer.transform.position.get_value(animation.start_frame)
            next_layer.transform.rotation.value = layer.transform.rotation.get_value(animation.start_frame)

            if first:
                first = False
                animation.transition = objects.easing.Bezier(
                    NVector(
                        action.easingFunction[0],
                        action.easingFunction[1],
                    ),
                    NVector(
                        action.easingFunction[2],
                        action.easingFunction[3],
                    )
                )

                # TODO SLIDE IN/OUT
                match action.transitionType:
                    case TransitionType.INSTANT_TRANSITION:
                        layer.transform.opacity.add_keyframe(animation.start_frame, 100, objects.easing.Hold())
                        layer.transform.opacity.add_keyframe(animation.end_frame, 0)
                        layers.add_under(sub_layers)
                    case TransitionType.DISSOLVE:
                        layer.transform.opacity.add_keyframe(animation.start_frame, 100, animation.transition)
                        layer.transform.opacity.add_keyframe(animation.end_frame, 0)
                        layers.add_under(sub_layers)
                    case TransitionType.MOVE_FROM_RIGHT | TransitionType.SLIDE_FROM_RIGHT:
                        push_layer(next_layer, NVector(node.figma.size.x, 0), NVector(0, 0), animation)
                        layers.add_over(sub_layers)
                    case TransitionType.MOVE_FROM_LEFT | TransitionType.SLIDE_FROM_LEFT:
                        push_layer(next_layer, NVector(-node.figma.size.x, 0), NVector(0, 0), animation)
                        layers.add_over(sub_layers)
                    case TransitionType.MOVE_FROM_TOP | TransitionType.SLIDE_FROM_TOP:
                        push_layer(next_layer, NVector(0, -node.figma.size.y), NVector(0, 0), animation)
                        layers.add_over(sub_layers)
                    case TransitionType.MOVE_FROM_BOTTOM | TransitionType.SLIDE_FROM_BOTTOM:
                        push_layer(next_layer, NVector(0, node.figma.size.y), NVector(0, 0), animation)
                        layers.add_over(sub_layers)
                    case TransitionType.MOVE_OUT_TO_RIGHT | TransitionType.SLIDE_OUT_TO_RIGHT:
                        push_layer(layer, NVector(-node.figma.size.x, 0), NVector(0, 0), animation)
                        layers.add_under(sub_layers)
                    case TransitionType.MOVE_OUT_TO_LEFT | TransitionType.SLIDE_OUT_TO_LEFT:
                        push_layer(layer, NVector(node.figma.size.x, 0), NVector(0, 0), animation)
                        layers.add_under(sub_layers)
                    case TransitionType.MOVE_OUT_TO_TOP | TransitionType.SLIDE_OUT_TO_TOP:
                        push_layer(layer, NVector(0, -node.figma.size.y), NVector(0, 0), animation)
                        layers.add_under(sub_layers)
                    case TransitionType.MOVE_OUT_TO_BOTTOM | TransitionType.SLIDE_OUT_TO_BOTTOM:
                        push_layer(layer, NVector(0, node.figma.size.y), NVector(0, 0), animation)
                        layers.add_under(sub_layers)
                    case TransitionType.PUSH_FROM_RIGHT:
                        push_layer(next_layer, NVector(node.figma.size.x, 0), NVector(0, 0), animation)
                        push_layer(layer, NVector(0, 0), NVector(-node.figma.size.x, 0), animation)
                        layers.add_under(sub_layers)
                    case TransitionType.PUSH_FROM_LEFT:
                        push_layer(next_layer, NVector(-node.figma.size.x, 0), NVector(0, 0), animation)
                        push_layer(layer, NVector(0, 0), NVector(node.figma.size.x, 0), animation)
                        layers.add_under(sub_layers)
                    case TransitionType.PUSH_FROM_TOP:
                        push_layer(next_layer, NVector(0, -node.figma.size.y), NVector(0, 0), animation)
                        push_layer(layer, NVector(0, 0), NVector(0, node.figma.size.y), animation)
                        layers.add_under(sub_layers)
                    case TransitionType.PUSH_FROM_BOTTOM:
                        push_layer(next_layer, NVector(0, node.figma.size.y), NVector(0, 0), animation)
                        push_layer(layer, NVector(0, 0), NVector(0, -node.figma.size.y), animation)
                        layers.add_under(sub_layers)
                    case _:
                        layers.add_under(sub_layers)


def smart_animate(node: NodeItem, next_node: NodeItem, animation: AnimationArgs, layers: LayerSpan):
    original = node.child_dict()

    for child in next_node.children:
        smart_animate_node(original, child, node.lottie.index, animation, layers)


def smart_animate_node(original_nodes, node: NodeItem, parent_index, animation: AnimationArgs, layers: LayerSpan):
    original = original_nodes.get(node.figma.name, None)
    if not original or original.figma.type != node.figma.type:
        layer = figma_to_lottie_layer(node, layers, parent_index, [], True)
        animation.set(layer.transform.opacity, 0, 100)
        if original:
            animation.set(original.transform.opacity, 100, 0)
        return

    layer: objects.layers.ShapeLayer = original.lottie
    otf = original.lottie.transform
    tf = transform_to_lottie(node.figma.transform)[0]
    p = tf.position.get_value(animation.start_frame)
    node.lottie = layer
    if not math.isclose(p.x, otf.position.value.x) or not math.isclose(p.y, otf.position.value.y):
        animation.set(otf.position, p, otf.position.value)

    r = tf.rotation.get_value(animation.start_frame)
    if not math.isclose(r, otf.rotation.value):
        animation.set(otf.rotation, r, otf.rotation.value)

    shape = layer.shapes[0].shapes[0]
    func, type, args = shape_args(node)
    writer = ShapePropertyWriter(node, shape)
    if isinstance(shape, objects.shapes.Group):
        writer.shape_wrapper = shape
        writer.shape = shape.shapes[0]
    func(writer, *args)
    # TODO style
