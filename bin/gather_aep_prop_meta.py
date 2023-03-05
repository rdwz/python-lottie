import os
import sys
import argparse
import dataclasses
sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "lib"
))
from lottie.importers.aep import RiffList, AepParser

mn_category = {
    "ADBE Marker": "marker",
    "ADBE Fresnel Coefficient": "scalar",
    "ADBE Transp Rolloff": "scalar",
    "ADBE Opacity": "scalar",
    "ADBE Vector Shape Direction": "enum",
    "ADBE Extrsn Depth": "scalar",
    "ADBE Vector Stroke Width": "scalar",
    "ADBE Hole Bevel Depth": "scalar",
    "ADBE Vector Stroke Line Cap": "enum",
    "ADBE Vector Shape": "shape",
    "ADBE Vector Grad Colors": "grad",
    "ADBE Vector Star Type": "enum",
    "ADBE Vector Position": "pos",
    "ADBE Glossiness Coefficient": "scalar",
    "ADBE Appears in Reflections": "enum",
    "ADBE Vector Trim Start": "scalar",
    "ADBE Anchor Point": "pos",
    "ADBE Vector Scale": "multi",
    "ADBE Bevel Direction": "enum",
    "ADBE Vector Fill Color": "color",
    "ADBE Vector Star Outer Radius": "scalar",
    "ADBE Vector Rect Roundness": "scalar",
    "ADBE Bevel Styles": "enum",
    "ADBE Rotate Y": "scalar",
    "ADBE Transparency Coefficient": "scalar",
    "ADBE Orientation": "orientation",
    "ADBE Camera Zoom": "scalar",
    "ADBE Position_1": "scalar",
    "ADBE Vector Trim Offset": "scalar",
    "ADBE Vector Grad End Pt": "pos",
    "ADBE Rotate Z": "scalar",
    "ADBE Vector Star Inner Roundess": "scalar",
    "ADBE Position_2": "scalar",
    "ADBE Vector Stroke Color": "color",
    "ADBE Position": "pos",
    "ADBE Envir Appear in Reflect": "enum",
    "ADBE Vector Ellipse Size": "multi",
    "ADBE Bevel Depth": "scalar",
    "ADBE Vector Rect Size": "multi",
    "ADBE Scale": "multi",
    "ADBE Vector Fill Rule": "enum",
    "ADBE Reflection Coefficient": "scalar",
    "ADBE Vector Star Inner Radius": "scalar",
    "ADBE Vector Stroke Line Join": "enum",
    "ADBE Index of Refraction": "scalar",
    "ADBE Vector Grad Start Pt": "pos",
    "ADBE Vector Trim End": "scalar",
    "ADBE Rotate X": "scalar",
    "ADBE Position_0": "scalar",
    "ADBE Vector Stroke Miter Limit": "scalar",
    "ADBE Vector Star Points": "scalar",
    "ADBE Mask Shape": "shape",
    "ADBE Vector Group Opacity": "scalar",
    "ADBE Vector Anchor": "pos",
    "ADBE Time Remapping": "scalar",
    "ADBE Vector Rotation": "scalar",
    "ADBE Vector Merge Type": "enum",
    "ADBE Vector Rect Position": "pos",
    "ADBE Vector Repeater Copies": "scalar",
    "ADBE Vector Repeater Rotation": "scalar",
    "ADBE Vector Repeater Position": "pos",
    "ADBE Vector Repeater Anchor Point": "pos",
    "ADBE Vector Repeater Scale": "multi",
    "ADBE Vector Repeater Start Opacity": "scalar",
    "ADBE Vector Repeater End Opacity": "scalar",
}

@dataclasses.dataclass(frozen=True)
class Prop:
    mn: str
    animated: bool
    category: str
    tdb4: bytes

    def __str__(self):
        return "%s | %s | %s" % (
            self.category,
            "animat" if self.animated else "static",
            self.mn
        )


class Group:
    def __init__(self, title):
        self.title = title
        self.items = []

    def add(self, prop):
        self.items.append(prop)


class CommonBytes:
    def __init__(self):
        self.common = None
        self.different_indexes = set()

    def add(self, data):
        if self.common is None:
            self.common = list(data)
        elif len(self.common) != len(data):
            raise Exception("Length mismatch")
        else:
            for index, value in enumerate(data):
                if self.common[index] != value:
                    self.common[index] = None
                    self.different_indexes.add(index)

    def finalize(self):
        self.different_indexes = sorted(self.different_indexes)

    def extract_diff(self, data):
        diff = []
        for i in self.different_indexes:
            diff.append(data[i])
        return diff



def gather_tdb4(chunk, data, const, mn=None, is_ef=False):
    tdb4 = None
    has_cdat = False

    for sub in chunk.data.children:
        if sub.header == "tdmn":
            mn = sub.data
        elif sub.header == "LIST":
            gather_tdb4(sub, data, const, mn, is_ef or sub.data.type == "sspc")
        elif sub.header == "tdb4":
            tdb4 = sub.data.raw_bytes
        elif sub.header == "cdat":
            has_cdat = True

    if tdb4:
        const.add(tdb4)
        if mn in mn_category:
            cat = mn_category[mn]
        elif mn.startswith("ADBE ") and "Control-" in mn:
            if "Color" in mn:
                cat = "color"
            elif "Point" in mn:
                cat = "pos"
            elif "Slider" in mn:
                cat = "scalar"
            elif "Checkbox" in mn:
                cat = "enum"
            else:
                raise KeyError(mn)
        elif is_ef:
            cat = "effect"
        else:
            raise KeyError(mn)
        data.add(Prop(mn, not has_cdat, cat, tdb4))


def group_by(items, axis, title_tuple, result):
    for prop in items:
        grouping = getattr(prop, axis)
        title = title_tuple + (str(grouping),)
        if title not in result:
            result[title] = Group(grouping)
        result[title].add(prop)


parser = argparse.ArgumentParser()
parser.add_argument("files", nargs="+")
parser.add_argument("--group", "-g", default=[], action="append", choices=["category", "animated", "mn"])
args = parser.parse_args()

# Gather Data
data = set()
const = CommonBytes()
for infile in args.files:
    sys.stderr.write("%s\n" % infile)
    with open(infile, "rb") as f:
        aep_parser = AepParser(f)

        for chunk in aep_parser:
            if isinstance(chunk.data, RiffList):
                gather_tdb4(chunk, data, const)
const.finalize()

# Output Common bytes
for i in range(0, 124, 4):
    for j in range(4):
        if const.common[i+j] is None:
            sys.stdout.write(".. ")
        else:
            sys.stdout.write("%02x " % const.common[i+j])
    sys.stdout.write("\n")

sys.stdout.write("\n")

# Group
group_axes = ["category"] if not args.group else args.group
items = None
for axis in group_axes:
    if items is None:
        items = {}
        group_by(data, axis, tuple(), items)
    else:
        new_items = {}
        for title, subitems in items.values():
            group_by(subitems, axis, title, new_items)
        items = new_items


# Print output
for titles, group in sorted(items.items()):
    print(" ".join(titles))

    group_common = CommonBytes()

    for prop in group.items:
        unique = const.extract_diff(prop.tdb4)
        group_common.add(unique)

    for item in group_common.common:
        if item is None:
            sys.stdout.write(".. ")
        else:
            sys.stdout.write("%02x " % item)
    sys.stdout.write("\n")

    for prop in group.items:
        for index in const.different_indexes:
            sys.stdout.write("%02x " % prop.tdb4[index])

        sys.stdout.write(" %s\n" % prop)

    sys.stdout.write("\n\n")
