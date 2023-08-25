import io
import enum
import struct


class Endian(enum.Enum):
    Big = ">"
    Little = "<"


class Type(enum.Enum):
    Int16 = "h"
    Uint16 = "H"
    Int32 = "i"
    Uint32 = "I"
    Int64 = "q"
    Uint64 = "Q"
    Float32 = "f"
    Float64 = "d"


class BinStream:
    def __init__(self, wrapped = None, endian: Endian = None):
        if isinstance(wrapped, bytes):
            wrapped = io.BytesIO(wrapped)
        elif wrapped is None:
            wrapped = io.BytesIO()

        self.wrapped = wrapped
        self.endian = endian

    def read(self, type: Type|str|None|int, endian: Endian|None):
        if isinstance(type, int):
            return self.wrapped.read(type)

        f, length = self.struct_format(type, endian)
        raw = self.wrapped.read(length)
        return struct.unpack(f, raw)[0]


    def write(self, value, type: Type|str|None, endian: Endian|None = None):
        if type is None:
            self.wrapped.write(value)
            return

        f = self.struct_format(type, endian)[0]
        self.wrapped.write(struct.pack(f, value))

    def type_from_string(self, type_str: str):
        type_str = type_str.lower()

        endian = None
        if type_str.endswith("e"):
            if type_str[-2] == "l":
                endian = Endian.Little
            elif type_str[-2] == "b":
                endian = Endian.Big
            type_str = type_str[:-2]

        type = Type[type_str.title()]

        return type, endian

    def struct_format(self, type: Type|str|None, endian: Endian|None = None):
        if isinstance(type, str):
            type, endian = self.type_from_string(type)

        length = int(type.name[-2:]) // 8
        if endian is None:
            endian = self.endian
            if endian is None:
                raise ValueError("Missing endianness")

        return (endian.value + type.value), length

    def __getattr__(self, name: str):
        if name.startswith("read_"):
            type, endian = self.type_from_string(name.split("_", 1)[-1])
            def reader():
                return self.read(type, endian)
            return reader
        elif name.startswith("write_"):
            type, endian = self.type_from_string(name.split("_", 1)[-1])
            def writer(value):
                return self.write(value, type, endian)
            return writer

        return super().__getattr__(name)

    def skip(self, size):
        self.wrapped.read(size)
