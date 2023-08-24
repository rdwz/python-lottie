#!/usr/bin/env python3
import io
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
from lottie.parsers.figma.to_lottie import message_to_lottie
from lottie.exporters.core import export_lottie


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
    "--figma",
    "-f",
    default=None,
    type=pathlib.Path,
    help="Path to write the internal figma file to",
)
parser.add_argument(
    "file",
    type=pathlib.Path,
    help="Path to the figma file",
    nargs="?",
)
parser.add_argument(
    "--blob",
    default=[],
    nargs=2,
    action="append",
    help="Extract a blob",
)
parser.add_argument(
    "--clipboard",
    "-c",
    action="store_true",
    help="Extract data from the clipboard"
)
parser.add_argument(
    "--lottie",
    "-l",
    default=None,
    type=pathlib.Path,
    help="Path to write the converted lottie to",
)

args = parser.parse_args()


if args.clipboard:
    from PyQt5.QtWidgets import QApplication

    app = QApplication([])
    clipboard = app.clipboard()
    html = clipboard.mimeData().html()

    file = FigmaFile()
    if not file.load_clipboard_data(html):
        sys.stderr.write("No clipboard data\n")
        sys.exit(1)
else:
    with open(args.file, "rb") as f:
        file = FigmaFile()
        file.load(f)

if args.output:
    with open(args.output, "w") as f:
        json.dump(file.data, f, indent=4, default=json_encode)

if args.schema:
    with open(args.schema, "w") as f:
        file.schema.write_text_schema(f)

if args.binary_schema:
    with open(args.binary_schema, "wb") as f:
        file.schema.write_binary_schema(f)

for index, filename in args.blob:
    with open(filename, "wb") as f:
        f.write(file.data.blobs[int(index)].bytes)

if args.lottie:
    anim = message_to_lottie(file.data, file.schema.module)

    with open(args.lottie, "w") as f:
        export_lottie(anim, f, pretty=True)

if args.figma:
    with open(args.figma, "wb") as f:
        file.write_data(f)
