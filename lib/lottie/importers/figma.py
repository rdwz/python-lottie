import pathlib
from .base import importer
from ..parsers.baseporter import ExtraOption
from ..parsers.figma.to_lottie import message_to_lottie
from ..parsers.figma.file import FigmaFile


@importer("Figma", ["fig"], [])
def import_figma(animation, file, frame=0):
    ff = FigmaFile()
    if isinstance(file, (str, pathlib.Path)):
        with open(file, "rb") as f:
            ff.load(f)
    else:
        ff.load(file)

    return message_to_lottie(ff.data, ff.schema.module)
