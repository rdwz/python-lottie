#!/usr/bin/env python3
import os
import sys
import pathlib
import argparse
sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "lib"
))
from lottie.parsers.figma.kiwi import Schema
from lottie.utils.script import open_output


parser = argparse.ArgumentParser(
    description="Convert kiwi binary schema to text"
)
parser.add_argument(
    "schema",
    type=pathlib.Path,
    help="Path to the binary schema",
)
parser.add_argument(
    "--output",
    "-o",
    default=None,
    help="Path to write the schema to",
)
parser.add_argument(
    "--binary",
    "-b",
    action="store_true",
    help="Output binary schema",
)
parser.add_argument(
    "--python",
    "-p",
    action="store_true",
    help="Output python module",
)

args = parser.parse_args()

with open(args.schema, "rb") as f:
    schema = Schema()
    schema.read_binary_schema(f)


if args.binary:
    with open_output(args.output, "wb") as f:
        schema.write_binary_schema(f)
elif args.python:
    with open_output(args.output, "w") as f:
        schema.write_python_schema(f)
else:
    with open_output(args.output, "w") as f:
        schema.write_text_schema(f)
