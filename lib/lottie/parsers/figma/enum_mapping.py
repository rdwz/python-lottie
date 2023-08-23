from . import schema

class EnumMapping:
    def __init__(self, figma_default, lottie_default, mapping=None):
        self.figma_enum = type(figma_default)
        self.figma_default = figma_default
        self.lottie_default = lottie_default
        self.lottie_enum = type(lottie_default)
        self.mapping = mapping

    def to_figma(self, value):
        if value is None:
            return self.figma_default

        if self.mapping is None:
            caps = model.camel_to_caps(value.name)
            if hasattr(self.figma_enum, caps):
                return getattr(self.figma_enum, caps)
            return self.figma_default
        else:
            return self.mapping.get(value, self.figma_default)



blend_mode = EnumMapping(schema.BlendMode.PASS_THROUGH)
