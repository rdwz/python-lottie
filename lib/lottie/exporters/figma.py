from .base import exporter
from ..parsers.baseporter import ExtraOption
from ..parsers.figma.from_lottie import animation_to_figma


@exporter("Figma", ["fig"], [], {"frame"})
def export_figma(animation, file, frame=0):
    document = animation_to_figma(animation, frame)
    fig = document.to_figma_file()
    fig.write_zip(file)
