from . import model, schema
from ... import objects


def comp_layers_to_figma(comp: objects.animation.Composition, parent: model.FigmaNode, time):
    from_index = {}
    all = []

    for layer in comp.layers:
        canvas = layer_to_figma(layer, time)
        if layer.index is not None:
            from_index[layer.index] = canvas
        all.append((layer, canvas))

    for layer, canvas in all:
        if layer.parent_index is not None:
            from_index[layer.parent_index].add_child(canvas)
        else:
            parent.add_child(canvas)


def animation_to_figma(obj, time):
    doc = model.Document()
    doc.name = obj.name
    comp_layers_to_figma(obj, doc, time)
    return doc


def transform_to_figma(obj: objects.helpers.Transform, time, auto_orient):
    mat = obj.to_matrix(time, auto_orient)
    return schema.Matrix(
        mat.a, mat.b, mat.tx,
        mat.c, mat.d, mat.ty,
    )


def empty_layer_to_figma(obj: objects.layers.Layer, time):
    fig = model.Canvas()
    fig.name = obj.name
    fig.visible = not obj.hidden
    fig.transform = transform_to_figma(obj.transform, time, obj.auto_orient)
    return fig


class EnumMapping:
    def __init__(self, figma_default, mapping=None):
        self.figma_enum = type(figma_default)
        self.figma_default = figma_default
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


blend_mode_mapping = EnumMapping(schema.BlendMode.PASS_THROUGH)


def visual_layer_to_figma(obj: objects.layers.VisualLayer, time):
    fig = empty_layer_to_figma(obj, time)
    fig.blendMode = blend_mode_mapping.to_figma(obj.blend_mode)
    return fig


def style_to_figma(obj, time):
    if isinstance(obj, objects.shapes.Gradient):
        # TODO
        fig = model.SolidPaint(schema.Color(1, 1, 1, 1))
    else:
        c = obj.color.get_value(time)
        fig = model.SolidPaint(schema.color(c.r, c.g, c.b, 1))

    fig.opacity = obj.opacity.get_value(time) / 100
    fig.blendMode = blend_mode_mapping.to_figma(obj.blend_mode)

    return fig


def shapes_to_figma(shapes, time):
    fig_shapes = []
    strokes = []
    fills = []
    stroke_style = None

    for shape in shapes:
        if isinstance(shape, objects.shapes.Shape):
            fig = shape_to_figma(shape, time)
            if fig:
                fig_shapes.append(fig)
        elif isinstance(shape, objects.shapes.BaseStroke):
            strokes.append(style_to_figma(shape))
            stroke_style = shape
        elif isinstance(shape, (objects.shapes.Fill, objects.shapes.GradientFill)):
            fills.append(style_to_figma(shape))

    for shape in fig_shapes:
        shape.fillPaints = fills
        shape.strokePaints = strokes
        if stroke_style:
            shape.miterLimit = stroke_style.miter_limit
            shape.strokeWeight = stroke_style.width.get_value(time)
            # TODO: dashes cap join

    return fig_shapes


def shape_layer_to_figma(obj: objects.layers.ShapeLayer, time):
    fig = visual_layer_to_figma(obj, time)
    for shape in shapes_to_figma(obj.shapes, time):
        fig.add_child(shape)


def rect_to_figma(obj: objects.shapes.Rect, time):
    fig = model.RoundedRectangle()
    p = obj.position.get_value(time)
    fig.transform = model.translated(fig.transform, p.x, p.y)
    s = obj.size.get_value(time)
    fig.size.x = s.x
    fig.size.y = s.y
    r = obj.rounded.get_value(time)
    fig.rectangleTopLeftCornerRadius = r
    fig.rectangleBottomLeftCornerRadius = r
    fig.rectangleBottomRightCornerRadius = r
    fig.rectangleTopRightCornerRadius = r
    return fig


def ellipse_to_figma(obj: objects.shapes.Ellipse, time):
    fig = model.Ellipse()
    p = obj.position.get_value(time)
    fig.transform = model.translated(fig.transform, p.x, p.y)
    s = obj.size.get_value(time)
    fig.size.x = s.x
    fig.size.y = s.y
    return fig


def path_to_figma(obj: objects.shapes.Path, time):
    fig = model.Vector()
    sz = obj.bounding_box(time)
    fig.size.x = sz.x
    fig.size.y = sz.y

    bez = obj.shape.get_value(time)
    fig.bezier.closed = bez.closed

    for point in bez.points:
        fig.bezier.add_point(
            point.vertex,
            point.in_tangent,
            point.out_tangent
        )
    return fig


def star_to_figma(obj: objects.shapes.Star, time):
    rad = obj.outer_radius.get_value(time)

    if obj.type == objects.shapes.StarType.Star:
        fig = model.Star()
        fig.starInnerScale = obj.inner_radius.get_value(time) / rad
    else:
        fig = model.RegularPolygon()

    fig.size.x = fig.size.y = rad
    fig.count = obj.points.get_value(time)
    fig.cornerRadius = obj.outer_radius.get_value(time)

    # TODO: rotation
    p = obj.position.get_value(time)
    fig.transform = model.translated(fig.transform, p.x, p.y)

    return fig

def group_to_figma(obj: objects.shapes.Group, time):
    shapes = shapes_to_figma(obj.shapes, time)

    fig = model.Frame()
    fig.visible = not obj.hidden
    fig.name = obj.name
    fig.blendMode = blend_mode_mapping.to_figma(obj.blend_mode)

    for shape in shapes:
        fig.add_child(shape)

    fig.transform = transform_to_figma(obj.transform, time, False)
    return fig


def layer_to_figma(obj, time):
    if isinstance(obj, objects.layers.ShapeLayer):
        return shape_layer_to_figma(obj, time)
    elif isinstance(obj, objects.layers.ImageLayer):
        return image_layer_to_figma(obj, time)
    elif isinstance(obj, objects.layers.SolidColorLayer):
        return solid_layer_to_figma(obj, time)
    elif isinstance(obj, objects.layers.VisualLayer):
        return visual_layer_to_figma(obj, time)
    elif isinstance(obj, objects.layers.Layer):
        return empty_layer_to_figma(obj, time)


def shape_to_figma(obj, time):
    if isinstance(obj, objects.shapes.Rect):
        return rect_to_figma(obj, time)
    elif isinstance(obj, objects.shapes.Ellipse):
        return ellipse_to_figma(obj, time)
    elif isinstance(obj, objects.shapes.Path):
        return path_to_figma(obj, time)
    elif isinstance(obj, objects.shapes.Star):
        return star_to_figma(obj, time)
    elif isinstance(obj, objects.shapes.Group):
        return group_to_figma(obj, time)
