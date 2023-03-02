import io
from xml.etree import ElementTree
from dataclasses import dataclass
import struct
from PIL import ImageCms

from .base import importer
from .. import objects
from .. import NVector
from ..utils.color import Color


class Endianness:
    def read(self, file, size):
        return self.decode(file.read(size))

    def decode(self, data):
        raise NotImplementedError()


class BigEndian(Endianness):
    @staticmethod
    def decode_data(data):
        value = 0
        for byte in data:
            value <<= 8
            value |= byte

        return value

    def decode(self, data):
        return self.decode_data(data)

    def decode_float64(self, data):
        return struct.unpack(">d", data)[0]

    def decode_float32(self, data):
        return struct.unpack(">f", data)[0]


class LittleEndian(Endianness):
    def decode(self, data):
        return BigEndian.decode_data(reversed(data))

    def decode_float64(self, data):
        return struct.unpack("<d", data)[0]

    def decode_float32(self, data):
        return struct.unpack("<f", data)[0]


@dataclass
class RiffChunk:
    header: str
    length: int
    data: bytes


@dataclass
class RiffList:
    type: str
    children: tuple

    def find(self, header):
        for ch in self.children:
            if ch.header == header:
                return ch

    def find_list(self, type):
        for ch in self.children:
            if ch.header == "LIST" and ch.data.type == type:
                return ch


@dataclass
class RiffHeader:
    endianness: Endianness
    length: int
    format: str


class RiffParser:
    def __init__(self, file):
        self.file = file
        magic = self.read(4)
        if magic == b"RIFF":
            endian = LittleEndian()
        elif magic == b"RIFX":
            endian = BigEndian()
        else:
            raise Exception("Expected RIFF or RIFX")

        self.endian = endian
        length = self.read_number(4)
        self.end = file.tell() + length
        format = self.read_str(4)

        self.header = RiffHeader(self.endian, length, format)
        self.chunk_parsers = {}

    def read(self, length):
        return self.file.read(length)

    def read_str(self, length):
        return self.read(length).decode("ascii")

    def read_number(self, length):
        return self.endian.read(self.file, length)

    def read_chunk(self):
        header = self.read_str(4)

        length = self.read_number(4)

        if header == "LIST":
            end = self.file.tell() + length
            type = self.read_str(4)
            self.on_list_start(type)
            children = []
            while self.file.tell() < end:
                children.append(self.read_chunk())
            data = RiffList(type, tuple(children))
        elif header in self.chunk_parsers:
            data = self.chunk_parsers[header](self, length)
        else:
            data = self.read(length)

        if data is None:
            raise Exception("Incomplete chunk")

        chunk = RiffChunk(header, length, data)

        self.on_chunk(chunk)

        # Skip pad byte
        if length % 2:
            self.read(1)

        return chunk

    def __iter__(self):
        while True:
            if self.file.tell() >= self.end:
                return

            yield self.read_chunk()

    def on_chunk(self, chunk):
        pass

    def on_list_start(self, type):
        pass


    def read_sub_chunks(self, length):
        end = self.file.tell() + length
        children = []
        while self.file.tell() < end:
            children.append(self.read_chunk())
        return RiffList("", tuple(children))


class StructuredData:
    @classmethod
    def reader(cls, parser, length):
        reader = StructuredReader(parser, length, cls.structure, cls)
        reader.read_structure()
        return reader.value


class StructuredReader:
    def __init__(self, parser, length, structure, cls=StructuredData):
        self.value = cls()
        self.structure = structure
        self.index = 0
        self.parser = parser
        self.length = length
        self.to_read = length

    def skip(self, byte_count):
        self.read_attribute("", byte_count, bytes)

    def read_attribute_string0(self, name):
        self.set_attribute(name, self.read_string0())

    def set_attribute(self, name, value):
        if name == "":
            name = "_%s" % self.index
            self.index += 1

        setattr(self.value, name, value)

    def read_attribute(self, name, size, type):
        self.set_attribute(name, self.read_value(size, type))

    def read_structure(self):
        for name, size, type in self.structure:
            self.read_attribute(name, size, type)

        self.finalize()

        return self.value

    def finalize(self):
        if self.to_read:
            setattr(self.value, "_%s" % self.index, self.parser.read(self.to_read))

    def read_string0(self):
        read = b''
        while self.to_read > 0:
            byte = self.parser.read(1)
            self.to_read -= 1
            if byte == b'\0':
                break
            read += byte
        return read.decode("utf8")

    def read_value(self, length, type):
        if isinstance(type, list):
            val = []
            for name, size, subtype in type:
                val.append(self.read_value(size, subtype))
            return val

        if length > self.to_read:
            raise Exception("Not enough data in chunk")

        data = self.parser.read(length)
        self.to_read -= length

        if type is bytes:
            return data
        elif type is int:
            return self.parser.endian.decode(data)
        elif type is str:
            return data.decode("utf8")
        elif type is float:
            return self.parser.endian.decode_float64(data)


    def attr_bit(self, name, byte, bit):
        setattr(self.value, name, (self.value.attrs[byte] & (1 << bit)) != 0)


def read_floats(parser, length):
    if length < 8:
        return parser.read(length)

    if length == 8:
        return parser.endian.decode_float64(parser.read(8))

    floats = {}
    to_read = length
    while to_read >= 8:
        floats["_%s" % len(floats)] = parser.endian.decode_float64(parser.read(8))
        to_read -= 8

    if to_read:
        floats["_%s" % len(floats)] = parser.read(to_read)
    return floats


def read_floats32(parser, length):
    if length < 4:
        return parser.read(length)

    if length == 4:
        return parser.endian.decode_float64(parser.read(8))

    floats = {}
    to_read = length
    while to_read >= 4:
        floats["_%s" % len(floats)] = parser.endian.decode_float32(parser.read(4))
        to_read -= 4

    if to_read:
        floats["_%s" % len(floats)] = parser.read(to_read)
    return floats


def convert_value_color(arr):
    return Color(arr[1] / 255, arr[2] / 255, arr[3] / 255, arr[0] / 255)


class AepParser(RiffParser):
    placeholder = "-_0_/-"
    shapes = {
        "ADBE Vector Filter - Trim": objects.shapes.Trim,
        "ADBE Vector Graphic - Stroke": objects.shapes.Stroke,
        "ADBE Vector Graphic - Fill": objects.shapes.Fill,
        "ADBE Vector Group": objects.shapes.Group,
        "ADBE Vector Shape - Group": objects.shapes.Path,
        "ADBE Vector Shape - Rect": objects.shapes.Rect,
        "ADBE Vector Shape - Ellipse": objects.shapes.Ellipse,
        "ADBE Vector Graphic - G-Fill": objects.shapes.GradientFill,
    }
    properties = {
        "ADBE Vector Position": ("position", None),
        "ADBE Vector Trim Start": ("start", None),
        #"ADBE Vector Shape": ("shape", None)
        "ADBE Vector Stroke Color": ("color", convert_value_color),
        "ADBE Vector Fill Color": ("color", convert_value_color),
        "ADBE Vector Stroke Width": ("width", None),
        "ADBE Anchor Point": ("anchor_point", None),
        "ADBE Position": ("position", None),
        "ADBE Rotate Z": ("rotation", None),
        "ADBE Opacity": ("opacity", lambda v: v * 100),
        "ADBE Scale": ("scale", lambda v: v * 100),
        "ADBE Vector Rect Size": ("size", None),
        "ADBE Vector Ellipse Size": ("size", None),
        "ADBE Vector Grad Start Pt": ("start_point", None),
        "ADBE Vector Grad End Pt": ("end_point", None),
        "ADBE Vector Grad Colors": ("colors", None),
    }

    def __init__(self, file):
        super().__init__(file)

        if self.header.format != "Egg!":
            raise Exception("Not an AEP file")

        self.chunk_parsers = {
            "tdsn": RiffParser.read_sub_chunks,
            "Utf8": AepParser.read_utf8,
            "tdmn": AepParser.read_mn,
            "cdta": AepParser.read_cdta,
            "ldta": AepParser.read_ldta,
            "idta": AepParser.read_idta,
            "tdb4": AepParser.read_tdb4,
            "cdat": AepParser.read_cdat,
            "ldat": AepParser.read_ldat,
            "tdum": read_floats,
            "tduM": read_floats,
            "tdsb": AepParser.read_number,
            "pprf": AepParser.read_pprf,
            "fvdv": AepParser.read_number,
            "ftts": AepParser.read_number,
            "fifl": AepParser.read_number,
            "fipc": AepParser.read_number,
            "fiop": AepParser.read_number,
            "foac": AepParser.read_number,
            "fiac": AepParser.read_number,
            "fvdv": AepParser.read_number,
            "wsnm": AepParser.read_utf16,
            "fcid": AepParser.read_number,
            "fovc": AepParser.read_number,
            "fovi": AepParser.read_number,
            "fits": AepParser.read_number,
            "fivc": AepParser.read_number,
            "fivi": AepParser.read_number,
            "fidi": AepParser.read_number,
            "fimr": AepParser.read_number,
            "CsCt": AepParser.read_number,
            "CapL": AepParser.read_number,
            "CcCt": AepParser.read_number,
            "mrid": AepParser.read_number,
            "numS": AepParser.read_number,
        }
        self.prop_dimension = None
        self.prop_animated = False
        self.prop_shape = False
        self.prop_position = False
        self.prop_gradient = False
        self.frame_mult = 1

    def read_mn(self, length):
        return self.read(length).strip(b"\0").decode("utf8")

    def read_pprf(self, length):
        return ImageCms.ImageCmsProfile(io.BytesIO(self.read(length)))

    def read_tdb4(self, length):
        reader = StructuredReader(self, length, None)
        reader.skip(3)
        reader.read_attribute("components", 1, int)
        reader.read_attribute("attrs", 2, bytes)
        reader.finalize()
        reader.attr_bit("position", 1, 3)
        data = reader.value

        self.prop_dimension = data.components
        self.prop_animated = False
        self.prop_shape = False
        self.prop_position = data.position
        return data

    def read_cdat(self, length):
        dim = self.prop_dimension
        self.prop_dimension = None

        if dim is None or length < dim * 8:
            return self.read(length)

        value = StructuredReader(self, length, [("value", 0, [("", 8, float)] * dim)])
        return value.read_structure()

    def read_cdta(self, length):
        reader = StructuredReader(self, length, None)

        reader.skip(13)
        reader.read_attribute("comp_start", 2, int)
        reader.skip(6)
        reader.read_attribute("playhead_position", 2, int)
        reader.skip(6)
        reader.read_attribute("start_frame", 2, int)
        reader.skip(6)
        reader.read_attribute("end_frame", 2, int)
        reader.skip(6)
        reader.read_attribute("comp_duration", 2, int)
        reader.skip(5)
        reader.read_attribute("color", 3, [
            ("", 1, int),
            ("", 1, int),
            ("", 1, int),
        ])
        reader.skip(85)
        reader.read_attribute("width", 2, int)
        reader.read_attribute("height", 2, int)
        reader.skip(12)
        reader.read_attribute("frame_rate", 2, int)

        reader.finalize()
        return reader.value

    def read_ldta(self, length):
        reader = StructuredReader(self, length, None)
        reader.skip(4)
        reader.read_attribute("quality", 2, int)
        reader.skip(15)
        reader.read_attribute("start_frame", 2, int)
        reader.skip(6)
        reader.read_attribute("end_frame", 2, int)
        reader.skip(6)
        reader.read_attribute("attrs", 3, bytes)
        reader.read_attribute("source_id", 4, int)
        reader.skip(20)
        reader.read_attribute_string0("name")

        reader.finalize()

        reader.attr_bit("ddd", 1, 2)
        reader.attr_bit("motion_blur", 2, 3)
        reader.attr_bit("effects", 2, 2)
        reader.attr_bit("locked", 2, 5)

        return reader.value


    def read_idta(self, length):
        reader = StructuredReader(self, length, None)

        reader.read_attribute("type", 2, int)
        reader.skip(14)
        reader.read_attribute("id", 4, int)

        reader.finalize()

        reader.value.type_name = "?"
        if reader.value.type == 4:
            reader.value.type_name = "composition"
        elif reader.value.type == 1:
            reader.value.type_name = "folder"
        elif reader.value.type == 7:
            reader.value.type_name = "footage"

        return reader.value

    def read_ldat(self, length):
        if not self.prop_animated or self.prop_gradient:
            return self.read(length)

        self.prop_animated = False

        reader = StructuredReader(self, length, None)
        value = reader.value
        value.keyframes = []
        size = (6 + 3 * self.prop_dimension) if self.prop_position else (4 + self.prop_dimension)
        while reader.to_read >= 8 + size * 8:
            reader.value = StructuredData()
            reader.read_attribute("attrs", 1, bytes)
            if reader.value.attrs != b'\0':
                reader.skip(7 + size * 8)
                value.keyframes.append(reader.value)
                continue

            reader.read_attribute("time", 2, int)
            reader.skip(5)
            if self.prop_position:
                reader.read_attribute("", 0, [("", 8, float)] * 6)
                reader.read_attribute("value", 0, [("", 8, float)] * self.prop_dimension)
                reader.read_attribute("pos_tan_in", 0, [("", 8, float)] * self.prop_dimension)
                reader.read_attribute("pos_tan_out", 0, [("", 8, float)] * self.prop_dimension)
            else:
                reader.read_attribute("value", 0, [("", 8, float)] * self.prop_dimension)
                reader.read_attribute("", 0, [("", 8, float)] * 3)
                reader.read_attribute("o_x", 8, float)
            value.keyframes.append(reader.value)

        reader.value = value
        reader.finalize()

        return value

    def on_chunk(self, chunk):
        if chunk.header == "shph":
            self.prop_shape = True
        elif chunk.header == "lhd3":
            self.prop_animated = not self.prop_shape
        elif chunk.header == "LIST" and chunk.data.type == "GCst":
            self.prop_gradient = False

    def on_list_start(self, type):
        if type == "GCst":
            self.prop_gradient = True

    def read_properties(self, object, chunk):
        match_name = None
        for item in chunk.data.children:
            if item.header == "tdmn":
                match_name = item.data
            elif item.header == "tdsb":
                object.hidden = (item.data & 1) == 0
            elif item.header == "tdsn" and len(item.data.children) > 0:
                name = item.data.children[0]
                if name.header == "Utf8" and name.data != self.placeholder:
                    object.name = name.data
            elif item.header == "Utf8" and item.data != self.placeholder:
                object.name = item.data
            elif item.header == "LIST" and item.data.type == "tdbs":
                self.set_property(object, match_name, item)
            elif item.header == "LIST" and item.data.type == "tdgp":
                if match_name == "ADBE Vectors Group" or match_name == "ADBE Root Vectors Group":
                    self.read_properties(object, item)
                elif match_name == "ADBE Vector Transform Group" or match_name == "ADBE Transform Group":
                    self.read_properties(object.transform, item)
                elif match_name in self.shapes:
                    child = self.shapes[match_name]()
                    object.add_shape(child)
                    child.match_name = match_name
                    self.read_properties(child, item)
            elif item.header == "LIST" and item.data.type == "GCst" and match_name == "ADBE Vector Grad Colors":
                prop = object.colors.colors
                for i, grad in enumerate(item.data.find_list("GCky").data.children):
                    if grad.header == "Utf8":
                        if not prop.animated:
                            prop.value = parse_gradient_xml(grad.data, object.colors)
                            break
                        elif len(prop.keyframes) < i:
                            prop.keyframes[i].value = parse_gradient_xml(grad.data, object.colors)

    def read_utf8(self, length):
        data = self.read(length).decode("utf8")
        if data.startswith("<?xml version='1.0'?>"):
            dom = ElementTree.fromstring(data)
            if dom.tag == "prop.map":
                return xml_value_to_python(dom)
            else:
                return dom
        else:
            return data

    def read_utf16(self, length):
        return self.read(length).decode("utf16")

    def set_property(self, object, match_name, chunk):
        meta = self.properties.get(match_name)
        if not meta:
            return

        prop_name, converter = meta
        if converter is None:
            converter = lambda x: x

        prop = objects.MultiDimensional()
        for item in chunk.data.children:
            if item.header == "cdat":
                if len(item.data.value) == 1:
                    prop.value = converter(item.data.value[0])
                else:
                    prop.value = converter(NVector(*item.data.value))
            elif item.header == "LIST" and item.data.type == "list":
                self.set_property_keyframes(prop, converter, item)

        setattr(object, prop_name, prop)

    def set_property_keyframes(self, prop, converter, chunk):
        for item in chunk.data.children:
            if item.header == "ldat" and hasattr(item.data, "keyframes"):
                for keyframe in item.data.keyframes:
                    if keyframe.attrs == b'\0':
                        prop.add_keyframe(keyframe.time * self.frame_mult, converter(NVector(*keyframe.value)))

        if len(prop.keyframes) == 1:
            prop.clear_animation(prop.keyframes[0].start)

    def chunk_to_layer(self, chunk):
        lottie_obj = objects.layers.ShapeLayer()

        for item in chunk.data.children:
            if item.header == "Utf8":
                lottie_obj.name = item.data
            elif item.header == "ldta":
                lottie_obj.in_point = item.data.start_frame * self.frame_mult
                lottie_obj.out_point = item.data.end_frame * self.frame_mult
                lottie_obj.threedimensional = item.data.ddd
            elif item.header == "LIST":
                self.read_properties(lottie_obj, item)

        return lottie_obj

    def chunk_to_animation(self, fold):
        anim = objects.Animation()
        for chunk in fold.data.children:
            if chunk.header == "LIST" and chunk.data.type == "Item" and chunk.data.find("idta").data.type == 4:
                break

        for item in chunk.data.children:
            if item.header == "Utf8":
                anim.name = item.data
            elif item.header == "cdta":
                anim.width = item.data.width
                anim.height = item.data.height
                anim.frame_rate = item.data.frame_rate
                self.frame_mult = item.data.frame_rate / 100
                anim.in_point = item.data.start_frame * self.frame_mult
                anim.out_point = item.data.end_frame * self.frame_mult
            elif item.header == "LIST" and item.data.type == "Layr":
                anim.layers.append(self.chunk_to_layer(item))

        return anim


def xml_value_to_python(element):
    if element.tag == "prop.map":
        return xml_value_to_python(element[0])
    elif element.tag == "prop.list":
        return xml_list_to_dict(element)
    elif element.tag == "array":
        return xml_array_to_list(element)
    elif element.tag == "int":
        return int(element.text)
    elif element.tag == "float":
        return float(element.text)
    elif element.tag == "string":
        return element.text
    else:
        return element


def xml_array_to_list(element):
    data = []
    for ch in element:
        if ch.tag != "array.type":
            data.append(xml_value_to_python(ch))
    return data


def xml_list_to_dict(element):
    data = {}
    for pair in element.findall("prop.pair"):
        key = None
        value = None
        for ch in pair:
            if ch.tag == "key":
                key = ch.text
            else:
                value = xml_value_to_python(ch)
        data[key] = value

    return data


def parse_gradient_xml(gradient, colors_prop):
    flat = []

    data = gradient["Gradient Color Data"]

    for stop in data["Color Stops"]["Stops List"].values():
        colors = stop["Stops Color"]
        flat += [colors[0], colors[2], colors[3], colors[4]]

    for stop in data["Alpha Stops"]["Stops List"].values():
        alpha = stop["Stops Alpha"]
        flat += [alpha[0], alpha[2]]

    colors_prop.count = data["Color Stops"]["Stops Size"]

    return NVector(*flat)


@importer("AfterEffect Project", ["aep"])
def import_aep(file):
    if isinstance(file, str):
        with open(file, "rb") as fileobj:
            return import_aep(fileobj)

    parser = AepParser(file)

    for chunk in parser:
        if chunk.header == "LIST" and chunk.data.type == "Fold":
            return parser.chunk_to_animation(chunk)
