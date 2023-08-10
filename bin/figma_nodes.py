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
from lottie.utils.script import open_output


parser = argparse.ArgumentParser(
    description="Extract node changes from a figma file"
)
parser.add_argument(
    "--output",
    "-o",
    default=None,
    help="Path to write the data to",
)
parser.add_argument(
    "--append",
    "-a",
    action="store_true",
    help="If present, append to existing data",
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

unique = {}


if args.append and args.output and pathlib.Path(args.output).exists:
    with open(args.output) as f:
        unique = json.load(f)

for change in file.data.nodeChanges:
    if change.type.name not in unique:
        unique[change.type.name] = change

with open_output(args.output) as f:
    json.dump(unique, f, indent=4, default=json_encode)
