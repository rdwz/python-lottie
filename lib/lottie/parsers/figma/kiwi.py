import enum
import struct
import ctypes
import typing
import dataclasses


def read_byte(file):
    return file.read(1)[0]


def read_bool(file):
    return bool(read_byte(file))


def read_uint(file):
    result = 0
    shift = 0

    while True:
        byte = read_byte(file)

        result |= (byte & 0x7f) << shift
        shift += 7

        if not (byte & 0x80):
            return result


def read_int(file):
    uint = read_uint(file)
    if uint & 1:
        return ~(uint >> 1)
    return uint >> 1


def read_float(file):
    first = read_byte(file)

    if first == 0:
        return 0

    bits = first
    bits |= read_byte(file) << 8
    bits |= read_byte(file) << 16
    bits |= read_byte(file) << 24

    bits = ctypes.c_int32((bits << 23) | (bits >> 9)).value

    return struct.unpack(">f", struct.pack(">i", bits))[0]


def read_string(file):
    data = b''
    while True:
        b = file.read(1)
        if b == b'' or b == b'\0':
            break
        data += b

    return data.decode("utf-8")


def read_array(file, item_read_func):
    count = read_uint(file)
    vals = []
    for i in range(count):
        vals.append(item_read_func(file))
    return vals


def read_byte_array(file):
    count = read_uint(file)
    return file.read(count)


def write_byte(file, byte):
    file.write(bytes([byte]))


def write_bool(file, v):
    write_byte(file, v)


def write_uint(file, v):
    while True:
        byte = v & 0x7f
        v >>= 7
        if v == 0:
            write_byte(file, byte)
            break

        write_byte(file, byte | 0x80)


def write_int(file, v):
    write_uint(file, ctypes.c_uint32((v << 1) ^ (v >> 31)).value)


def write_float(file, v):
    bits = struct.unpack(">i", struct.pack(">f", v))[0]
    bits = ctypes.c_uint32((bits >> 23) | (bits << 9)).value;

    if (bits & 0xff) == 0:
        file.write(b'\0')
        return

    file.write(bytes([
        bits & 0xff,
        (bits >> 8) & 0xff,
        (bits >> 16) & 0xff,
        (bits >> 24) & 0xff,
    ]))


def write_string(file, v: str):
    file.write(v.encode("utf8"))
    file.write(b'\0')


def write_array(file, v, item_write_func):
    write_uint(file, len(v))

    for item in v:
        item_write_func(file, item)


def write_byte_array(file, v):
    write_uint(file, len(v))
    file.write(v)


class DefinitionType(enum.Enum):
    Enum = 0
    Struct = 1
    Message = 2


class FieldType(enum.Enum):
    Bool = -1
    Byte = -2
    Int = -3
    Uint = -4
    Float = -5
    String = -6

    def to_python_type(self):
        if self == FieldType.Bool:
            return bool
        if self in (FieldType.Byte, FieldType.Int, FieldType.Uint):
            return int
        if self == FieldType.Float:
            return float
        if self == FieldType.String:
            return str

    def read_value(self, file):
        if self == FieldType.Bool:
            return read_bool(file)
        if self == FieldType.Byte:
            return read_byte(file)
        if self == FieldType.Int:
            return read_int(file)
        if self == FieldType.Uint:
            return read_uint(file)
        if self == FieldType.Float:
            return read_float(file)
        if self == FieldType.String:
            return read_string(file)

    def write_value(self, file, v):
        if self == FieldType.Bool:
            return write_bool(file, v)
        if self == FieldType.Byte:
            return write_byte(file, v)
        if self == FieldType.Int:
            return write_int(file, v)
        if self == FieldType.Uint:
            return write_uint(file, v)
        if self == FieldType.Float:
            return write_float(file, v)
        if self == FieldType.String:
            return write_string(file, v)


class Field:
    def __init__(self):
        self.name = ""
        self.type = None
        self.is_array = False
        self.value = 0

    @property
    def is_byte_array(self):
        return self.is_array and self.type == FieldType.Byte

    def read_value(self, file, schema):
        if self.is_byte_array:
            return read_byte_array(file)

        if isinstance(self.type, FieldType):
            read_item = self.type.read_value
        else:
            definition = schema.definitions[self.type]
            read_item = lambda file: schema.read_value(file, definition)

        if self.is_array:
            return read_array(file, read_item)

        return read_item(file)

    def write_value(self, file, schema, v):
        if self.is_byte_array:
            return write_byte_array(file, v)

        if isinstance(self.type, FieldType):
            write_item = self.type.write_value
        else:
            definition = schema.definitions[self.type]
            write_item = lambda file, v: schema.write_value(file, definition, v)

        if self.is_array:
            return write_array(file, write_item, v)

        return write_item(file, v)

    @classmethod
    def read_binary_schema(cls, file):
        field = cls()
        field.name = read_string(file)
        field.type = read_int(file)
        if field.type < 0:
            field.type = FieldType(field.type)
        field.is_array = read_bool(file)
        field.value = read_uint(file)
        return field

    def write_binary_schema(self, file):
        write_string(file, self.name)
        write_int(file, self.type.value if isinstance(self.type, FieldType) else self.type)
        write_bool(file, self.is_array)
        write_uint(file, self.value)

    def __repr__(self):
        return "<Field %s %s%s %s>" % (self.name, self.type, "[]" if self.is_array else "", self.value)


def write_binary_schema(file, v):
    v.write_binary_schema(file)

class Definition:
    def __init__(self):
        self.name = ""
        self.type = None
        self.fields = []
        self.python_type = None

    def compile(self, schema):
        fields = []
        for field in self.fields:
            if isinstance(field.type, int):
                if field.type > len(schema.definitions):
                    raise ValueError(
                        "Invalid field type %s for %s.%s" % (
                            field.type,
                            self.name,
                            field.name
                        )
                    )
                py_type = schema.definitions[field.type].name
            else:
                if field.is_array and field.type == FieldType.Byte:
                    py_type = bytes
                py_type = field.type.to_python_type()

            fields.append((field.name, py_type, field.value))

        if self.type == DefinitionType.Struct:
            self.python_type = dataclasses.make_dataclass(
                self.name,
                [(f[0], f[1]) for f in fields],
                slots=True
            )
        elif self.type == DefinitionType.Enum:
            self.python_type = enum.Enum(
                self.name,
                [(f[0], f[2]) for f in fields]
            )
        elif self.type == DefinitionType.Message:
            self.python_type = dataclasses.make_dataclass(
                self.name,
                [(f[0], typing.Optional[f[1]], dataclasses.field(default=None)) for f in fields],
            )

    def write_text_schema(self, file, schema):
        file.write("\n%s %s {\n" % (self.type.name.lower(), self.name))
        if self.type == DefinitionType.Enum:
            for field in self.fields:
                file.write("    %s = %s;\n" % (field.name, field.value))
        elif self.type == DefinitionType.Struct:
            for field in self.fields:
                file.write("    %s %s;\n" % (schema.type_name(field), field.name))
        elif self.type == DefinitionType.Message:
            for field in self.fields:
                file.write("    %s %s = %s;\n" % (schema.type_name(field), field.name, field.value))

        file.write("}\n")

    def write_binary_schema(self, file):
        write_string(file, self.name)
        write_byte(file, self.type.value)
        write_array(file, self.fields, write_binary_schema)

    def __str__(self):
        return "%s %s" % (self.type.name.lower(), self.name)

    def __repr__(self):
        return "<Definition %s>" % self


class Schema:
    def __init__(self):
        self.definitions = []

    def read_binary_schema(self, file):
        self.definitions = read_array(file, self.read_binary_schema_definition)

        for definition in self.definitions:
            definition.compile(self)

    def write_binary_schema(self, file):
        write_array(file, self.definitions, write_binary_schema)

    def read_binary_schema_definition(self, file):
        definition = Definition()
        definition.name = read_string(file)
        definition.type = DefinitionType(read_byte(file))
        definition.fields = read_array(file, Field.read_binary_schema)
        if definition.type == DefinitionType.Enum:
            for field in definition.fields:
                field.type = FieldType.Uint
        return definition

    def read_data(self, file, definition):
        if definition.type == DefinitionType.Enum:
            return definition.python_type(read_uint(file))

        val = definition.python_type()
        for field in fields:
            setattr(val, field.name, field.read_value(file, self))

    def type_name(self, type):
        if isinstance(type, Field):
            base = self.type_name(type.type)
            if type.is_array:
                base += "[]"
            return base

        if isinstance(type, FieldType):
            return type.name.lower()
        return self.definitions[type].name

    def write_text_schema(self, file):
        for definition in self.definitions:
            definition.write_text_schema(file, self)
