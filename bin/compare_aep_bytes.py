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

    "ADBE Text Document": "text",
    "ADBE Camera Aperture": "scalar",
}


class Prop:

    def __init__(self, raw: bytes, **data):
        self.raw = raw
        self.data = data

    def __str__(self):
        return " | ".join(self.data.values())

    def __hash__(self):
        return hash((self.raw,) + tuple(self.data.values()))


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
        else:
            if len(self.common) != len(data):
                index_min = min(len(self.common), len(data))
                index_max = max(len(self.common), len(data))
                #sys.stderr.write("Length mismatch\n")
            else:
                index_min = len(data)
                index_max = index_min

            for index in range(index_min):
                if self.common[index] != data[index]:
                    self.common[index] = None
                    self.different_indexes.add(index)

            if index_max > len(self.common):
                for index in range(index_min, index_max):
                    self.common.append(None)
                    self.different_indexes.add(index)
            elif index_min < len(self.common):
                for index in range(index_min, index_max):
                    self.common[index] = None
                    self.different_indexes.add(index)

    def finalize(self):
        self.different_indexes = sorted(self.different_indexes)

    def extract_diff(self, data):
        diff = []
        for i in self.different_indexes:
            try:
                diff.append(data[i])
            except IndexError:
                break
        return diff


class Gatherer:
    def process(self, filename, parser, data, const):
        return self.gather(filename, parser.parse(), data, const)


class GatherTdb4(Gatherer):
    default_group = ["category"]

    def gather(self, filename, chunk, data, const, mn=None, is_ef=False):
        if not isinstance(chunk.data, RiffList):
            return

        tdb4 = None
        has_cdat = False

        for sub in chunk.data.children:
            if sub.header == "tdmn":
                mn = sub.data
            elif sub.header == "LIST":
                self.gather(filename, sub, data, const, mn, is_ef or sub.data.type == "sspc")
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
            anim = "animat" if not has_cdat else "static"
            data.add(Prop(tdb4, category=cat, animated=anim, mn=mn, filename=filename))


class GatherSspc(Gatherer):
    default_group = ["type"]

    def gather(self, filename, chunk, data, const, type="??", name="??"):
        if not isinstance(chunk.data, RiffList):
            return

        if chunk.data.type == "Pin ":
            sspc = chunk.data.find("sspc").data.raw_bytes
            opti = chunk.data.find("opti")
            if opti:
                raw_name = opti.data.raw_bytes.strip(b'\0')
                name = ''
                for b in reversed(raw_name):
                    if 32 <= b <= 126:
                        name = chr(b) + name
                    else:
                        break

            const.add(sspc)
            data.add(Prop(sspc, type=type, name=name, filename=filename))
        else:
            for sub in chunk.data.children:
                if sub.header == "LIST":
                    if sub.data.type == "Item":
                        type = sub.data.find("idta").data.type_name
                    self.gather(filename, sub, data, const, type, name)


class GatherLdta(Gatherer):
    default_group = ["type", "asset"]

    def tdgp_mns(self, tdgp):
        mn = set()
        for item in tdgp.data.children:
            if item.header == "tdmn":
                mn.add(item.data)
        return mn

    def gather(self, filename, chunk, data, const):
        if not isinstance(chunk.data, RiffList):
            return

        if chunk.data.type == "Fold":

            self.assets = {}
            for sub in chunk.data.children:
                self.gather_assets(sub)

            for sub in chunk.data.children:
                if sub.header == "LIST":
                    self.gather(filename, sub, data, const)

        elif chunk.data.type == "Layr":

            ldta = chunk.data.find("ldta").data
            name = chunk.data.find("Utf8").data
            if ldta.source_id == 0:
                asset = "    "
            else:
                asset, asname = self.assets[ldta.source_id]
                if not name:
                    name = asname
            match_names = self.tdgp_mns(chunk.data.find("tdgp"))
            if "ADBE Text Properties" in match_names:
                type = "text"
            elif "ADBE Root Vectors Group" in match_names:
                type = "shape"
            elif "ADBE Camera Options Group" in match_names:
                type = "camra"
            elif "ADBE Light Options Group" in match_names:
                type = "light"
            elif asset:
                type = "asset"
            else:
                type = "dunno"

            const.add(ldta.raw_bytes)
            data.add(Prop(ldta.raw_bytes, type=type, asset=asset, name=name, filename=filename))

        else:
            for sub in chunk.data.children:
                if sub.header == "LIST":
                    self.gather(filename, sub, data, const)

    def gather_assets(self, chunk):
        if chunk.header == "LIST" and chunk.data.type == "Item":
            data = chunk.data.find("idta").data
            name = chunk.data.find("Utf8").data
            if data.type == 7:
                opti = chunk.data.find("Pin ").data.find("opti").data
                if not name:
                    name = getattr(opti, "name", "")
                self.assets[data.id] = (opti.type, name)
            elif data.type == 4:
                self.assets[data.id] = ("comp", name)
            elif data.type == 1:
                for sub in chunk.data.find("Sfdr").data.children:
                    self.gather_assets(sub)


class GatherRawTop(Gatherer):
    def __init__(self, header):
        self.header = header

    default_group = []

    def gather(self, filename, chunk, data, const):
        if chunk.header == self.header:
            const.add(chunk.data)
            data.add(Prop(chunk.data, filename=filename))


class GatherLhd3(Gatherer):
    default_group = ["type", "list"]

    def process(self, filename, parser, data, const):
        parser.keep_ldat_bytes = True
        return self.gather(filename, parser.parse(), data, const)

    def gather(self, filename, chunk, data, const, plist="", type="~dunno", mn="", kf="??"):
        if not isinstance(chunk.data, RiffList):
            return

        for sub in chunk.data.children:
            if sub.header == "tdmn":
                mn = sub.data
            elif sub.header == "LIST":
                subtype = type
                subkf = kf
                if sub.data.type == "shap":
                    subtype = "shape"
                elif sub.data.type == "om-s":
                    subkf = "shape"
                elif sub.data.type == "GCst":
                    subkf = "grad"

                sub_pl = plist if sub.data.type == "list" else sub.data.type
                self.gather(filename, sub, data, const, sub_pl, subtype, mn, subkf)
            elif sub.header == "tdb4":
                type = "key"
                if kf == "??":
                    kf = "multi"
                    if sub.data.color:
                        kf = "color"
                    elif sub.data.position:
                        kf = "pos"
                    elif sub.data.special:
                        kf = "special"
                    kf += " %sD" % sub.data.components
            elif sub.header == "lhd3":
                const.add(sub.data.raw_bytes)
                ptype = type
                if type == "key":
                    ptype += " " + kf
                item_size = "?"
                ldat = chunk.data.find("ldat")
                if ldat:
                    item_size = hex(len(ldat.data.raw_bytes) // sub.data.count)
                data.add(Prop(sub.data.raw_bytes, list=plist, type=ptype, item_size=item_size, mn=mn, filename=filename))


def group_by(items, axes, result):
    for prop in items:
        title = tuple(prop.data[axis] for axis in axes)
        if title not in result:
            result[title] = Group(title)
        result[title].add(prop)


parser = argparse.ArgumentParser()
parser.add_argument("files", nargs="+")
parser.add_argument("--what", "-w", default="tdb4")
parser.add_argument("--group", "-g", default=[], action="append")
args = parser.parse_args()

# Gather Data
data = set()
const = CommonBytes()
if args.what in ["head", "svap"]:
    gatherer = GatherRawTop(args.what)
else:
    gatherer = globals()["Gather" + args.what[0].upper() + args.what[1:]]()

for infile in args.files:
    base = os.path.basename(infile)
    sys.stderr.write("%s\n" % infile)
    with open(infile, "rb") as f:
        aep_parser = AepParser(f)
        gatherer.process(base, aep_parser, data, const)

const.finalize()

# Output Common bytes
for i in range(0, len(const.common), 4):
    for j in range(4):
        if const.common[i+j] is None:
            sys.stdout.write(".. ")
        else:
            sys.stdout.write("%02x " % const.common[i+j])
    sys.stdout.write("\n")

sys.stdout.write("\n")

# Group
group_axes = gatherer.default_group if not args.group else args.group
items = {}
group_by(data, group_axes, items)

# Print output
for titles, group in sorted(items.items()):
    print(" ".join(titles))

    group_common = CommonBytes()

    for prop in group.items:
        unique = const.extract_diff(prop.raw)
        group_common.add(unique)

    for item in group_common.common:
        if item is None:
            sys.stdout.write(".. ")
        else:
            sys.stdout.write("%02x " % item)
    sys.stdout.write("\n")

    for prop in group.items:
        for index in const.different_indexes:
            try:
                sys.stdout.write("%02x " % prop.raw[index])
            except IndexError:
                sys.stdout.write("   ")

        sys.stdout.write(" %s\n" % prop)

    sys.stdout.write("\n\n")
