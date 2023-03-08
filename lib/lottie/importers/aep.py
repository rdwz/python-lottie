import io

from xml.etree import ElementTree

from .base import importer
from ..parsers.baseporter import ExtraOption
from ..parsers.aep.aep_riff import AepParser
from ..parsers.aep.converter import AepConverter
from ..parsers.aep.aepx import aepx_to_chunk


@importer("AfterEffect Project", ["aep"], [
    ExtraOption("comp", help="Name of the composition to extract", default=None)
], slug="aep")
def import_aep(file, comp=None):
    if isinstance(file, str):
        with open(file, "rb") as fileobj:
            return import_aep(fileobj, comp)

    parser = AepParser(file)
    return AepConverter().import_aep(parser.parse(), comp)


@importer("AfterEffect Project XML", ["aepx"], [
    ExtraOption("comp", help="Name of the composition to extract", default=None)
], slug="aepx")
def import_aepx(file, comp=None):
    dom = ElementTree.parse(file)
    parser = AepParser(None)
    rifx = aepx_to_chunk(dom.getroot(), parser)
    return AepConverter().import_aep(rifx, comp)
