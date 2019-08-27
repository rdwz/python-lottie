#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "lib"
))
from tgs.utils import script
from tgs import objects
from tgs.parsers.svg import parse_svg_file
from tgs.utils.color import ManagedColor

last_frame = 60
an = parse_svg_file(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "blep.svg"
), last_frame)

layer = an.find("durg")

n_frames = 24

for fill in layer.find_all((objects.Fill, objects.Stroke)):
    color = ManagedColor.from_color(fill.color.value).convert(ManagedColor.Mode.HSV)
    for frame in range(n_frames):
        off = frame / (n_frames-1)
        color.hue = (color.hue + 1 / (n_frames-1)) % 1
        fill.color.add_keyframe(off * last_frame, color.converted(ManagedColor.Mode.RGB).vector)

script.script_main(an)
