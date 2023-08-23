import math

from . import model, schema, enum_mapping
from ... import objects
from ...nvector import NVector
from ...utils.transform import TransformMatrix


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
            canvas_to_lottie(canvas, anim)
            parsed_main = True
        else:
            comp = anim.assets.append(objects.composition.Composition())
            canvas_to_lottie(canvas, comp)


def canvas_to_lottie(canvas: NodeItem, comp: objects.composition.Composition):
    comp.name = canvas.figma.name
    # TODO
