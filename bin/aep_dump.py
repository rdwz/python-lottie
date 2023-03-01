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
        return "\"%s\"" % str(val)[2:-1]
    return val


def chunk_to_yaml(chunk, indp=""):
    ind = indp + ("- " if indp else "")
    if isinstance(chunk.data, RiffList):
        print("%s%s: %s" % (ind, chunk.header, chunk.data.type))
        for sub in chunk.data.children:
            chunk_to_yaml(sub, indp + "    ")
    else:
        dict_data = {}

        if isinstance(chunk.data, dict):
            print_data = ""
            dict_data = chunk.data
        elif isinstance(chunk.data, StructuredData):
            print_data = ""
            dict_data = vars(chunk.data)
        else:
            print_data = chunk.data

        print("%s%s: %s" % (ind, chunk.header, value_to_yaml(print_data)))

        for k, v in dict_data.items():
            if k[0] != "_":
                print("%s    - %s: %s" % (indp, k, value_to_yaml(v)))
            else:
                print("%s    - %s" % (indp, value_to_yaml(v)))



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
