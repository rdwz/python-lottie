import enum
import typing
import dataclasses


class uint(int):
    pass


class MessageType(enum.Enum):
    JOIN_START = 0
    NODE_CHANGES = 1
    USER_CHANGES = 2
    JOIN_END = 3
    SIGNAL = 4
    STYLE = 5
    STYLE_SET = 6
    JOIN_START_SKIP_RELOAD = 7
    NOTIFY_SHOULD_UPGRADE = 8
    UPGRADE_DONE = 9
    UPGRADE_REFRESH = 10
    SCENE_GRAPH_QUERY = 11
    SCENE_GRAPH_REPLY = 12
    DIFF = 13
    CLIENT_BROADCAST = 14
    JOIN_START_JOURNALED = 15
    STREAM_START = 16
    STREAM_END = 17


class Axis(enum.Enum):
    X = 0
    Y = 1


class Access(enum.Enum):
    READ_ONLY = 0
    READ_WRITE = 1


class NodePhase(enum.Enum):
    CREATED = 0
    REMOVED = 1


class WindingRule(enum.Enum):
    NONZERO = 0
    ODD = 1


class NodeType(enum.Enum):
    NONE = 0
    DOCUMENT = 1
    CANVAS = 2
    GROUP = 3
    FRAME = 4
    BOOLEAN_OPERATION = 5
    VECTOR = 6
    STAR = 7
    LINE = 8
    ELLIPSE = 9
    RECTANGLE = 10
    REGULAR_POLYGON = 11
    ROUNDED_RECTANGLE = 12
    TEXT = 13
    SLICE = 14
    SYMBOL = 15
    INSTANCE = 16
    STICKY = 17
    SHAPE_WITH_TEXT = 18
    CONNECTOR = 19
    CODE_BLOCK = 20
    WIDGET = 21
    STAMP = 22
    MEDIA = 23
    HIGHLIGHT = 24
    SECTION = 25
    SECTION_OVERLAY = 26
    WASHI_TAPE = 27
    VARIABLE = 28
    TABLE = 29
    TABLE_CELL = 30
    VARIABLE_SET = 31
    SLIDE = 32


class ShapeWithTextType(enum.Enum):
    SQUARE = 0
    ELLIPSE = 1
    DIAMOND = 2
    TRIANGLE_UP = 3
    TRIANGLE_DOWN = 4
    ROUNDED_RECTANGLE = 5
    PARALLELOGRAM_RIGHT = 6
    PARALLELOGRAM_LEFT = 7
    ENG_DATABASE = 8
    ENG_QUEUE = 9
    ENG_FILE = 10
    ENG_FOLDER = 11
    TRAPEZOID = 12
    PREDEFINED_PROCESS = 13
    SHIELD = 14
    DOCUMENT_SINGLE = 15
    DOCUMENT_MULTIPLE = 16
    MANUAL_INPUT = 17
    HEXAGON = 18
    CHEVRON = 19
    PENTAGON = 20
    OCTAGON = 21
    STAR = 22
    PLUS = 23
    ARROW_LEFT = 24
    ARROW_RIGHT = 25
    SUMMING_JUNCTION = 26
    OR = 27
    SPEECH_BUBBLE = 28
    INTERNAL_STORAGE = 29


class BlendMode(enum.Enum):
    PASS_THROUGH = 0
    NORMAL = 1
    DARKEN = 2
    MULTIPLY = 3
    LINEAR_BURN = 4
    COLOR_BURN = 5
    LIGHTEN = 6
    SCREEN = 7
    LINEAR_DODGE = 8
    COLOR_DODGE = 9
    OVERLAY = 10
    SOFT_LIGHT = 11
    HARD_LIGHT = 12
    DIFFERENCE = 13
    EXCLUSION = 14
    HUE = 15
    SATURATION = 16
    COLOR = 17
    LUMINOSITY = 18


class PaintType(enum.Enum):
    SOLID = 0
    GRADIENT_LINEAR = 1
    GRADIENT_RADIAL = 2
    GRADIENT_ANGULAR = 3
    GRADIENT_DIAMOND = 4
    IMAGE = 5
    EMOJI = 6
    VIDEO = 7


class ImageScaleMode(enum.Enum):
    STRETCH = 0
    FIT = 1
    FILL = 2
    TILE = 3


class EffectType(enum.Enum):
    INNER_SHADOW = 0
    DROP_SHADOW = 1
    FOREGROUND_BLUR = 2
    BACKGROUND_BLUR = 3


class TextCase(enum.Enum):
    ORIGINAL = 0
    UPPER = 1
    LOWER = 2
    TITLE = 3
    SMALL_CAPS = 4
    SMALL_CAPS_FORCED = 5


class TextDecoration(enum.Enum):
    NONE = 0
    UNDERLINE = 1
    STRIKETHROUGH = 2


class LeadingTrim(enum.Enum):
    NONE = 0
    CAP_HEIGHT = 1


class NumberUnits(enum.Enum):
    RAW = 0
    PIXELS = 1
    PERCENT = 2


class ConstraintType(enum.Enum):
    MIN = 0
    CENTER = 1
    MAX = 2
    STRETCH = 3
    SCALE = 4
    FIXED_MIN = 5
    FIXED_MAX = 6


class StrokeAlign(enum.Enum):
    CENTER = 0
    INSIDE = 1
    OUTSIDE = 2


class StrokeCap(enum.Enum):
    NONE = 0
    ROUND = 1
    SQUARE = 2
    ARROW_LINES = 3
    ARROW_EQUILATERAL = 4
    DIAMOND_FILLED = 5
    TRIANGLE_FILLED = 6
    HIGHLIGHT = 7
    WASHI_TAPE_1 = 8
    WASHI_TAPE_2 = 9
    WASHI_TAPE_3 = 10
    WASHI_TAPE_4 = 11
    WASHI_TAPE_5 = 12
    WASHI_TAPE_6 = 13
    CIRCLE_FILLED = 14


class StrokeJoin(enum.Enum):
    MITER = 0
    BEVEL = 1
    ROUND = 2


class BooleanOperation(enum.Enum):
    UNION = 0
    INTERSECT = 1
    SUBTRACT = 2
    XOR = 3


class TextAlignHorizontal(enum.Enum):
    LEFT = 0
    CENTER = 1
    RIGHT = 2
    JUSTIFIED = 3


class TextAlignVertical(enum.Enum):
    TOP = 0
    CENTER = 1
    BOTTOM = 2


class MouseCursor(enum.Enum):
    DEFAULT = 0
    CROSSHAIR = 1
    EYEDROPPER = 2
    HAND = 3
    PAINT_BUCKET = 4
    PEN = 5
    PENCIL = 6
    MARKER = 7
    ERASER = 8
    HIGHLIGHTER = 9


class VectorMirror(enum.Enum):
    NONE = 0
    ANGLE = 1
    ANGLE_AND_LENGTH = 2


class DashMode(enum.Enum):
    CLIP = 0
    STRETCH = 1


class ImageType(enum.Enum):
    PNG = 0
    JPEG = 1
    SVG = 2
    PDF = 3


class ExportConstraintType(enum.Enum):
    CONTENT_SCALE = 0
    CONTENT_WIDTH = 1
    CONTENT_HEIGHT = 2


class LayoutGridType(enum.Enum):
    MIN = 0
    CENTER = 1
    STRETCH = 2
    MAX = 3


class LayoutGridPattern(enum.Enum):
    STRIPES = 0
    GRID = 1


class TextAutoResize(enum.Enum):
    NONE = 0
    WIDTH_AND_HEIGHT = 1
    HEIGHT = 2


class TextTruncation(enum.Enum):
    DISABLED = 0
    ENDING = 1


class StyleSetType(enum.Enum):
    PERSONAL = 0
    TEAM = 1
    CUSTOM = 2
    FREQUENCY = 3
    TEMPORARY = 4


class StyleSetContentType(enum.Enum):
    SOLID = 0
    GRADIENT = 1
    IMAGE = 2


class StackMode(enum.Enum):
    NONE = 0
    HORIZONTAL = 1
    VERTICAL = 2


class StackAlign(enum.Enum):
    MIN = 0
    CENTER = 1
    MAX = 2
    BASELINE = 3


class StackCounterAlign(enum.Enum):
    MIN = 0
    CENTER = 1
    MAX = 2
    STRETCH = 3
    AUTO = 4
    BASELINE = 5


class StackJustify(enum.Enum):
    MIN = 0
    CENTER = 1
    MAX = 2
    SPACE_EVENLY = 3
    SPACE_BETWEEN = 4


class StackSize(enum.Enum):
    FIXED = 0
    RESIZE_TO_FIT = 1
    RESIZE_TO_FIT_WITH_IMPLICIT_SIZE = 2


class StackPositioning(enum.Enum):
    AUTO = 0
    ABSOLUTE = 1


class StackWrap(enum.Enum):
    NO_WRAP = 0
    WRAP = 1


class StackCounterAlignContent(enum.Enum):
    AUTO = 0
    SPACE_BETWEEN = 1


class ConnectionType(enum.Enum):
    NONE = 0
    INTERNAL_NODE = 1
    URL = 2
    BACK = 3
    CLOSE = 4
    SET_VARIABLE = 5
    UPDATE_MEDIA_RUNTIME = 6
    CONDITIONAL = 7


class InteractionType(enum.Enum):
    ON_CLICK = 0
    AFTER_TIMEOUT = 1
    MOUSE_IN = 2
    MOUSE_OUT = 3
    ON_HOVER = 4
    MOUSE_DOWN = 5
    MOUSE_UP = 6
    ON_PRESS = 7
    NONE = 8
    DRAG = 9
    ON_KEY_DOWN = 10
    ON_VOICE = 11
    ON_MEDIA_HIT = 12
    ON_MEDIA_END = 13
    MOUSE_ENTER = 14
    MOUSE_LEAVE = 15


class TransitionType(enum.Enum):
    INSTANT_TRANSITION = 0
    DISSOLVE = 1
    FADE = 2
    SLIDE_FROM_LEFT = 3
    SLIDE_FROM_RIGHT = 4
    SLIDE_FROM_TOP = 5
    SLIDE_FROM_BOTTOM = 6
    PUSH_FROM_LEFT = 7
    PUSH_FROM_RIGHT = 8
    PUSH_FROM_TOP = 9
    PUSH_FROM_BOTTOM = 10
    MOVE_FROM_LEFT = 11
    MOVE_FROM_RIGHT = 12
    MOVE_FROM_TOP = 13
    MOVE_FROM_BOTTOM = 14
    SLIDE_OUT_TO_LEFT = 15
    SLIDE_OUT_TO_RIGHT = 16
    SLIDE_OUT_TO_TOP = 17
    SLIDE_OUT_TO_BOTTOM = 18
    MOVE_OUT_TO_LEFT = 19
    MOVE_OUT_TO_RIGHT = 20
    MOVE_OUT_TO_TOP = 21
    MOVE_OUT_TO_BOTTOM = 22
    MAGIC_MOVE = 23
    SMART_ANIMATE = 24
    SCROLL_ANIMATE = 25


class EasingType(enum.Enum):
    IN_CUBIC = 0
    OUT_CUBIC = 1
    INOUT_CUBIC = 2
    LINEAR = 3
    IN_BACK_CUBIC = 4
    OUT_BACK_CUBIC = 5
    INOUT_BACK_CUBIC = 6
    CUSTOM_CUBIC = 7
    SPRING = 8
    GENTLE_SPRING = 9
    CUSTOM_SPRING = 10
    SPRING_PRESET_ONE = 11
    SPRING_PRESET_TWO = 12
    SPRING_PRESET_THREE = 13


class ScrollDirection(enum.Enum):
    NONE = 0
    HORIZONTAL = 1
    VERTICAL = 2
    BOTH = 3


class ScrollContractedState(enum.Enum):
    EXPANDED = 0
    CONTRACTED = 1


@dataclasses.dataclass(slots=True)
class GUID:
    sessionID: uint
    localID: uint


@dataclasses.dataclass(slots=True)
class Color:
    r: float
    g: float
    b: float
    a: float


@dataclasses.dataclass(slots=True)
class Vector:
    x: float
    y: float


@dataclasses.dataclass(slots=True)
class Rect:
    x: float
    y: float
    w: float
    h: float


@dataclasses.dataclass(slots=True)
class ColorStop:
    color: 'Color'
    position: float


@dataclasses.dataclass(slots=True)
class Matrix:
    m00: float
    m01: float
    m02: float
    m10: float
    m11: float
    m12: float


@dataclasses.dataclass(slots=True)
class ParentIndex:
    guid: 'GUID'
    position: str


@dataclasses.dataclass(slots=True)
class Number:
    value: float
    units: 'NumberUnits'


@dataclasses.dataclass(slots=True)
class FontName:
    family: str
    style: str
    postscript: str


class FontVariantNumericFigure(enum.Enum):
    NORMAL = 0
    LINING = 1
    OLDSTYLE = 2


class FontVariantNumericSpacing(enum.Enum):
    NORMAL = 0
    PROPORTIONAL = 1
    TABULAR = 2


class FontVariantNumericFraction(enum.Enum):
    NORMAL = 0
    DIAGONAL = 1
    STACKED = 2


class FontVariantCaps(enum.Enum):
    NORMAL = 0
    SMALL = 1
    ALL_SMALL = 2
    PETITE = 3
    ALL_PETITE = 4
    UNICASE = 5
    TITLING = 6


class FontVariantPosition(enum.Enum):
    NORMAL = 0
    SUB = 1
    SUPER = 2


class FontStyle(enum.Enum):
    NORMAL = 0
    ITALIC = 1


class OpenTypeFeature(enum.Enum):
    PCAP = 0
    C2PC = 1
    CASE = 2
    CPSP = 3
    TITL = 4
    UNIC = 5
    ZERO = 6
    SINF = 7
    ORDN = 8
    AFRC = 9
    DNOM = 10
    NUMR = 11
    LIGA = 12
    CLIG = 13
    DLIG = 14
    HLIG = 15
    RLIG = 16
    AALT = 17
    CALT = 18
    RCLT = 19
    SALT = 20
    RVRN = 21
    VERT = 22
    SWSH = 23
    CSWH = 24
    NALT = 25
    CCMP = 26
    STCH = 27
    HIST = 28
    SIZE = 29
    ORNM = 30
    ITAL = 31
    RAND = 32
    DTLS = 33
    FLAC = 34
    MGRK = 35
    SSTY = 36
    KERN = 37
    FWID = 38
    HWID = 39
    HALT = 40
    TWID = 41
    QWID = 42
    PWID = 43
    JUST = 44
    LFBD = 45
    OPBD = 46
    RTBD = 47
    PALT = 48
    PKNA = 49
    LTRA = 50
    LTRM = 51
    RTLA = 52
    RTLM = 53
    ABRV = 54
    ABVM = 55
    ABVS = 56
    VALT = 57
    VHAL = 58
    BLWF = 59
    BLWM = 60
    BLWS = 61
    AKHN = 62
    CJCT = 63
    CFAR = 64
    CPCT = 65
    CURS = 66
    DIST = 67
    EXPT = 68
    FALT = 69
    FINA = 70
    FIN2 = 71
    FIN3 = 72
    HALF = 73
    HALN = 74
    HKNA = 75
    HNGL = 76
    HOJO = 77
    INIT = 78
    ISOL = 79
    JP78 = 80
    JP83 = 81
    JP90 = 82
    JP04 = 83
    LJMO = 84
    LOCL = 85
    MARK = 86
    MEDI = 87
    MED2 = 88
    MKMK = 89
    NLCK = 90
    NUKT = 91
    PREF = 92
    PRES = 93
    VPAL = 94
    PSTF = 95
    PSTS = 96
    RKRF = 97
    RPHF = 98
    RUBY = 99
    SMPL = 100
    TJMO = 101
    TNAM = 102
    TRAD = 103
    VATU = 104
    VJMO = 105
    VKNA = 106
    VKRN = 107
    VRTR = 108
    VRT2 = 109
    SS01 = 110
    SS02 = 111
    SS03 = 112
    SS04 = 113
    SS05 = 114
    SS06 = 115
    SS07 = 116
    SS08 = 117
    SS09 = 118
    SS10 = 119
    SS11 = 120
    SS12 = 121
    SS13 = 122
    SS14 = 123
    SS15 = 124
    SS16 = 125
    SS17 = 126
    SS18 = 127
    SS19 = 128
    SS20 = 129
    CV01 = 130
    CV02 = 131
    CV03 = 132
    CV04 = 133
    CV05 = 134
    CV06 = 135
    CV07 = 136
    CV08 = 137
    CV09 = 138
    CV10 = 139
    CV11 = 140
    CV12 = 141
    CV13 = 142
    CV14 = 143
    CV15 = 144
    CV16 = 145
    CV17 = 146
    CV18 = 147
    CV19 = 148
    CV20 = 149
    CV21 = 150
    CV22 = 151
    CV23 = 152
    CV24 = 153
    CV25 = 154
    CV26 = 155
    CV27 = 156
    CV28 = 157
    CV29 = 158
    CV30 = 159
    CV31 = 160
    CV32 = 161
    CV33 = 162
    CV34 = 163
    CV35 = 164
    CV36 = 165
    CV37 = 166
    CV38 = 167
    CV39 = 168
    CV40 = 169
    CV41 = 170
    CV42 = 171
    CV43 = 172
    CV44 = 173
    CV45 = 174
    CV46 = 175
    CV47 = 176
    CV48 = 177
    CV49 = 178
    CV50 = 179
    CV51 = 180
    CV52 = 181
    CV53 = 182
    CV54 = 183
    CV55 = 184
    CV56 = 185
    CV57 = 186
    CV58 = 187
    CV59 = 188
    CV60 = 189
    CV61 = 190
    CV62 = 191
    CV63 = 192
    CV64 = 193
    CV65 = 194
    CV66 = 195
    CV67 = 196
    CV68 = 197
    CV69 = 198
    CV70 = 199
    CV71 = 200
    CV72 = 201
    CV73 = 202
    CV74 = 203
    CV75 = 204
    CV76 = 205
    CV77 = 206
    CV78 = 207
    CV79 = 208
    CV80 = 209
    CV81 = 210
    CV82 = 211
    CV83 = 212
    CV84 = 213
    CV85 = 214
    CV86 = 215
    CV87 = 216
    CV88 = 217
    CV89 = 218
    CV90 = 219
    CV91 = 220
    CV92 = 221
    CV93 = 222
    CV94 = 223
    CV95 = 224
    CV96 = 225
    CV97 = 226
    CV98 = 227
    CV99 = 228


@dataclasses.dataclass(slots=True)
class ExportConstraint:
    type: 'ExportConstraintType'
    value: float


@dataclasses.dataclass(slots=True)
class GUIDMapping:
    from_: 'GUID'
    to: 'GUID'


@dataclasses.dataclass(slots=True)
class Blob:
    bytes: bytes


@dataclasses.dataclass
class Image:
    hash: typing.Optional[bytes] = None
    name: typing.Optional[str] = None
    dataBlob: typing.Optional[uint] = None


@dataclasses.dataclass
class Video:
    hash: typing.Optional[bytes] = None
    s3Url: typing.Optional[str] = None


@dataclasses.dataclass(slots=True)
class FilterColorAdjust:
    tint: float
    shadows: float
    highlights: float
    detail: float
    exposure: float
    vignette: float
    temperature: float
    vibrance: float


@dataclasses.dataclass
class PaintFilterMessage:
    tint: typing.Optional[float] = None
    shadows: typing.Optional[float] = None
    highlights: typing.Optional[float] = None
    detail: typing.Optional[float] = None
    exposure: typing.Optional[float] = None
    vignette: typing.Optional[float] = None
    temperature: typing.Optional[float] = None
    vibrance: typing.Optional[float] = None
    contrast: typing.Optional[float] = None
    brightness: typing.Optional[float] = None


@dataclasses.dataclass
class Paint:
    type: typing.Optional['PaintType'] = None
    color: typing.Optional['Color'] = None
    opacity: typing.Optional[float] = None
    visible: typing.Optional[bool] = None
    blendMode: typing.Optional['BlendMode'] = None
    stops: typing.Optional[list['ColorStop']] = None
    transform: typing.Optional['Matrix'] = None
    image: typing.Optional['Image'] = None
    imageThumbnail: typing.Optional['Image'] = None
    animatedImage: typing.Optional['Image'] = None
    animationFrame: typing.Optional[uint] = None
    imageScaleMode: typing.Optional['ImageScaleMode'] = None
    imageShouldColorManage: typing.Optional[bool] = None
    rotation: typing.Optional[float] = None
    scale: typing.Optional[float] = None
    filterColorAdjust: typing.Optional['FilterColorAdjust'] = None
    paintFilter: typing.Optional['PaintFilterMessage'] = None
    emojiCodePoints: typing.Optional[list[uint]] = None
    video: typing.Optional['Video'] = None
    originalImageWidth: typing.Optional[uint] = None
    originalImageHeight: typing.Optional[uint] = None
    colorVar: typing.Optional['VariableData'] = None


@dataclasses.dataclass
class FontMetaData:
    key: typing.Optional['FontName'] = None
    fontLineHeight: typing.Optional[float] = None
    fontDigest: typing.Optional[bytes] = None
    fontStyle: typing.Optional['FontStyle'] = None
    fontWeight: typing.Optional[int] = None


@dataclasses.dataclass
class FontVariation:
    axisTag: typing.Optional[uint] = None
    axisName: typing.Optional[str] = None
    value: typing.Optional[float] = None


@dataclasses.dataclass
class TextData:
    characters: typing.Optional[str] = None
    characterStyleIDs: typing.Optional[list[uint]] = None
    styleOverrideTable: typing.Optional[list['NodeChange']] = None
    layoutSize: typing.Optional['Vector'] = None
    baselines: typing.Optional[list['Baseline']] = None
    glyphs: typing.Optional[list['Glyph']] = None
    decorations: typing.Optional[list['Decoration']] = None
    blockquotes: typing.Optional[list['Blockquote']] = None
    layoutVersion: typing.Optional[uint] = None
    fontMetaData: typing.Optional[list['FontMetaData']] = None
    fallbackFonts: typing.Optional[list['FontName']] = None
    hyperlinkBoxes: typing.Optional[list['HyperlinkBox']] = None
    lines: typing.Optional[list['TextLineData']] = None
    truncationStartIndex: typing.Optional[int] = None
    truncatedHeight: typing.Optional[float] = None
    logicalIndexToCharacterOffsetMap: typing.Optional[list[float]] = None
    minContentHeight: typing.Optional[float] = None
    mentionBoxes: typing.Optional[list['MentionBox']] = None
    derivedLines: typing.Optional[list['DerivedTextLineData']] = None


@dataclasses.dataclass
class DerivedTextData:
    layoutSize: typing.Optional['Vector'] = None
    baselines: typing.Optional[list['Baseline']] = None
    glyphs: typing.Optional[list['Glyph']] = None
    decorations: typing.Optional[list['Decoration']] = None
    blockquotes: typing.Optional[list['Blockquote']] = None
    fontMetaData: typing.Optional[list['FontMetaData']] = None
    hyperlinkBoxes: typing.Optional[list['HyperlinkBox']] = None
    truncationStartIndex: typing.Optional[int] = None
    truncatedHeight: typing.Optional[float] = None
    logicalIndexToCharacterOffsetMap: typing.Optional[list[float]] = None
    mentionBoxes: typing.Optional[list['MentionBox']] = None
    derivedLines: typing.Optional[list['DerivedTextLineData']] = None


@dataclasses.dataclass
class HyperlinkBox:
    bounds: typing.Optional['Rect'] = None
    url: typing.Optional[str] = None
    guid: typing.Optional['GUID'] = None
    hyperlinkID: typing.Optional[int] = None


@dataclasses.dataclass
class MentionBox:
    bounds: typing.Optional['Rect'] = None
    startIndex: typing.Optional[uint] = None
    endIndex: typing.Optional[uint] = None
    isValid: typing.Optional[bool] = None
    mentionKey: typing.Optional[uint] = None


@dataclasses.dataclass
class Baseline:
    position: typing.Optional['Vector'] = None
    width: typing.Optional[float] = None
    lineY: typing.Optional[float] = None
    lineHeight: typing.Optional[float] = None
    lineAscent: typing.Optional[float] = None
    ignoreLeadingTrim: typing.Optional[float] = None
    firstCharacter: typing.Optional[uint] = None
    endCharacter: typing.Optional[uint] = None


@dataclasses.dataclass
class Glyph:
    commandsBlob: typing.Optional[uint] = None
    position: typing.Optional['Vector'] = None
    styleID: typing.Optional[uint] = None
    fontSize: typing.Optional[float] = None
    firstCharacter: typing.Optional[uint] = None
    advance: typing.Optional[float] = None
    emojiCodePoints: typing.Optional[list[uint]] = None


@dataclasses.dataclass
class Decoration:
    rects: typing.Optional[list['Rect']] = None
    styleID: typing.Optional[uint] = None


@dataclasses.dataclass
class Blockquote:
    verticalBar: typing.Optional['Rect'] = None
    quoteMarkBounds: typing.Optional['Rect'] = None
    styleID: typing.Optional[uint] = None


@dataclasses.dataclass
class VectorData:
    vectorNetworkBlob: typing.Optional[uint] = None
    normalizedSize: typing.Optional['Vector'] = None
    styleOverrideTable: typing.Optional[list['NodeChange']] = None


@dataclasses.dataclass
class GUIDPath:
    guids: typing.Optional[list['GUID']] = None


@dataclasses.dataclass
class SymbolData:
    symbolID: typing.Optional['GUID'] = None
    symbolOverrides: typing.Optional[list['NodeChange']] = None
    uniformScaleFactor: typing.Optional[float] = None


@dataclasses.dataclass
class GUIDPathMapping:
    id: typing.Optional['GUID'] = None
    path: typing.Optional['GUIDPath'] = None


@dataclasses.dataclass
class NodeGenerationData:
    overrides: typing.Optional[list['NodeChange']] = None
    useFineGrainedSyncing: typing.Optional[bool] = None
    diffOnlyRemovals: typing.Optional[list['NodeChange']] = None


@dataclasses.dataclass
class DerivedImmutableFrameData:
    overrides: typing.Optional[list['NodeChange']] = None
    version: typing.Optional[uint] = None


@dataclasses.dataclass
class AssetRef:
    key: typing.Optional[str] = None
    version: typing.Optional[str] = None


@dataclasses.dataclass
class StateGroupId:
    guid: typing.Optional['GUID'] = None
    assetRef: typing.Optional['AssetRef'] = None


@dataclasses.dataclass
class StyleId:
    guid: typing.Optional['GUID'] = None
    assetRef: typing.Optional['AssetRef'] = None


@dataclasses.dataclass
class SymbolId:
    guid: typing.Optional['GUID'] = None
    assetRef: typing.Optional['AssetRef'] = None


@dataclasses.dataclass
class VariableID:
    guid: typing.Optional['GUID'] = None
    assetRef: typing.Optional['AssetRef'] = None


@dataclasses.dataclass
class VariableSetID:
    guid: typing.Optional['GUID'] = None
    assetRef: typing.Optional['AssetRef'] = None


@dataclasses.dataclass
class SharedSymbolReference:
    fileKey: typing.Optional[str] = None
    symbolID: typing.Optional['GUID'] = None
    versionHash: typing.Optional[str] = None
    guidPathMappings: typing.Optional[list['GUIDPathMapping']] = None
    bytes: typing.Optional[bytes] = None
    libraryGUIDToSubscribingGUID: typing.Optional[list['GUIDMapping']] = None
    componentKey: typing.Optional[str] = None
    unflatteningMappings: typing.Optional[list['GUIDPathMapping']] = None
    isUnflattened: typing.Optional[bool] = None


@dataclasses.dataclass
class SharedComponentMasterData:
    componentKey: typing.Optional[str] = None
    publishingGUIDPathToTeamLibraryGUID: typing.Optional[list['GUIDPathMapping']] = None
    isUnflattened: typing.Optional[bool] = None


@dataclasses.dataclass
class InstanceOverrideStash:
    overridePathOfSwappedInstance: typing.Optional['GUIDPath'] = None
    componentKey: typing.Optional[str] = None
    overrides: typing.Optional[list['NodeChange']] = None


@dataclasses.dataclass
class InstanceOverrideStashV2:
    overridePathOfSwappedInstance: typing.Optional['GUIDPath'] = None
    localSymbolID: typing.Optional['GUID'] = None
    overrides: typing.Optional[list['NodeChange']] = None


@dataclasses.dataclass
class Effect:
    type: typing.Optional['EffectType'] = None
    color: typing.Optional['Color'] = None
    offset: typing.Optional['Vector'] = None
    radius: typing.Optional[float] = None
    visible: typing.Optional[bool] = None
    blendMode: typing.Optional['BlendMode'] = None
    spread: typing.Optional[float] = None
    showShadowBehindNode: typing.Optional[bool] = None


@dataclasses.dataclass
class TransitionInfo:
    type: typing.Optional['TransitionType'] = None
    duration: typing.Optional[float] = None


class PrototypeDeviceType(enum.Enum):
    NONE = 0
    PRESET = 1
    CUSTOM = 2
    PRESENTATION = 3


class DeviceRotation(enum.Enum):
    NONE = 0
    CCW_90 = 1


@dataclasses.dataclass
class PrototypeDevice:
    type: typing.Optional['PrototypeDeviceType'] = None
    size: typing.Optional['Vector'] = None
    presetIdentifier: typing.Optional[str] = None
    rotation: typing.Optional['DeviceRotation'] = None


class OverlayPositionType(enum.Enum):
    CENTER = 0
    TOP_LEFT = 1
    TOP_CENTER = 2
    TOP_RIGHT = 3
    BOTTOM_LEFT = 4
    BOTTOM_CENTER = 5
    BOTTOM_RIGHT = 6
    MANUAL = 7


class OverlayBackgroundInteraction(enum.Enum):
    NONE = 0
    CLOSE_ON_CLICK_OUTSIDE = 1


class OverlayBackgroundType(enum.Enum):
    NONE = 0
    SOLID_COLOR = 1


@dataclasses.dataclass
class OverlayBackgroundAppearance:
    backgroundType: typing.Optional['OverlayBackgroundType'] = None
    backgroundColor: typing.Optional['Color'] = None


class NavigationType(enum.Enum):
    NAVIGATE = 0
    OVERLAY = 1
    SWAP = 2
    SWAP_STATE = 3
    SCROLL_TO = 4


class ExportColorProfile(enum.Enum):
    DOCUMENT = 0
    SRGB = 1
    DISPLAY_P3_V4 = 2


@dataclasses.dataclass
class ExportSettings:
    suffix: typing.Optional[str] = None
    imageType: typing.Optional['ImageType'] = None
    constraint: typing.Optional['ExportConstraint'] = None
    svgDataName: typing.Optional[bool] = None
    svgIDMode: typing.Optional['ExportSVGIDMode'] = None
    svgOutlineText: typing.Optional[bool] = None
    contentsOnly: typing.Optional[bool] = None
    svgForceStrokeMasks: typing.Optional[bool] = None
    useAbsoluteBounds: typing.Optional[bool] = None
    colorProfile: typing.Optional['ExportColorProfile'] = None


class ExportSVGIDMode(enum.Enum):
    IF_NEEDED = 0
    ALWAYS = 1


@dataclasses.dataclass
class LayoutGrid:
    type: typing.Optional['LayoutGridType'] = None
    axis: typing.Optional['Axis'] = None
    visible: typing.Optional[bool] = None
    numSections: typing.Optional[int] = None
    offset: typing.Optional[float] = None
    sectionSize: typing.Optional[float] = None
    gutterSize: typing.Optional[float] = None
    color: typing.Optional['Color'] = None
    pattern: typing.Optional['LayoutGridPattern'] = None


@dataclasses.dataclass
class Guide:
    axis: typing.Optional['Axis'] = None
    offset: typing.Optional[float] = None
    guid: typing.Optional['GUID'] = None


@dataclasses.dataclass
class Path:
    windingRule: typing.Optional['WindingRule'] = None
    commandsBlob: typing.Optional[uint] = None
    styleID: typing.Optional[uint] = None


class StyleType(enum.Enum):
    NONE = 0
    FILL = 1
    STROKE = 2
    TEXT = 3
    EFFECT = 4
    EXPORT = 5
    GRID = 6


@dataclasses.dataclass
class SharedStyleReference:
    styleKey: typing.Optional[str] = None
    versionHash: typing.Optional[str] = None


@dataclasses.dataclass
class SharedStyleMasterData:
    styleKey: typing.Optional[str] = None
    sortPosition: typing.Optional[str] = None
    fileKey: typing.Optional[str] = None


class ScrollBehavior(enum.Enum):
    SCROLLS = 0
    FIXED_WHEN_CHILD_OF_SCROLLING_FRAME = 1
    STICKY_SCROLLS = 2


@dataclasses.dataclass
class ArcData:
    startingAngle: typing.Optional[float] = None
    endingAngle: typing.Optional[float] = None
    innerRadius: typing.Optional[float] = None


@dataclasses.dataclass
class SymbolLink:
    uri: typing.Optional[str] = None
    displayName: typing.Optional[str] = None
    displayText: typing.Optional[str] = None


@dataclasses.dataclass
class PluginData:
    pluginID: typing.Optional[str] = None
    value: typing.Optional[str] = None
    key: typing.Optional[str] = None


@dataclasses.dataclass
class PluginRelaunchData:
    pluginID: typing.Optional[str] = None
    message: typing.Optional[str] = None
    command: typing.Optional[str] = None
    isDeleted: typing.Optional[bool] = None


@dataclasses.dataclass
class MultiplayerFieldVersion:
    counter: typing.Optional[uint] = None
    sessionID: typing.Optional[uint] = None


class ConnectorMagnet(enum.Enum):
    NONE = 0
    AUTO = 1
    TOP = 2
    LEFT = 3
    BOTTOM = 4
    RIGHT = 5
    CENTER = 6


@dataclasses.dataclass
class ConnectorEndpoint:
    endpointNodeID: typing.Optional['GUID'] = None
    position: typing.Optional['Vector'] = None
    magnet: typing.Optional['ConnectorMagnet'] = None


@dataclasses.dataclass
class ConnectorControlPoint:
    position: typing.Optional['Vector'] = None
    axis: typing.Optional['Vector'] = None


class ConnectorTextSection(enum.Enum):
    MIDDLE_TO_START = 0
    MIDDLE_TO_END = 1


@dataclasses.dataclass
class ConnectorTextMidpoint:
    section: typing.Optional['ConnectorTextSection'] = None
    offset: typing.Optional[float] = None


class ConnectorLineStyle(enum.Enum):
    ELBOWED = 0
    STRAIGHT = 1


@dataclasses.dataclass
class LibraryMoveInfo:
    oldKey: typing.Optional[str] = None
    pasteFileKey: typing.Optional[str] = None


@dataclasses.dataclass
class LibraryMoveHistoryItem:
    sourceNodeId: typing.Optional['GUID'] = None
    sourceComponentKey: typing.Optional[str] = None


@dataclasses.dataclass
class DeveloperRelatedLink:
    nodeId: typing.Optional[str] = None
    fileKey: typing.Optional[str] = None
    linkName: typing.Optional[str] = None
    linkUrl: typing.Optional[str] = None


@dataclasses.dataclass
class WidgetPointer:
    nodeId: typing.Optional['GUID'] = None


@dataclasses.dataclass
class EditInfo:
    timestampIso8601: typing.Optional[str] = None
    userId: typing.Optional[str] = None
    lastEditedAt: typing.Optional[uint] = None
    createdAt: typing.Optional[uint] = None


class EditorType(enum.Enum):
    DESIGN = 0
    WHITEBOARD = 1
    SLIDES = 2


class MaskType(enum.Enum):
    ALPHA = 0
    OUTLINE = 1
    LUMINANCE = 2


class SectionStatus(enum.Enum):
    NONE = 0
    BUILD = 1


@dataclasses.dataclass
class SectionStatusInfo:
    status: typing.Optional['SectionStatus'] = None


@dataclasses.dataclass
class NodeChange:
    guid: typing.Optional['GUID'] = None
    guidTag: typing.Optional[uint] = None
    phase: typing.Optional['NodePhase'] = None
    phaseTag: typing.Optional[uint] = None
    parentIndex: typing.Optional['ParentIndex'] = None
    parentIndexTag: typing.Optional[uint] = None
    type: typing.Optional['NodeType'] = None
    typeTag: typing.Optional[uint] = None
    name: typing.Optional[str] = None
    nameTag: typing.Optional[uint] = None
    isPublishable: typing.Optional[bool] = None
    description: typing.Optional[str] = None
    libraryMoveInfo: typing.Optional['LibraryMoveInfo'] = None
    libraryMoveHistory: typing.Optional[list['LibraryMoveHistoryItem']] = None
    key: typing.Optional[str] = None
    styleID: typing.Optional[uint] = None
    styleIDTag: typing.Optional[uint] = None
    isSoftDeletedStyle: typing.Optional[bool] = None
    isNonUpdateable: typing.Optional[bool] = None
    isFillStyle: typing.Optional[bool] = None
    isStrokeStyle: typing.Optional[bool] = None
    styleType: typing.Optional['StyleType'] = None
    styleDescription: typing.Optional[str] = None
    version: typing.Optional[str] = None
    sharedStyleMasterData: typing.Optional['SharedStyleMasterData'] = None
    sharedStyleReference: typing.Optional['SharedStyleReference'] = None
    sortPosition: typing.Optional[str] = None
    ojansSuperSecretNodeField: typing.Optional['SharedStyleMasterData'] = None
    sevMoonlitLilyData: typing.Optional['SharedStyleMasterData'] = None
    inheritFillStyleID: typing.Optional['GUID'] = None
    inheritStrokeStyleID: typing.Optional['GUID'] = None
    inheritTextStyleID: typing.Optional['GUID'] = None
    inheritExportStyleID: typing.Optional['GUID'] = None
    inheritEffectStyleID: typing.Optional['GUID'] = None
    inheritGridStyleID: typing.Optional['GUID'] = None
    inheritFillStyleIDForStroke: typing.Optional['GUID'] = None
    styleIdForFill: typing.Optional['StyleId'] = None
    styleIdForStrokeFill: typing.Optional['StyleId'] = None
    styleIdForText: typing.Optional['StyleId'] = None
    styleIdForEffect: typing.Optional['StyleId'] = None
    styleIdForGrid: typing.Optional['StyleId'] = None
    backgroundPaints: typing.Optional[list['Paint']] = None
    inheritFillStyleIDForBackground: typing.Optional['GUID'] = None
    isStateGroup: typing.Optional[bool] = None
    stateGroupPropertyValueOrders: typing.Optional[list['StateGroupPropertyValueOrder']] = None
    sharedSymbolReference: typing.Optional['SharedSymbolReference'] = None
    isSymbolPublishable: typing.Optional[bool] = None
    sharedSymbolMappings: typing.Optional[list['GUIDPathMapping']] = None
    sharedSymbolVersion: typing.Optional[str] = None
    sharedComponentMasterData: typing.Optional['SharedComponentMasterData'] = None
    symbolDescription: typing.Optional[str] = None
    unflatteningMappings: typing.Optional[list['GUIDPathMapping']] = None
    forceUnflatteningMappings: typing.Optional[list['GUIDPathMapping']] = None
    publishFile: typing.Optional[str] = None
    publishID: typing.Optional['GUID'] = None
    componentKey: typing.Optional[str] = None
    isC2: typing.Optional[bool] = None
    publishedVersion: typing.Optional[str] = None
    originComponentKey: typing.Optional[str] = None
    componentPropDefs: typing.Optional[list['ComponentPropDef']] = None
    componentPropRefs: typing.Optional[list['ComponentPropRef']] = None
    symbolData: typing.Optional['SymbolData'] = None
    symbolDataTag: typing.Optional[uint] = None
    derivedSymbolData: typing.Optional[list['NodeChange']] = None
    overriddenSymbolID: typing.Optional['GUID'] = None
    componentPropAssignments: typing.Optional[list['ComponentPropAssignment']] = None
    propsAreBubbled: typing.Optional[bool] = None
    overrideStash: typing.Optional[list['InstanceOverrideStash']] = None
    overrideStashV2: typing.Optional[list['InstanceOverrideStashV2']] = None
    guidPath: typing.Optional['GUIDPath'] = None
    guidPathTag: typing.Optional[uint] = None
    overrideLevel: typing.Optional[int] = None
    fontSize: typing.Optional[float] = None
    fontSizeTag: typing.Optional[uint] = None
    paragraphIndent: typing.Optional[float] = None
    paragraphIndentTag: typing.Optional[uint] = None
    paragraphSpacing: typing.Optional[float] = None
    paragraphSpacingTag: typing.Optional[uint] = None
    textAlignHorizontal: typing.Optional['TextAlignHorizontal'] = None
    textAlignHorizontalTag: typing.Optional[uint] = None
    textAlignVertical: typing.Optional['TextAlignVertical'] = None
    textAlignVerticalTag: typing.Optional[uint] = None
    textCase: typing.Optional['TextCase'] = None
    textCaseTag: typing.Optional[uint] = None
    textDecoration: typing.Optional['TextDecoration'] = None
    textDecorationTag: typing.Optional[uint] = None
    lineHeight: typing.Optional['Number'] = None
    lineHeightTag: typing.Optional[uint] = None
    fontName: typing.Optional['FontName'] = None
    fontNameTag: typing.Optional[uint] = None
    textData: typing.Optional['TextData'] = None
    textDataTag: typing.Optional[uint] = None
    derivedTextData: typing.Optional['DerivedTextData'] = None
    fontVariantCommonLigatures: typing.Optional[bool] = None
    fontVariantContextualLigatures: typing.Optional[bool] = None
    fontVariantDiscretionaryLigatures: typing.Optional[bool] = None
    fontVariantHistoricalLigatures: typing.Optional[bool] = None
    fontVariantOrdinal: typing.Optional[bool] = None
    fontVariantSlashedZero: typing.Optional[bool] = None
    fontVariantNumericFigure: typing.Optional['FontVariantNumericFigure'] = None
    fontVariantNumericSpacing: typing.Optional['FontVariantNumericSpacing'] = None
    fontVariantNumericFraction: typing.Optional['FontVariantNumericFraction'] = None
    fontVariantCaps: typing.Optional['FontVariantCaps'] = None
    fontVariantPosition: typing.Optional['FontVariantPosition'] = None
    letterSpacing: typing.Optional['Number'] = None
    fontVersion: typing.Optional[str] = None
    leadingTrim: typing.Optional['LeadingTrim'] = None
    hangingPunctuation: typing.Optional[bool] = None
    hangingList: typing.Optional[bool] = None
    maxLines: typing.Optional[int] = None
    sectionStatus: typing.Optional['SectionStatus'] = None
    sectionStatusInfo: typing.Optional['SectionStatusInfo'] = None
    textUserLayoutVersion: typing.Optional[uint] = None
    toggledOnOTFeatures: typing.Optional[list['OpenTypeFeature']] = None
    toggledOffOTFeatures: typing.Optional[list['OpenTypeFeature']] = None
    hyperlink: typing.Optional['Hyperlink'] = None
    mention: typing.Optional['Mention'] = None
    fontVariations: typing.Optional[list['FontVariation']] = None
    textBidiVersion: typing.Optional[uint] = None
    textTruncation: typing.Optional['TextTruncation'] = None
    hasHadRTLText: typing.Optional[bool] = None
    visible: typing.Optional[bool] = None
    visibleTag: typing.Optional[uint] = None
    locked: typing.Optional[bool] = None
    lockedTag: typing.Optional[uint] = None
    opacity: typing.Optional[float] = None
    opacityTag: typing.Optional[uint] = None
    blendMode: typing.Optional['BlendMode'] = None
    blendModeTag: typing.Optional[uint] = None
    size: typing.Optional['Vector'] = None
    sizeTag: typing.Optional[uint] = None
    transform: typing.Optional['Matrix'] = None
    transformTag: typing.Optional[uint] = None
    dashPattern: typing.Optional[list[float]] = None
    dashPatternTag: typing.Optional[uint] = None
    mask: typing.Optional[bool] = None
    maskTag: typing.Optional[uint] = None
    maskIsOutline: typing.Optional[bool] = None
    maskIsOutlineTag: typing.Optional[uint] = None
    maskType: typing.Optional['MaskType'] = None
    backgroundOpacity: typing.Optional[float] = None
    backgroundOpacityTag: typing.Optional[uint] = None
    cornerRadius: typing.Optional[float] = None
    cornerRadiusTag: typing.Optional[uint] = None
    strokeWeight: typing.Optional[float] = None
    strokeWeightTag: typing.Optional[uint] = None
    strokeAlign: typing.Optional['StrokeAlign'] = None
    strokeAlignTag: typing.Optional[uint] = None
    strokeCap: typing.Optional['StrokeCap'] = None
    strokeCapTag: typing.Optional[uint] = None
    strokeJoin: typing.Optional['StrokeJoin'] = None
    strokeJoinTag: typing.Optional[uint] = None
    fillPaints: typing.Optional[list['Paint']] = None
    fillPaintsTag: typing.Optional[uint] = None
    strokePaints: typing.Optional[list['Paint']] = None
    strokePaintsTag: typing.Optional[uint] = None
    effects: typing.Optional[list['Effect']] = None
    effectsTag: typing.Optional[uint] = None
    backgroundColor: typing.Optional['Color'] = None
    backgroundColorTag: typing.Optional[uint] = None
    fillGeometry: typing.Optional[list['Path']] = None
    fillGeometryTag: typing.Optional[uint] = None
    strokeGeometry: typing.Optional[list['Path']] = None
    strokeGeometryTag: typing.Optional[uint] = None
    rectangleTopLeftCornerRadius: typing.Optional[float] = None
    rectangleTopRightCornerRadius: typing.Optional[float] = None
    rectangleBottomLeftCornerRadius: typing.Optional[float] = None
    rectangleBottomRightCornerRadius: typing.Optional[float] = None
    rectangleCornerRadiiIndependent: typing.Optional[bool] = None
    rectangleCornerToolIndependent: typing.Optional[bool] = None
    proportionsConstrained: typing.Optional[bool] = None
    useAbsoluteBounds: typing.Optional[bool] = None
    borderTopHidden: typing.Optional[bool] = None
    borderBottomHidden: typing.Optional[bool] = None
    borderLeftHidden: typing.Optional[bool] = None
    borderRightHidden: typing.Optional[bool] = None
    bordersTakeSpace: typing.Optional[bool] = None
    borderTopWeight: typing.Optional[float] = None
    borderBottomWeight: typing.Optional[float] = None
    borderLeftWeight: typing.Optional[float] = None
    borderRightWeight: typing.Optional[float] = None
    borderStrokeWeightsIndependent: typing.Optional[bool] = None
    horizontalConstraint: typing.Optional['ConstraintType'] = None
    horizontalConstraintTag: typing.Optional[uint] = None
    stackMode: typing.Optional['StackMode'] = None
    stackModeTag: typing.Optional[uint] = None
    stackSpacing: typing.Optional[float] = None
    stackSpacingTag: typing.Optional[uint] = None
    stackPadding: typing.Optional[float] = None
    stackPaddingTag: typing.Optional[uint] = None
    stackCounterAlign: typing.Optional['StackCounterAlign'] = None
    stackJustify: typing.Optional['StackJustify'] = None
    stackAlign: typing.Optional['StackAlign'] = None
    stackHorizontalPadding: typing.Optional[float] = None
    stackVerticalPadding: typing.Optional[float] = None
    stackWidth: typing.Optional['StackSize'] = None
    stackHeight: typing.Optional['StackSize'] = None
    stackPrimarySizing: typing.Optional['StackSize'] = None
    stackPrimaryAlignItems: typing.Optional['StackJustify'] = None
    stackCounterAlignItems: typing.Optional['StackAlign'] = None
    stackChildPrimaryGrow: typing.Optional[float] = None
    stackPaddingRight: typing.Optional[float] = None
    stackPaddingBottom: typing.Optional[float] = None
    stackChildAlignSelf: typing.Optional['StackCounterAlign'] = None
    stackPositioning: typing.Optional['StackPositioning'] = None
    stackReverseZIndex: typing.Optional[bool] = None
    stackWrap: typing.Optional['StackWrap'] = None
    stackCounterSpacing: typing.Optional[float] = None
    minSize: typing.Optional['OptionalVector'] = None
    maxSize: typing.Optional['OptionalVector'] = None
    stackCounterAlignContent: typing.Optional['StackCounterAlignContent'] = None
    isSnakeGameBoard: typing.Optional[bool] = None
    transitionNodeID: typing.Optional['GUID'] = None
    prototypeStartNodeID: typing.Optional['GUID'] = None
    prototypeBackgroundColor: typing.Optional['Color'] = None
    transitionInfo: typing.Optional['TransitionInfo'] = None
    transitionType: typing.Optional['TransitionType'] = None
    transitionDuration: typing.Optional[float] = None
    easingType: typing.Optional['EasingType'] = None
    transitionPreserveScroll: typing.Optional[bool] = None
    connectionType: typing.Optional['ConnectionType'] = None
    connectionURL: typing.Optional[str] = None
    prototypeDevice: typing.Optional['PrototypeDevice'] = None
    interactionType: typing.Optional['InteractionType'] = None
    transitionTimeout: typing.Optional[float] = None
    interactionMaintained: typing.Optional[bool] = None
    interactionDuration: typing.Optional[float] = None
    destinationIsOverlay: typing.Optional[bool] = None
    transitionShouldSmartAnimate: typing.Optional[bool] = None
    prototypeInteractions: typing.Optional[list['PrototypeInteraction']] = None
    prototypeStartingPoint: typing.Optional['PrototypeStartingPoint'] = None
    pluginData: typing.Optional[list['PluginData']] = None
    pluginRelaunchData: typing.Optional[list['PluginRelaunchData']] = None
    connectorStart: typing.Optional['ConnectorEndpoint'] = None
    connectorEnd: typing.Optional['ConnectorEndpoint'] = None
    connectorLineStyle: typing.Optional['ConnectorLineStyle'] = None
    connectorStartCap: typing.Optional['StrokeCap'] = None
    connectorEndCap: typing.Optional['StrokeCap'] = None
    connectorControlPoints: typing.Optional[list['ConnectorControlPoint']] = None
    connectorTextMidpoint: typing.Optional['ConnectorTextMidpoint'] = None
    shapeWithTextType: typing.Optional['ShapeWithTextType'] = None
    shapeUserHeight: typing.Optional[float] = None
    derivedImmutableFrameData: typing.Optional['DerivedImmutableFrameData'] = None
    derivedImmutableFrameDataVersion: typing.Optional['MultiplayerFieldVersion'] = None
    nodeGenerationData: typing.Optional['NodeGenerationData'] = None
    codeBlockLanguage: typing.Optional['CodeBlockLanguage'] = None
    linkPreviewData: typing.Optional['LinkPreviewData'] = None
    shapeTruncates: typing.Optional[bool] = None
    sectionContentsHidden: typing.Optional[bool] = None
    videoPlayback: typing.Optional['VideoPlayback'] = None
    stampData: typing.Optional['StampData'] = None
    widgetSyncedState: typing.Optional['MultiplayerMap'] = None
    widgetSyncCursor: typing.Optional[uint] = None
    widgetDerivedSubtreeCursor: typing.Optional['WidgetDerivedSubtreeCursor'] = None
    widgetCachedAncestor: typing.Optional['WidgetPointer'] = None
    widgetInputBehavior: typing.Optional['WidgetInputBehavior'] = None
    widgetTooltip: typing.Optional[str] = None
    widgetHoverStyle: typing.Optional['WidgetHoverStyle'] = None
    isWidgetStickable: typing.Optional[bool] = None
    shouldHideCursorsOnWidgetHover: typing.Optional[bool] = None
    widgetMetadata: typing.Optional['WidgetMetadata'] = None
    widgetEvents: typing.Optional[list['WidgetEvent']] = None
    widgetPropertyMenuItems: typing.Optional[list['WidgetPropertyMenuItem']] = None
    tableRowPositions: typing.Optional['TableRowColumnPositionMap'] = None
    tableColumnPositions: typing.Optional['TableRowColumnPositionMap'] = None
    tableRowHeights: typing.Optional['TableRowColumnSizeMap'] = None
    tableColumnWidths: typing.Optional['TableRowColumnSizeMap'] = None
    internalEnumForTest: typing.Optional['InternalEnumForTest'] = None
    internalDataForTest: typing.Optional['InternalDataForTest'] = None
    count: typing.Optional[uint] = None
    countTag: typing.Optional[uint] = None
    autoRename: typing.Optional[bool] = None
    autoRenameTag: typing.Optional[uint] = None
    backgroundEnabled: typing.Optional[bool] = None
    backgroundEnabledTag: typing.Optional[uint] = None
    exportContentsOnly: typing.Optional[bool] = None
    exportContentsOnlyTag: typing.Optional[uint] = None
    starInnerScale: typing.Optional[float] = None
    starInnerScaleTag: typing.Optional[uint] = None
    miterLimit: typing.Optional[float] = None
    miterLimitTag: typing.Optional[uint] = None
    textTracking: typing.Optional[float] = None
    textTrackingTag: typing.Optional[uint] = None
    booleanOperation: typing.Optional['BooleanOperation'] = None
    booleanOperationTag: typing.Optional[uint] = None
    verticalConstraint: typing.Optional['ConstraintType'] = None
    verticalConstraintTag: typing.Optional[uint] = None
    handleMirroring: typing.Optional['VectorMirror'] = None
    handleMirroringTag: typing.Optional[uint] = None
    exportSettings: typing.Optional[list['ExportSettings']] = None
    exportSettingsTag: typing.Optional[uint] = None
    textAutoResize: typing.Optional['TextAutoResize'] = None
    textAutoResizeTag: typing.Optional[uint] = None
    layoutGrids: typing.Optional[list['LayoutGrid']] = None
    layoutGridsTag: typing.Optional[uint] = None
    vectorData: typing.Optional['VectorData'] = None
    vectorDataTag: typing.Optional[uint] = None
    frameMaskDisabled: typing.Optional[bool] = None
    frameMaskDisabledTag: typing.Optional[uint] = None
    resizeToFit: typing.Optional[bool] = None
    resizeToFitTag: typing.Optional[uint] = None
    exportBackgroundDisabled: typing.Optional[bool] = None
    guides: typing.Optional[list['Guide']] = None
    internalOnly: typing.Optional[bool] = None
    scrollDirection: typing.Optional['ScrollDirection'] = None
    cornerSmoothing: typing.Optional[float] = None
    scrollOffset: typing.Optional['Vector'] = None
    exportTextAsSVGText: typing.Optional[bool] = None
    scrollContractedState: typing.Optional['ScrollContractedState'] = None
    contractedSize: typing.Optional['Vector'] = None
    fixedChildrenDivider: typing.Optional[str] = None
    scrollBehavior: typing.Optional['ScrollBehavior'] = None
    arcData: typing.Optional['ArcData'] = None
    derivedSymbolDataLayoutVersion: typing.Optional[int] = None
    navigationType: typing.Optional['NavigationType'] = None
    overlayPositionType: typing.Optional['OverlayPositionType'] = None
    overlayRelativePosition: typing.Optional['Vector'] = None
    overlayBackgroundInteraction: typing.Optional['OverlayBackgroundInteraction'] = None
    overlayBackgroundAppearance: typing.Optional['OverlayBackgroundAppearance'] = None
    overrideKey: typing.Optional['GUID'] = None
    containerSupportsFillStrokeAndCorners: typing.Optional[bool] = None
    stackCounterSizing: typing.Optional['StackSize'] = None
    containersSupportFillStrokeAndCorners: typing.Optional[bool] = None
    keyTrigger: typing.Optional['KeyTrigger'] = None
    voiceEventPhrase: typing.Optional[str] = None
    ancestorPathBeforeDeletion: typing.Optional[list['GUID']] = None
    symbolLinks: typing.Optional[list['SymbolLink']] = None
    textListData: typing.Optional['TextListData'] = None
    detachOpticalSizeFromFontSize: typing.Optional[bool] = None
    listSpacing: typing.Optional[float] = None
    embedData: typing.Optional['EmbedData'] = None
    richMediaData: typing.Optional['RichMediaData'] = None
    renderedSyncedState: typing.Optional['MultiplayerMap'] = None
    simplifyInstancePanels: typing.Optional[bool] = None
    accessibleHTMLTag: typing.Optional['HTMLTag'] = None
    ariaRole: typing.Optional['ARIARole'] = None
    accessibleLabel: typing.Optional[str] = None
    variableData: typing.Optional['VariableData'] = None
    variableConsumptionMap: typing.Optional['VariableDataMap'] = None
    variableModeBySetMap: typing.Optional['VariableModeBySetMap'] = None
    variableSetModes: typing.Optional[list['VariableSetMode']] = None
    variableSetID: typing.Optional['VariableSetID'] = None
    variableResolvedType: typing.Optional['VariableResolvedDataType'] = None
    variableDataValues: typing.Optional['VariableDataValues'] = None
    variableTokenName: typing.Optional[str] = None
    variableScopes: typing.Optional[list['VariableScope']] = None
    codeSyntax: typing.Optional['CodeSyntaxMap'] = None
    handoffStatusMap: typing.Optional['HandoffStatusMap'] = None
    agendaPositionMap: typing.Optional['AgendaPositionMap'] = None
    agendaMetadataMap: typing.Optional['AgendaMetadataMap'] = None
    migrationStatus: typing.Optional['MigrationStatus'] = None
    isSoftDeleted: typing.Optional[bool] = None
    editInfo: typing.Optional['EditInfo'] = None
    colorProfile: typing.Optional['ColorProfile'] = None
    detachedSymbolId: typing.Optional['SymbolId'] = None
    childReadingDirection: typing.Optional['ChildReadingDirection'] = None
    readingIndex: typing.Optional[str] = None
    documentColorProfile: typing.Optional['DocumentColorProfile'] = None
    developerRelatedLinks: typing.Optional[list['DeveloperRelatedLink']] = None
    slideActiveThemeLibKey: typing.Optional[str] = None
    ariaAttributes: typing.Optional['ARIAAttributesMap'] = None


@dataclasses.dataclass
class VideoPlayback:
    autoplay: typing.Optional[bool] = None
    mediaLoop: typing.Optional[bool] = None
    muted: typing.Optional[bool] = None


class MediaAction(enum.Enum):
    PLAY = 0
    PAUSE = 1
    TOGGLE_PLAY_PAUSE = 2
    MUTE = 3
    UNMUTE = 4
    TOGGLE_MUTE_UNMUTE = 5
    SKIP_FORWARD = 6
    SKIP_BACKWARD = 7
    SKIP_TO = 8


@dataclasses.dataclass
class WidgetHoverStyle:
    fillPaints: typing.Optional[list['Paint']] = None
    strokePaints: typing.Optional[list['Paint']] = None
    opacity: typing.Optional[float] = None
    areFillPaintsSet: typing.Optional[bool] = None
    areStrokePaintsSet: typing.Optional[bool] = None
    isOpacitySet: typing.Optional[bool] = None


@dataclasses.dataclass
class WidgetDerivedSubtreeCursor:
    sessionID: typing.Optional[uint] = None
    counter: typing.Optional[uint] = None


@dataclasses.dataclass
class MultiplayerMap:
    entries: typing.Optional[list['MultiplayerMapEntry']] = None


@dataclasses.dataclass
class MultiplayerMapEntry:
    key: typing.Optional[str] = None
    value: typing.Optional[str] = None


@dataclasses.dataclass
class VariableDataMap:
    entries: typing.Optional[list['VariableDataMapEntry']] = None


@dataclasses.dataclass
class VariableDataMapEntry:
    nodeField: typing.Optional[uint] = None
    variableData: typing.Optional['VariableData'] = None
    variableField: typing.Optional['VariableField'] = None


class VariableField(enum.Enum):
    MISSING = 0
    CORNER_RADIUS = 1
    PARAGRAPH_SPACING = 2
    PARAGRAPH_INDENT = 3
    STROKE_WEIGHT = 4
    STACK_SPACING = 5
    STACK_PADDING_LEFT = 6
    STACK_PADDING_TOP = 7
    STACK_PADDING_RIGHT = 8
    STACK_PADDING_BOTTOM = 9
    VISIBLE = 10
    TEXT_DATA = 11
    WIDTH = 12
    HEIGHT = 13
    RECTANGLE_TOP_LEFT_CORNER_RADIUS = 14
    RECTANGLE_TOP_RIGHT_CORNER_RADIUS = 15
    RECTANGLE_BOTTOM_LEFT_CORNER_RADIUS = 16
    RECTANGLE_BOTTOM_RIGHT_CORNER_RADIUS = 17
    BORDER_TOP_WEIGHT = 18
    BORDER_BOTTOM_WEIGHT = 19
    BORDER_LEFT_WEIGHT = 20
    BORDER_RIGHT_WEIGHT = 21
    VARIANT_PROPERTIES = 22
    STACK_COUNTER_SPACING = 23
    MIN_WIDTH = 24
    MAX_WIDTH = 25
    MIN_HEIGHT = 26
    MAX_HEIGHT = 27


@dataclasses.dataclass
class VariableModeBySetMap:
    entries: typing.Optional[list['VariableModeBySetMapEntry']] = None


@dataclasses.dataclass
class VariableModeBySetMapEntry:
    variableSetID: typing.Optional['VariableSetID'] = None
    variableModeID: typing.Optional['GUID'] = None


@dataclasses.dataclass
class CodeSyntaxMap:
    entries: typing.Optional[list['CodeSyntaxMapEntry']] = None


@dataclasses.dataclass
class CodeSyntaxMapEntry:
    platform: typing.Optional['CodeSyntaxPlatform'] = None
    value: typing.Optional[str] = None


@dataclasses.dataclass
class TableRowColumnPositionMap:
    entries: typing.Optional[list['TableRowColumnPositionMapEntry']] = None


@dataclasses.dataclass
class TableRowColumnPositionMapEntry:
    id: typing.Optional['GUID'] = None
    position: typing.Optional[str] = None


@dataclasses.dataclass
class TableRowColumnSizeMap:
    entries: typing.Optional[list['TableRowColumnSizeMapEntry']] = None


@dataclasses.dataclass
class TableRowColumnSizeMapEntry:
    id: typing.Optional['GUID'] = None
    size: typing.Optional[float] = None


@dataclasses.dataclass
class AgendaPositionMap:
    entries: typing.Optional[list['AgendaPositionMapEntry']] = None


@dataclasses.dataclass
class AgendaPositionMapEntry:
    id: typing.Optional['GUID'] = None
    position: typing.Optional[str] = None


class AgendaItemType(enum.Enum):
    NODE = 0
    BLOCK = 1


@dataclasses.dataclass
class AgendaMetadataMap:
    entries: typing.Optional[list['AgendaMetadataMapEntry']] = None


@dataclasses.dataclass
class AgendaMetadataMapEntry:
    id: typing.Optional['GUID'] = None
    data: typing.Optional['AgendaMetadata'] = None


@dataclasses.dataclass
class AgendaMetadata:
    name: typing.Optional[str] = None
    type: typing.Optional['AgendaItemType'] = None
    targetNodeID: typing.Optional['GUID'] = None
    timerInfo: typing.Optional['AgendaTimerInfo'] = None
    voteInfo: typing.Optional['AgendaVoteInfo'] = None
    musicInfo: typing.Optional['AgendaMusicInfo'] = None


@dataclasses.dataclass
class AgendaTimerInfo:
    timerLength: typing.Optional[uint] = None


@dataclasses.dataclass
class AgendaVoteInfo:
    voteCount: typing.Optional[uint] = None


@dataclasses.dataclass
class AgendaMusicInfo:
    songID: typing.Optional[str] = None
    startTimeMs: typing.Optional[uint] = None


@dataclasses.dataclass
class ComponentPropRef:
    nodeField: typing.Optional[uint] = None
    defID: typing.Optional['GUID'] = None
    zombieFallbackName: typing.Optional[str] = None
    componentPropNodeField: typing.Optional['ComponentPropNodeField'] = None
    isDeleted: typing.Optional[bool] = None


class ComponentPropNodeField(enum.Enum):
    VISIBLE = 0
    TEXT_DATA = 1
    OVERRIDDEN_SYMBOL_ID = 2
    INHERIT_FILL_STYLE_ID = 3


@dataclasses.dataclass
class ComponentPropAssignment:
    defID: typing.Optional['GUID'] = None
    value: typing.Optional['ComponentPropValue'] = None


@dataclasses.dataclass
class ComponentPropDef:
    id: typing.Optional['GUID'] = None
    name: typing.Optional[str] = None
    initialValue: typing.Optional['ComponentPropValue'] = None
    sortPosition: typing.Optional[str] = None
    parentPropDefId: typing.Optional['GUID'] = None
    type: typing.Optional['ComponentPropType'] = None
    isDeleted: typing.Optional[bool] = None
    preferredValues: typing.Optional['ComponentPropPreferredValues'] = None


@dataclasses.dataclass
class ComponentPropValue:
    boolValue: typing.Optional[bool] = None
    textValue: typing.Optional['TextData'] = None
    guidValue: typing.Optional['GUID'] = None


class ComponentPropType(enum.Enum):
    BOOL = 0
    TEXT = 1
    COLOR = 2
    INSTANCE_SWAP = 3


@dataclasses.dataclass
class ComponentPropPreferredValues:
    stringValues: typing.Optional[list[str]] = None
    instanceSwapValues: typing.Optional[list['InstanceSwapPreferredValue']] = None


@dataclasses.dataclass
class InstanceSwapPreferredValue:
    type: typing.Optional['InstanceSwapPreferredValueType'] = None
    key: typing.Optional[str] = None


class InstanceSwapPreferredValueType(enum.Enum):
    COMPONENT = 0
    STATE_GROUP = 1


class WidgetEvent(enum.Enum):
    MOUSE_DOWN = 0
    CLICK = 1
    TEXT_EDIT_END = 2
    ATTACHED_STICKABLES_CHANGED = 3
    STUCK_STATUS_CHANGED = 4


class WidgetInputBehavior(enum.Enum):
    WRAP = 0
    TRUNCATE = 1
    MULTILINE = 2


@dataclasses.dataclass
class WidgetMetadata:
    pluginID: typing.Optional[str] = None
    pluginVersionID: typing.Optional[str] = None
    widgetName: typing.Optional[str] = None


class WidgetPropertyMenuItemType(enum.Enum):
    ACTION = 0
    SEPARATOR = 1
    COLOR = 2
    DROPDOWN = 3
    COLOR_SELECTOR = 4
    TOGGLE = 5
    LINK = 6


@dataclasses.dataclass
class WidgetPropertyMenuSelectorOption:
    option: typing.Optional[str] = None
    tooltip: typing.Optional[str] = None


@dataclasses.dataclass
class WidgetPropertyMenuItem:
    propertyName: typing.Optional[str] = None
    tooltip: typing.Optional[str] = None
    itemType: typing.Optional['WidgetPropertyMenuItemType'] = None
    icon: typing.Optional[str] = None
    options: typing.Optional[list['WidgetPropertyMenuSelectorOption']] = None
    selectedOption: typing.Optional[str] = None
    isToggled: typing.Optional[bool] = None
    href: typing.Optional[str] = None
    allowCustomColor: typing.Optional[bool] = None


class CodeBlockLanguage(enum.Enum):
    TYPESCRIPT = 0
    CPP = 1
    RUBY = 2
    CSS = 3
    JAVASCRIPT = 4
    HTML = 5
    JSON = 6
    GRAPHQL = 7
    PYTHON = 8
    GO = 9
    SQL = 10
    SWIFT = 11
    KOTLIN = 12
    RUST = 13
    BASH = 14
    PLAINTEXT = 15


class InternalEnumForTest(enum.Enum):
    OLD = 1


@dataclasses.dataclass
class InternalDataForTest:
    testFieldA: typing.Optional[int] = None


@dataclasses.dataclass
class StateGroupPropertyValueOrder:
    property: typing.Optional[str] = None
    values: typing.Optional[list[str]] = None


@dataclasses.dataclass
class TextListData:
    listID: typing.Optional[int] = None
    bulletType: typing.Optional['BulletType'] = None
    indentationLevel: typing.Optional[int] = None
    lineNumber: typing.Optional[int] = None


class BulletType(enum.Enum):
    ORDERED = 0
    UNORDERED = 1
    INDENT = 2
    NO_LIST = 3


@dataclasses.dataclass
class TextLineData:
    lineType: typing.Optional['LineType'] = None
    indentationLevel: typing.Optional[int] = None
    sourceDirectionality: typing.Optional['SourceDirectionality'] = None
    directionality: typing.Optional['Directionality'] = None
    directionalityIntent: typing.Optional['DirectionalityIntent'] = None
    downgradeStyleId: typing.Optional[int] = None
    consistencyStyleId: typing.Optional[int] = None
    listStartOffset: typing.Optional[int] = None
    isFirstLineOfList: typing.Optional[bool] = None


@dataclasses.dataclass
class DerivedTextLineData:
    directionality: typing.Optional['Directionality'] = None


class LineType(enum.Enum):
    PLAIN = 0
    ORDERED_LIST = 1
    UNORDERED_LIST = 2
    BLOCKQUOTE = 3
    HEADER = 4


class SourceDirectionality(enum.Enum):
    AUTO = 0
    LTR = 1
    RTL = 2


class Directionality(enum.Enum):
    LTR = 0
    RTL = 1


class DirectionalityIntent(enum.Enum):
    IMPLICIT = 0
    EXPLICIT = 1


@dataclasses.dataclass
class PrototypeInteraction:
    id: typing.Optional['GUID'] = None
    event: typing.Optional['PrototypeEvent'] = None
    actions: typing.Optional[list['PrototypeAction']] = None
    isDeleted: typing.Optional[bool] = None
    stateManagementVersion: typing.Optional[int] = None


@dataclasses.dataclass
class PrototypeEvent:
    interactionType: typing.Optional['InteractionType'] = None
    interactionMaintained: typing.Optional[bool] = None
    interactionDuration: typing.Optional[float] = None
    keyTrigger: typing.Optional['KeyTrigger'] = None
    voiceEventPhrase: typing.Optional[str] = None
    transitionTimeout: typing.Optional[float] = None
    mediaHitTime: typing.Optional[float] = None


@dataclasses.dataclass
class PrototypeVariableTarget:
    id: typing.Optional['VariableID'] = None


@dataclasses.dataclass
class ConditionalActions:
    actions: typing.Optional[list['PrototypeAction']] = None
    condition: typing.Optional['VariableData'] = None


@dataclasses.dataclass
class PrototypeAction:
    transitionNodeID: typing.Optional['GUID'] = None
    transitionType: typing.Optional['TransitionType'] = None
    transitionDuration: typing.Optional[float] = None
    easingType: typing.Optional['EasingType'] = None
    transitionTimeout: typing.Optional[float] = None
    transitionShouldSmartAnimate: typing.Optional[bool] = None
    connectionType: typing.Optional['ConnectionType'] = None
    connectionURL: typing.Optional[str] = None
    overlayRelativePosition: typing.Optional['Vector'] = None
    navigationType: typing.Optional['NavigationType'] = None
    transitionPreserveScroll: typing.Optional[bool] = None
    easingFunction: typing.Optional[list[float]] = None
    extraScrollOffset: typing.Optional['Vector'] = None
    targetVariableID: typing.Optional['GUID'] = None
    targetVariableValue: typing.Optional['VariableAnyValue'] = None
    mediaAction: typing.Optional['MediaAction'] = None
    transitionResetVideoPosition: typing.Optional[bool] = None
    openUrlInNewTab: typing.Optional[bool] = None
    targetVariable: typing.Optional['PrototypeVariableTarget'] = None
    targetVariableData: typing.Optional['VariableData'] = None
    mediaSkipToTime: typing.Optional[float] = None
    mediaSkipByAmount: typing.Optional[float] = None
    conditions: typing.Optional[list['VariableData']] = None
    conditionalActions: typing.Optional[list['ConditionalActions']] = None
    transitionResetScrollPosition: typing.Optional[bool] = None
    transitionResetInteractiveComponents: typing.Optional[bool] = None


@dataclasses.dataclass
class PrototypeStartingPoint:
    name: typing.Optional[str] = None
    description: typing.Optional[str] = None
    position: typing.Optional[str] = None


class TriggerDevice(enum.Enum):
    KEYBOARD = 0
    UNKNOWN_CONTROLLER = 1
    XBOX_ONE = 2
    PS4 = 3
    SWITCH_PRO = 4


@dataclasses.dataclass
class KeyTrigger:
    keyCodes: typing.Optional[list[int]] = None
    triggerDevice: typing.Optional['TriggerDevice'] = None


@dataclasses.dataclass
class Hyperlink:
    url: typing.Optional[str] = None
    guid: typing.Optional['GUID'] = None


class MentionSource(enum.Enum):
    DEFAULT = 0
    COPY_DUPLICATE = 1


@dataclasses.dataclass
class Mention:
    id: typing.Optional['GUID'] = None
    mentionedUserId: typing.Optional[str] = None
    mentionedByUserId: typing.Optional[str] = None
    fileKey: typing.Optional[str] = None
    source: typing.Optional['MentionSource'] = None
    mentionedUserIdInt: typing.Optional['ChildReadingDirection'] = None
    mentionedByUserIdInt: typing.Optional['ChildReadingDirection'] = None


@dataclasses.dataclass
class EmbedData:
    url: typing.Optional[str] = None
    srcUrl: typing.Optional[str] = None
    title: typing.Optional[str] = None
    thumbnailUrl: typing.Optional[str] = None
    width: typing.Optional[float] = None
    height: typing.Optional[float] = None
    embedType: typing.Optional[str] = None
    thumbnailImageHash: typing.Optional[str] = None
    faviconImageHash: typing.Optional[str] = None
    provider: typing.Optional[str] = None
    originalText: typing.Optional[str] = None
    description: typing.Optional[str] = None
    embedVersionId: typing.Optional[str] = None


@dataclasses.dataclass
class StampData:
    userId: typing.Optional[str] = None
    votingSessionId: typing.Optional[str] = None
    stampedByUserId: typing.Optional[str] = None


@dataclasses.dataclass
class LinkPreviewData:
    url: typing.Optional[str] = None
    title: typing.Optional[str] = None
    provider: typing.Optional[str] = None
    description: typing.Optional[str] = None
    thumbnailImageHash: typing.Optional[str] = None
    faviconImageHash: typing.Optional[str] = None
    thumbnailImageWidth: typing.Optional[float] = None
    thumbnailImageHeight: typing.Optional[float] = None


@dataclasses.dataclass
class Viewport:
    canvasSpaceBounds: typing.Optional['Rect'] = None
    pixelPreview: typing.Optional[bool] = None
    pixelDensity: typing.Optional[float] = None
    canvasGuid: typing.Optional['GUID'] = None


@dataclasses.dataclass
class Mouse:
    cursor: typing.Optional['MouseCursor'] = None
    canvasSpaceLocation: typing.Optional['Vector'] = None
    canvasSpaceSelectionBox: typing.Optional['Rect'] = None
    canvasGuid: typing.Optional['GUID'] = None
    cursorHiddenReason: typing.Optional[uint] = None


@dataclasses.dataclass(slots=True)
class Click:
    id: uint
    point: 'Vector'


@dataclasses.dataclass(slots=True)
class ScrollPosition:
    node: 'GUID'
    scrollOffset: 'Vector'


@dataclasses.dataclass(slots=True)
class TriggeredOverlay:
    overlayGuid: 'GUID'
    hotspotGuid: 'GUID'
    swapGuid: 'GUID'


@dataclasses.dataclass
class TriggeredOverlayData:
    overlayGuid: typing.Optional['GUID'] = None
    hotspotGuid: typing.Optional['GUID'] = None
    swapGuid: typing.Optional['GUID'] = None
    prototypeInteractionGuid: typing.Optional['GUID'] = None
    hotspotBlueprintId: typing.Optional['GUIDPath'] = None


@dataclasses.dataclass
class PresentedState:
    baseScreenID: typing.Optional['GUID'] = None
    overlays: typing.Optional[list['TriggeredOverlayData']] = None


class TransitionDirection(enum.Enum):
    FORWARD = 0
    REVERSE = 1


@dataclasses.dataclass
class TopLevelPlaybackChange:
    oldState: typing.Optional['PresentedState'] = None
    newState: typing.Optional['PresentedState'] = None
    hotspotBlueprintID: typing.Optional['GUIDPath'] = None
    interactionID: typing.Optional['GUID'] = None
    isHotspotInNewPresentedState: typing.Optional[bool] = None
    direction: typing.Optional['TransitionDirection'] = None
    instanceStablePath: typing.Optional['GUIDPath'] = None


@dataclasses.dataclass
class InstanceStateChange:
    stateID: typing.Optional['GUID'] = None
    interactionID: typing.Optional['GUID'] = None
    hotspotStablePath: typing.Optional['GUIDPath'] = None
    instanceStablePath: typing.Optional['GUIDPath'] = None
    phase: typing.Optional['PlaybackChangePhase'] = None


@dataclasses.dataclass
class TextCursor:
    selectionBox: typing.Optional['Rect'] = None
    canvasGuid: typing.Optional['GUID'] = None
    textNodeGuid: typing.Optional['GUID'] = None


@dataclasses.dataclass
class TextSelection:
    selectionBoxes: typing.Optional[list['Rect']] = None
    canvasGuid: typing.Optional['GUID'] = None
    textNodeGuid: typing.Optional['GUID'] = None
    textSelectionRange: typing.Optional['Vector'] = None
    textNodeOrContainingIfGuid: typing.Optional['GUID'] = None
    tableCellRowId: typing.Optional['GUID'] = None
    tableCellColId: typing.Optional['GUID'] = None


class PlaybackChangePhase(enum.Enum):
    INITIATED = 0
    ABORTED = 1
    COMMITTED = 2


@dataclasses.dataclass
class PlaybackChangeKeyframe:
    phase: typing.Optional['PlaybackChangePhase'] = None
    progress: typing.Optional[float] = None
    timestamp: typing.Optional[float] = None


@dataclasses.dataclass
class StateMapping:
    stablePath: typing.Optional['GUIDPath'] = None
    lastTopLevelChange: typing.Optional['TopLevelPlaybackChange'] = None
    lastTopLevelChangeStatus: typing.Optional['PlaybackChangeKeyframe'] = None
    timestamp: typing.Optional[float] = None


@dataclasses.dataclass
class ScrollMapping:
    blueprintID: typing.Optional['GUIDPath'] = None
    overlayIndex: typing.Optional[uint] = None
    scrollOffset: typing.Optional['Vector'] = None


@dataclasses.dataclass
class PlaybackUpdate:
    lastTopLevelChange: typing.Optional['TopLevelPlaybackChange'] = None
    lastTopLevelChangeStatus: typing.Optional['PlaybackChangeKeyframe'] = None
    scrollMappings: typing.Optional[list['ScrollMapping']] = None
    timestamp: typing.Optional[float] = None
    pointerLocation: typing.Optional['Vector'] = None
    isTopLevelFrameChange: typing.Optional[bool] = None
    stateMappings: typing.Optional[list['StateMapping']] = None


@dataclasses.dataclass
class ChatMessage:
    text: typing.Optional[str] = None
    previousText: typing.Optional[str] = None


@dataclasses.dataclass
class VoiceMetadata:
    connectedCallId: typing.Optional[str] = None


class Heartbeat(enum.Enum):
    FOREGROUND = 0
    BACKGROUND = 1


@dataclasses.dataclass
class UserChange:
    sessionID: typing.Optional[uint] = None
    connected: typing.Optional[bool] = None
    name: typing.Optional[str] = None
    color: typing.Optional['Color'] = None
    imageURL: typing.Optional[str] = None
    viewport: typing.Optional['Viewport'] = None
    mouse: typing.Optional['Mouse'] = None
    selection: typing.Optional[list['GUID']] = None
    observing: typing.Optional[list[uint]] = None
    deviceName: typing.Optional[str] = None
    recentClicks: typing.Optional[list['Click']] = None
    scrollPositions: typing.Optional[list['ScrollPosition']] = None
    triggeredOverlays: typing.Optional[list['TriggeredOverlay']] = None
    userID: typing.Optional[str] = None
    lastTriggeredHotspot: typing.Optional['GUID'] = None
    lastTriggeredPrototypeInteractionID: typing.Optional['GUID'] = None
    triggeredOverlaysData: typing.Optional[list['TriggeredOverlayData']] = None
    playbackUpdates: typing.Optional[list['PlaybackUpdate']] = None
    chatMessage: typing.Optional['ChatMessage'] = None
    voiceMetadata: typing.Optional['VoiceMetadata'] = None
    canWrite: typing.Optional[bool] = None
    highFiveStatus: typing.Optional[bool] = None
    instanceStateChanges: typing.Optional[list['InstanceStateChange']] = None
    textCursor: typing.Optional['TextCursor'] = None
    textSelection: typing.Optional['TextSelection'] = None
    connectedAtTimeS: typing.Optional[uint] = None
    focusOnTextCursor: typing.Optional[bool] = None
    heartbeat: typing.Optional['Heartbeat'] = None


@dataclasses.dataclass
class SceneGraphQuery:
    startingNode: typing.Optional['GUID'] = None
    depth: typing.Optional[uint] = None


@dataclasses.dataclass
class NodeChangesMetadata:
    blobsFieldOffset: typing.Optional[uint] = None


@dataclasses.dataclass
class CursorReaction:
    imageUrl: typing.Optional[str] = None


@dataclasses.dataclass
class TimerInfo:
    isPaused: typing.Optional[bool] = None
    timeRemainingMs: typing.Optional[uint] = None
    totalTimeMs: typing.Optional[uint] = None
    timerID: typing.Optional[uint] = None
    setBy: typing.Optional[str] = None
    songID: typing.Optional[uint] = None
    lastReceivedSongTimestampMs: typing.Optional[uint] = None
    songUUID: typing.Optional[str] = None


@dataclasses.dataclass
class MusicInfo:
    isPaused: typing.Optional[bool] = None
    messageID: typing.Optional[uint] = None
    songID: typing.Optional[str] = None
    lastReceivedSongTimestampMs: typing.Optional[uint] = None
    isStopped: typing.Optional[bool] = None


@dataclasses.dataclass
class PresenterNomination:
    sessionID: typing.Optional[uint] = None
    isCancelled: typing.Optional[bool] = None


@dataclasses.dataclass
class PresenterInfo:
    sessionID: typing.Optional[uint] = None
    nomination: typing.Optional['PresenterNomination'] = None


@dataclasses.dataclass
class ClientBroadcast:
    sessionID: typing.Optional[uint] = None
    cursorReaction: typing.Optional['CursorReaction'] = None
    timer: typing.Optional['TimerInfo'] = None
    presenter: typing.Optional['PresenterInfo'] = None
    prototypePresenter: typing.Optional['PresenterInfo'] = None
    music: typing.Optional['MusicInfo'] = None


@dataclasses.dataclass
class Message:
    type: typing.Optional['MessageType'] = None
    sessionID: typing.Optional[uint] = None
    ackID: typing.Optional[uint] = None
    nodeChanges: typing.Optional[list['NodeChange']] = None
    userChanges: typing.Optional[list['UserChange']] = None
    blobs: typing.Optional[list['Blob']] = None
    blobBaseIndex: typing.Optional[uint] = None
    signalName: typing.Optional[str] = None
    access: typing.Optional['Access'] = None
    styleSetName: typing.Optional[str] = None
    styleSetType: typing.Optional['StyleSetType'] = None
    styleSetContentType: typing.Optional['StyleSetContentType'] = None
    pasteID: typing.Optional[int] = None
    pasteOffset: typing.Optional['Vector'] = None
    pasteFileKey: typing.Optional[str] = None
    signalPayload: typing.Optional[str] = None
    sceneGraphQueries: typing.Optional[list['SceneGraphQuery']] = None
    nodeChangesMetadata: typing.Optional['NodeChangesMetadata'] = None
    fileVersion: typing.Optional[uint] = None
    pasteIsPartiallyOutsideEnclosingFrame: typing.Optional[bool] = None
    pastePageId: typing.Optional['GUID'] = None
    isCut: typing.Optional[bool] = None
    localUndoStack: typing.Optional[list['Message']] = None
    localRedoStack: typing.Optional[list['Message']] = None
    broadcasts: typing.Optional[list['ClientBroadcast']] = None
    reconnectSequenceNumber: typing.Optional[uint] = None
    pasteBranchSourceFileKey: typing.Optional[str] = None
    pasteEditorType: typing.Optional['EditorType'] = None
    postSyncActions: typing.Optional[str] = None
    publishedAssetGuids: typing.Optional[list['GUID']] = None
    dirtyFromInitialLoad: typing.Optional[bool] = None


@dataclasses.dataclass
class DiffChunk:
    nodeChanges: typing.Optional[list[uint]] = None
    phase: typing.Optional['NodePhase'] = None
    displayNode: typing.Optional['NodeChange'] = None
    canvasId: typing.Optional['GUID'] = None
    canvasName: typing.Optional[str] = None
    canvasIsInternal: typing.Optional[bool] = None
    chunksAffectingThisChunk: typing.Optional[list[uint]] = None
    basisParentHierarchy: typing.Optional[list['NodeChange']] = None
    parentHierarchy: typing.Optional[list['NodeChange']] = None
    basisParentHierarchyGuids: typing.Optional[list['GUID']] = None
    parentHierarchyGuids: typing.Optional[list['GUID']] = None


@dataclasses.dataclass
class DiffPayload:
    nodeChanges: typing.Optional[list['NodeChange']] = None
    blobs: typing.Optional[list['Blob']] = None
    diffChunks: typing.Optional[list['DiffChunk']] = None
    diffBasis: typing.Optional[list['NodeChange']] = None
    basisParentNodeChanges: typing.Optional[list['NodeChange']] = None
    parentNodeChanges: typing.Optional[list['NodeChange']] = None


class RichMediaType(enum.Enum):
    ANIMATED_IMAGE = 0
    VIDEO = 1


@dataclasses.dataclass
class RichMediaData:
    mediaHash: typing.Optional[str] = None
    richMediaType: typing.Optional['RichMediaType'] = None


class VariableDataType(enum.Enum):
    BOOLEAN = 0
    FLOAT = 1
    STRING = 2
    ALIAS = 3
    COLOR = 4
    EXPRESSION = 5
    MAP = 6
    SYMBOL_ID = 7


class VariableResolvedDataType(enum.Enum):
    BOOLEAN = 0
    FLOAT = 1
    STRING = 2
    COLOR = 4
    MAP = 5
    SYMBOL_ID = 6


@dataclasses.dataclass
class VariableAnyValue:
    boolValue: typing.Optional[bool] = None
    textValue: typing.Optional[str] = None
    floatValue: typing.Optional[float] = None
    alias: typing.Optional['VariableID'] = None
    colorValue: typing.Optional['Color'] = None
    expressionValue: typing.Optional['Expression'] = None
    mapValue: typing.Optional['VariableMap'] = None
    symbolIdValue: typing.Optional['SymbolId'] = None


class ExpressionFunction(enum.Enum):
    ADDITION = 0
    SUBTRACTION = 1
    RESOLVE_VARIANT = 2
    MULTIPLY = 3
    DIVIDE = 4
    EQUALS = 5
    NOT_EQUAL = 6
    LESS_THAN = 7
    LESS_THAN_OR_EQUAL = 8
    GREATER_THAN = 9
    GREATER_THAN_OR_EQUAL = 10
    AND = 11
    OR = 12
    NOT = 13
    STRINGIFY = 14
    TERNARY = 15
    VAR_MODE_LOOKUP = 16


@dataclasses.dataclass
class Expression:
    expressionFunction: typing.Optional['ExpressionFunction'] = None
    expressionArguments: typing.Optional[list['VariableData']] = None


@dataclasses.dataclass
class VariableMapValue:
    key: typing.Optional[str] = None
    value: typing.Optional['VariableData'] = None


@dataclasses.dataclass
class VariableMap:
    values: typing.Optional[list['VariableMapValue']] = None


@dataclasses.dataclass
class VariableData:
    value: typing.Optional['VariableAnyValue'] = None
    dataType: typing.Optional['VariableDataType'] = None
    resolvedDataType: typing.Optional['VariableResolvedDataType'] = None


@dataclasses.dataclass
class VariableSetMode:
    id: typing.Optional['GUID'] = None
    name: typing.Optional[str] = None
    sortPosition: typing.Optional[str] = None


@dataclasses.dataclass
class VariableDataValues:
    entries: typing.Optional[list['VariableDataValuesEntry']] = None


@dataclasses.dataclass
class VariableDataValuesEntry:
    modeID: typing.Optional['GUID'] = None
    variableData: typing.Optional['VariableData'] = None


class VariableScope(enum.Enum):
    ALL_SCOPES = 0
    TEXT_CONTENT = 1
    CORNER_RADIUS = 2
    WIDTH_HEIGHT = 3
    GAP = 4
    ALL_FILLS = 5
    FRAME_FILL = 6
    SHAPE_FILL = 7
    TEXT_FILL = 8
    STROKE = 9


class CodeSyntaxPlatform(enum.Enum):
    WEB = 0
    ANDROID = 1
    iOS = 2


@dataclasses.dataclass
class OptionalVector:
    value: typing.Optional['Vector'] = None


class HTMLTag(enum.Enum):
    AUTO = 0
    ARTICLE = 1
    SECTION = 2
    NAV = 3
    ASIDE = 4
    H1 = 5
    H2 = 6
    H3 = 7
    H4 = 8
    H5 = 9
    H6 = 10
    HGROUP = 11
    HEADER = 12
    FOOTER = 13
    ADDRESS = 14
    P = 15
    HR = 16
    PRE = 17
    BLOCKQUOTE = 18
    OL = 19
    UL = 20
    MENU = 21
    LI = 22
    DL = 23
    DT = 24
    DD = 25
    FIGURE = 26
    FIGCAPTION = 27
    MAIN = 28
    DIV = 29
    A = 30
    EM = 31
    STRONG = 32
    SMALL = 33
    S = 34
    CITE = 35
    Q = 36
    DFN = 37
    ABBR = 38
    RUBY = 39
    RT = 40
    RP = 41
    DATA = 42
    TIME = 43
    CODE = 44
    VAR = 45
    SAMP = 46
    KBD = 47
    SUB = 48
    SUP = 49
    I = 50
    B = 51
    U = 52
    MARK = 53
    BDI = 54
    BDO = 55
    SPAN = 56
    BR = 57
    WBR = 58
    PICTURE = 59
    SOURCE = 60
    IMG = 61
    FORM = 62
    LABEL = 63
    INPUT = 64
    BUTTON = 65
    SELECT = 66
    DATALIST = 67
    OPTGROUP = 68
    OPTION = 69
    TEXTAREA = 70
    OUTPUT = 71
    PROGRESS = 72
    METER = 73
    FIELDSET = 74
    LEGEND = 75


class ARIARole(enum.Enum):
    AUTO = 0
    NONE = 52
    APPLICATION = 30
    BANNER = 67
    COMPLEMENTARY = 68
    CONTENTINFO = 69
    FORM = 70
    MAIN = 71
    NAVIGATION = 72
    REGION = 73
    SEARCH = 74
    SEPARATOR = 13
    ARTICLE = 31
    COLUMNHEADER = 35
    DEFINITION = 36
    DIRECTORY = 38
    DOCUMENT = 39
    GROUP = 44
    HEADING = 45
    IMG = 46
    LIST = 48
    LISTITEM = 49
    MATH = 50
    NOTE = 53
    PRESENTATION = 55
    ROW = 56
    ROWGROUP = 57
    ROWHEADER = 58
    TABLE = 62
    TOOLBAR = 65
    BUTTON = 1
    CHECKBOX = 2
    GRIDCELL = 3
    LINK = 4
    MENUITEM = 5
    MENUITEMCHECKBOX = 6
    MENUITEMRADIO = 7
    OPTION = 8
    PROGRESSBAR = 9
    RADIO = 10
    SCROLLBAR = 11
    SLIDER = 14
    SPINBUTTON = 15
    TAB = 17
    TABPANEL = 18
    TEXTBOX = 19
    TREEITEM = 20
    COMBOBOX = 21
    GRID = 22
    LISTBOX = 23
    MENU = 24
    MENUBAR = 25
    RADIOGROUP = 26
    TABLIST = 27
    TREE = 28
    TREEGRID = 29
    TOOLTIP = 66
    ALERT = 75
    LOG = 76
    MARQUEE = 77
    STATUS = 78
    TIMER = 79
    ALERTDIALOG = 80
    DIALOG = 81
    SEARCHBOX = 12
    SWITCH = 16
    BLOCKQUOTE = 32
    CAPTION = 33
    CELL = 34
    DELETION = 37
    EMPHASIS = 40
    FEED = 41
    FIGURE = 42
    GENERIC = 43
    INSERTION = 47
    METER = 51
    PARAGRAPH = 54
    STRONG = 59
    SUBSCRIPT = 60
    SUPERSCRIPT = 61
    TERM = 63
    TIME = 64
    IMAGE = 82
    HEADING_1 = 83
    HEADING_2 = 84
    HEADING_3 = 85
    HEADING_4 = 86
    HEADING_5 = 87
    HEADING_6 = 88
    HEADER = 89
    FOOTER = 90
    SIDEBAR = 91
    SECTION = 92
    MAINCONTENT = 93
    TABLE_CELL = 94
    WIDGET = 95


@dataclasses.dataclass
class MigrationStatus:
    dsdCleanup: typing.Optional[bool] = None


@dataclasses.dataclass
class NodeFieldMap:
    entries: typing.Optional[list['NodeFieldMapEntry']] = None


@dataclasses.dataclass
class NodeFieldMapEntry:
    guid: typing.Optional['GUID'] = None
    field: typing.Optional[uint] = None
    lastModifiedSequenceNumber: typing.Optional[uint] = None


class ColorProfile(enum.Enum):
    SRGB = 0
    DISPLAY_P3 = 1


class DocumentColorProfile(enum.Enum):
    LEGACY = 0
    SRGB = 1
    DISPLAY_P3 = 2


class ChildReadingDirection(enum.Enum):
    NONE = 0
    LEFT_TO_RIGHT = 1
    RIGHT_TO_LEFT = 2


@dataclasses.dataclass
class ARIAAttributeAnyValue:
    boolValue: typing.Optional[bool] = None
    stringValue: typing.Optional[str] = None
    floatValue: typing.Optional[float] = None
    intValue: typing.Optional[int] = None
    stringArrayValue: typing.Optional[list[str]] = None


class ARIAAttributeDataType(enum.Enum):
    BOOLEAN = 0
    STRING = 1
    FLOAT = 2
    INT = 3
    STRING_LIST = 4


@dataclasses.dataclass
class ARIAAttributeData:
    type: typing.Optional['ARIAAttributeDataType'] = None
    value: typing.Optional['ARIAAttributeAnyValue'] = None


@dataclasses.dataclass
class ARIAAttributesMap:
    entries: typing.Optional[list['ARIAAttributesMapEntry']] = None


@dataclasses.dataclass
class ARIAAttributesMapEntry:
    attribute: typing.Optional[str] = None
    value: typing.Optional['ARIAAttributeData'] = None


@dataclasses.dataclass
class HandoffStatusMapEntry:
    guid: typing.Optional['GUID'] = None
    handoffStatus: typing.Optional['SectionStatusInfo'] = None


@dataclasses.dataclass
class HandoffStatusMap:
    entries: typing.Optional[list['HandoffStatusMapEntry']] = None

