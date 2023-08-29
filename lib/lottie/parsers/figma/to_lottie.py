import io
import math
import json
import bisect
import base64
import urllib.request
import PIL.Image

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


class NodeMap:
    def __init__(self, schema):
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
        self.pending_images = {}

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

                    index = item.interaction_index

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
            req_data = json.dumps({"sha1s": list(self.pending_images.keys())}).encode("ascii")
            query_url = "https://www.figma.com/file/%s/image/batch" % self.paste_key
            request = urllib.request.Request(query_url, req_data, {"Content-Type": "application/json"})
            response = urllib.request.urlopen(request)
            resp_data = json.loads(response.read())
            for hash, url in resp_data["meta"]["s3_urls"]:
                asset = self.pending_images[hash]
                asset.path = url
                img_data = urllib.request.urlopen(url).read()
                img = PIL.Image.open(io.BytesIO(img_data))

            self.pending_images = {}

    def image_id(self, image: schema.Image):
        if image.hash in self.images:
            return self.images[image.hash]

        asset = objects.assets.Image()
        asset.id = image.hash
        asset.name = image.name or "Image"
        self.images[image.hash] = asset
        hex_hash = base64.b16encode(image.hash).lower().decode("ascii")
        self.pending_images[hex_hash] = asset
        return asset


def message_to_lottie(message: schema.Message, kiwi_schema=schema):
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
            shape = figma_to_lottie_shape(node)
            if shape is None:
                return None
            layer = objects.layers.ShapeLayer()
            layer.shapes.append(shape)

    layer.in_point = layer.out_point = None  # Calculated later
    layer.name = node.figma.name
    layer.parent_index = parent_index
    layers.add_layer(layer)


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


def figma_to_lottie_shape(node: NodeItem):
    NodeType = node.map.schema.NodeType

    match node.type:
        case NodeType.ELLIPSE:
            shape = ellipse_to_lottie(node)
        case NodeType.VECTOR:
            shape = vector_shape_to_lottie(node)
        case NodeType.RECTANGLE | NodeType.ROUNDED_RECTANGLE | NodeType.SECTION  | NodeType.FRAME:
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


def push_layer(layer, before, after, transition, start_frame, end_frame):
    start_pos = layer.transform.position.get_value(start_frame)
    layer.transform.position.add_keyframe(start_frame, start_pos + before, transition)
    layer.transform.position.add_keyframe(end_frame, start_pos + after)


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
            start_frame = node.animation_start + delay
            end_frame = action.transitionDuration * fps + start_frame
            next_node.animation_start = end_frame
            next_layer = figma_to_lottie_layer(next_node, sub_layers, layer.parent_index, [], True)
            next_layer.transform = objects.helpers.Transform()
            next_layer.transform.position.value = layer.transform.position.get_value(start_frame)
            next_layer.transform.rotation.value = layer.transform.rotation.get_value(start_frame)

            if layer.out_point is None or layer.out_point < end_frame:
                layer.out_point = round(end_frame)

            if layer.in_point is None or layer.in_point > start_frame:
                layer.in_point = round(start_frame)

            if first:
                first = False
                transition = objects.easing.Bezier(
                    NVector(
                        action.easingFunction[0],
                        action.easingFunction[1],
                    ),
                    NVector(
                        action.easingFunction[2],
                        action.easingFunction[3],
                    )
                )

                # TODO SMART_ANIMATE SLIDE IN/OUT
                match action.transitionType:
                    case TransitionType.INSTANT_TRANSITION:
                        layer.transform.opacity.add_keyframe(start_frame, 100, objects.easing.Hold())
                        layer.transform.opacity.add_keyframe(end_frame, 0)
                        layers.add_under(sub_layers)
                    case TransitionType.DISSOLVE | TransitionType.SMART_ANIMATE:
                        layer.transform.opacity.add_keyframe(start_frame, 100, transition)
                        layer.transform.opacity.add_keyframe(end_frame, 0)
                        layers.add_under(sub_layers)
                    case TransitionType.MOVE_FROM_RIGHT | TransitionType.SLIDE_FROM_RIGHT:
                        push_layer(next_layer, NVector(node.figma.size.x, 0), NVector(0, 0), transition, start_frame, end_frame)
                        layers.add_over(sub_layers)
                    case TransitionType.MOVE_FROM_LEFT | TransitionType.SLIDE_FROM_LEFT:
                        push_layer(next_layer, NVector(-node.figma.size.x, 0), NVector(0, 0), transition, start_frame, end_frame)
                        layers.add_over(sub_layers)
                    case TransitionType.MOVE_FROM_TOP | TransitionType.SLIDE_FROM_TOP:
                        push_layer(next_layer, NVector(0, -node.figma.size.y), NVector(0, 0), transition, start_frame, end_frame)
                        layers.add_over(sub_layers)
                    case TransitionType.MOVE_FROM_BOTTOM | TransitionType.SLIDE_FROM_BOTTOM:
                        push_layer(next_layer, NVector(0, node.figma.size.y), NVector(0, 0), transition, start_frame, end_frame)
                        layers.add_over(sub_layers)
                    case TransitionType.MOVE_OUT_TO_RIGHT | TransitionType.SLIDE_OUT_TO_RIGHT:
                        push_layer(layer, NVector(-node.figma.size.x, 0), NVector(0, 0), transition, start_frame, end_frame)
                        layers.add_under(sub_layers)
                    case TransitionType.MOVE_OUT_TO_LEFT | TransitionType.SLIDE_OUT_TO_LEFT:
                        push_layer(layer, NVector(node.figma.size.x, 0), NVector(0, 0), transition, start_frame, end_frame)
                        layers.add_under(sub_layers)
                    case TransitionType.MOVE_OUT_TO_TOP | TransitionType.SLIDE_OUT_TO_TOP:
                        push_layer(layer, NVector(0, -node.figma.size.y), NVector(0, 0), transition, start_frame, end_frame)
                        layers.add_under(sub_layers)
                    case TransitionType.MOVE_OUT_TO_BOTTOM | TransitionType.SLIDE_OUT_TO_BOTTOM:
                        push_layer(layer, NVector(0, node.figma.size.y), NVector(0, 0), transition, start_frame, end_frame)
                        layers.add_under(sub_layers)
                    case TransitionType.PUSH_FROM_RIGHT:
                        push_layer(next_layer, NVector(node.figma.size.x, 0), NVector(0, 0), transition, start_frame, end_frame)
                        push_layer(layer, NVector(0, 0), NVector(-node.figma.size.x, 0), transition, start_frame, end_frame)
                        layers.add_under(sub_layers)
                    case TransitionType.PUSH_FROM_LEFT:
                        push_layer(next_layer, NVector(-node.figma.size.x, 0), NVector(0, 0), transition, start_frame, end_frame)
                        push_layer(layer, NVector(0, 0), NVector(node.figma.size.x, 0), transition, start_frame, end_frame)
                        layers.add_under(sub_layers)
                    case TransitionType.PUSH_FROM_TOP:
                        push_layer(next_layer, NVector(0, -node.figma.size.y), NVector(0, 0), transition, start_frame, end_frame)
                        push_layer(layer, NVector(0, 0), NVector(0, node.figma.size.y), transition, start_frame, end_frame)
                        layers.add_under(sub_layers)
                    case TransitionType.PUSH_FROM_BOTTOM:
                        push_layer(next_layer, NVector(0, node.figma.size.y), NVector(0, 0), transition, start_frame, end_frame)
                        push_layer(layer, NVector(0, 0), NVector(0, -node.figma.size.y), transition, start_frame, end_frame)
                        layers.add_under(sub_layers)
                    case _:
                        layers.add_under(sub_layers)
