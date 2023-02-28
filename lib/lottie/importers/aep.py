from dataclasses import dataclass
import struct

from .base import importer
from .. import objects


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


class LittleEndian(Endianness):
    def decode(self, data):
        return BigEndian.decode_data(reversed(data))

    def decode_float64(self, data):
        return struct.unpack("<d", data)[0]


@dataclass
class RiffChunk:
    header : str
    length : int
    data : bytes


@dataclass
class RiffList:
    type : str
    children : tuple

@dataclass
class RiffHeader:
    endianness : Endianness
    length : int
    format : str


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
            children = []
            while self.file.tell() < end:
                children.append(self.read_chunk())
            data = RiffList(type, tuple(children))
        elif header in self.chunk_parsers:
            data = self.chunk_parsers[header](self, header, length)
        else:
            data = self.read(length)

        if data is None:
            raise Exception("Incomplete chunk")

        chunk = RiffChunk(header, length, data)

        # Skip pad byte
        if length % 2:
            self.read(1)

        return chunk

    def __iter__(self):
        while True:
            if self.file.tell() >= self.end:
                return

            yield self.read_chunk()


def read_sub_chunks(parser, header, length):
    end = parser.file.tell() + length
    children = []
    while parser.file.tell() < end:
        children.append(parser.read_chunk())
    return RiffList("", tuple(children))


def read_utf8(parser, header, length):
    return parser.read(length).decode("utf8")


def read_mn(parser, header, length):
    return parser.read(length).strip(b"\0").decode("utf8")


class StructuredData:
    def __init__(self, parser, header, length):
        data = parser.read(length)
        self.parse(data, parser.endian)


class CompData(StructuredData):
    def __init__(self, parser, header, length):
        start = parser.file.tell()
        parser.read(4)
        self.fr_den = parser.read_number(4)
        self.fr_num = parser.read_number(4)
        parser.read(32)
        self.time_den = parser.read_number(4)
        self.time_num = parser.read_number(4)
        self.color = parser.read(3)
        parser.read(85)
        self.width = parser.read_number(2)
        self.height = parser.read_number(2)
        parser.read(12)
        self.frame_rate = parser.read_number(2)
        read = parser.file.tell() - start
        if read > length:
            raise Exception("Missing composition data")
        elif read < length:
            parser.read(length - read)



class LayerData(StructuredData):
    def attr_bit(self, byte, bit):
        return (self.attrs[byte] & (1 << bit)) >> bit

    def parse(self, data, endian):
        self.quality = endian.decode(data[4:6])
        self.attrs = data[37:40]
        self.source_id = endian.decode(data[40:44])
        self.blend_mode = self.attr_bit(0, 2)
        self.ddd = self.attr_bit(1, 2) == 1
        self.motion_blur = self.attr_bit(2, 3) == 1
        self.effects = self.attr_bit(2, 2) == 1
        self.locked = self.attr_bit(2, 5) == 1


class ItemData(StructuredData):
    def parse(self, data, endian):
        self.type = endian.decode(data[0:2])
        self.id = endian.decode(data[16:20])
        self.type_name = "?"
        if self.type == 4:
            self.type_name = "composition"
        elif self.type == 1:
            self.type_name = "folder"
        elif self.type == 7:
            self.type_name = "footage"


class PropertyMeta(StructuredData):
    def parse(self, data, endian):
        self._1 = data[0:3]
        self.components = data[3]
        self._2 = data[4:]


def read_floats(parser, header, length):
        if length < 8:
            return parser.read(length)

        if length == 8:
            return parser.endian.decode_float64(parser.read(8))

        floats = {}
        to_read = length
        while to_read >= 8:
            floats[len(floats)] = parser.endian.decode_float64(parser.read(8))
            to_read -= 8

        if to_read:
            floats["?"] = parser.read(to_read)
        return floats


def format_yaml(val):
    if isinstance(val, bytes):
        return "\"%s\"" % str(val)[2:-1]
    return val

def debug_yaml(chunk, indp=""):
    ind = indp + ("- " if indp else "")
    if isinstance(chunk.data, RiffList):
        print("%s%s: %s" % (ind, chunk.header, chunk.data.type))
        for sub in chunk.data.children:
            debug_yaml(sub, indp + "    ")
    else:
        dict_data = {}

        if isinstance(chunk.data, dict):
            print_data = ""
            dict_data = chunk.data
        elif isinstance(chunk.data, StructuredData):
            print_data = ""
            dict_data = vars(chunk.data)
        else:
            print_data = chunk.data

        print("%s%s: %s" % (ind, chunk.header, format_yaml(print_data)))

        for k, v in dict_data.items():
            print("%s    - %s: %s" % (indp, k, format_yaml(v)))


def chunk_to_group(chunk, endian):
    lottie_obj = objects.shapes.Group()

    for item in chunk.data.children:
        pass

    return lottie_obj


def chunk_to_shape(chunk, endian):
    if chunk.data.type == "tdgp":
        return chunk_to_group(chunk, endian)


def chunk_to_layer(chunk, endian):
    lottie_obj = objects.layers.ShapeLayer()

    for item in chunk.data.children:
        if item.header == "Utf8":
            lottie_obj.name = item.data
        elif item.header == "LIST":
            shape = chunk_to_shape(item, endian)
            if shape:
                lottie_obj.add_shape(shape)

    return lottie_obj



def chunk_to_animation(fold, endian):
    anim = objects.Animation()
    for chunk in fold.data.children:
        if chunk.header == "LIST" and chunk.data.type == "Item":
            break

    for item in chunk.data.children:
        if item.header == "Utf8":
            anim.name = item.data
        elif item.header == "cdta":
            anim.width = item.data.width
            anim.height = item.data.height
            anim.frame_rate = item.data.frame_rate
        elif item.header == "LIST" and item.data.type == "Layr":
            anim.layers.append(chunk_to_layer(item, endian))

    return anim


@importer("AfterEffect Project", ["aep"])
def import_aep(file):
    if isinstance(file, str):
        with open(file, "rb") as fileobj:
            return import_aep(fileobj)

    parser = RiffParser(file)

    if parser.header.format != "Egg!":
        raise Exception("Not an AEP file")

    parser.chunk_parsers = {
        "tdsn": read_sub_chunks,
        "Utf8": read_utf8,
        "tdmn": read_mn,
        "cdta": CompData,
        "ldta": LayerData,
        "idta": ItemData,
        "tdb4": PropertyMeta,
        "cdat": read_floats,
        "ldat": read_floats,
        "tdum": read_floats,
        "tduM": read_floats,
    }

    for chunk in parser:
        debug_yaml(chunk)
        if chunk.header == "LIST" and chunk.data.type == "Fold":
            return chunk_to_animation(chunk, parser.endian)
