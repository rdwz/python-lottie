#!/usr/bin/env python3

import re
import os
import sys
import argparse
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(root, "lib"))
from lottie.utils import script
from lottie.utils import funky_parser


parser = script.get_parser()
parser.description = "Generate an animation fron a textual description"
parser.add_argument("text")


if __name__ == "__main__":
    ns = parser.parse_args()

    text_parser = funky_parser.Parser(ns.text, funky_parser.Logger())
    svg_loader = funky_parser.SvgLoader()
    text_parser.svg_shapes.append(funky_parser.SvgShape(
        os.path.join(root, "examples", "blep.svg"),
        ["glax", "blep"],
        {
            "scales": funky_parser.SvgFeature([], ["#3250b0", "#292f75"]),
            "belly": funky_parser.SvgFeature([], ["#c4d9f5"]),
            "eyes": funky_parser.SvgFeature([], ["#f01d0a"]),
            "horns": funky_parser.SvgFeature([], ["#3a3c3f"]),
        },
        "scales",
        1,
        svg_loader
    ))

    animation = text_parser.parse()

    script.run(animation, ns)
