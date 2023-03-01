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
    def read_structure(self, structure, parser, length):
        start = parser.file.tell()

        i = 0
        for name, size, type in structure:
            if name == "":
                name = "_%s" % i
                i += 1

            setattr(self, name, self.read_value(parser, size, type))

        read = parser.file.tell() - start
        if read > length:
            raise Exception("Missing data for %s" % self.__class__.__name__)
        elif read < length:
            setattr(self, "_%s" % i, parser.read(length - read))


    def read_value(self, parser, length, type):
        if isinstance(type, list):
            val = []
            for name, size, subtype in type:
                val.append(self.read_value(parser, size, subtype))
            return val

        data = parser.read(length)
        if type is bytes:
            return data
        elif type is int:
            return parser.endian.decode(data)
        elif type is str:
            return data.decode("utf8")
        elif type is float:
            return parser.endian.decode_float64(data)

    @classmethod
    def read(cls, parser, header, length):
        value = cls()
        value.read_structure(cls.structure, parser, length)
        return value


class CompData(StructuredData):
    structure = [
        ("", 13, bytes),
        ("comp_start", 2, int),
        ("", 6, bytes),
        ("playhead_position", 2, int),
        ("", 6, bytes),
        ("start_frame", 2, int),
        ("", 6, bytes),
        ("end_frame", 2, int),
        ("", 6, bytes),
        ("comp_duration", 2, int),
        ("", 5, bytes),
        ("color", 3, [
            ("", 1, int),
            ("", 1, int),
            ("", 1, int),
        ]),
        ("", 85, bytes),
        ("width", 2, int),
        ("height", 2, int),
        ("", 12, bytes),
        ("frame_rate", 2, int),
    ]

    def read_structure(self, structure, parser, length):
        super().read_structure(structure, parser, length)
        self.playhead_position /= 2
        self.start_frame /= 2
        self.end_frame /= 2
        self.comp_duration /= 2
        self.comp_start /= 2


class LayerData(StructuredData):
    structure = [
        ("", 4, bytes),
        ("quality", 2, int),
        ("", 15, bytes),
        ("start_frame", 2, int),
        ("", 6, bytes),
        ("end_frame", 2, int),
        ("", 6, bytes),
        ("attrs", 3, bytes),
        ("source_id", 4, int),
    ]

    def attr_bit(self, byte, bit):
        return (self.attrs[byte] & (1 << bit)) >> bit

    def read_structure(self, structure, parser, length):
        super().read_structure(structure, parser, length)
        self.ddd = self.attr_bit(1, 2) == 1
        self.motion_blur = self.attr_bit(2, 3) == 1
        self.effects = self.attr_bit(2, 2) == 1
        self.locked = self.attr_bit(2, 5) == 1
        self.start_frame /= 2
        self.end_frame /= 2


class ItemData(StructuredData):
    structure = [
        ("type", 2, int),
        ("", 14, bytes),
        ("id", 4, int),
    ]

    def read_structure(self, structure, parser, length):
        super().read_structure(structure, parser, length)
        self.type_name = "?"
        if self.type == 4:
            self.type_name = "composition"
        elif self.type == 1:
            self.type_name = "folder"
        elif self.type == 7:
            self.type_name = "footage"


class PropertyMeta(StructuredData):
    structure = [
        ("", 3, bytes),
        ("components", 1, int),
    ]


def read_floats(parser, header, length):
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


def read_floats32(parser, header, length):
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


class AepParser(RiffParser):
    def __init__(self, file):
        super().__init__(file)

        if self.header.format != "Egg!":
            raise Exception("Not an AEP file")

        self.chunk_parsers = {
            "tdsn": read_sub_chunks,
            "Utf8": read_utf8,
            "tdmn": read_mn,
            "cdta": CompData.read,
            "ldta": LayerData.read,
            "idta": ItemData.read,
            "tdb4": AepParser.read_tdb4,
            "cdat": AepParser.read_cdat,
            "tdum": read_floats,
            "tduM": read_floats,
            "tdsb": lambda p, h, l: p.read_number(l),
        }
        self.prop_dimension = None

    def read_tdb4(self, header, length):
        data = PropertyMeta.read(self, header, length)
        self.prop_dimension = data.components
        return data

    def read_cdat(self, header, length):
        dim = self.prop_dimension
        self.prop_dimension = None

        if dim is None or length < dim * 8:
            return self.read(length)

        value = StructuredData()
        value.read_structure([("value", 0, [("", 8, float)] * dim)], self, length)
        return value

    def chunk_to_group(self, chunk):
        lottie_obj = objects.shapes.Group()

        for item in chunk.data.children:
            pass

        return lottie_obj

    def chunk_to_shape(self, chunk,):
        if chunk.data.type == "tdgp":
            return self.chunk_to_group(chunk)

    def chunk_to_layer(self, chunk):
        lottie_obj = objects.layers.ShapeLayer()

        for item in chunk.data.children:
            if item.header == "Utf8":
                lottie_obj.name = item.data
            elif item.header == "LIST":
                shape = self.chunk_to_shape(item)
                if shape:
                    lottie_obj.add_shape(shape)

        return lottie_obj


    def chunk_to_animation(self, fold):
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
                anim.layers.append(self.chunk_to_layer(item))

        return anim


@importer("AfterEffect Project", ["aep"])
def import_aep(file):
    if isinstance(file, str):
        with open(file, "rb") as fileobj:
            return import_aep(fileobj)

    parser = AepParser(file)

    for chunk in parser:
        if chunk.header == "LIST" and chunk.data.type == "Fold":
            return parser.chunk_to_animation(chunk)
