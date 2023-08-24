import enum
import struct
import ctypes
import typing
import inspect
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
    bits = ctypes.c_uint32((bits >> 23) | (bits << 9)).value

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


# TODO: Do the same for byte?
class uint(int):
    pass


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
        if self == FieldType.Uint:
            return uint
        if self in (FieldType.Byte, FieldType.Int):
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
    keywords = {"if", "in" "def", "else", "elif", "from", "import", "class", "lambda"}

    def __init__(self):
        self._name = ""
        self.type = None
        self.is_array = False
        self.value = 0
        self.original_name = ""

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, v):
        self.original_name = v
        self._name = v
        if v in self.keywords:
            self._name += "_"

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
            read_item = lambda file: definition.read_data(file, schema)

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
            write_item = lambda file, v: definition.write_data(file, schema, v)

        if self.is_array:
            return write_array(file, v, write_item)

        return write_item(file, v)

    @classmethod
    def read_binary_schema(cls, file):
        field = cls()
        field.name = read_string(file)
        field.type = read_int(file)
        if field.type < 0:
            try:
                field.type = FieldType(field.type)
            except ValueError:
                pass
        field.is_array = read_bool(file)
        field.value = read_uint(file)
        return field

    def write_binary_schema(self, file):
        write_string(file, self.original_name)
        write_int(file, self.type.value if isinstance(self.type, FieldType) else self.type)
        write_bool(file, self.is_array)
        write_uint(file, self.value)

    def __repr__(self):
        return "<Field %s %s%s %s>" % (self.name, self.type, "[]" if self.is_array else "", self.value)


def write_binary_schema(file, v):
    v.write_binary_schema(file)


def get_item(dict, key):
    return dict[key]


class Definition:
    def __init__(self):
        self.name = ""
        self.type = None
        self.fields = []
        self.field_by_id = {}
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
            self.field_by_id[field.value] = field

        if self.python_type:
            return

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

        setattr(schema.module, self.name, self.python_type)

    def write_text_schema(self, file, schema):
        file.write("\n%s %s {\n" % (self.type.name.lower(), self.name))
        if self.type == DefinitionType.Enum:
            for field in self.fields:
                file.write("    %s = %s;\n" % (field.original_name, field.value))
        elif self.type == DefinitionType.Struct:
            for field in self.fields:
                file.write("    %s %s;\n" % (schema.type_name(field), field.original_name))
        elif self.type == DefinitionType.Message:
            for field in self.fields:
                file.write("    %s %s = %s;\n" % (schema.type_name(field), field.original_name, field.value))

        file.write("}\n")

    def write_binary_schema(self, file):
        write_string(file, self.name)
        write_byte(file, self.type.value)
        write_array(file, self.fields, write_binary_schema)

    def write_python_schema(self, file, schema):
        ind = " " * 4
        file.write("\n")

        if self.type == DefinitionType.Enum:
            file.write("class %s(enum.Enum):\n" % self.name)
            for field in self.fields:
                file.write("%s%s = %s\n" % (ind, field.name, field.value))
        elif self.type == DefinitionType.Struct:
            file.write("@dataclasses.dataclass(slots=True)\n")
            file.write("class %s:\n" % self.name)
            for field in self.fields:
                file.write("%s%s: %s\n" % (ind, field.name, schema.python_type_string(field)))
        elif self.type == DefinitionType.Message:
            file.write("@dataclasses.dataclass\n")
            file.write("class %s:\n" % self.name)
            for field in self.fields:
                file.write("%s%s: typing.Optional[%s] = None\n" % (ind, field.name, schema.python_type_string(field)))

        file.write("\n")

    def read_data(self, file, schema):
        if self.type == DefinitionType.Enum:
            return self.python_type(read_uint(file))

        if self.type == DefinitionType.Struct:
            kw = {}
            for field in self.fields:
                kw[field.name] = field.read_value(file, schema)
            return self.python_type(**kw)

        if self.type == DefinitionType.Message:
            val = self.python_type()
            while True:
                field_id = read_uint(file)
                if field_id == 0:
                    break
                field = self.field_by_id[field_id]
                setattr(val, field.name, field.read_value(file, schema))
            return val

    def write_data(self, file, schema, v):
        if self.type == DefinitionType.Enum:
            if isinstance(v, str):
                v = self.python_type[v]
            if not isinstance(v, int):
                v = v.value
            write_uint(file, v)

        elif self.type == DefinitionType.Struct:
            if isinstance(v, dict):
                getter = get_item
            else:
                getter = getattr

            for field in self.fields:
                fv = getter(v, field.name)
                field.write_value(file, schema, fv)

        elif self.type == DefinitionType.Message:
            if isinstance(v, dict):
                getter = get_item
            else:
                getter = getattr

            for field in self.fields:
                try:
                    fv = getter(v, field.name)
                except Exception:
                    fv = None

                if fv is not None:
                    write_uint(file, field.value)
                    field.write_value(file, schema, fv)

            file.write(b'\0')

    def __str__(self):
        return "%s %s" % (self.type.name.lower(), self.name)

    def __repr__(self):
        return "<Definition %s>" % self


class Module:
    pass


class Schema:
    def __init__(self):
        self.definitions = []
        self.module = Module()

    def read_binary_schema(self, file):
        self.definitions = read_array(file, self.read_binary_schema_definition)
        self.compile()

    def compile(self):
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

    def type_name(self, type):
        if isinstance(type, Field):
            base = self.type_name(type.type)
            if type.is_array:
                base += "[]"
            return base

        if isinstance(type, FieldType):
            return type.name.lower()
        return self.definitions[type].name

    def python_type(self, type):
        if isinstance(type, Field):
            if type.is_byte_array:
                return bytes
            base = self.python_type(type.type)
            if type.is_array:
                return list[base]
            return base

        if isinstance(type, FieldType):
            return type.to_python_type()

        return self.definitions[type].name

    def python_type_string(self, type):
        if isinstance(type, Field) and type.is_array and type.type == FieldType.Uint:
            return "list[uint]"
        pt = self.python_type(type)
        if pt in (int, float, str, bytes, bool, uint):
            if isinstance(type, Field) and type.name == pt.__name__:
                return '__builtins__["%s"]' % pt.__name__
            return pt.__name__
        return repr(pt)

    def write_text_schema(self, file):
        for definition in self.definitions:
            definition.write_text_schema(file, self)

    def write_python_schema(self, file):
        file.write("import enum\nimport typing\nimport dataclasses\n\n\nclass uint(int):\n    pass\n\n")
        for definition in self.definitions:
            definition.write_python_schema(file, self)

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.definitions[key]
        for d in self.definitions:
            if d.name == key:
                return d
        raise KeyError(key)


def json_encode(v):
    if hasattr(type(v), "__slots__"):
        out = {}
        for slot in v.__slots__:
            s = getattr(v, slot)
            if s is not None:
                out[slot] = s
        return out
    elif isinstance(v, enum.Enum):
        return v.name
    elif isinstance(v, bytes):
        return list(v)
    else:
        out = {}
        for k, s in vars(v).items():
            if s is not None:
                out[k] = s
        return out


def module_to_schema_type(field, type, uint, fields_to_fix):
    if typing.get_origin(type) is typing.Union:
        type = typing.get_args(type)[0]

    if type is bytes:
        field.is_array = True
        field.type = FieldType.Byte
        return

    if typing.get_origin(type) is list:
        field.is_array = True
        type = typing.get_args(type)[0]

    if isinstance(type, typing.ForwardRef):
        field.type = type.__forward_arg__
        fields_to_fix.append(field)
    elif isinstance(type, str):
        field.type = type
        fields_to_fix.append(field)
    elif type is int:
        field.type = FieldType.Int
    elif type is bool:
        field.type = FieldType.Bool
    elif type is uint:
        field.type = FieldType.Uint
    elif type is float:
        field.type = FieldType.Float
    elif type is str:
        field.type = FieldType.String
    else:
        breakpoint()
        raise ValueError("Not a valid type: %s" % type)


def module_to_schema(module):
    index = 0
    schema = Schema()
    fields_to_fix = []
    uint_class = uint
    definitions = {}

    for name, value in vars(module).items():
        if name.startswith("_") or not inspect.isclass(value):
            continue

        if issubclass(value, int):
            uint_class = value
            continue

        definition = Definition()
        definitions[name] = len(schema.definitions)
        schema.definitions.append(definition)
        definition.name = name
        definition.python_type = value

        if issubclass(value, enum.Enum):
            definition.type = DefinitionType.Enum
            for v in value:
                f = Field()
                f.name = v.name.strip("_")
                f.type = FieldType.Uint
                f.value = v.value
                definition.fields.append(f)
        elif hasattr(value, "__slots__"):
            definition.type = DefinitionType.Struct
            for field in value.__dataclass_fields__.values():
                f = Field()
                f.name = field.name.strip("_")
                module_to_schema_type(f, field.type, uint_class, fields_to_fix)
                definition.fields.append(f)
        else:
            definition.type = DefinitionType.Message
            for index, field in enumerate(value.__dataclass_fields__.values()):
                f = Field()
                f.name = field.name.strip("_")
                module_to_schema_type(f, field.type, uint_class, fields_to_fix)
                f.value = index + 1
                definition.fields.append(f)

    for field in fields_to_fix:
        field.type = definitions[field.type]

    schema.compile()
    schema.module = module
    return schema
