from . import model, schema, enum_mapping
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
    doc.name = obj.name or "Unnamed"
    page = model.Canvas()
    doc.add_child(page)
    page.name = obj.name or "Page"
    comp_layers_to_figma(obj, page, time)
    return doc


def transform_to_figma(obj: objects.helpers.Transform, time, auto_orient):
    mat = obj.to_matrix(time, auto_orient)
    return schema.Matrix(
        m00=mat.a,
        m01=mat.c,
        m02=mat.ty,
        m10=mat.b,
        m11=mat.d,
        m12=mat.tx,
    )


def empty_layer_to_figma(obj: objects.layers.Layer, time):
    fig = model.Canvas()
    fig.name = obj.name or "Layer"
    fig.visible = not obj.hidden
    fig.transform = transform_to_figma(obj.transform, time, obj.auto_orient)
    return fig


def visual_layer_to_figma(obj: objects.layers.VisualLayer, time):
    fig = empty_layer_to_figma(obj, time)
    fig.blendMode = enum_mapping.blend_mode.to_figma(obj.blend_mode)
    return fig


def style_to_figma(obj, time):
    if isinstance(obj, objects.shapes.Gradient):
        # TODO
        fig = model.SolidPaint(schema.Color(1, 1, 1, 1))
    else:
        c = obj.color.get_value(time)
        fig = model.SolidPaint(schema.Color(c.r, c.g, c.b, 1))

    fig.opacity = obj.opacity.get_value(time) / 100
    fig.blendMode = enum_mapping.blend_mode.to_figma(obj.blend_mode)

    return fig


def shapes_to_figma(shapes, time):
    fig_shapes = []
    strokes = []
    fills = []
    stroke_style = None

    for shape in shapes:
        if isinstance(shape, objects.shapes.BaseStroke):
            strokes.append(style_to_figma(shape, time))
            stroke_style = shape
        elif isinstance(shape, (objects.shapes.Fill, objects.shapes.GradientFill)):
            fills.append(style_to_figma(shape, time))
        else:
            fig = shape_to_figma(shape, time)
            if fig:
                fig_shapes.append(fig)

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
    return fig


def rect_to_figma(obj: objects.shapes.Rect, time):
    fig = model.RoundedRectangle()
    fig.name = obj.name or "Rectangle"
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
    fig.name = obj.name or "Ellipse"
    p = obj.position.get_value(time)
    fig.transform = model.translated(fig.transform, p.x, p.y)
    s = obj.size.get_value(time)
    fig.size.x = s.x
    fig.size.y = s.y
    return fig


def path_to_figma(obj: objects.shapes.Path, time):
    fig = model.Vector()
    fig.name = obj.name or "Shape"
    sz = obj.bounding_box(time)
    fig.size.x = sz.width
    fig.size.y = sz.height

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
        fig.name = obj.name or "Star"
        fig.starInnerScale = obj.inner_radius.get_value(time) / rad
    else:
        fig = model.RegularPolygon()
        fig.name = obj.name or "Polygon"

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
    fig.name = obj.name or "Group"
    fig.blendMode = enum_mapping.blend_mode.to_figma(obj.blend_mode)

    for shape in shapes:
        fig.add_child(shape)

    fig.transform = transform_to_figma(obj.transform, time, False)
    return fig


def layer_to_figma(obj, time):
    if isinstance(obj, objects.layers.ShapeLayer):
        return shape_layer_to_figma(obj, time)
    # elif isinstance(obj, objects.layers.ImageLayer):
        # return image_layer_to_figma(obj, time)
    # elif isinstance(obj, objects.layers.SolidColorLayer):
        # return solid_layer_to_figma(obj, time)
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
