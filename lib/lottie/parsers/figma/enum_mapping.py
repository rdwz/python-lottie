from . import schema
from ... import objects
from ...utils.string import camel_to_caps, snake_to_camel


class EnumMapping:
    def __init__(self, figma_default, lottie_default, mapping=None):
        self.figma_enum = type(figma_default)
        self.figma_default = figma_default
        self.lottie_default = lottie_default
        self.lottie_enum = type(lottie_default)
        self.f2l_mapping = self.l2f_mapping = None
        if mapping:
            self.l2f_mapping = {}
            self.f2l_mapping = {}
            for f, l in mapping:
                if l not in self.l2f_mapping:
                    self.l2f_mapping[l] = f
                if f not in self.f2l_mapping:
                    self.f2l_mapping[f] = l

    def to_figma(self, value):
        if value is None:
            return self.figma_default

        if self.l2f_mapping is None:
            caps = camel_to_caps(value.name)
            if hasattr(self.figma_enum, caps):
                return getattr(self.figma_enum, caps)
            return self.figma_default
        else:
            return self.l2f_mapping.get(value, self.figma_default)

    def to_lottie(self, value):
        if value is None:
            return self.lottie_default

        if self.f2l_mapping is None:
            caps = snake_to_camel(value.name)
            if hasattr(self.lottie_enum, caps):
                return getattr(self.lottie_enum, caps)
            return self.lottie_default
        else:
            return self.f2l_mapping.get(value, self.lottie_default)


blend_mode = EnumMapping(schema.BlendMode.PASS_THROUGH, objects.shapes.BlendMode.Normal)
line_cap = EnumMapping(schema.StrokeCap.NONE, objects.shapes.LineCap.Butt)
line_join = EnumMapping(schema.StrokeJoin.MITER, objects.shapes.LineJoin.Miter)

text_align = EnumMapping(schema.TextAlignHorizontal.LEFT, objects.text.TextJustify.Left, [
    (schema.TextAlignHorizontal.LEFT, objects.text.TextJustify.Left),
    (schema.TextAlignHorizontal.RIGHT, objects.text.TextJustify.Right),
    (schema.TextAlignHorizontal.CENTER, objects.text.TextJustify.Center),
    (schema.TextAlignHorizontal.JUSTIFIED, objects.text.TextJustify.JustifyWithLastLineFull),
    (schema.TextAlignHorizontal.JUSTIFIED, objects.text.TextJustify.JustifyWithLastLineLeft),
    (schema.TextAlignHorizontal.JUSTIFIED, objects.text.TextJustify.JustifyWithLastLineRight),
])


matte_mode = EnumMapping(schema.MaskType.ALPHA, objects.layers.MatteMode.Alpha, [
    (schema.MaskType.ALPHA, objects.layers.MatteMode.Alpha),
    (schema.MaskType.ALPHA, objects.layers.MatteMode.Normal),
    (schema.MaskType.OUTLINE, objects.layers.MatteMode.InvertedAlpha),
    (schema.MaskType.LUMINANCE, objects.layers.MatteMode.Luma),
    (schema.MaskType.LUMINANCE, objects.layers.MatteMode.InvertedLuma),
])
