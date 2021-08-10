from PIL import Image
import glaxnimate
from . import glaxnimate_helpers
import enum
from .. import objects
from ..nvector import NVector
from .pixel import _vectorizing_func


class QuanzationMode(enum.Enum):
    Nearest = 1
    Exact = 2


class RasterImage:
    def __init__(self, image):
        self.image = image

    #@classmethod
    #def open(cls, filename):
        #return cls.from_pil(Image.open(filename))

    def quantize(self, n_colors):
        """!
        Returns a list of RGB values
        """
        return glaxnimate.utils.quantize.octree(self.image, n_colors)

    def trace(self, codebook, quantization_mode=QuanzationMode.Nearest):
        """!
        Returns a list of tuple [color, data] where for each color in codebook
        data is a list of bezier

        You can get codebook from quantize
        """

        options = glaxnimate.utils.trace.TraceOptions()

        if codebook is None or len(codebook) == 0:
            tracer = glaxnimate.utils.trace.Tracer(self.image, options)
            tracer.set_target_alpha(128, False)
            return [glaxnimate.utils.Color(0, 0, 0), tracer.trace()]

        if quantization_mode == QuanzationMode.Nearest:
            return list(zip(codebook, glaxnimate.utils.trace.quantize_and_trace(self.image, options, codebook)))

        mono_data = []
        tracer = glaxnimate.utils.trace.Tracer(self.image, options)
        for color in codebook:
            tracer.set_target_color(color, 100)
            mono_data.append((color, tracer.trace()))

        return mono_data


class Vectorizer:
    def __init__(self, stroke_width):
        self.palette = None
        self.layers = {}
        self.stroke_width = stroke_width

    def _create_layer(self, animation, layer_name):
        layer = animation.add_layer(objects.ShapeLayer())
        if layer_name:
            self.layers[layer_name] = layer
            layer.name = layer_name
        return layer

    def prepare_layer(self, animation, layer_name=None):
        layer = self._create_layer(animation, layer_name)
        layer._max_verts = {}
        for color in self.palette:
            group = layer.add_shape(objects.Group())
            group.name = "color_%s" % color.name
            layer._max_verts[group.name] = 0
            fcol = glaxnimate_helpers.color_from_glaxnimate(color)
            group.add_shape(objects.Fill(NVector(*fcol)))
            if self.stroke_width > 0:
                group.add_shape(objects.Stroke(NVector(*fcol), self.stroke_width))
        return layer

    def raster_to_layer(self, animation, raster, layer_name=None, mode=QuanzationMode.Nearest):
        layer = self.prepare_layer(animation, layer_name)
        mono_data = raster.trace(self.palette, mode)
        for (color, beziers), group in zip(mono_data, layer.shapes):
            self.traced_to_shapes(group, beziers)
        return layer

    def traced_to_shapes(self, group, beziers):
        shapes = []
        for bezier in beziers:
            shape = group.insert_shape(0, objects.Path())
            shapes.append(shape)
            shape.shape.value = self.traced_to_bezier(bezier)
        return shapes

    def traced_to_bezier(self, path):
        bezier = objects.Bezier()
        for point in path:
            pos = glaxnimate_helpers.point_from_glaxnimate(point.pos)
            tan_in = glaxnimate_helpers.point_from_glaxnimate(point.tan_in - point.pos)
            tan_out = glaxnimate_helpers.point_from_glaxnimate(point.tan_out - point.pos)
            bezier.add_point(pos, tan_in, tan_out)
        if path.closed:
            bezier.closed = True
        return bezier


def raster_to_animation(filenames, n_colors=1, frame_delay=1,
                        looping=True, framerate=60, palette=[],
                        mode=QuanzationMode.Nearest,
                        stroke=1):

    vc = Vectorizer(stroke)

    def callback(animation, raster, frame):
        raster = RasterImage(raster)
        if vc.palette is None:
            if palette:
                vc.palette = [glaxnimate_helpers.color_to_glaxnimate(c) for c in palette]
            elif n_colors > 1:
                vc.palette = raster.quantize(n_colors)
            else:
                vc.palette = [glaxnimate.utils.Color(0, 0, 0, 255)]
        layer = vc.raster_to_layer(animation, raster, "frame_%s" % frame, mode)
        layer.in_point = frame * frame_delay
        layer.out_point = (frame + 1) * frame_delay

    animation = _vectorizing_func(filenames, frame_delay, framerate, callback)

    return animation
