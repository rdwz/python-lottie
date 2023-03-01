#!/usr/bin/env python3

import sys
import os
import argparse
sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "lib"
))
from lottie.importers.aep import RiffList, StructuredData, AepParser


def value_to_yaml(val):
    if isinstance(val, bytes):
        naked = str(val)[2:-1]
        naked = naked.replace(r'"', r'\"')
        return "\"%s\"" % naked
    return val


def chunk_to_yaml(chunk, indp=""):
    ind = indp + ("- " if indp else "")
    if isinstance(chunk.data, RiffList):
        print("%s%s: %s" % (ind, chunk.header, chunk.data.type))
        for sub in chunk.data.children:
            chunk_to_yaml(sub, indp + "    ")
    else:
        structured_value_to_yaml(chunk.header, chunk.data, indp)


def structured_value_to_yaml(title, value, indp):
    ind = indp + ("- " if indp else "")
    items = []

    if isinstance(value, dict):
        print_data = ""
        items = value.items()
    elif isinstance(value, StructuredData):
        print_data = ""
        items = vars(value).items()
    elif isinstance(value, (list, tuple)):
        if len(value) < 5 and len(value) > 0 and isinstance(value[0], (int, float)):
            print_data = value
        else:
            print_data = ""
            items = [("", it) for it in value]
    else:
        print_data = value

    if title:
        print("%s%s: %s" % (ind, title, value_to_yaml(print_data)))
    else:
        print("%s%s" % (ind, value_to_yaml(print_data)))

    for k, v in items:
        structured_value_to_yaml("" if k.startswith("_") else k, v, indp + "    ")




parser = argparse.ArgumentParser(
    description="Dump an AEP file into sort of readable Yaml"
)
parser.add_argument(
    "infile",
    help="Input file"
)

with open(parser.parse_args().infile, "rb") as f:
    aep_parser = AepParser(f)

    for chunk in aep_parser:
        chunk_to_yaml(chunk)
