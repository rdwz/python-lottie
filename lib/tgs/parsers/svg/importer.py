import re
import math
from xml.etree import ElementTree
from ... import objects
from ...utils.nvector import NVector
from .svgdata import color_table, css_atrrs
from .handler import SvgHandler, NameMode

nocolor = {"none"}


def hsl_to_rgb(h, s, l):
    if l < 0.5:
        m2 = l * (s + 1)
    else:
        m2 = l + s - l * s
    m1 = l*2 - m2
    r = hue_to_rgb(m1, m2, h+1/3)
    g = hue_to_rgb(m1, m2, h)
    b = hue_to_rgb(m1, m2, h-1/3)
    return [r, g, b]


def hue_to_rgb(m1, m2, h):
    if h < 0:
        h += 1
    elif h > 1:
        h -= 1
    if h*6 < 1:
        return m1+(m2-m1)*h*6
    elif h*2 < 1:
        return m2
    elif h*3 < 2:
        return m1+(m2-m1)*(2/3-h)*6
    return m1


class SvgGradientCoord:
    def __init__(self, name, comp, value, percent):
        self.name = name
        self.comp = comp
        self.value = value
        self.percent = percent

    def to_value(self, bbox, default=None):
        if self.value is None:
            return default

        if not self.percent:
            return self.value

        if self.comp == "w":
            return (bbox.x2 - bbox.x1) * self.value

        if self.comp == "x":
            return bbox.x1 + (bbox.x2 - bbox.x1) * self.value

        return bbox.y1 + (bbox.y2 - bbox.y1) * self.value

    def parse(self, attr, default_percent):
        if attr is None:
            return
        if attr.endswith("%"):
            self.percent = True
            self.value = float(attr[:-1])/100
        else:
            self.percent = default_percent
            self.value = float(attr)


class SvgGradient:
    def __init__(self):
        self.colors = []
        self.coords = []

    def add_color(self, offset, color):
        self.colors.append((offset, color[:3]))

    def to_lottie(self, gradient_shape, shape, time=0):
        """
        gradient_shape should be a GradientFill or GradientStroke
        """
        for off, col in self.colors:
            gradient_shape.colors.add_color(off, col)

    def add_coord(self, value):
        setattr(self, value.name, value)
        self.coords.append(value)

    def parse_attrs(self, attrib):
        relunits = attrib.get("gradientUnits", "") != "userSpaceOnUse"
        for c in self.coords:
            c.parse(attrib.get(c.name, None), relunits)


class SvgLinearGradient(SvgGradient):
    def __init__(self):
        super().__init__()
        self.add_coord(SvgGradientCoord("x1", "x", 0, True))
        self.add_coord(SvgGradientCoord("y1", "y", 0, True))
        self.add_coord(SvgGradientCoord("x2", "x", 1, True))
        self.add_coord(SvgGradientCoord("y2", "y", 0, True))

    def to_lottie(self, gradient_shape, shape, time=0):
        """
        gradient_shape should be a GradientFill or GradientStroke
        """
        bbox = shape.bounding_box(time)
        gradient_shape.start_point.value = [
            self.x1.to_value(bbox),
            self.y1.to_value(bbox),
        ]
        gradient_shape.end_point.value = [
            self.x2.to_value(bbox),
            self.y2.to_value(bbox),
        ]
        gradient_shape.gradient_type = objects.GradientType.Linear

        super().to_lottie(gradient_shape, shape, time)


class SvgRadialGradient(SvgGradient):
    def __init__(self):
        super().__init__()
        self.add_coord(SvgGradientCoord("cx", "x", 0.5, True))
        self.add_coord(SvgGradientCoord("cy", "y", 0.5, True))
        self.add_coord(SvgGradientCoord("fx", "x", None, True))
        self.add_coord(SvgGradientCoord("fy", "y", None, True))
        self.add_coord(SvgGradientCoord("r", "w", 0.5, True))

    def to_lottie(self, gradient_shape, shape, time=0):
        """
        gradient_shape should be a GradientFill or GradientStroke
        """
        bbox = shape.bounding_box(time)
        cx = self.cx.to_value(bbox)
        cy = self.cy.to_value(bbox)
        gradient_shape.start_point.value = [cx, cy]
        r = self.r.to_value(bbox)
        gradient_shape.end_point.value = [cx+r, cy]

        fx = self.fx.to_value(bbox, cx) - cx
        fy = self.fy.to_value(bbox, cy) - cy
        gradient_shape.highlight_angle.value = math.atan2(fy, fx) * 180 / math.pi
        gradient_shape.highlight_length.value = math.hypot(fx, fy)

        gradient_shape.gradient_type = objects.GradientType.Radial

        super().to_lottie(gradient_shape, shape, time)


def parse_color(color, current_color=[0, 0, 0, 1]):
    # #fff
    if re.match(r"^#[0-9a-fA-F]{6}$", color):
        return [int(color[1:3], 16) / 0xff, int(color[3:5], 16) / 0xff, int(color[5:7], 16) / 0xff, 1]
    # #112233
    if re.match(r"^#[0-9a-fA-F]{3}$", color):
        return [int(color[1], 16) / 0xf, int(color[2], 16) / 0xf, int(color[3], 16) / 0xf, 1]
    # rgba(123, 123, 123, 0.7)
    match = re.match(r"^rgba\s*\(\s*([0-9]+)\s*,\s*([0-9]+)\s*,\s*([0-9]+)\s*,\s*([0-9.eE]+)\s*\)$", color)
    if match:
        return [int(match[1])/255, int(match[2])/255, int(match[3])/255, float(match[4])]
    # rgb(123, 123, 123)
    match = re.match(r"^rgb\s*\(\s*([0-9]+)\s*,\s*([0-9]+)\s*,\s*([0-9]+)\s*\)$", color)
    if match:
        return [int(match[1])/255, int(match[2])/255, int(match[3])/255, 1]
    # rgb(60%, 30%, 20%)
    match = re.match(r"^rgb\s*\(\s*([0-9]+)%\s*,\s*([0-9]+)%\s*,\s*([0-9]+)%\s*\)$", color)
    if match:
        return [int(match[1])/100, int(match[2])/100, int(match[3])/100, 1]
    # rgba(60%, 30%, 20%, 0.7)
    match = re.match(r"^rgb\s*\(\s*([0-9]+)%\s*,\s*([0-9]+)%\s*,\s*([0-9]+)%\s*,\s*([0-9.eE]+)\s*\)$", color)
    if match:
        return [int(match[1])/100, int(match[2])/100, int(match[3])/100, float(match[4])]
    # transparent
    if color == "transparent":
        return [0, 0, 0, 0]
    # hsl(60, 30%, 20%)
    match = re.match(r"^hsl\s*\(\s*([0-9]+)\s*,\s*([0-9]+)%\s*,\s*([0-9]+)%\s*\)$", color)
    if match:
        return hsl_to_rgb(int(match[1])/360, int(match[2])/100, int(match[3])/100) + [1]
    # hsla(60, 30%, 20%, 0.7)
    match = re.match(r"^hsl\s*\(\s*([0-9]+)\s*,\s*([0-9]+)%\s*,\s*([0-9]+)%\s*,\s*([0-9.eE]+)\s*\)$", color)
    if match:
        return hsl_to_rgb(int(match[1])/360, int(match[2])/100, int(match[3])/100) + [float(match[4])]
    # currentColor
    if color in {"currentColor", "inherit"}:
        return current_color
    # red
    return color_table[color]


class SvgParser(SvgHandler):
    def __init__(self, name_mode=NameMode.Inkscape):
        self.init_etree()
        self.name_mode = name_mode
        self.current_color = [0, 0, 0, 1]
        self.gradients = {}

    def _get_name(self, element, inkscapequal):
        if self.name_mode == NameMode.Inkscape:
            return element.attrib.get(inkscapequal, element.attrib.get("id"))
        return self._get_id(element)

    def _get_id(self, element):
        if self.name_mode != NameMode.NoName:
            return element.attrib.get("id")
        return None

    def parse_color(self, color):
        return parse_color(color, self.current_color)

    def parse_transform(self, element, group, dest_trans):
        itcx = self.qualified("inkscape", "transform-center-x")
        if itcx in element.attrib:
            cx = float(element.attrib[itcx])
            cy = float(element.attrib[self.qualified("inkscape", "transform-center-y")])
            bb = group.bounding_box()
            if not bb.isnull():
                bbx, bby = bb.center()
                cx += bbx
                cy = bby - cy
                dest_trans.anchor_point.value = [cx, cy]
                dest_trans.position.value = [cx, cy]

        if "transform" not in element.attrib:
            return

        for t in re.finditer(r"([a-zA-Z]+)\s*\(([^\)]*)\)", element.attrib["transform"]):
            name = t[1]
            params = list(map(float, t[2].strip().replace(",", " ").split()))
            if name == "translate":
                dest_trans.position.value = [
                    dest_trans.position.value[0] + params[0],
                    dest_trans.position.value[1] + (params[1] if len(params) > 1 else 0),
                ]
            elif name == "scale":
                xfac = params[0]
                dest_trans.scale.value[0] = (dest_trans.scale.value[0] / 100 * xfac) * 100
                yfac = params[1] if len(params) > 1 else xfac
                dest_trans.scale.value[1] = (dest_trans.scale.value[1] / 100 * yfac) * 100
            elif name == "rotate":
                ang = params[0]
                x = y = 0
                if len(params) > 2:
                    x = params[1]
                    y = params[2]
                    dest_trans.position.value = [
                        dest_trans.position.value[0] + x,
                        dest_trans.position.value[1] + y
                    ]
                dest_trans.anchor_point.value = [x, y]
                dest_trans.rotation.value = ang
            elif name == "skewX":
                dest_trans.skew.value = -params[0]
                dest_trans.skew_axis.value = 0
            elif name == "skewY":
                dest_trans.skew.value = params[0]
                dest_trans.skew_axis.value = 90
            elif name == "matrix":
                dest_trans.position.value = params[-2:]
                v1 = NVector(*params[0:2])
                v2 = NVector(*params[2:4])
                dest_trans.scale.value = [v1.length * 100, v2.length * 100]
                v1 /= v1.length
                #v2 /= v2.length
                angle = math.atan2(v1[1], v1[0])
                #angle1 = math.atan2(v2[1], v2[0])
                dest_trans.rotation.value = angle / math.pi * 180

    def parse_style(self, element):
        style = {}
        for att in css_atrrs & set(element.attrib.keys()):
            if att in element.attrib:
                style[att] = element.attrib[att]
        if "style" in element.attrib:
            style.update(**dict(map(
                lambda x: map(lambda y: y.strip(), x.split(":")),
                filter(bool, element.attrib["style"].split(";"))
            )))
        return style

    def apply_common_style(self, style, transform):
        opacity = float(style.get("opacity", 1))
        if style.get("display", "inline") == "none":
            opacity = 0
        if style.get("visibility", "visible") == "hidden":
            opacity = 0
        transform.opacity.value = opacity * 100

    def add_shapes(self, element, shapes, shape_parent):
        # TODO inherit style
        style = self.parse_style(element)

        group = objects.Group()
        self.apply_common_style(style, group.transform)
        group.name = self._get_id(element)

        shape_parent.shapes.insert(0, group)
        for shape in shapes:
            group.add_shape(shape)

        stroke_color = style.get("stroke", "none")
        if stroke_color not in nocolor:
            if stroke_color.startswith("url"):
                stroke = self.get_color_url(stroke_color, objects.GradientStroke, group)
                opacity = 1
            else:
                stroke = objects.Stroke()
                color = self.parse_color(stroke_color)
                stroke.color.value = color[:3]
                opacity = color[3]
            stroke.opacity.value = opacity * float(style.get("stroke-opacity", 1)) * 100
            group.add_shape(stroke)
            stroke.width.value = float(style.get("stroke-width", 1))
            linecap = style.get("stroke-linecap")
            if linecap == "round":
                stroke.line_cap = objects.shapes.LineCap.Round
            elif linecap == "butt":
                stroke.line_cap = objects.shapes.LineCap.Butt
            elif linecap == "square":
                stroke.line_cap = objects.shapes.LineCap.Square
            linejoin = style.get("stroke-linejoin")
            if linejoin == "round":
                stroke.line_join = objects.shapes.LineJoin.Round
            elif linejoin == "bevel":
                stroke.line_join = objects.shapes.LineJoin.Bevel
            elif linejoin in {"miter", "arcs", "miter-clip"}:
                stroke.line_join = objects.shapes.LineJoin.Miter
            stroke.miter_limit = float(style.get("stroke-miterlimit", 0))

        fill_color = style.get("fill", "inherit")
        if fill_color not in nocolor:
            if fill_color.startswith("url"):
                fill = self.get_color_url(fill_color, objects.GradientFill, group)
                opacity = 1
            else:
                color = self.parse_color(fill_color)
                fill = objects.Fill(color[:3])
                opacity = color[3]
            opacity *= float(style.get("fill-opacity", 1))
            fill.opacity.value = opacity * 100
            group.add_shape(fill)

        self.parse_transform(element, group, group.transform)

        return group

    def _parseshape_g(self, element, shape_parent):
        group = objects.Group()
        shape_parent.shapes.insert(0, group)
        style = self.parse_style(element)
        self.apply_common_style(style, group.transform)
        group.name = self._get_name(element, self.qualified("inkscape", "label"))
        self.parse_children(element, group)
        self.parse_transform(element, group, group.transform)

    def _parseshape_ellipse(self, element, shape_parent):
        ellipse = objects.Ellipse()
        ellipse.position.value = [
            float(element.attrib["cx"]),
            float(element.attrib["cy"])
        ]
        ellipse.size.value = [
            float(element.attrib["rx"]) * 2,
            float(element.attrib["ry"]) * 2
        ]
        self.add_shapes(element, [ellipse], shape_parent)

    def _parseshape_circle(self, element, shape_parent):
        ellipse = objects.Ellipse()
        ellipse.position.value = [
            float(element.attrib["cx"]),
            float(element.attrib["cy"])
        ]
        r = float(element.attrib["r"]) * 2
        ellipse.size.value = [r, r]
        self.add_shapes(element, [ellipse], shape_parent)

    def _parseshape_rect(self, element, shape_parent):
        rect = objects.Rect()
        w = float(element.attrib["width"])
        h = float(element.attrib["height"])
        rect.position.value = [
            float(element.attrib["x"]) + w / 2,
            float(element.attrib["y"]) + h / 2
        ]
        rect.size.value = [w, h]
        rx = float(element.attrib.get("rx", 0))
        ry = float(element.attrib.get("ry", 0))
        rect.rounded.value = (rx + ry) / 2
        self.add_shapes(element, [rect], shape_parent)

    def _parseshape_line(self, element, shape_parent):
        line = objects.Shape()
        line.vertices.value.add_point([
            float(element.attrib["x1"]),
            float(element.attrib["y1"])
        ])
        line.vertices.value.add_point([
            float(element.attrib["x2"]),
            float(element.attrib["y2"])
        ])
        self.add_shapes(element, [line], shape_parent)

    def _handle_poly(self, element):
        line = objects.Shape()
        coords = list(map(float, element.attrib["points"].replace(",", " ").split()))
        for i in range(0, len(coords), 2):
            line.vertices.value.add_point(coords[i:i+2])
        return line

    def _parseshape_polyline(self, element, shape_parent):
        line = self._handle_poly(element)
        self.add_shapes(element, [line], shape_parent)

    def _parseshape_polygon(self, element, shape_parent):
        line = self._handle_poly(element)
        line.vertices.value.close()
        self.add_shapes(element, [line], shape_parent)

    def _parseshape_path(self, element, shape_parent):
        d_parser = PathDParser(element.attrib.get("d", ""))
        d_parser.parse()
        paths = []
        for path in d_parser.paths:
            p = objects.Shape()
            p.vertices.value = path
            paths.append(p)
        #if len(d_parser.paths) > 1:
            #paths.append(objects.shapes.Merge())
        self.add_shapes(element, paths, shape_parent)

    def parse_children(self, element, shape_parent, limit=None):
        for child in element:
            tag = self.unqualified(child.tag)
            if limit and tag not in limit:
                continue
            handler = getattr(self, "_parseshape_" + tag, None)
            if handler:
                handler(child, shape_parent)
            else:
                handler = getattr(self, "_parse_" + tag, None)
                if handler:
                    handler(child)

    def parse_etree(self, etree, *args, **kwargs):
        animation = objects.Animation(*args, **kwargs)
        svg = etree.getroot()
        if "width" in svg.attrib and "height" in svg.attrib:
            animation.width = int(svg.attrib["width"])
            animation.height = int(svg.attrib["height"])
        else:
            _, _, animation.width, animation.height = map(int, svg.attrib["viewBox"].split(" "))
        animation.name = self._get_name(svg, self.qualified("sodipodi", "docname"))
        layer = objects.ShapeLayer()
        animation.add_layer(layer)
        self.parse_children(svg, layer)
        return animation

    def _parse_defs(self, element):
        self.parse_children(element, None, {"linearGradient", "radialGradient"})

    def _gradient(self, element, grad):
        id = element.attrib["id"]
        if id in self.gradients:
            grad.colors = self.gradients[id].colors
        grad.parse_attrs(element.attrib)
        href = element.attrib.get(self.qualified("xlink", "href"))
        if href:
            srcid = href.strip("#")
            if srcid in self.gradients:
                src = self.gradients[srcid]
            else:
                src = grad.__class__()
                self.gradients[srcid] = src
            grad.colors = src.colors
        else:
            for stop in element.findall("./%s" % self.qualified("svg", "stop")):
                off = float(stop.attrib["offset"].strip("%")) / 100
                style = self.parse_style(stop)
                grad.add_color(off, self.parse_color(style["stop-color"]))
        self.gradients[id] = grad

    def _parse_linearGradient(self, element):
        self._gradient(element, SvgLinearGradient())

    def _parse_radialGradient(self, element):
        self._gradient(element, SvgRadialGradient())

    def get_color_url(self, color, gradientclass, shape):
        match = re.match(r"""url\(['"]?#([^)'"]+)['"]?\)""", color)
        if not match:
            return None
        id = match[1]
        if id not in self.gradients:
            return None
        grad = self.gradients[id]
        outgrad = gradientclass()
        grad.to_lottie(outgrad, shape)
        if self.name_mode != NameMode.NoName:
            grad.name = id
        return outgrad


class PathDParser:
    def __init__(self, d_string):
        self.path = objects.properties.Bezier()
        self.paths = []
        self.p = NVector(0, 0)
        self.la = None
        self.la_type = None
        self.tokens = list(map(self.d_subsplit, re.findall("[a-zA-Z]|[-+.0-9eE]+", d_string)))
        self.add_p = True
        self.implicit = "M"

    def d_subsplit(self, tok):
        if tok.isalpha():
            return tok
        return float(tok)

    def next_token(self):
        if self.tokens:
            self.la = self.tokens.pop(0)
            if isinstance(self.la, str):
                self.la_type = 0
            else:
                self.la_type = 1
        else:
            self.la = None
        return self.la

    def next_vec(self):
        x = self.next_token()
        y = self.next_token()
        return NVector(x, y)

    def cur_vec(self):
        x = self.la
        y = self.next_token()
        return NVector(x, y)

    def parse(self):
        self.next_token()
        while self.la is not None:
            if self.la_type == 0:
                parser = "_parse_" + self.la
                self.next_token()
                getattr(self, parser)()
            else:
                parser = "_parse_" + self.implicit
                getattr(self, parser)()

    def _push_path(self):
        self.path = objects.properties.Bezier()
        self.add_p = True

    def _parse_M(self):
        if self.la_type != 1:
            self.next_token()
            return
        self.p = self.cur_vec()
        self.implicit = "L"
        if not self.add_p:
            self._push_path()
        self.next_token()

    def _parse_m(self):
        if self.la_type != 1:
            self.next_token()
            return
        self.p += self.cur_vec()
        self.implicit = "l"
        if not self.add_p:
            self._push_path()
        self.next_token()

    def _rpoint(self, point, rel=None):
        return (point - (rel or self.p)).to_list() if point is not None else [0, 0]

    def _do_add_p(self, outp=None):
        if self.add_p:
            self.paths.append(self.path)
            self.path.add_point(self.p.to_list(), [0, 0], self._rpoint(outp))
            self.add_p = False
        elif outp:
            rp = NVector(*self.path.vertices[-1])
            self.path.out_point[-1] = self._rpoint(outp, rp)

    def _parse_L(self):
        if self.la_type != 1:
            self.next_token()
            return
        self._do_add_p()
        self.p = self.cur_vec()
        self.path.add_point(self.p.to_list(), NVector(0, 0), NVector(0, 0))
        self.implicit = "L"
        self.next_token()

    def _parse_l(self):
        if self.la_type != 1:
            self.next_token()
            return
        self._do_add_p()
        self.p += self.cur_vec()
        self.path.add_point(self.p.to_list(), [0, 0], [0, 0])
        self.implicit = "l"
        self.next_token()

    def _parse_H(self):
        if self.la_type != 1:
            self.next_token()
            return
        self._do_add_p()
        self.p[0] = self.la
        self.path.add_point(self.p.to_list(), [0, 0], [0, 0])
        self.implicit = "H"
        self.next_token()

    def _parse_h(self):
        if self.la_type != 1:
            self.next_token()
            return
        self._do_add_p()
        self.p[0] += self.la
        self.path.add_point(self.p.to_list(), [0, 0], [0, 0])
        self.implicit = "h"
        self.next_token()

    def _parse_V(self):
        if self.la_type != 1:
            self.next_token()
            return
        self._do_add_p()
        self.p[1] = self.la
        self.path.add_point(self.p.to_list(), [0, 0], [0, 0])
        self.implicit = "V"
        self.next_token()

    def _parse_v(self):
        if self.la_type != 1:
            self.next_token()
            return
        self._do_add_p()
        self.p[1] += self.la
        self.path.add_point(self.p.to_list(), [0, 0], [0, 0])
        self.implicit = "v"
        self.next_token()

    def _parse_C(self):
        if self.la_type != 1:
            self.next_token()
            return
        pout = self.cur_vec()
        self._do_add_p(pout)
        pin = self.next_vec()
        self.p = self.next_vec()
        self.path.add_point(
            self.p.to_list(),
            (pin - self.p).to_list(),
            [0, 0]
        )
        self.implicit = "C"
        self.next_token()

    def _parse_c(self):
        if self.la_type != 1:
            self.next_token()
            return
        pout = self.p + self.cur_vec()
        self._do_add_p(pout)
        pin = self.p + self.next_vec()
        self.p += self.next_vec()
        self.path.add_point(
            self.p.to_list(),
            (pin - self.p).to_list(),
            [0, 0]
        )
        self.implicit = "c"
        self.next_token()

    def _parse_S(self):
        if self.la_type != 1:
            self.next_token()
            return
        pin = self.cur_vec()
        self._do_add_p()
        handle = NVector(*self.path.in_point[-1])
        self.path.out_point[-1] = (-handle).to_list()
        self.p = self.next_vec()
        self.path.add_point(
            self.p.to_list(),
            (pin - self.p).to_list(),
            [0, 0]
        )
        self.implicit = "S"
        self.next_token()

    def _parse_s(self):
        if self.la_type != 1:
            self.next_token()
            return
        pin = self.cur_vec() + self.p
        self._do_add_p()
        handle = NVector(*self.path.in_point[-1])
        self.path.out_point[-1] = (-handle).to_list()
        self.p += self.next_vec()
        self.path.add_point(
            self.p.to_list(),
            (pin - self.p).to_list(),
            [0, 0]
        )
        self.implicit = "s"
        self.next_token()

    def _parse_Q(self):
        if self.la_type != 1:
            self.next_token()
            return
        self._do_add_p()
        pin = self.cur_vec()
        self.p = self.next_vec()
        self.path.add_point(
            self.p.to_list(),
            (pin - self.p).to_list(),
            [0, 0]
        )
        self.implicit = "Q"
        self.next_token()

    def _parse_q(self):
        if self.la_type != 1:
            self.next_token()
            return
        self._do_add_p()
        pin = self.p + self.cur_vec()
        self.p += self.next_vec()
        self.path.add_point(
            self.p.to_list(),
            (pin - self.p).to_list(),
            [0, 0]
        )
        self.implicit = "q"
        self.next_token()

    def _parse_T(self):
        if self.la_type != 1:
            self.next_token()
            return
        self._do_add_p()
        handle = self.p - NVector(*self.path.in_point[-1])
        self.p = self.cur_vec()
        self.path.add_point(
            self.p.to_list(),
            (handle - self.p).to_list(),
            [0, 0]
        )
        self.implicit = "T"
        self.next_token()

    def _parse_t(self):
        if self.la_type != 1:
            self.next_token()
            return
        self._do_add_p()
        handle = -NVector(*self.path.in_point[-1]) + self.p
        self.p += self.cur_vec()
        self.path.add_point(
            self.p.to_list(),
            (handle - self.p).to_list(),
            [0, 0]
        )
        self.implicit = "t"
        self.next_token()

    def _parse_A(self):
        if self.la_type != 1:
            self.next_token()
            return
        r = self.cur_vec()
        xrot = self.next_token()
        large = self.next_token()
        sweep = self.next_token()
        dest = self.next_vec()
        self._do_arc(r[0], r[1], xrot, large, sweep, dest)
        self.implicit = "A"
        self.next_token()

    def _arc_matrix_mul(self, phi, x, y, sin_mul=1):
        c = math.cos(phi)
        s = math.sin(phi) * sin_mul

        xr = c * x - s * y
        yr = s * x + c * y
        return xr, yr

    def _arc_angle(self, u, v):
        arg = math.acos(max(-1, min(1, u.dot(v) / (u.length * v.length))))
        if u[0] * v[1] - u[1] * v[0] < 0:
            return -arg
        return arg

    def _arc_point(self, c, r, xangle, t):
        return NVector(
            c[0] + r[0] * math.cos(xangle) * math.cos(t) - r[1] * math.sin(xangle) * math.sin(t),
            c[1] + r[0] * math.sin(xangle) * math.cos(t) + r[1] * math.cos(xangle) * math.sin(t)
        )

    def _arc_derivative(self, c, r, xangle, t):
        return NVector(
            -r[0] * math.cos(xangle) * math.sin(t) - r[1] * math.sin(xangle) * math.cos(t),
            -r[0] * math.sin(xangle) * math.sin(t) + r[1] * math.cos(xangle) * math.cos(t)
        )

    def _arc_alpha(self, step):
        return math.sin(step) * (math.sqrt(4+3*math.tan(step/2)**2) - 1) / 3

    def _do_arc(self, rx, ry, xrot, large, sweep, dest):
        self._do_add_p()
        if self.p == dest:
            return
        rx = abs(rx)
        ry = abs(ry)

        if rx == 0 or ry == 0:
            # Straight line
            self.p = dest
            self.path.add_point(
                self.p.to_list(),
                [0, 0],
                [0, 0]
            )
            return

        x1 = self.p[0]
        y1 = self.p[1]
        x2 = dest[0]
        y2 = dest[1]
        phi = math.pi * xrot / 180

        tx = (x1 - x2) / 2
        ty = (y1 - y2) / 2
        x1p, y1p = self._arc_matrix_mul(phi, tx, ty, -1)

        cr = x1p ** 2 / rx**2 + y1p**2 / ry**2
        if cr > 1:
            s = math.sqrt(cr)
            rx *= s
            ry *= s

        dq = rx**2 * y1p**2 + ry**2 * x1p**2
        pq = (rx**2 * ry**2 - dq) / dq
        cpm = math.sqrt(max(0, pq))
        if large == sweep:
            cpm = -cpm
        cp = NVector(cpm * rx * y1p / ry, -cpm * ry * x1p / rx)
        c = NVector(*self._arc_matrix_mul(phi, cp[0], cp[1])) + NVector((x1+x2)/2, (y1+y2)/2)
        theta1 = self._arc_angle(NVector(1, 0), NVector((x1p - cp[0]) / rx, (y1p - cp[1]) / ry))
        deltatheta = self._arc_angle(
            NVector((x1p - cp[0]) / rx, (y1p - cp[1]) / ry),
            NVector((-x1p - cp[0]) / rx, (-y1p - cp[1]) / ry)
        ) % (2*math.pi)

        if not sweep and deltatheta > 0:
            deltatheta -= 2*math.pi
        elif sweep and deltatheta < 0:
            deltatheta += 2*math.pi

        r = NVector(rx, ry)
        angle1 = theta1
        angle_left = abs(deltatheta)
        step = math.pi / 2
        sign = -1 if theta1+deltatheta < angle1 else 1

        self._do_add_p()
        # We need to fix the first handle
        firststep = min(angle_left, step) * sign
        alpha = self._arc_alpha(firststep)
        q1 = self._arc_derivative(c, r, phi, angle1) * alpha
        self.path.out_point[-1] = q1.to_list()
        tolerance = step / 2
        # Then we iterate until the angle has been completed
        while angle_left > tolerance:
            lstep = min(angle_left, step)
            step_sign = lstep * sign
            angle2 = angle1 + step_sign
            angle_left -= abs(lstep)

            alpha = self._arc_alpha(step_sign)
            if angle_left <= tolerance:
                p2 = dest
            else:
                p2 = self._arc_point(c, r, phi, angle2)
            q2 = -self._arc_derivative(c, r, phi, angle2) * alpha

            self.path.add_smooth_point(
                p2.to_list(),
                q2.to_list(),
            )
            angle1 = angle2
        self.path.out_point[-1] = [0, 0]
        self.p = dest

    def _parse_a(self):
        if self.la_type != 1:
            self.next_token()
            return
        r = self.cur_vec()
        xrot = self.next_token()
        large = self.next_token()
        sweep = self.next_token()
        dest = self.p + self.next_vec()
        self._do_arc(r[0], r[1], xrot, large, sweep, dest)
        self.implicit = "a"
        self.next_token()

    def _parse_Z(self):
        if self.path.vertices:
            self.p = NVector(*self.path.vertices[0])
        self.path.close()
        self._push_path()

    def _parse_z(self):
        self._parse_Z()


def parse_svg_etree(etree, *args, **kwargs):
    parser = SvgParser()
    return parser.parse_etree(etree, *args, **kwargs)


def parse_svg_file(file, *args, **kwargs):
    return parse_svg_etree(ElementTree.parse(file), *args, **kwargs)
