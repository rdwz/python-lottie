#!/usr/bin/env python3
import sys
import os
import pkgutil
import importlib
import inspect
import re
import collections
import json
sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "lib"
))
import lottie
import lottie.objects
import lottie.objects.shapes
from lottie.objects.base import LottieEnum, LottieObject, PseudoList, LottieBase, PseudoBool


def class_to_ref(name):
    return re.sub("([a-z])([A-Z])", r"\1-\2", name).lower()


def get_docs(cls):
    if cls.__doc__ is None:
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


def scalar_type(json_prop, prop, default):
    name = prop.type.__name__

    if name == "NVector":
        json_prop["type"] = "number"
    elif prop.type in (int, float, str, bool):
        json_prop["type"] = builtin_type_name(prop.type)
    elif prop.type is PseudoBool:
        json_prop["$ref"] = "#/definitions/custom-types/int-boolean"
        if default is not None:
            default = int(default)
    elif name == "PositionValue":
        json_prop["$ref"] = "#/definitions/parameters/position"
    elif name == "ShapeProperty":
        json_prop["$ref"] = "#/definitions/parameters/shape"
        default = None
    elif name == "Color":
        json_prop["$ref"] = "#/definitions/parameter-values/color"
    elif name == "ColorValue":
        json_prop["$ref"] = "#/definitions/parameters/color"
    elif name == "MultiDimensional":
        json_prop["$ref"] = "#/definitions/parameters/multidimensional"
    elif name == "Value":
        json_prop["$ref"] = "#/definitions/parameters/number"
    elif name in ("GradientColors", "StrokeDash", "RepeaterTransform"):
        json_prop["$ref"] = "#/definitions/parameters/" + class_to_ref(name)
        default = None
    elif inspect.isclass(prop.type) and issubclass(prop.type, LottieEnum):
        json_prop["$ref"] = "#/definitions/constants/" + class_to_ref(name) + "-types"
        default = default.value if default else None
    elif inspect.isclass(prop.type) and issubclass(prop.type, LottieObject):
        json_prop["$ref"] = "#/definitions/abstractions/" + class_to_ref(name)
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
        json_prop["item"] = item
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


def class_data(json_data, cls):
    clsname = cls.__name__
    if issubclass(cls, LottieObject):
        structure = []
        index = 0
        for base in cls.__bases__:
            if base != LottieObject:
                structure.append({
                    "$ref": "#/definitions/abstractions/" + class_to_ref(base.__name__)
                })
            index += len(getattr(base, "_props", []))

        required = []
        json_properties = {}

        for prop in cls._props[:index]:
            if hasattr(cls, prop.name):
                required.append(prop.lottie)
                json_properties[prop.lottie] = {
                    "title": property_title(prop.name),
                    "type": builtin_type_name(prop.type),
                    "const": getattr(cls, prop.name)
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

        json_data[class_to_ref(clsname)] = {
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

        json_data[class_to_ref(clsname) + "-types"] = {
            "type": type,
            "title": clsname,
            "description": get_docs(cls),
            "oneOf": values
        }


def module_data(module):
    json_data = {}
    for clsname, cls in inspect.getmembers(module):
        if inspect.isclass(cls):
            class_data(json_data, cls)
    return json_data


if __name__ == "__main__":
    subject = lottie.objects
    if len(sys.argv) > 1:
        what = sys.argv[1]
        for chunk in what.split("."):
            subject = getattr(subject, chunk)

    if inspect.isclass(subject):
        json_data = {}
        class_data(json_data, subject)
    else:
        json_data = module_data(subject)
    json.dump(json_data, sys.stdout, indent=4)
