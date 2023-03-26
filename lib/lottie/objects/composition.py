from .base import Index, LottieProp, PseudoBool
from .layers import Layer, PreCompLayer
from .assets import Asset
from .helpers import Marker

## @ingroup Lottie
class Composition(Asset):
    """!
    Base class for layer holders
    """
    _props = [
        LottieProp("frame_rate", "fr", float, False),
        LottieProp("in_point", "ip", float, False),
        LottieProp("out_point", "op", float, False),
        LottieProp("width", "w", int, False),
        LottieProp("height", "h", int, False),
        LottieProp("threedimensional", "ddd", PseudoBool, False),
        LottieProp("markers", "markers", Marker, True),
        LottieProp("layers", "layers", Layer, True),
    ]

    def __init__(self, width=512, height=512, n_frames=60, framerate=60):
        super().__init__()
        ## The time when the composition work area begins, in frames.
        self.in_point = 0
        ## The time when the composition work area ends.
        ## Sets the final Frame of the animation
        self.out_point = n_frames
        ## Frames per second
        self.frame_rate = framerate
        ## Composition Width
        self.width = 512
        ## Composition has 3-D layers
        self.threedimensional = False
        ## Composition Height
        self.height = 512
        ## List of Composition Layers
        self.layers = [] # ShapeLayer, SolidLayer, CompLayer, ImageLayer, NullLayer, TextLayer

        self.markers = None
        self.id = None
        self.project = None
        self._index_gen = Index()

    def layer(self, index):
        for layer in self.layers:
            if layer.index == index:
                return layer
        raise IndexError("No layer %s" % index)

    def add_layer(self, layer: Layer):
        """!
        @brief Appends a layer to the composition
        @see insert_layer
        """
        return self.insert_layer(len(self.layers), layer)

    @classmethod
    def load(cls, lottiedict):
        obj = super().load(lottiedict)
        obj._fixup()
        return obj

    def _fixup(self):
        for layer in self.layers:
            layer.composition = self

    def insert_layer(self, index, layer: Layer):
        """!
        @brief Inserts a layer to the composition
        @note Layers added first will be rendered on top of later layers
        """
        self.layers.insert(index, layer)
        self.prepare_layer(layer)
        return layer

    def prepare_layer(self, layer: Layer):
        layer.composition = self
        if layer.index is None:
            layer.index = next(self._index_gen)
        self._prepare_layer_interval(layer)

    def _self_or_main(self, attr):
        val = getattr(self, attr)
        if val is None and self.project is not None:
            val = getattr(self.project.main, attr)
        return val

    def _prepare_layer_interval(self, layer):
        if layer.in_point is None:
            layer.in_point = self._self_or_main("in_point")
        if layer.out_point is None:
            layer.out_point = self._self_or_main("out_point")

    def clone(self):
        c = super().clone()
        c._index_gen._i = self._index_gen._i
        return c

    def remove_layer(self, layer: Layer):
        """!
        @brief Removes a layer (and all of its children) from this composition
        @param layer    Layer to be removed
        """
        if layer.composition is not self:
            return

        children = list(layer.children)

        layer.composition = None
        self.layers.remove(layer)

        for c in children:
            self.remove_layer(c)

    def precomp_layer(self):
        """! creates a precomp layer for this comp """
        precomp_layer = PreCompLayer()
        precomp_layer.width = self.width
        precomp_layer.height = self.height
        self._prepare_layer_interval(self.in_point, self.out_point)
        precomp_layer.reference_id = self.id
        precomp_layer.name = self.name

    def copy_attributes(self, other_comp):
        for attr in ["in_point", "out_point", "frame_rate", "width", "height"]:
            setattr(self, attr, getattr(other_comp, attr))


    def __str__(self):
        return self.name or super().__str__()


    def set_timing(self, outpoint, inpoint=0, override=True):
        for layer in self.layers:
            if override or layer.in_point is None:
                layer.in_point = inpoint
            if override or layer.out_point is None:
                layer.out_point = outpoint
