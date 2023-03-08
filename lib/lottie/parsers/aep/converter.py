import os
import enum

from ... import objects
from ...nvector import NVector
from ...utils.color import Color
from .gradient_xml import parse_gradient_xml


def convert_value_color(arr):
    return Color(arr[1] / 255, arr[2] / 255, arr[3] / 255, arr[0] / 255)


def shape_with_defaults(cls, **defaults):
    def callback():
        obj = cls()
        for k, v in defaults.items():
            prop = getattr(obj, k)
            if isinstance(prop, objects.properties.AnimatableMixin):
                prop.value = v
            else:
                setattr(obj, k, v)
        return obj

    return callback


class PropertyPolicyMultidim:
    def __init__(self, converter=lambda x: x):
        self.converter = converter

    def static(self, cdat):
        if len(cdat.data.value) == 1:
            return self.converter(NVector(*cdat.data.value))[0]
        else:
            return self.converter(NVector(*cdat.data.value))

    def keyframe(self, keyframe, index):
        return self.converter(NVector(*keyframe.value))


class PropertyPolicyPrepared:
    def __init__(self, values):
        self.values = values

    def static(self, cdat):
        return self.values[0]

    def keyframe(self, keyframe, index):
        return self.values[index]


class AepConverter:
    placeholder = "-_0_/-"
    shapes = {
        "ADBE Vector Group": objects.shapes.Group,

        "ADBE Vector Shape - Group": objects.shapes.Path,
        "ADBE Vector Shape - Rect": objects.shapes.Rect,
        "ADBE Vector Shape - Star": objects.shapes.Star,
        "ADBE Vector Shape - Ellipse": objects.shapes.Ellipse,

        "ADBE Vector Graphic - Stroke": shape_with_defaults(
            objects.shapes.Stroke,
            width=2,
            color=Color(1, 1, 1),
            line_cap=objects.shapes.LineCap.Butt,
            line_join=objects.shapes.LineJoin.Miter,
            miter_limit=4,
        ),
        "ADBE Vector Graphic - Fill": shape_with_defaults(
            objects.shapes.Fill,
            color=Color(1, 0, 0),
            fill_rule=objects.shapes.FillRule.NonZero,
        ),
        "ADBE Vector Graphic - G-Fill": objects.shapes.GradientFill,
        "ADBE Vector Graphic - G-Stroke": objects.shapes.GradientStroke,

        "ADBE Vector Filter - Merge": objects.shapes.Merge,
        "ADBE Vector Filter - Offset": objects.shapes.OffsetPath,
        "ADBE Vector Filter - PB": objects.shapes.PuckerBloat,
        "ADBE Vector Filter - Repeater": objects.shapes.Repeater,
        "ADBE Vector Filter - RC": objects.shapes.RoundedCorners,
        "ADBE Vector Filter - Trim": objects.shapes.Trim,
        "ADBE Vector Filter - Twist": objects.shapes.Twist,
        "ADBE Vector Filter - Zigzag": objects.shapes.ZigZag,
    }
    properties = {
        "ADBE Time Remapping": ("time_remapping", None),

        "ADBE Vector Shape": ("shape", None),
        "ADBE Vector Shape Direction": ("direction", objects.shapes.ShapeDirection),
        "ADBE Vector Rect Roundness": ("rounded", None),
        "ADBE Vector Rect Size": ("size", None),
        "ADBE Vector Rect Position": ("position", None),
        "ADBE Vector Ellipse Size": ("size", None),
        "ADBE Vector Ellipse Position": ("position", None),

        "ADBE Vector Star Type": ("star_type", objects.shapes.StarType),
        "ADBE Vector Star Points": ("points", None),
        "ADBE Vector Star Position": ("position", None),
        "ADBE Vector Star Inner Radius": ("inner_radius", None),
        "ADBE Vector Star Outer Radius": ("outer_radius", None),
        "ADBE Vector Star Inner Roundess": ("inner_roundness", None),
        "ADBE Vector Star Outer Roundess": ("outer_roundness", None),
        "ADBE Vector Star Rotation": ("rotation", None),

        "ADBE Vector Fill Color": ("color", convert_value_color),

        "ADBE Vector Stroke Color": ("color", convert_value_color),
        "ADBE Vector Stroke Width": ("width", None),
        "ADBE Vector Stroke Miter Limit": ("animated_miter_limit", None),
        "ADBE Vector Stroke Line Cap": ("line_cap", objects.shapes.LineCap),
        "ADBE Vector Stroke Line Join": ("line_join", objects.shapes.LineJoin),

        "ADBE Vector Grad Start Pt": ("start_point", None),
        "ADBE Vector Grad End Pt": ("end_point", None),
        "ADBE Vector Grad Colors": ("colors", None),

        "ADBE Vector Merge Type": ("merge_mode", objects.shapes.MergeMode),

        "ADBE Vector Offset Amount": ("amount", None),
        "ADBE Vector Offset Line Join": ("line_join", objects.shapes.LineJoin),
        "ADBE Vector Offset Miter Limit": ("miter_limit", None),

        "ADBE Vector PuckerBloat Amount": ("amount", None),

        "ADBE Vector Repeater Copies": ("copies", None),
        "ADBE Vector Repeater Offset": ("offset", None),
        "ADBE Vector Repeater Order": ("composite", objects.shapes.Composite),
        #"ADBE Vector Repeater Transform": ??
        "ADBE Vector Repeater Anchor Point": ("anchor_point", None),
        "ADBE Vector Repeater Position": ("position", None),
        "ADBE Vector Repeater Rotation": ("rotation", None),
        "ADBE Vector Repeater Start Opacity": ("start_opacity", lambda v: v * 100),
        "ADBE Vector Repeater End Opacity": ("end_opacity", lambda v: v * 100),
        "ADBE Vector Repeater Scale": ("scale", lambda v: v * 100),

        "ADBE Vector RoundCorner Radius": ("radius", None),

        "ADBE Vector Trim Start": ("start", None),
        "ADBE Vector Trim End": ("end", None),
        "ADBE Vector Trim Offset": ("offset", None),

        "ADBE Vector Twist Angle": ("angle", None),
        "ADBE Vector Twist Center": ("center", None),

        "ADBE Vector Zigzag Size": ("amplitude", None),
        "ADBE Vector Zigzag Detail": ("frequency", None),

        "ADBE Anchor Point": ("anchor_point", None),
        "ADBE Position": ("position", None),
        "ADBE Rotate Z": ("rotation", None),
        "ADBE Opacity": ("opacity", lambda v: v * 100),
        "ADBE Scale": ("scale", lambda v: v * 100),

        "ADBE Vector Anchor Point": ("anchor_point", None),
        "ADBE Vector Position": ("position", None),
        "ADBE Vector Rotation": ("rotation", None),
        "ADBE Vector Group Opacity": ("opacity", None),
        "ADBE Vector Scale": ("scale", None),
    }

    class AssetType(enum.Enum):
        Comp = enum.auto()
        Solid = enum.auto()
        Image = enum.auto()

    class ParsedAsset:
        def __init__(self, id, name, type, block, data):
            self.id = id
            self.name = name
            self.block = block
            self.data = data
            self.parsed_object = None

    def __init__(self):
        self.time_mult = 1
        self.time_offset = 0
        self.assets = {}
        self.comps = {}
        self.layers = {}

    def read_properties(self, object, chunk):
        match_name = None
        for item in chunk.data.children:
            # Match name
            if item.header == "tdmn":
                match_name = item.data
            # Name
            elif item.header == "tdsn" and len(item.data.children) > 0:
                name = item.data.children[0]
                if name.header == "Utf8" and name.data != self.placeholder and name.data:
                    object.name = name.data
            # Shape hidden
            elif item.header == "tdsb":
                if (item.data & 1) == 0:
                    object.hidden = True
            # MultiDimensional property
            elif item.header == "LIST" and item.data.type == "tdbs":
                self.parse_property_multidimensional(object, match_name, item)
            # Shape property
            elif item.header == "LIST" and item.data.type == "om-s":
                self.parse_property_shape(object, match_name, item)
            # Sub-object
            elif item.header == "LIST" and item.data.type == "tdgp":
                if match_name == "ADBE Vectors Group" or match_name == "ADBE Root Vectors Group":
                    self.read_properties(object, item)
                elif match_name == "ADBE Vector Transform Group" or match_name == "ADBE Transform Group":
                    self.read_properties(object.transform, item)
                elif match_name in self.shapes:
                    child = self.shapes[match_name]()
                    object.add_shape(child)
                    child.match_name = match_name
                    self.read_properties(child, item)
            # Gradients
            elif item.header == "LIST" and item.data.type == "GCst" and match_name == "ADBE Vector Grad Colors":
                prop = object.colors.colors
                for i, grad in enumerate(item.data.find_list("GCky").data.children):
                    if grad.header == "Utf8":
                        if not prop.animated:
                            prop.value = parse_gradient_xml(grad.data, object.colors)
                            break
                        elif len(prop.keyframes) < i:
                            prop.keyframes[i].value = parse_gradient_xml(grad.data, object.colors)

    def parse_property_multidimensional(self, object, match_name, chunk):
        meta = self.properties.get(match_name)
        if not meta:
            return

        prop_name, converter = meta
        policy = PropertyPolicyMultidim()
        if converter is not None:
            policy.converter = converter

        prop = objects.properties.MultiDimensional()
        self.parse_property_tbds(chunk, prop, policy)

        setattr(object, prop_name, prop)

    def parse_property_tbds(self, chunk, prop, policy):
        static, kf, expr = chunk.data.find_multiple("cdat", "list", "Utf8")

        if static:
            prop.value = policy.static(static)

        if kf:
            self.set_property_keyframes(prop, policy, kf)

        if expr:
            # TODO should convert expressions the same way that bodymovin does
            prop.expression = expr.data

    def time(self, value):
        return (value + self.time_offset) * self.time_mult

    def set_property_keyframes(self, prop, policy, chunk):
        ldat = chunk.data.find("ldat")
        if ldat and hasattr(ldat.data, "keyframes"):
            for index, keyframe in enumerate(ldat.data.keyframes):
                if keyframe.attrs == b'\0':
                    prop.add_keyframe(self.time(keyframe.time), policy.keyframe(keyframe, index))

        if len(prop.keyframes) == 1:
            prop.clear_animation(prop.keyframes[0].start)

    def parse_property_shape(self, object, match_name, chunk):
        meta = self.properties.get(match_name)
        if not meta:
            return

        prop_name = meta[0]

        prop = objects.properties.ShapeProperty()

        policy = PropertyPolicyPrepared([])
        tbds, omks = chunk.data.find_multiple("tdbs", "omks")

        self.parse_shape_omks(omks, policy)
        self.parse_property_tbds(tbds, prop, policy)

        setattr(object, prop_name, prop)

    def parse_shape_omks(self, chunk, policy):
        for item in chunk.data.children:
            if item.header == "LIST" and item.data.type == "shap":
                policy.values.append(self.parse_shape_shap(item))

    def parse_shape_shap(self, chunk):
        bez = objects.bezier.Bezier()
        shph, list = chunk.data.find_multiple("shph", "list")

        top_left = shph.data.top_left
        bottom_right = shph.data.bottom_right
        bez.closed = not shph.data.open

        points = list.data.find("ldat").data.points
        for i in range(0, len(points), 3):
            vertex = self.absolute_bezier_point(top_left, bottom_right, points[i])
            tan_in = self.absolute_bezier_point(top_left, bottom_right, points[(i-1) % len(points)])
            tan_ou = self.absolute_bezier_point(top_left, bottom_right, points[i+1])
            print(i, vertex, tan_in, tan_ou)
            bez.add_point(vertex, tan_in - vertex, tan_ou - vertex)
        return bez

    def absolute_bezier_point(self, tl, br, p):
        return NVector(
            tl[0] * (1-p.x) + br[0] * p.x,
            tl[1] * (1-p.y) + br[1] * p.y
        )

    def chunk_to_layer(self, chunk):
        lottie_obj = objects.layers.ShapeLayer()
        lottie_obj.transform.position.value = NVector(self.anim.width / 2, self.anim.height / 2)

        for item in chunk.data.children:
            if item.header == "Utf8":
                lottie_obj.name = item.data
            elif item.header == "ldta":
                self.time_offset = item.data.start_time
                lottie_obj.start_time = self.time_offset * self.time_mult
                lottie_obj.in_point = self.time(item.data.in_time)
                lottie_obj.out_point = self.time(item.data.out_time)
                lottie_obj.threedimensional = item.data.ddd
                lottie_obj.hidden = not item.data.visible
            elif item.header == "LIST":
                self.read_properties(lottie_obj, item)

        return lottie_obj

    def item_chunk_to_animation(self, chunk):
        anim = objects.Animation()
        self.anim = anim

        for item in chunk.data.children:
            if item.header == "Utf8":
                anim.name = item.data
            elif item.header == "cdta":
                anim.width = item.data.width
                anim.height = item.data.height
                anim.frame_rate = item.data.frame_rate
                self.time_mult = 1 / item.data.time_scale
                self.time_offset = 0
                anim.in_point = self.time(item.data.start_time)
                if item.data.end_time == 0xffff:
                    anim.out_point = self.time(item.data.comp_duration)
                else:
                    anim.out_point = self.time(item.data.end_time)
            elif item.header == "LIST" and item.data.type == "Layr":
                anim.layers.append(self.chunk_to_layer(item))

        return anim

    def items_from_fold(self, fold):
        for chunk in fold.data.children:
            if chunk.header == "LIST" and chunk.data.type == "Item":
                item_data = chunk.data.find("idta").data
                name = chunk.data.find("Utf8").data
                if item_data.type == 1:
                    self.items_from_fold(chunk)
                    return
                elif item_data.type == 4:
                    type = self.AssetType.Comp
                    self.comps[name] = item_data.id
                    data = chunk.data.find("cdta").data
                elif item_data.type == 7:
                    pin = chunk.find("Pin ").data
                    opti = pin.find("opti")

                    if opti.type == "Soli":
                        type = self.AssetType.Solid
                        name = name or opti.name
                        data = opti
                    else:
                        type = self.AssetType.Image
                        filename = pin.find("Als2").data.find("alas").data["fullpath"]
                        name = name or os.path.basename(filename)
                        sspc = pin.find("sspc").data
                        data = {
                            "width": sspc.width,
                            "height": sspc.height,
                            "filename": filename
                        }

                self.assets[item_data.id] = self.ParsedAsset(item_data.id, name, type, chunk, data)

    def import_aep(self, top_level, name):
        self.items_from_fold(top_level.data.find("Fold"))
        if not name:
            id = next(iter(self.comps.values()))
        else:
            id = self.comps[name]

        return self.item_chunk_to_animation(self.assets[id].block)
