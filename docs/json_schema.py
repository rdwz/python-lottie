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


def class_name_to_ref(name):
    if name == "Precomp":
        return "precomposition"
    elif name == "Matte3Effect":
        return "matte3-effect"
    elif name == "PreCompLayer":
        return "precomposition-layer"
    elif name == "AnimatableMixin":
        return "animated-property"
    elif name == "Rect":
        return "rectangle"
    elif name == "Star":
        return "polystar"
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
    return module


def class_full_ref(cls):
    return "#/$defs/%s/%s" % (class_dirname(cls), class_name_to_ref(cls.__name__))


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


def check_error(cls, msg):
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


def do_check_class(cls, schema: Schema):
    ref = class_full_ref(cls)
    class_schema = schema.find(ref)
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
            ef = properties.pop("ef")
            schema_values = ef.get("prefixItems", [])
            if len(schema_values) != len(cls._effects):
                check_error(cls, "Mismatching effect values")

            for (schema_value, value) in zip(schema_values, cls._effects):
                if schema_value["title"] != value[0]:
                    check_error(cls, "Mismatching effect value name: %s != %s" % (schema_value["title"], value[0]))
                expected_ref = class_full_ref(value[1])
                if schema_value["$ref"] != expected_ref:
                    check_error(cls, "Mismatching effect value class for %s: %s != %s" % (value[0], expected_ref, schema_value["ref"]))

        instance = cls()
        for prop in cls._props[index:]:
            check_prop(cls, prop, properties, instance)

        for prop in properties.keys():
            #for parent_prop in cls._props[:index]:
                #if parent_prop.lottie == prop and getattr(instance, parent_prop.name):
                    #break
            #else:
            if prop != "ty":
                check_error(cls, "Missing property %s" % prop)

    elif issubclass(cls, LottieEnum):
        values = set()
        for enum_value in class_schema["oneOf"]:
            name = enum_value["title"].replace(" ", "")
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


def check_class(cls, schema: Schema):
    try:
        do_check_class(cls, schema)
    except Exception:
        check_error(cls, "Exception!")
        raise


def check_module(module, schema: Schema):
    for clsname, cls in inspect.getmembers(module):
        if inspect.isclass(cls) and issubclass(cls, LottieBase) and cls.__module__ == module.__name__:
            check_class(cls, schema)


def action_check(subject, ns):
    with open(ns.schema) as f:
        schema = Schema(json.load(f))

    if subject is None:
        for module in loop_modules():
            check_module(module, schema)
    elif inspect.isclass(subject):
        check_class(subject, schema)
    else:
        check_module(subject, schema)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("what", default=None, nargs="?")
    parser.add_argument("--output", default=pathlib.Path("/tmp/json-schema"), type=pathlib.Path)
    parser.add_argument("--schema", default="https://json-schema.org/draft/2020-12/schema")
    parser.add_argument("--check", action="store_true")
    ns = parser.parse_args()

    subject = None
    what = ns.what
    if what is not None:
        subject = lottie.objects
        for chunk in what.split("."):
            subject = getattr(subject, chunk)

    if ns.check:
        action_check(subject, ns)
    else:
        action_output(subject, ns)

