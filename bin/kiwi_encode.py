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
from lottie.parsers.figma.kiwi import Schema


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

def open_output(mode):
    if args.output is None:
        return os.fdopen(sys.stdout.fileno(), mode, closefd=False)
    else:
        return open(args.output, mode)

if args.decode:
    with open(args.data, "rb") as f:
        data = root.read_data(f, schema)

    def encode(v):
        if hasattr(type(v), "__slots__"):
            out = {}
            for slot in v.__slots__:
                out[slot] = getattr(v, slot)
            return out
        elif isinstance(v, enum.Enum):
            return v.name
        else:
            return vars(v)

    with open_output("w") as f:
        json.dump(data, f, indent=4, default=encode)
else:
    with open(args.data, "r") as f:
        data = json.load(f)

    with open_output("wb") as f:
        root.write_data(f, schema, data)
