import math
from collections import namedtuple
from ... import objects
from . import api, ast
from ... import NVector, PolarVector
from ...utils.transform import TransformMatrix

try:
    from ...utils import font
    has_font = True
except ImportError:
    has_font = False


def convert(canvas: api.Canvas):
    return Converter().convert(canvas)


class BoneTransform:
    Snapshot = namedtuple("Snapshot", ["time", "origin", "angle", "scalelx", "scalex"])

    def __init__(self):
        self.snapshots = []
        self.cache = {}

    def add_snapshot(self, snapshot: Snapshot):
        self.snapshots.append(snapshot)

    def closest(self, time):
        if time <= self.snapshots[0].time:
            return self.snapshots[0]
        if time >= self.snapshots[-1].time:
            return self.snapshots[-1]

        for i in range(1, len(self.snapshots)):
            if self.snapshots[i].time > time:
                return self.snapshots[i-1]


class Converter:
    def __init__(self):
        pass

    def _animated(self, sifval):
        return isinstance(sifval, ast.SifAnimated)

    def convert(self, canvas: api.Canvas):
        self.canvas = canvas
        self.animation = objects.Animation(
            self._time(canvas.end_time),
            canvas.fps
        )
        self.animation.in_point = self._time(canvas.begin_time)
        self.animation.width = canvas.width
        self.animation.height = canvas.height
        self.view_p1 = NVector(canvas.view_box[0], canvas.view_box[1])
        self.view_p2 = NVector(canvas.view_box[2], canvas.view_box[3])
        self.target_size = NVector(canvas.width, canvas.height)
        self.shape_layer = self.animation.add_layer(objects.ShapeLayer())
        self._bone_matrices = {}
        self._process_layers(canvas.layers, self.shape_layer)
        return self.animation

    def _time(self, t: api.FrameTime):
        return self.canvas.time_to_frames(t)

    def _process_layers(self, layers, parent):
        for layer in reversed(layers):
            if not layer.active:
                continue
            elif isinstance(layer, api.GroupLayerBase):
                parent.add_shape(self._convert_group(layer))
            elif isinstance(layer, api.RectangleLayer):
                parent.add_shape(self._convert_fill(layer, self._convert_rect))
            elif isinstance(layer, api.CircleLayer):
                parent.add_shape(self._convert_fill(layer, self._convert_circle))
            elif isinstance(layer, api.StarLayer):
                parent.add_shape(self._convert_fill(layer, self._convert_star))
            elif isinstance(layer, api.PolygonLayer):
                parent.add_shape(self._convert_fill(layer, self._convert_polygon))
            elif isinstance(layer, api.RegionLayer):
                parent.add_shape(self._convert_fill(layer, self._convert_bline))
            elif isinstance(layer, api.AbstractOutline):
                parent.add_shape(self._convert_outline(layer, self._convert_bline))
            elif isinstance(layer, api.GradientLayer):
                parent.add_shape(self._convert_gradient(layer, parent))
            elif isinstance(layer, api.TransformDown):
                shape = self._convert_transform_down(layer)
                parent.add_shape(shape)
                parent = shape
            elif isinstance(layer, api.TextLayer):
                if has_font:
                    parent.add_shape(self._convert_fill(layer, self._convert_text))

    def _convert_group(self, layer: api.GroupLayer):
        shape = objects.Group()
        self._set_name(shape, layer)
        shape.transform.anchor_point = self._adjust_coords(self._convert_vector(layer.origin))
        self._convert_transform(layer.transformation, shape.transform)
        self._process_layers(layer.layers, shape)
        shape.transform.opacity = self._adjust_animated(
            self._convert_scalar(layer.amount),
            lambda x: x*100
        )
        return shape

    def _bone_transform(self, bone):
        if bone not in self._bone_matrices:
            transform = BoneTransform()
            tgso = self._adjust_coords(self._convert_vector(bone.origin))
            tgsa = self._adjust_angle(self._convert_scalar(bone.angle))
            tgsscalelx = self._convert_scalar(bone.scalelx)
            tgsscalex = self._convert_scalar(bone.scalex)
            for vals in self._mix_animations(tgso, tgsa, tgsscalelx, tgsscalex):
                transform.add_snapshot(BoneTransform.Snapshot(*vals))
            self._bone_matrices[bone] = transform
        else:
            transform = self._bone_matrices[bone]

        return transform

    def _bone_transform_keyframes(self, bone):
        if not isinstance(bone, api.Bone):
            return set()

        return set(s.time for s in self._bone_transform(bone).snapshots) | self._bone_transform_keyframes(bone.parent)

    def _bone_transform_snapshot(self, bone, time, child_origin=None):
        if not isinstance(bone, api.Bone):
            return TransformMatrix()

        transform = self._bone_transform(bone)
        if time in transform.cache:
            matrix = transform.cache[time].clone()
        else:
            snapshot = transform.closest(time)
            matrix = self._bone_transform_snapshot(bone.parent, time, snapshot.origin)
            matrix.rotate(snapshot.angle / 180 * math.pi)
            matrix.scale(snapshot.scalex, 1)

            transform.cache[time] = matrix.clone()

        if child_origin:
            matrix.translate(child_origin.x * snapshot.scalelx, child_origin.y)

        return matrix

    def _bone_animated_transform(self, bone):
        for time in sorted(self._bone_transform_keyframes(bone)):
            yield time, self._bone_transform_snapshot(bone, time)

    def _convert_transform(self, sif_transform: api.AbstractTransform, lottie_transform: objects.Transform):
        if isinstance(sif_transform, api.BoneLinkTransform):
            base_transform = sif_transform.base_value
        else:
            base_transform = sif_transform

        position = self._adjust_coords(self._convert_vector(base_transform.offset))
        rotation = self._adjust_angle(self._convert_scalar(base_transform.angle))
        scale = self._adjust_animated(
            self._convert_vector(base_transform.scale),
            lambda x: x * 100
        )

        lottie_transform.skew_axis = self._adjust_angle(self._convert_scalar(base_transform.skew_angle))

        if isinstance(sif_transform, api.BoneLinkTransform):
            #lottie_transform.position = position
            #lottie_transform.rotation = rotation
            #lottie_transform.scale = scale

            ap = lottie_transform.anchor_point.value
            lottie_transform.anchor_point.value = NVector(0, 0)

            for time, matrix in self._bone_animated_transform(sif_transform.bone):
                base_matrix = TransformMatrix()
                base_pos = position.get_value(time)
                base_scale = scale.get_value(time)
                base_matrix.translate(base_pos.x, base_pos.y)
                base_matrix.scale(base_scale.x / 100, base_scale.y / 100)
                base_matrix.rotation(math.radians(rotation.get_value(time)))

                matrix *= base_matrix
                trans = matrix.extract_transform()

                lottie_transform.position.add_keyframe(time, trans["translation"])
                lottie_transform.skew_axis.add_keyframe(time, math.degrees(trans["skew_axis"]))
                lottie_transform.skew.add_keyframe(time, -math.degrees(trans["skew_angle"]))
                lottie_transform.rotation.add_keyframe(time, math.degrees(trans["angle"]))
                lottie_transform.scale.add_keyframe(time, trans["scale"] * 100.)
        else:
            lottie_transform.position = position
            lottie_transform.rotation = rotation
            lottie_transform.scale = scale

    def _mix_animations_into(self, animations, output, mix):
        if not any(x.animated for x in animations):
            output.value = mix(*(x.value for x in animations))
        else:
            for vals in self._mix_animations(*animations):
                time = vals.pop(0)
                output.add_keyframe(time, mix(*vals))

    def _convert_fill(self, layer, converter):
        shape = objects.Group()
        self._set_name(shape, layer)
        shape.add_shape(converter(layer))
        if layer.invert.value:
            shape.add_shape(objects.Rect(self.target_size/2, self.target_size))

        fill = objects.Fill()
        fill.color = self._convert_color(layer.color)
        fill.opacity = self._adjust_animated(
            self._convert_scalar(layer.amount),
            lambda x: x * 100
        )
        shape.add_shape(fill)
        return shape

    def _convert_linecap(self, lc: api.LineCap):
        if lc == api.LineCap.Rounded:
            return objects.LineCap.Round
        if lc == api.LineCap.Squared:
            return objects.LineCap.Square
        return objects.LineCap.Butt

    def _convert_cusp(self, lc: api.CuspStyle):
        if lc == api.CuspStyle.Miter:
            return objects.LineJoin.Miter
        if lc == api.CuspStyle.Bevel:
            return objects.LineJoin.Bevel
        return objects.LineJoin.Round

    def _convert_outline(self, layer: api.AbstractOutline, converter):
        shape = objects.Group()
        self._set_name(shape, layer)
        shape.add_shape(converter(layer))
        stroke = objects.Stroke()
        stroke.color = self._convert_color(layer.color)
        stroke.line_cap = self._convert_linecap(layer.start_tip)
        stroke.line_join = self._convert_cusp(layer.cusp_type)
        stroke.width = self._adjust_scalar(self._convert_scalar(layer.width))
        shape.add_shape(stroke)
        return shape

    def _convert_rect(self, layer: api.RectangleLayer):
        rect = objects.Rect()
        p1 = self._adjust_coords(self._convert_vector(layer.point1))
        p2 = self._adjust_coords(self._convert_vector(layer.point2))
        if p1.animated or p2.animated:
            for time, p1v, p2v in self._mix_animations(p1, p2):
                rect.position.add_keyframe(time, (p1v + p2v) / 2)
                rect.size.add_keyframe(time, abs(p2v - p1v))
            pass
        else:
            rect.position.value = (p1.value + p2.value) / 2
            rect.size.value = abs(p2.value - p1.value)
        rect.rounded = self._adjust_scalar(self._convert_scalar(layer.bevel))
        return rect

    def _convert_circle(self, layer: api.CircleLayer):
        shape = objects.Ellipse()
        shape.position = self._convert_coord_vector(layer.origin)
        radius = self._adjust_scalar(self._convert_scalar(layer.radius))
        shape.size = self._adjust_add_dimension(radius, lambda x: NVector(x, x) * 2)
        return shape

    def _convert_star(self, layer: api.StarLayer):
        shape = objects.Star()
        shape.position = self._adjust_coords(self._convert_vector(layer.origin))
        shape.inner_radius = self._adjust_scalar(self._convert_scalar(layer.radius2))
        shape.outer_radius = self._adjust_scalar(self._convert_scalar(layer.radius1))
        shape.rotation = self._adjust_animated(
            self._convert_scalar(layer.angle),
            lambda x: 90-x
        )
        shape.points = self._convert_scalar(layer.points)
        if layer.regular_polygon.value:
            shape.star_type = objects.StarType.Polygon
        return shape

    def _mix_animations(self, *animatable):
        times = set()
        for v in animatable:
            self._force_animated(v)
            for kf in v.keyframes:
                times.add(kf.time)

        for time in sorted(times):
            yield [time] + [v.get_value(time) for v in animatable]

    def _force_animated(self, lottieval):
        if not lottieval.animated:
            v = lottieval.value
            lottieval.add_keyframe(0, v)
            lottieval.add_keyframe(self.animation.out_point, v)

    def _convert_animatable(self, v: ast.SifAstNode, lot: objects.properties.AnimatableMixin):
        if self._animated(v):
            if len(v.keyframes) == 1:
                lot.value = self._convert_ast_value(v.keyframes[0].value)
            else:
                for kf in v.keyframes:
                    # TODO easing
                    lot.add_keyframe(self._time(kf.time), self._convert_ast_value(kf.value))
        else:
            lot.value = self._convert_ast_value(v)
        return lot

    def _convert_ast_value(self, v):
        if isinstance(v, ast.SifRadialComposite):
            return self._polar(v.radius.value, v.theta.value, 1)
        elif isinstance(v, ast.SifValue):
            return v.value
        elif isinstance(v, ast.SifVectorComposite):
            return NVector(v.x.value, v.y.value)
        else:
            return v

    def _converted_vector_values(self, v):
        if isinstance(v, ast.SifRadialComposite):
            return [self._convert_scalar(v.radius), self._convert_scalar(v.theta)]
        return self._convert_vector(v)

    def _convert_color(self, v: ast.SifAstNode):
        return self._convert_animatable(v, objects.ColorValue())

    def _convert_vector(self, v: ast.SifAstNode):
        return self._convert_animatable(v, objects.MultiDimensional())

    def _convert_coord_vector(self, v: ast.SifAstNode):
        if isinstance(v, ast.SifAstBoneLink):
            base = self._convert_coord_vector(v.base_value)
            print(base)
            animated = objects.MultiDimensional()
            for time, matrix in self._bone_animated_transform(v.bone):
                print((time, matrix.apply(base.get_value(time))))
                animated.add_keyframe(time, matrix.apply(base.get_value(time)))
            print("")
            return animated
        else:
            return self._adjust_coords(self._convert_vector(v))

    def _convert_scalar(self, v: ast.SifAstNode):
        return self._convert_animatable(v, objects.Value())

    def _adjust_animated(self, lottieval, transform):
        if lottieval.animated:
            for kf in lottieval.keyframes:
                if kf.start is not None:
                    kf.start = transform(kf.start)
                if kf.end is not None:
                    kf.end = transform(kf.end)
        else:
            lottieval.value = transform(lottieval.value)
        return lottieval

    def _adjust_scalar(self, lottieval: objects.Value):
        return self._adjust_animated(lottieval, self._scalar_mult)

    def _adjust_angle(self, lottieval: objects.Value):
        return self._adjust_animated(lottieval, lambda x: -x)

    def _adjust_add_dimension(self, lottieval, transform):
        to_val = objects.MultiDimensional()
        to_val.animated = lottieval.animated
        if lottieval.animated:
            to_val.keyframes = []
            for kf in lottieval.keyframes:
                if kf.start is not None:
                    kf.start = transform(kf.start[0])
                if kf.end is not None:
                    kf.end = transform(kf.end[0])
                to_val.keyframes.append(kf)
        else:
            to_val.value = transform(lottieval.value)
        return to_val

    def _scalar_mult(self, x):
        return x * 60

    def _adjust_coords(self, lottieval: objects.MultiDimensional):
        return self._adjust_animated(lottieval, self._coord)

    def _coord(self, val: NVector):
        return NVector(
            self.target_size.x * (val.x / (self.view_p2.x - self.view_p1.x) + 0.5),
            self.target_size.y * (val.y / (self.view_p2.y - self.view_p1.y) + 0.5),
        )

    def _convert_polygon(self, layer: api.PolygonLayer):
        lot = objects.Path()
        animatables = [self._convert_vector(layer.origin)] + [
            self._convert_vector(p)
            for p in layer.points
        ]
        animated = any(x.animated for x in animatables)
        if not animated:
            lot.shape.value = self._polygon([x.value for x in animatables[1:]], animatables[0].value)
        else:
            for values in self._mix_animations(*animatables):
                time = values[0]
                origin = values[1]
                points = values[2:]
                lot.shape.add_keyframe(time, self._polygon(points, origin))
        return lot

    def _polygon(self, points, origin):
        bezier = objects.Bezier()
        bezier.closed = True
        for point in points:
            bezier.add_point(self._coord(point+origin))
        return bezier

    def _convert_bline(self, layer: api.AbstractOutline):
        lot = objects.Path()
        closed = layer.bline.loop
        animatables = [
            self._convert_vector(layer.origin)
        ]
        for p in layer.bline.points:
            animatables += [
                self._convert_vector(p.point),
                self._convert_scalar(p.t1.radius) if hasattr(p.t1, "radius") else objects.Value(0),
                self._convert_scalar(p.t1.theta) if hasattr(p.t1, "radius") else objects.Value(0),
                self._convert_scalar(p.t2.radius) if hasattr(p.t2, "radius") else objects.Value(0),
                self._convert_scalar(p.t2.theta) if hasattr(p.t2, "radius") else objects.Value(0)
            ]
        animated = any(x.animated for x in animatables)
        if not animated:
            lot.shape.value = self._bezier(closed, [x.value for x in animatables[1:]], animatables[0].value, layer.bline.points)
        else:
            for values in self._mix_animations(*animatables):
                time = values[0]
                origin = values[1]
                values = values[2:]
                lot.shape.add_keyframe(time, self._bezier(closed, values, origin, layer.bline.points))
        return lot

    def _bezier(self, closed, values, origin, points):
        chunk_size = 5
        bezier = objects.Bezier()
        bezier.closed = closed
        for i in range(0, len(values), chunk_size):
            point, r1, a1, r2, a2 = values[i:i+chunk_size]
            sifvert = point+origin
            vert = self._coord(sifvert)
            if not points[i//chunk_size].split_radius.value:
                r2 = r1
            if not points[i//chunk_size].split_angle.value:
                a2 = a1
            t1 = self._coord(sifvert + self._polar(r1, a1, 1)) - vert
            t2 = self._coord(sifvert + self._polar(r2, a2, 2)) - vert
            bezier.add_point(vert, t1, t2)
        return bezier

    def _polar(self, radius, angle, dir):
        offset_angle = 0
        if dir == 1:
            offset_angle += 180
        return PolarVector(radius/3, (angle+offset_angle) * math.pi / 180)

    def _convert_transform_down(self, tl: api.TransformDown):
        group = objects.Group()
        self._set_name(group, tl)

        if isinstance(tl, api.TranslateLayer):
            group.transform.anchor_point.value = self.target_size / 2
            group.transform.position = self._adjust_coords(self._convert_vector(tl.origin))
        elif isinstance(tl, api.RotateLayer):
            group.transform.anchor_point = self._adjust_coords(self._convert_vector(tl.origin))
            group.transform.position = group.transform.anchor_point.clone()
            group.transform.rotation = self._adjust_angle(self._convert_scalar(tl.amount))
        elif isinstance(tl, api.ScaleLayer):
            group.transform.anchor_point = self._adjust_coords(self._convert_vector(tl.center))
            group.transform.position = group.transform.anchor_point.clone()
            group.transform.scale = self._adjust_add_dimension(
                self._convert_scalar(tl.amount),
                self._zoom_to_scale
            )

        return group

    def _zoom_to_scale(self, value):
        zoom = math.e ** value * 100
        return NVector(zoom, zoom)

    def _set_name(self, lottie, sif):
        lottie.name = sif.desc if sif.desc is not None else sif.__class__.__name__

    def _convert_gradient(self, layer: api.GradientLayer, parent):
        group = objects.Group()

        parent_shapes = parent.shapes
        parent.shapes = []
        if isinstance(parent, objects.Group):
            parent.shapes.append(parent_shapes[-1])

        self._gradient_gather_shapes(parent_shapes, group)

        gradient = objects.GradientFill()
        self._set_name(gradient, layer)
        group.add_shape(gradient)
        gradient.colors = self._convert_gradient_stops(layer.gradient)
        gradient.opacity = self._adjust_animated(
            self._convert_scalar(layer.amount),
            lambda x: x * 100
        )

        if isinstance(layer, api.LinearGradient):
            gradient.start_point = self._adjust_coords(self._convert_vector(layer.p1))
            gradient.end_point = self._adjust_coords(self._convert_vector(layer.p2))
            gradient.gradient_type = objects.GradientType.Linear
        elif isinstance(layer, api.RadialGradient):
            gradient.gradient_type = objects.GradientType.Radial
            gradient.start_point = self._adjust_coords(self._convert_vector(layer.center))
            radius = self._adjust_animated(self._convert_scalar(layer.radius), lambda x: x*45)
            if not radius.animated and not gradient.start_point.animated:
                gradient.end_point.value = gradient.start_point.value + NVector(radius.value, radius.value)
            else:
                for time, c, r in self._mix_animations(gradient.start_point.clone(), radius):
                    gradient.end_point.add_keyframe(time, c + NVector(r + r))

        return group

    def _gradient_gather_shapes(self, shapes, output: objects.Group):
        for shape in shapes:
            if isinstance(shape, objects.Shape):
                output.add_shape(shape)
            elif isinstance(shape, objects.Group):
                self._gradient_gather_shapes(shape.shapes, output)

    def _convert_gradient_stops(self, sif_gradient):
        stops = objects.GradientColors()
        if not self._animated(sif_gradient):
            stops.set_stops(self._flatten_gradient_colors(sif_gradient.value))
            stops.count = len(sif_gradient.value)
        else:
            # TODO easing
            for kf in sif_gradient.keyframes:
                stops.add_keyframe(self._time(kf.time), self._flatten_gradient_colors(kf.value))
                stops.count = len(kf.value)

        return stops

    def _flatten_gradient_colors(self, stops):
        return [
            (stop.pos, stop.color)
            for stop in stops
        ]

    def _convert_text(self, layer: api.TextLayer):
        shape = font.FontShape(layer.text.value, font.FontStyle(layer.family.value, 110, font.TextJustify.Center))
        shape.refresh()
        trans = shape.wrapped.transform
        trans.anchor_point.value = shape.wrapped.bounding_box().center()
        trans.anchor_point.value.x /= 2
        trans.position = self._adjust_coords(self._convert_vector(layer.origin))
        trans.scale = self._adjust_animated(
            self._convert_vector(layer.size),
            lambda v: v * 100
        )
        return shape
