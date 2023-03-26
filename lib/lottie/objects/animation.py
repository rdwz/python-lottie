from .base import LottieObject, LottieProp, PseudoBool, Index
from .layers import Layer, PreCompLayer
from .assets import Asset
from .text import FontList, Chars
from .composition import Composition

##\defgroup Lottie Lottie
#
# Objects of the lottie file structure.

## \defgroup LottieCheck Lottie (to check)
#
# Lottie objects that have not been tested


## @ingroup Lottie
class Metadata(LottieObject):
    """!
    Document metadata
    """
    _props = [
        LottieProp("author", "a", str, False),
        LottieProp("generator", "g", str, False),
        LottieProp("keywords", "k", str, True),
        LottieProp("description", "d", str, False),
        LottieProp("theme_color", "tc", str, False),
    ]

    def __init__(self):
        self.generator = None
        self.author = None
        self.keywords = None
        self.description = None
        self.theme_color = None


#ingroup Lottie
class UserMetadata(LottieObject):
    """!
    User-defined metadata
    """
    _props = [
        LottieProp("filename", "filename", str, False),
        LottieProp("custom_properties", "customProps", dict, False),
    ]

    def __init__(self):
        super().__init__()

        self.filename = None
        self.custom_properties = {}


#ingroup Lottie
class MotionBlur(LottieObject):
    """!
    Motion blur settings
    """
    _props = [
        LottieProp("shutter_angle", "sa", float, False),
        LottieProp("shutter_phase", "sp", float, False),
        LottieProp("samples_per_frame", "spf", float, False),
        LottieProp("adaptive_sample_limit", "asl", float, False),
    ]

    def __init__(self):
        super().__init__()

        ## Angle in degrees
        self.shutter_angle = None
        ## Angle in degrees
        self.shutter_phase = None
        self.samples_per_frame = None
        self.adaptive_sample_limit = None


## @ingroup Lottie
class Project(LottieObject):
    """!
    Top level object, describing the animation

    @see http://docs.aenhancers.com/items/compitem/
    """
    _props = [
        LottieProp("version", "v", str, False),
        LottieProp("assets", "assets", Asset, True),
        LottieProp("extra_compositions", "comps", Composition, True),
        LottieProp("fonts", "fonts", FontList),
        LottieProp("chars", "chars", Chars, True),
        LottieProp("motion_blur", "mb", MotionBlur, False),
        LottieProp("metadata", "meta", Metadata, False),
        LottieProp("user_metadata", "metadata", UserMetadata, False),
    ]
    _version = "5.5.2"

    def __init__(self, n_frames=60, framerate=60):
        super().__init__()
        ## Bodymovin Version
        self.version = self._version
        ## source items that can be used in multiple places. Comps and Images for now.
        self.assets = [] # Image, Composition
        ## List of Extra compositions not referenced by anything
        self.extra_compositions = None
        ## source chars for text layers
        self.chars = None
        ## Available fonts
        self.fonts = None
        self.metadata = None
        self.user_metadata = None
        self.motion_blur = None
        self.main = Composition(512, 512, n_frames, framerate)

    @property
    def width(self):
        return self.main.width

    @property
    def height(self):
        return self.main.height

    def precomp(self, name):
        for ass in self.assets:
            if isinstance(ass, Composition) and ass.id == name:
                return ass
        return None

    def to_precomp(self):
        """!
        Turns the main comp into a precomp
        """
        name_id = 0
        base_name = self.main.name or "Animation"
        name = base_name
        index = 0
        while True:
            if index >= len(self.assets):
                break

            while self.assets[index].id == name:
                name_id += 1
                name = "%s %s" % (base_name, name_id)
                index = -1

            index += 1

        self.main.id = name
        self.assets.append(self.main)
        new_main = Composition()
        new_main.copy_attributes(self.main)
        new_main.layers = [self.name.precomp_layer()]
        self.main = new_main
        return self.assets[-1]

    def scale(self, width, height):
        """!
        Scales the animation so it fits in width/height
        """
        if self.main.width != width or self.main.height != height:
            self.to_precomp()

            scale = min(width/self.main.width, height/self.main.height)
            self.main.width = width
            self.main.height = height

            self.layers[0].transform.scale.value *= scale

    def tgs_sanitize(self):
        """!
        Cleans up some things to ensure it works as a telegram sticker
        """
        self.scale(512, 512)

        if self.main.frame_rate < 45:
            self.main.frame_rate = 30
        else:
            self.main.frame_rate = 60

    def _fixup(self):
        super()._fixup()
        self.main._fixup()
        self.main.project = self
        if self.assets:
            for ass in self.assets:
                if isinstance(ass, Composition):
                    ass.animation = self
                    ass.project = self
                    ass._fixup()

    def __str__(self):
        return self.main.name or super().__str__()


def Animation(self, n_frames=60, framerate=60):
    return Composition(512, 512, n_frames, framerate)
