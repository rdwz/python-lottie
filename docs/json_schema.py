#!/usr/bin/env python3
import os
import re
import sys
import json
import inspect
import pkgutil
import pathlib
import argparse
import importlib
import collections
sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "lib"
))
import lottie
import lottie.objects
import lottie.objects.shapes
from lottie.objects.base import LottieEnum, LottieObject, PseudoList, LottieBase, PseudoBool, LottieProp

name_map = {
    "EffectNoValue": "no-value",
    "Precomp": "precomposition",
    "Matte3Effect": "matte3-effect",
    "PreCompLayer": "precomposition-layer",
    "AnimatableMixin": "animated-property",
    "Rect": "rectangle",
    "Star": "polystar",
    "EffectValue": "effect-value",
    "Chars": "character-data",
    "CharacterData": "character-data-shape",
    "TransformShape": "transform",
    "PositionValue": "position",
    "PseudoBool": "int-boolean",
}


def class_name_to_ref(name):
    if name in name_map:
        return name_map[name]
    elif name.startswith("EffectValue"):
        name = name[len("EffectValue"):]
    return re.sub("([a-z])([A-Z])", r"\1-\2", name).lower()


def get_docs(cls):
    if cls.__doc__ is None or cls.__doc__ == "An enumeration.":
        return ""
    return inspect.cleandoc(cls.__doc__.lstrip("!"))


def builtin_type_name(type):
    if type is float:
        return "number"
    if type is int:
        return "integer"
    if type is str:
        return "string"
    if type is bool:
        return "boolean"
    return None


def class_dirname(cls):
    if issubclass(cls, LottieEnum):
        return "constants"
    module = cls.__module__.split(".")[-1]
    if module == "bezier":
        return "helpers"
    elif module == "properties" or module == "easing":
        return "animated-properties"
    elif module == "composition":
        return "animation"
    if issubclass(cls, lottie.objects.effects.EffectValue):
        return "effect-values"
    return module


def class_full_ref(cls):
    return "#/$defs/%s/%s" % (class_dirname(cls), class_name_to_ref(cls.__name__))


def chunks_to_camel(chunks):
    return "".join(x[0].upper() + x[1:] for x in chunks)

def class_name_from_full_ref(ref):
    if ref.startswith("#/$defs/"):
        ref = ref[len("#/$defs/"):]

    dirname, classname = ref.split("/")

    py_class_name = None

    for key, value in name_map.items():
        if value == classname:
            py_class_name = key
            break
    else:
        if dirname == "effect-values":
            classname = "effect-value-" + classname
        py_class_name = chunks_to_camel(classname.split("-"))

    return py_class_name


def class_from_full_ref(ref):
    return getattr(lottie.objects, class_name_from_full_ref(ref))


def scalar_type(json_prop, prop, default):
    name = prop.type.__name__

    if name == "NVector":
        json_prop["type"] = "number"
    elif prop.type in (int, float, str, bool):
        json_prop["type"] = builtin_type_name(prop.type)
    elif prop.type is PseudoBool:
        json_prop["$ref"] = "#/$defs/helpers/int-boolean"
        if default is not None:
            default = int(default)
    elif name == "Color":
        json_prop["$ref"] = "#/$defs/helpers/color"
    elif inspect.isclass(prop.type) and issubclass(prop.type, LottieEnum):
        json_prop["$ref"] = class_full_ref(prop.type)
        default = default.value if default else None
    elif inspect.isclass(prop.type) and issubclass(prop.type, LottieObject):
        json_prop["$ref"] = class_full_ref(prop.type)
        default = None
    elif name == "Color string":
        json_prop["type"] = "string"
    elif name == "dict":
        json_prop["type"] = "object"
    else:
        raise Exception("Handle scalar type %s" % name)

    if default is not None:
        if isinstance(default, lottie.objects.properties.AnimatableMixin):
            default = default.value
        if isinstance(default, lottie.NVector):
            default = default.components
        json_prop["default"] = default


def extract_type(json_prop, prop, instance):
    name = prop.type.__name__
    default = getattr(instance, prop.name, None)
    if name == "NVector" or prop.list:
        json_prop["type"] = "array"
        item = {}
        scalar_type(item, prop, default)
        json_prop["items"] = item
    else:
        scalar_type(json_prop, prop, default)
    return name


def add_property(json_properties, property, instance):
    json_prop = {
        "title": property_title(property.name)
    }
    extract_type(json_prop, property, instance)
    json_properties[property.lottie] = json_prop


def property_title(prop_name):
    return " ".join(
        word[0].upper() + word[1:]
        for word in prop_name.split("_")
    )


def class_title(name):
    return re.sub("([a-z])([A-Z])", r"\1 \2", name)


def class_data(cls):
    clsname = cls.__name__
    if issubclass(cls, LottieObject):
        structure = []
        index = 0
        for base in cls.__bases__:
            if base != LottieObject:
                structure.append({
                    "$ref": class_full_ref(base)
                })
            index += len(getattr(base, "_props", []))

        required = []
        json_properties = {}

        for prop in cls._props[:index]:
            if hasattr(cls, prop.name) and not isinstance(getattr(cls, prop.name), property):
                required.append(prop.lottie)
                json_properties[prop.lottie] = {
                    "title": property_title(prop.name),
                    "type": builtin_type_name(prop.type),
                    "const": getattr(cls, prop.name)
                }

        if issubclass(cls, lottie.objects.Effect):
            json_properties["ef"] = {
                "title": "Effect values",
                "type": "array",
                "prefixItems": [
                    {
                        "title": name,
                        "$ref": class_full_ref(ev_class),
                    }
                    for name, ev_class in cls._effects
                ]
            }

        instance = cls()
        for prop in cls._props[index:]:
            add_property(json_properties, prop, instance)

        own_structure = {
            "type": "object",
            "properties": json_properties,
            "required": required,
        }

        structure.append(own_structure)

        return {
            "type": "object",
            "title": class_title(clsname),
            "description": get_docs(cls),
            "allOf": structure,
        }
    elif issubclass(cls, LottieEnum):
        type = "integer"
        values = []

        for name, val in cls.__members__.items():
            if isinstance(val, str):
                type = "string"
            values.append({
                "title": class_title(name),
                "const": val.value
            })

        return {
            "type": type,
            "title": clsname,
            "description": get_docs(cls),
            "oneOf": values
        }


def output_module(module, schema, output):
    print(module)
    for clsname, cls in inspect.getmembers(module):
        if inspect.isclass(cls) and issubclass(cls, LottieBase) and cls.__module__ == module.__name__:
            output_class(cls, schema, output)


def output_class(cls, schema, output: pathlib.Path):
    print(cls)
    json_data = {
        "$schema": schema
    }
    json_data.update(class_data(cls))
    path = output / class_dirname(cls)
    path.mkdir(parents=True, exist_ok=True)
    with open(path / (class_name_to_ref(cls.__name__) + ".json"), "w") as file:
        json.dump(json_data, file, indent=4)


def loop_modules():
    for _, modname, _ in pkgutil.iter_modules(lottie.objects.__path__):
        if modname == "base":
            continue

        full_modname = "lottie.objects." + modname
        yield importlib.import_module(full_modname)


def action_output(subject, ns):
    if subject is None:
        for module in loop_modules():
            output_module(module, ns.schema, ns.output)
    elif inspect.isclass(subject):
        output_class(subject, ns.schema, ns.output)
    else:
        output_module(subject, ns.schema, ns.output)


class Schema:
    def __init__(self, json):
        self.data = json

    def find(self, ref: str):
        try:
            return self.get_ref(ref)
        except KeyError:
            return None

    def get_ref(self, ref: str):
        if not ref.startswith("#/"):
            ref = "$defs/" + ref
        return self.get_path(ref.strip("#").strip("/").split("/"))

    def get_path(self, path):
        schema = self.data
        for chunk in path:
            schema = schema[chunk]
        return schema


error_class = None


def check_error(cls, msg):
    global error_class
    if error_class is not cls:
        print("")
        print(class_full_ref(cls))
        error_class = cls
    print("%s.%s: %s" % (cls.__module__, cls.__name__, msg))


def check_error_prop(cls, prop, msg):
    check_error(cls, "%s (%s): %s" % (prop.name, prop.lottie, msg))


def check_class_schema_of(schema_obj: dict, schema_bases: set, properties: dict):
    if "$ref" in schema_obj:
        schema_bases.add(schema_obj["$ref"])
    elif "properties" in schema_obj:
        properties.update(schema_obj["properties"])
    elif "if" in schema_obj:
        check_class_schema_of(schema_obj.get("then", {}), schema_bases, properties)
        check_class_schema_of(schema_obj.get("else", {}), schema_bases, properties)


def get_type_from_schema_obj(obj):
    if "$ref" in obj:
        return obj["$ref"]
    return obj.get("type", None)


def check_prop(cls, prop: LottieProp, properties: dict, instance: LottieObject):
    try:
        if prop.lottie not in properties:
            check_error_prop(cls, prop, "not in schema")
            return

        prop_schema = properties.pop(prop.lottie)
        title = prop_schema["title"].replace(" ", "_").lower()
        if title != prop.name:
            check_error_prop(cls, prop, "Name mismatch: %s" % (title))

        expected_type_schema = {}
        extract_type(expected_type_schema, prop, instance)

        # TODO check defaults

        expected_type = get_type_from_schema_obj(expected_type_schema)
        actual_type = get_type_from_schema_obj(prop_schema)
        if expected_type != actual_type:
            check_error_prop(cls, prop, "type mismatch: %s %s" % (expected_type, actual_type))
        elif expected_type == "array":
            expected_type = get_type_from_schema_obj(expected_type_schema["items"])
            actual_type = get_type_from_schema_obj(prop_schema["items"])
    except Exception:
        check_error_prop(cls, prop, "Exception!")
        raise


def do_check_class(cls, schema: Schema, all_defs):
    ref = class_full_ref(cls)
    class_schema = schema.find(ref)
    all_defs.discard(ref)
    if class_schema is None:
        check_error(cls, "Not found in the schema")
        return

    if issubclass(cls, LottieObject):
        properties = dict(class_schema.get("properties", {}))
        schema_bases = set()
        for base in class_schema.get("allOf", []):
            check_class_schema_of(base, schema_bases, properties)
        for base in class_schema.get("anyOf", []):
            check_class_schema_of(base, schema_bases, properties)

        index = 0
        for base in cls.__bases__:
            base_ref = class_full_ref(base)
            if base_ref in schema_bases:
                schema_bases.remove(base_ref)
            elif base != LottieObject:
                check_error(cls, "Base not in schema: %s" % base)
            index += len(getattr(base, "_props", []))

        if schema_bases:
            check_error(cls, "Missing bases: %s" % " ".join(schema_bases))

        if issubclass(cls, lottie.objects.Effect) and cls is not lottie.objects.Effect:
            ef = properties.pop("ef", {})
            schema_values = ef.get("prefixItems", [])
            if len(schema_values) != len(cls._effects):
                check_error(cls, "Mismatching effect values")

            for (schema_value, value) in zip(schema_values, cls._effects):
                if schema_value["title"] != value[0]:
                    check_error(cls, "Mismatching effect value name: %s != %s" % (schema_value["title"], value[0]))
                expected_ref = class_full_ref(value[1])
                if schema_value["$ref"] != expected_ref:
                    check_error(cls, "Mismatching effect value class for %s: %s != %s" % (value[0], expected_ref, schema_value["$ref"]))

        instance = cls()
        for prop in cls._props[index:]:
            check_prop(cls, prop, properties, instance)

        for prop in properties.keys():
            if prop != "ty":
                check_error(cls, "Missing property %s" % prop)

    elif issubclass(cls, LottieEnum):
        values = set()
        for enum_value in class_schema["oneOf"]:
            name = chunks_to_camel(enum_value["title"].split())
            value = enum_value["const"]
            try:
                py_value = cls(value)
                values.add(py_value)
            except ValueError:
                check_error(cls, "Missing value %s %r" % (name, value))
                continue

            if py_value.name != name:
                check_error(cls, "Name mismatch for %r: %s != %s" % (value, py_value.name, name))

        for val in cls.__members__.values():
            if val not in values:
                check_error(cls, "Value not in schema: %s %r" % (val.name, val.value))


def check_class(cls, schema: Schema, all_defs):
    try:
        do_check_class(cls, schema, all_defs)
    except Exception:
        check_error(cls, "Exception!")
        raise


def check_module(module, schema: Schema, all_defs):
    for clsname, cls in inspect.getmembers(module):
        if inspect.isclass(cls) and issubclass(cls, LottieBase) and cls.__module__ == module.__name__:
            check_class(cls, schema, all_defs)


def action_check(subject, ns):
    with open(ns.schema) as f:
        schema = Schema(json.load(f))

    all_defs = set()
    for group_name, group in schema.data["$defs"].items():
        for type_name in group:
            all_defs.add("#/$defs/%s/%s" % (group_name, type_name))

    all_defs.discard("#/$defs/helpers/color")
    all_defs.discard("#/$defs/animated-properties/animated-property")
    all_defs.discard("#/$defs/animated-properties/position")
    all_defs.discard("#/$defs/animated-properties/position-keyframe")
    all_defs.discard("#/$defs/animated-properties/shape-keyframe")
    all_defs.discard("#/$defs/helpers/color")
    all_defs.discard("#/$defs/helpers/int-boolean")
    all_defs.discard("#/$defs/shapes/shape-list")

    if subject is None:
        for module in loop_modules():
            check_module(module, schema, all_defs)

        if all_defs:
            print("\nMissing:")
            for missing in sorted(all_defs):
                print(missing)
    elif inspect.isclass(subject):
        check_class(subject, schema, all_defs)
    else:
        check_module(subject, schema, all_defs)


def py_string(str):
    return repr(str).replace("'", '"')


class SchemaProperty:
    builtins = {
        "string": "str",
        "integer": "int",
        "number": "float",
        "boolean": "bool"
    }

    def __init__(self, lottie_name, schema):
        self.lottie = lottie_name
        self.schema = schema
        self.title = schema.get("title", lottie_name)
        if lottie_name is None:
            self.python = chunks_to_camel(self.title.lower().split())
        else:
            self.python = self.title.lower().replace(" ", "_")
        self.description = schema.get("description", "")

        self.type_dep = None

        if schema.get("type", "") == "array":
            self.is_list = True
            items = schema.get("items", {})
            if items.get("type") == "number":
                self.type = "NVector"
                self.is_list = False
            else:
                self.get_type(items)
        else:
            self.get_type(schema)
            self.is_list = False

        self.default = py_string(schema.get("default", schema.get("const", None)))

    def get_type(self, schema):
        if "$ref" in schema:
            self.type = class_name_from_full_ref(schema["$ref"])
            try:
                self.type_dep = getattr(lottie.objects, self.type)
            except AttributeError:
                pass
        else:
            type = schema.get("type", "???")
            self.type = self.builtins.get(type, type)

    def declare(self):
        return "LottieProp(%s, %s, %s, %s)" % (
            py_string(self.python),
            py_string(self.lottie),
            self.type,
            self.is_list
        )

    def initialize(self):
        return "%s = %s" % (self.python, self.default)


def get_all_properties(schema, properties):
    for k, v in schema.get("properties", {}).items():
        if k not in properties:
            properties[k] = SchemaProperty(k, v)

    for split in ["oneOf", "allOf", "anyOf"]:
        if split in schema:
            for item in schema[split]:
                get_all_properties(item, properties)

    for cond in ["if", "then", "else"]:
        if split in schema:
            get_all_properties(schema[split], properties)

    if "$ref" in schema:
        properties["__base__"] = class_from_full_ref(schema["$ref"])


class PythonDependencies:
    def __init__(self):
        self.modules = {}

    def add_module_name(self, module):
        if module not in self.modules:
            items = set()
            self.modules[module] = items
            return items
        return self.modules[module]

    def add_class(self, cls):
        self.add_module_name(cls.__module__).add(cls.__name__)

    def __str__(self):
        data = ""
        for name, items in sorted(self.modules.items()):
            data += "from %s import %s\n" % (name, ",".join(sorted(items)))
        data += "\n"
        return data


def clean_ref(ref):
    return "#/$defs/" + "/".join(ref.split("/")[-2:])


def action_generate_python(ref, property_names, schema_path):
    with open(schema_path) as f:
        schema = Schema(json.load(f))

    ref = clean_ref(ref)

    class_schema = schema.get_ref(ref)
    class_name = class_name_from_full_ref(ref)
    deps = PythonDependencies()
    enum = False
    properties = {}

    if class_schema.get("type", "object") == "integer":
        base = LottieEnum
        enum = True
        for i, val in enumerate(class_schema["oneOf"]):
            properties[i] = SchemaProperty(None, val)
    else:
        get_all_properties(class_schema, properties)
        if property_names:
            properties = {k: v for k, v in properties.items() if k in property_names}

        base = properties.pop("__base__", lottie.objects.LottieObject)

        for prop in properties.values():
            if prop.type_dep:
                deps.add_class(prop.type_dep)

    deps.add_class(base)
    print(deps)
    print("#ingroup Lottie")
    print("class %s(%s):" % (class_name, base.__name__))
    indent = " " * 4
    desc = class_schema.get("description", "")
    if desc:
        for comment in ['"""!'] + desc.split("\n") + ['"""']:
            print(indent + comment)

    if enum:
        for prop in properties.values():
            if prop.description:
                for line in prop.description.split("\n"):
                    print(indent + "## " + line)
            print(indent + prop.initialize())
    elif base is lottie.objects.Effect:
        print(indent + "_effects = [")
        for ef in properties["ef"].schema.get("prefixItems"):
            print(indent*2 + "(%s, %s)," % (py_string(ef["title"]), class_name_from_full_ref(ef["$ref"])))
        print(indent + "]")
        print(indent + "## %Effect type.")
        print(indent + properties["ty"].initialize())
    else:
        print(indent + "_props = [")
        for prop in properties.values():
            print(indent * 2 + prop.declare() + ",")
        print(indent + "]")

        print()
        print(indent + "def __init__(self):")
        print(indent * 2 + "super().__init__()")
        print()
        for prop in properties.values():
            if prop.description:
                for line in prop.description.split("\n"):
                    print(indent * 2 + "## " + line)
            print(indent * 2 + "self." + prop.initialize())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="action")

    generate = sub.add_parser("generate", aliases=["g"])
    generate.add_argument("what", default=None, nargs="?", help="Python class or module to generate")
    generate.add_argument("--output", default=pathlib.Path("/tmp/json-schema"), type=pathlib.Path, help="Output path")
    generate.add_argument("--schema", default="https://json-schema.org/draft/2020-12/schema", help="Metaschema URL")

    check = sub.add_parser("check", aliases=["c"])
    check.add_argument("what", default=None, nargs="?", help="Python class or module to check")
    check.add_argument("--schema", required=True, help="Path to the schema file")

    python = sub.add_parser("python", aliases=["py"], help="Generate python class")
    python.add_argument("--schema", required=True, help="Path to the schema file")
    python.add_argument("ref", help="$ref of the schema object to generate")
    python.add_argument("properties", default=[], nargs="*", help="Properties to extract")

    ns = parser.parse_args()

    if ns.action == "python" or ns.action == "py":
        action_generate_python(ns.ref, ns.properties, ns.schema)
        sys.exit(0)

    subject = None
    what = ns.what
    if what is not None:
        subject = lottie.objects
        for chunk in what.split("."):
            subject = getattr(subject, chunk)

    if ns.action == "check" or ns.action == "c":
        action_check(subject, ns)
    else:
        action_output(subject, ns)

