from .base import importer
from ..parsers.baseporter import ExtraOption
from ..parsers.pixel import pixel_to_animation_paths, pixel_to_animation
from ..parsers.svg.importer import parse_color

try:
    from ..parsers.raster import raster_to_animation
    raster = True
except ImportError:
    raster = False


@importer("Raster image", ["bmp", "png", "gif", "webp", "tiff"], [
    ExtraOption("n_colors", type=int, default=1, help="Number of colors to quantize"),
    ExtraOption("palette", type=parse_color, default=[], nargs="+", help="Custom palette"),
    ExtraOption(
        "mode",
        default="pixel",
        choices=["pixel", "polygon"] + (["bezier"] if raster else []),
        help="Vectorization mode"
    ),
    ExtraOption("frame_delay", type=int, default=4, help="Number of frames to skip between images"),
    ExtraOption("framerate", type=int, default=60, help="Frames per second"),
    ExtraOption("frame_files", nargs="+", default=[], help="Additional frames to import"),
    ExtraOption(
        "color_mode",
        default="nearest",
        choices=["nearest", "exact"],
        help="How to quantize colors." +
             "nearest will map each color to the most similar in the palette." +
             " exact will only match exact colors"
    ),
])
def import_raster(filenames, n_colors, palette, mode, frame_delay=1, framerate=60, frame_files=[], color_mode="nearest"):
    if not isinstance(filenames, list):
        filenames = [filenames]
    filenames = filenames + frame_files

    if mode == "bezier":
        from ..parsers.raster import QuanzationMode
        # TODO QuanzationMode for raster
        cm = QuanzationMode.Nearest if ns.color_mode == "nearest" else QuanzationMode.Exact

        return raster_to_animation(
            filenames, n_colors, frame_delay,
            framerate=framerate,
            palette=palette,
            mode=cm
        )
    elif mode == "polygon":
        return pixel_to_animation_paths(filenames, frame_delay, framerate)
    else:
        return pixel_to_animation(filenames, frame_delay, framerate)

