try:
    import glaxnimate
    has_glaxnimate = True
except ImportError:
    has_glaxnimate = False

import json


def convert(animation, exporter_slug):
    with glaxnimate.environment.Headless():
        document = glaxnimate.model.Document("")
        glaxnimate.io.registry.from_slug("lottie").load(document, json.dumps(animation.to_dict()).encode("utf8"))
        return glaxnimate.io.registry.from_slug(exporter_slug).save(document)
