#!/usr/bin/env python3
import os
import sys
import json
import argparse
sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "lib"
))
from lottie.parsers.aep.cos import CosParser


class IndirectEncoder(json.JSONEncoder):
        def default(self, o):
            if isinstance(o, bytes):
                try:
                    return o.decode("utf-8")
                except UnicodeDecodeError:
                    return '"' + str(o).replace("\"", "\\\"")[2:-1] + '"'
            return o.__dict__


parser = argparse.ArgumentParser(
    description="Dump a Carousel Object Storage file into sort of readable JSON"
)
parser.add_argument(
    "infile",
    help="Input file"
)


if __name__ == "__main__":
    args = parser.parse_args()


    with open(args.infile, "rb") as f:
        cosp = CosParser(f)
        json.dump(cosp.parse(), sys.stdout, indent=4, cls=IndirectEncoder)
