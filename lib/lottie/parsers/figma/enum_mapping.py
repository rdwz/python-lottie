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
            self.l2f_mapping = dict(mapping)
            self.f2l_mapping = {v: k for k, v in mapping}

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

text_align = EnumMapping(schema.TextAlignHorizontal.LEFT, objects.text.TextJustify.Left)
text_align.f2l_mapping[schema.TextAlignHorizontal.JUSTIFIED] = objects.text.TextJustify.JustifyWithLastLineFull
for tj in objects.text.TextJustify:
    if tj.name.startswith("Justify"):
         text_align.l2f_mapping[tj] = schema.TextAlignHorizontal.JUSTIFIED

