#!/usr/bin/env python3
import os
import sys
import json
import pathlib
import argparse
sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "lib"
))
from lottie.parsers.figma.kiwi import Schema, json_encode
from lottie.utils.script import open_output


parser = argparse.ArgumentParser(
    description="Convert kiwi data to/from JSON"
)
parser.add_argument(
    "--schema",
    type=pathlib.Path,
    required=True,
    help="Path to the binary schema",
)
parser.add_argument(
    "--output",
    "-o",
    default=None,
    help="Path to write the schema to",
)
parser.add_argument(
    "--decode",
    "-d",
    action="store_true",
    help="Decode binary data",
)
parser.add_argument(
    "--root",
    "-r",
    required=True,
    help="Root type",
)
parser.add_argument(
    "data",
    type=pathlib.Path,
    help="Path to the data file",
)

args = parser.parse_args()

with open(args.schema, "rb") as f:
    schema = Schema()
    schema.read_binary_schema(f)

root = schema[args.root]


if args.decode:
    with open(args.data, "rb") as f:
        data = root.read_data(f, schema)

    with open_output(args.output, "w") as f:
        json.dump(data, f, indent=4, default=json_encode)
else:
    with open(args.data, "r") as f:
        data = json.load(f)

    with open_output(args.output, "wb") as f:
        root.write_data(f, schema, data)
