#!/usr/bin/env python3
import sys
import os
import math
sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "lib"
))
from lottie.utils import script, charts
from lottie import Color

chart = charts.Chart()
chart.data.add(0.5, Color(1, 0, 0))
chart.data.add(0.3, Color(0, 1, 0))
chart.data.add(0.7, Color(0, 0, 1))
chart.compute_animation(150, 50, 30)
chart.order = charts.RandomOrder()

chart.data.normalize_values(True)
chart.type = charts.Pie()

animation = chart.animation()
animation.out_point = 180
script.script_main(animation)

