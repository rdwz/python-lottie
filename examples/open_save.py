#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "lib"
))
from lottie.importers.svg import import_svg
from lottie.exporters.core import export_lottie


# All import/export functions can take file names or file objects

animation = import_svg(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "blep.svg"
))

export_lottie(animation, "open_save.json")
