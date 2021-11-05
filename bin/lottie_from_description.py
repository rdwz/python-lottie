#!/usr/bin/env python3

import re
import sys
import os
import argparse
sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "lib"
))
from lottie.utils import script
from lottie.utils import funky_parser


arg_parser = script.get_parser()
arg_parser.add_argument("text")
ns = arg_parser.parse_args()

text_parser = funky_parser.Parser(ns.text, funky_parser.Logger())
animation = text_parser.parse()

script.run(animation, ns)
