#!/usr/bin/env python3
import os
import sys
import json
import enum
import pathlib
import argparse
sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "lib"
))
from lottie.parsers.figma.file import FigmaFile
from lottie.parsers.figma.kiwi import json_encode


parser = argparse.ArgumentParser(
    description="Extract data from a figma file"
)
parser.add_argument(
    "--output",
    "-o",
    default=None,
    help="Path to write the data to",
)
parser.add_argument(
    "file",
    type=pathlib.Path,
    help="Path to the figma file",
)

args = parser.parse_args()

with open(args.file, "rb") as f:
    file = FigmaFile()
    file.load(f)


def open_output(mode):
    if args.output is None:
        return os.fdopen(sys.stdout.fileno(), mode, closefd=False)
    else:
        return open(args.output, mode)


with open_output("w") as f:
    json.dump(file.data, f, indent=4, default=json_encode)

