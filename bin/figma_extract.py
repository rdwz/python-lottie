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
    description="Extract data from a figma file"
)
parser.add_argument(
    "--output",
    "-o",
    default=None,
    help="Path to write the data to",
)
parser.add_argument(
    "--schema",
    "-s",
    default=None,
    type=pathlib.Path,
    help="Path to write the text schema to",
)
parser.add_argument(
    "--binary-schema",
    "-b",
    default=None,
    type=pathlib.Path,
    help="Path to write the binary schema to",
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


with open_output(args.output, "w") as f:
    json.dump(file.data, f, indent=4, default=json_encode)

if args.schema:
    with open(args.schema, "w") as f:
        file.schema.write_text_schema(f)

if args.binary_schema:
    with open(args.binary_schema, "wb") as f:
        file.schema.write_binary_schema(f)
