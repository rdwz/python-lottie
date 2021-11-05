import re
import sys
import enum
import math
import typing
import dataclasses

from ..parsers.svg.svgdata import color_table
from ..objects.animation import Animation
from ..objects import layers
from ..objects import shapes
from ..nvector import NVector


color_words = {
    "alice": {"blue": {"_": 1}},
    "antique": {"white": {"_": 1}},
    "aqua": {
        "_": 1,
        "marine": {"_": 1}
    },
    "azure": {"_": 1},
    "beige": {"_": 1},
    "bisque": {"_": 1},
    "black": {"_": 1},
    "blanched": {"almond": {"_": 1}},
    "blue": {
        "_": 1,
        "navy": "navy",
        "violet": {"_": 1},
    },
    "brown": {"_": 1},
    "burly": {"wood": {"_": 1}},
    "cadet": {"blue": {"_": 1}},
    "chartreuse": {"_": 1},
    "chocolate": {"_": 1},
    "coral": {"_": 1},
    "cornflower": {"blue": {"_": 1}},
    "corn": {
        "silk": {"_": 1},
        "flower": {"blue": {"_": 1}},
    },
    "crimson": {"_": 1},
    "cyan": {"_": 1},
    "dark": {
        "blue": {"_": 1},
        "cyan": {"_": 1},
        "golden": {"rod": {"_": 1}},
        "gray": {"_": 1},
        "green": {"_": 1},
        "grey": {"_": 1},
        "khaki": {"_": 1},
        "magenta": {"_": 1},
        "olive": {"green": {"_": 1}},
        "orange": {"_": 1},
        "orchid": {"_": 1},
        "red": {"_": 1},
        "salmon": {"_": 1},
        "sea": {"green": {"_": 1}},
        "slate": {
            "blue": {"_": 1},
            "gray": {"_": 1},
            "grey": {"_": 1}
        },
        "turquoise": {"_": 1},
        "violet": {"_": 1}
    },
    "deep": {
        "pink": {"_": 1},
        "sky": {"blue": {"_": 1}},
    },
    "dim": {
        "gray": {"_": 1},
        "grey": {"_": 1}
    },
    "dodger": {"blue": {"_": 1}},
    "fire": {"brick": {"_": 1}},
    "floral": {"white": {"_": 1}},
    "forest": {"green": {"_": 1}},
    "fuchsia": {"_": 1},
    "gainsboro": {"_": 1},
    "ghost": {"white": {"_": 1}},
    "gold": {"_": 1},
    "golden": {"rod": {"_": 1}},
    "gray": {"_": 1},
    "green": {"_": 1},
    "green": {"yellow": {"_": 1}},
    "grey": {"_": 1},
    "honeydew": {"_": 1},
    "hotpink": {"_": 1},
    "indian": {"red": {"_": 1}},
    "indigo": {"_": 1},
    "ivory": {"_": 1},
    "khaki": {"_": 1},
    "lavender":  {
        "_": 1,
        "blush": {"_": 1},
    },
    "lawn": {"green": {"_": 1}},
    "lemon": {"chiffon": {"_": 1}},
    "light": {
        "blue": {"_": 1},
        "coral": {"_": 1},
        "cyan": {"_": 1},
        "golden": {
            "rod": {
                "_": 1,
                "yellow": {"_": 1},
            }
        },
        "gray": {"_": 1},
        "green": {"_": 1},
        "grey": {"_": 1},
        "pink": {"_": 1},
        "salmon": {"_": 1},
        "sea": {"green": {"_": 1}},
        "sky": {"blue": {"_": 1}},
        "slate": {
            "gray": {"_": 1},
            "grey": {"_": 1}
        },
        "steel": {"blue": {"_": 1}},
        "yellow": {"_": 1},
    },
    "lime": {
        "_": 1,
        "green": {"_": 1},
    },
    "linen": {"_": 1},
    "magenta": {"_": 1},
    "maroon": {"_": 1},
    "medium": {
        "aquamarine": {"_": 1},
        "blue": {"_": 1},
        "orchid": {"_": 1},
        "purple": {"_": 1},
        "sea": {"green": {"_": 1}},
        "slate": {"blue": {"_": 1}},
        "spring": {"green": {"_": 1}},
        "turquoise": {"_": 1},
        "violet": {"red": {"_": 1}},
    },
    "midnight": {"blue": {"_": 1}},
    "mint": {"cream": {"_": 1}},
    "misty": {"rose": {"_": 1}},
    "moccasin": {"_": 1},
    "navajo": {"white": {"_": 1}},
    "navy": {
        "_": 1,
        "blue": "navy",
    },
    "old": {"lace": {"_": 1}},
    "olive": {
        "_": 1,
        "drab": {"_": 1},
    },
    "orange": {
        "_": 1,
        "red": {"_": 1},
    },
    "orchid": {"_": 1},
    "pale": {
        "golden": {"rod": {"_": 1}},
        "green": {"_": 1},
        "turquoise": {"_": 1},
        "violet": {"red": {"_": 1}},
    },
    "papaya": {"whip": {"_": 1}},
    "peach": {"puff": {"_": 1}},
    "peru": {"_": 1},
    "pink": {"_": 1},
    "plum": {"_": 1},
    "powder": {"blue": {"_": 1}},
    "purple": {"_": 1},
    "red": {"_": 1},
    "rosy": {"brown": {"_": 1}},
    "royal": {"blue": {"_": 1}},
    "saddle": {"brown": {"_": 1}},
    "salmon": {"_": 1},
    "sandy": {"brown": {"_": 1}},
    "sea": {
        "green": {"_": 1},
        "shell": {"_": 1},
    },
    "seashell": {"_": 1},
    "sienna": {"_": 1},
    "silver": {"_": 1},
    "sky": {"blue": {"_": 1}},
    "slate": {
        "blue": {"_": 1},
        "gray": {"_": 1},
        "grey": {"_": 1},
    },
    "snow": {"_": 1},
    "spring": {"green": {"_": 1}},
    "steel": {"blue": {"_": 1}},
    "tan": {"_": 1},
    "teal": {"_": 1},
    "thistle": {"_": 1},
    "tomato": {"_": 1},
    "turquoise": {"_": 1},
    "violet": {"_": 1},
    "wheat": {"_": 1},
    "white": {
        "_": 1,
        "smoke": {"_": 1},
    },
    "yellow": {
        "_": 1,
        "green": {"_": 1},
    },
}


class TokenType(enum.Enum):
    Word = enum.auto()
    Number = enum.auto()
    Eof = enum.auto()
    String = enum.auto()
    Separator = enum.auto()


@dataclasses.dataclass
class Token:
    type: TokenType
    line: int
    col: int
    start: int
    end: int
    value: typing.Any = None

    def __repr__(self):
        if self.type == TokenType.Eof:
            return "End of file"
        return repr(self.value)


class ShapeData:
    def __init__(self, extent):
        self.color = [0, 0, 0]
        self.extent = extent
        self.portrait = False
        self.roundness = 0
        self.opacity = 1
        self.count = 1


class Lexer:
    expression = re.compile(
        r'[\r\t ]*(?P<token>(?P<punc>[:,;.])|(?P<word>[a-zA-Z\']+)|(?P<number>-?[0-9]+(?P<fraction>\.[0-9]+)?)|(?P<string>"(?:[^"\\]|\\["\\nbt])+"))[\r\t ]*'
    )

    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.queue = []
        self.token = None
        self.line = 1
        self.line_pos = 0

    def next(self):
        if self.queue:
            self.token = self.queue.pop(0)
            return self.token

        while True:
            if self.pos >= len(self.text):
                self.token = Token(TokenType.Eof, self.line, self.pos - self.line_pos, self.pos, self.pos)
                return self.token

            if self.text[self.pos] == '\n':
                self.line += 1
                self.pos += 1
                self.line_pos = self.pos
            else:
                match = self.expression.match(self.text, self.pos)
                if match:
                    break

                self.pos += 1

        if match.group("word"):
            type = TokenType.Word
            value = match.group("word").lower()
        elif match.group("number"):
            type = TokenType.Number
            if match.group("fraction"):
                value = float(match.group("number"))
            else:
                value = int(match.group("number"))
        elif match.group("string"):
            type = TokenType.String
            value = match.group("string")[1:-1]
        elif match.group("punc"):
            value = match.group("punc")
            if value == ",":
                type = TokenType.Word
                value = "and"
            elif value == ":":
                self.pos = match.end("token")
                return self.next()
            else:
                type = TokenType.Separator

        self.pos = match.end("token")
        self.token = Token(type, self.line, self.pos - self.line_pos, match.start("token"), self.pos, value)
        return self.token

    def back(self, token=None):
        self.queue.insert(0, token or self.token)


class Logger:
    def warn(self, message):
        sys.stderr.write(message)
        sys.stderr.write("\n")


class DummyLogger(Logger):
    def warn(self, message):
        pass


class StorageLogger(Logger):
    def __init__(self):
        self.messages = []

    def warn(self, message):
        self.messages.append(message)


class Parser:
    sides = {
        "penta": 5,
        "hexa": 6,
        "hepta": 7,
        "octa": 8,
        "ennea": 9,
        "deca": 10,
    }

    def __init__(self, text, logger: Logger):
        self.lexer = Lexer(text)
        self.lexer.next()
        self.logger = logger
        self.allow_resize = True
        self.max_duration = None

    def next(self):
        return self.lexer.next()

    @property
    def token(self):
        return self.lexer.token

    def color(self):
        return self.get_color(color_words, "")

    def get_color_value(self, value, complete_word: str):
        if isinstance(value, str):
            return color_table[value]
        elif isinstance(value, list):
            return value
        else:
            return color_table[complete_word]

    def complete_color(self, word_dict: dict, complete_word: str):
        if "_" in word_dict:
            return self.get_color_value(complete_word)
        else:
            next_item = next(iter(word_dict.item()))
            return self.complete_color(next_item[1], complete_word + next_item[0])

    def get_color(self, word_dict: dict, complete_word: str):
        if self.token.type != TokenType.Word:
            return None

        value = word_dict.get(self.token.value, None)
        if not value:
            return None

        if isinstance(value, dict):
            next_word = complete_word + self.token.value
            self.next()
            color = self.get_color(value, next_word)
            if color is not None:
                return color

            if "_" in value:
                return self.get_color_value(value["_"], next_word)

            self.warn("Incomplete color name")
        else:
            return self.get_color_value(value, complete_word)

    def warn(self, message):
        token = self.token
        self.logger.warn("At line %s column %s, near %r: %s" % (token.line, token.col, token, message))

    def parse(self):
        self.lottie = Animation(180, 60)
        self.article()
        if self.check_words("animation", "composition"):
            self.next()
            self.animation()
        self.layers(self.lottie)
        if self.token.type != TokenType.Eof:
            self.warn("Extra tokens")
        return self.lottie

    def article(self):
        if self.check_words("a", "an", "the"):
            self.next()
            return True
        return False

    def check_words(self, *words):
        if self.token.type != TokenType.Word:
            return False

        return self.token.value in words

    def require_one_of(self, *words):
        if self.check_words(*words):
            return True

        self.warn("Expected " + repr(words[0]))
        return False

    def check_word_sequence(self, words):
        token = self.token
        tokens = []
        for word in words:
            if token.type != TokenType.Word or token.value != word:
                break
            token = self.next()
            tokens.insert(0, token)
        else:
            return True

        self.lexer.queue = tokens + self.lexer.queue
        return False

    def properties(self, object, properties):
        while True:
            self.article()
            if self.check_words(*properties.keys()):
                prop = self.token.value
                self.next()
                if self.check_words("of"):
                    self.next()

                value = properties[prop](getattr(object, prop))
                setattr(object, prop, value)
            else:
                if self.check_words("with", "has"):
                    return
                self.warn("Unknown property")
                self.next()
                return
            if self.check_words("and"):
                self.next()
            else:
                break

    def animation(self):
        while True:
            if self.check_words("lasts", "lasting"):
                self.next()
                if self.check_words("for"):
                    self.next()
                self.lottie.out_point = self.time(self.lottie.out_point)
            elif self.check_words("stops", "stopping", "loops", "looping"):
                if self.check_words("for", "after"):
                    self.next()
                self.lottie.out_point = self.time(self.lottie.out_point)
                if self.max_duration and self.lottie.out_point > self.max_duration:
                    self.lottie.out_point = self.max_duration
            elif self.check_words("with", "has"):
                self.next()
                props = {
                    "width": self.integer,
                    "height": self.integer,
                    "name": self.string
                }
                if not self.allow_resize:
                    props.pop("width")
                    props.pop("height")
                self.properties(self.lottie, props)
            elif self.check_words("and"):
                self.next()
            else:
                return

    def time(self, default):
        if self.token.type != TokenType.Number:
            self.warn("Expected time")
            return default

        amount = self.token.value

        self.next()
        if self.check_words("seconds", "second"):
            amount *= self.lottie.frame_rate
        elif self.check_words("milliseconds", "millisecond"):
            amount *= self.lottie.frame_rate / 1000
        elif not self.check_words("frames", "frame"):
            self.warn("Missing time unit")
            return amount

        self.next()
        return amount

    def integer(self, default, warn=True):
        if self.token.type != TokenType.Number or not isinstance(self.token.value, int):
            if warn:
                self.warn("Expected integer")
            return default

        val = self.token.value
        self.next()
        return val

    def number(self, default):
        if self.token.type != TokenType.Number:
            self.warn("Expected number")
            return default

        val = self.token.value
        self.next()

        return val

    def string(self, default):
        if self.token.type != TokenType.String:
            self.warn("Expected string")
            return default

        val = self.token.value
        self.next()
        return val

    def layers(self, composition):
        while True:
            if self.check_words("and"):
                self.next()
            if self.check_words("then"):
                self.next()
            if self.check_words("finally"):
                self.next()
            if self.check_words("there's"):
                self.next()
                self.layer(composition)
            elif self.check_words("there"):
                self.next()
                if self.check_words("is", "are"):
                    self.next()
                    self.layer(composition)
            elif self.article():
                self.layer(composition)
            elif self.token.type == TokenType.Number and isinstance(self.token.value, int):
                self.layer(composition)
            else:
                break

    def count(self, default=1):
        if self.article():
            return 1
        return self.integer(default)

    def layer(self, composition):
        if self.token.type != TokenType.Word:
            self.warn("Expected shape")
            return

        layer = layers.ShapeLayer()
        layer.in_point = self.lottie.in_point
        layer.out_point = self.lottie.out_point
        composition.insert_layer(0, layer)

        self.shape_list(layer)

        if self.token.type == TokenType.Separator:
            self.next()

    def shape_list(self, parent):
        extent = min(self.lottie.width, self.lottie.height) * 0.4
        shape = ShapeData(extent)
        shape.count = self.count()

        while self.token.type == TokenType.Word:
            ok = False

            color = self.color()
            if color:
                ok = True
                shape.color = color

            if self.check_words("transparent"):
                self.next()
                shape.color = None
                ok = True

            size_mult = self.size_multiplitier()
            if size_mult:
                ok = True
                shape.extent *= size_mult

            if self.check_words("portrait"):
                self.next()
                shape.portrait = True
                ok = True

            if self.check_words("landscape"):
                self.next()
                shape.portrait = False
                ok = True

            tokens, qualifier = self.size_qualifier()
            if tokens:
                if self.check_words("rounded"):
                    shape.roundness = qualifier
                    self.next()
                    ok = True
                elif self.check_words("transparent"):
                    shape.opacity = (1 / qualifier)
                    self.next()
                    ok = True
                else:
                    self.lexer.queue = tokens + self.lexer.queue

            if self.check_words("star", "polygon", "ellipse", "rectangle", "circle", "square"):
                shape_type = self.token.value
                function = getattr(self, "shape_" + shape_type)
                self.next()
                shape_object = function(shape)
                self.add_shape(parent, shape_object, shape)
                return

            if self.token.type == TokenType.Word:
                for name, sides in self.sides.items():
                    if self.token.value.startswith(name):
                        if self.token.value.endswith("gon"):
                            self.next()
                            shape_object = self.shape_polygon(shape, sides)
                            self.add_shape(parent, shape_object, shape)
                            return
                        elif self.token.value.endswith("gram"):
                            self.next()
                            shape_object = self.shape_star(shape, sides)
                            self.add_shape(parent, shape_object, shape)
                            return

            if self.check_words("triangle"):
                self.next()
                shape_object = self.shape_polygon(shape, 3)
                self.add_shape(parent, shape_object, shape)
                return

            sides = self.integer(None, False)
            if sides is not None:
                if self.check_words("sided", "pointed"):
                    self.next()
                    if self.check_words("polygon", "star"):
                        shape_type = self.token.value
                        function = getattr(self, "shape_" + shape_type)
                        self.next()
                        shape_object = function(shape, sides)
                        self.add_shape(parent, shape_object, shape)
                        return
                    else:
                        self.warn("Expected 'star' or 'polygon'")
                        return
                else:
                    continue

            if not ok:
                self.next()
                break

        self.warn("Expected shape")

    def size_qualifier(self):
        base = 1
        tokens = []
        while True:
            if self.check_words("very", "much"):
                tokens.insert(0, self.token)
                self.next()
                base *= 1.33
            elif self.check_words("extremely"):
                tokens.insert(0, self.token)
                self.next()
                base *= 1.5
            elif self.check_words("incredibly"):
                tokens.insert(0, self.token)
                self.next()
                base *= 2
            else:
                break

        return tokens, base

    def size_multiplitier(self):
        base = 1
        tokens, qualifier = self.size_qualifier()
        if qualifier:
            base *= qualifier

        if self.check_words("small"):
            self.next()
            return 0.8 / base
        elif self.check_words("large", "big"):
            self.next()
            return 1.2 * base
        elif self.check_words("tiny"):
            self.next()
            return 0.5 / base
        elif self.check_words("huge"):
            self.next()
            return 1.6 * base
        else:
            self.lexer.queue = tokens + self.lexer.queue
            return None

    def add_shape(self, parent, shape_object, shape_data):
        g = shapes.Group()
        g.add_shape(shape_object)
        if shape_data.color:
            fill = shapes.Fill(shape_data.color)
            g.add_shape(fill)

        self.stroke(g)

        if shape_data.opacity != 1:
            g.transform.opacity.value = 100 * shape_data.opacity

        center = shape_object.position.value
        g.transform.position.value = self.position(g, 0) + center
        g.transform.anchor_point.value = NVector(*center)

        if self.check_words("rotated"):
            self.next()
            g.transform.rotation.value = self.angle(0)

        parent.insert_shape(0, g)

    def stroke(self, g):
        pass # TODO

    def shape_square(self, shape_data: ShapeData):
        pos = NVector(self.lottie.width / 2, self.lottie.height / 2)
        size = NVector(shape_data.extent, shape_data.extent)
        round_base = shape_data.extent / 5
        shape = shapes.Rect(pos, size, shape_data.roundness * round_base)

        return shape

    def shape_circle(self, shape_data: ShapeData):
        pos = NVector(self.lottie.width / 2, self.lottie.height / 2)
        size = NVector(shape_data.extent, shape_data.extent)
        shape = shapes.Ellipse(pos, size, shape_data.roundness)
        return shape

    def position(self, shape: shapes.Group, time: float):
        px = 0
        py = 0

        tokens, qual = self.size_qualifier()

        if self.check_words("to", "in", "towards"):
            self.next()
            if self.check_words("the"):
                self.next()
            if self.token.type != TokenType.Word:
                self.warn("Expected position")
                return

            while True:
                if self.check_words("left"):
                    px = -1
                elif self.check_words("right"):
                    px = 1
                elif self.check_words("top"):
                    py = -1
                elif self.check_words("bottom"):
                    py = 1
                elif self.check_words("center", "middle"):
                    pass
                else:
                    break

                self.next()

            if self.check_words("side", "corner"):
                self.next()

        if px == 0 and py == 0:
            return shape.transform.position.get_value(time)

        box = shape.bounding_box(time)
        center = box.center()
        left = box.width / 2
        right = self.lottie.width - box.width / 2
        top = box.height / 2
        bottom = self.lottie.height - box.height / 2

        pos = shape.transform.position.get_value(time)
        x = pos.x
        y = pos.y
        dx = dy = 0

        if px < 0:
            dx = left - center.x
        elif px > 0:
            dx = right - center.y

        if py < 0:
            dy = top - center.y
        elif py > 0:
            dy = bottom - center.y

        return NVector(
            x + dx * qual,
            y + dy * qual,
        )

    def shape_star(self, shape_data: ShapeData, sides: int = None):
        pos = NVector(self.lottie.width / 2, self.lottie.height / 2)
        round_base = shape_data.extent / 5
        roundness = shape_data.roundness * round_base
        shape = shapes.Star()
        shape.position.value = pos
        shape.inner_roundness.value = roundness
        shape.outer_radius.value = shape_data.extent / 2
        shape.outer_roundness.value = roundness
        shape.star_type = shapes.StarType.Star
        shape.points.value = sides or 5

        if self.check_words("with", "of"):
            while True:
                if self.check_words("with", "of"):
                    self.next()

                if self.check_words("radius"):
                    self.next()
                    shape.outer_radius.value = self.number(shape.outer_radius.value)
                elif self.check_words("diameter"):
                    shape.outer_radius.value = self.number(shape.outer_radius.value) / 2
                elif self.token.type == TokenType.Number:
                    if sides:
                        self.warn("Number of sides already specified")
                    shape.points.value = self.integer()
                    if self.require_one_of("points", "sides", "point", "side"):
                        self.next()
                elif self.check_words("and"):
                    continue
                else:
                    self.warn("Unknown property")
                    break

        shape.inner_radius.value = shape.outer_radius.value / 2

        return shape

    def shape_polygon(self, shape_data: ShapeData, sides: int = None):
        shape = self.shape_star(shape_data, sides)
        shape.inner_radius = None
        shape.inner_roundness = None
        shape.star_type = shapes.StarType.Polygon
        return shape

    def angle_direction(self):
        if self.check_words("clockwise"):
            self.next()
            return 1
        elif self.check_words("counter"):
            self.next()
            if self.check_words("clockwise"):
                self.next()
            return -1
        return 1

    def fraction(self):
        if self.article():
            amount = 1
        else:
            amount = self.number(1)

        if self.check_words("full", "entire"):
            self.next()
            return amount, True
        elif self.check_words("half", "halfs"):
            self.next()
            return amount / 2, True
        elif self.check_words("third", "thirds"):
            self.next()
            return amount / 3, True
        elif self.check_words("quarter", "quarters"):
            self.next()
            return amount / 3, True

        return amount, False

    def angle(self, default):
        direction = self.angle_direction()

        amount, has_fraction = self.fraction()

        if self.check_words("and"):
            self.next()
            more_frac = self.fraction()[0]
            if has_fraction:
                amount += amount * more_frac
            else:
                amount += more_frac

        if self.check_words("turns"):
            self.next()
            if self.check_words("and"):
                self.next()
                amount += self.fraction()[0]
            amount *= 360
        elif self.require_one_of("degrees"):
            self.next()

        return amount

    def rect_size(self, shape_data: ShapeData):
        extent = shape_data.extent
        width = None
        height = None
        ratio = math.sqrt(2)
        handle_orientation = True

        if self.check_words("with", "of"):
            while True:
                if self.check_words("with", "of"):
                    self.next()

                if self.check_words("ratio"):
                    self.next()
                    ratio = self.fraction()[0]
                    if ratio <= 0:
                        self.warn("Ratio must be positive")
                        ratio = math.sqrt(2)
                elif self.check_words("width"):
                    self.next()
                    width = self.number(0)
                elif self.check_words("height"):
                    self.next()
                    height = self.number(0)
                else:
                    self.warn("Unknown property")
                    break

        if width is None and height is None:
            width = extent
            height = width / ratio
        elif width is None:
            width = height * ratio
        elif height is None:
            height = width / ratio
        else:
            handle_orientation = False

        if handle_orientation:
            if (width > height and shape_data.portrait) or (width < height and not shape_data.portrait):
                width, height = height, width

        return NVector(width, height)

    def shape_rectangle(self, shape_data: ShapeData):
        pos = NVector(self.lottie.width / 2, self.lottie.height / 2)
        extent = shape_data.extent
        round_base = shape_data.extent / 5
        size = self.rect_size(shape_data)
        return shapes.Rect(pos, size, shape_data.roundness * round_base)

    def shape_ellipse(self, shape_data: ShapeData):
        pos = NVector(self.lottie.width / 2, self.lottie.height / 2)
        extent = shape_data.extent
        size = self.rect_size(shape_data)
        return shapes.Ellipse(pos, size)
