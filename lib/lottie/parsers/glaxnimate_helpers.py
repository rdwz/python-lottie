try:
    import glaxnimate
    has_glaxnimate = True
except ImportError:
    has_glaxnimate = False

import json
from ..nvector import NVector, Point


def convert(animation, exporter_slug):
    with glaxnimate.environment.Headless():
        document = glaxnimate.model.Document("")
        glaxnimate.io.registry.from_slug("lottie").load(document, json.dumps(animation.to_dict()).encode("utf8"))
        return glaxnimate.io.registry.from_slug(exporter_slug).save(document)


def serialize(animation, serializer_slug):
    with glaxnimate.environment.Headless():
        document = glaxnimate.model.Document("")
        glaxnimate.io.registry.from_slug("lottie").load(document, json.dumps(animation.to_dict()).encode("utf8"))
        return glaxnimate.io.registry.serializer_from_slug(serializer_slug).serialize([document.main])


def color_to_glaxnimate(color: NVector):
    return glaxnimate.utils.Color(*(color * 255).components)


def color_from_glaxnimate(color):
    return NVector(color.red / 255., color.green / 255., color.blue / 255., color.alpha / 255.)


def point_from_glaxnimate(point):
    return Point(point.x, point.y)


