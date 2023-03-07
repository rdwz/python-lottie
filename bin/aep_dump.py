#!/usr/bin/env python3
import os
import sys
import enum
import argparse
from xml.etree import ElementTree
from PIL import ImageCms
sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "lib"
))
from lottie.importers.aep import RiffList, StructuredData, AepParser, aepx_to_chunk


def format_bytes(val, bytes_fmt):
    if bytes_fmt == ByteOutputMode.Hex or (bytes_fmt == ByteOutputMode.HexChar and len(val) < 4):
        return " ".join("%02x" % c for c in val)
    elif bytes_fmt == ByteOutputMode.HexChar:
        char = ""
        hex = []
        for c in val:
            hex.append("%02x" % c)
            char += chr(c) if 32 <= c <= 126 else " "
        hexs = " ".join(hex)
        if char.strip():
            hexs += " " + char.rstrip()
        return hexs

    naked = str(val)[2:-1]
    naked = naked.replace(r'"', r'\"')
    return "\"%s\"" % naked


def value_to_yaml(val, wrap_bytes, bytes_fmt, indent):
    if isinstance(val, bytes):
        if len(val) <= wrap_bytes:
            return format_bytes(val, bytes_fmt)
        formatted = ""
        for i in range(0, len(val), wrap_bytes):
            if i == 0:
                formatted += format_bytes(val[0:wrap_bytes], bytes_fmt) + "\n"
            else:
                formatted += indent + format_bytes(val[i:i+wrap_bytes], bytes_fmt) + "\n"
        return formatted[:-1]
    elif isinstance(val, ImageCms.ImageCmsProfile):
        return ImageCms.getProfileName(val).strip()

    return val


def chunk_to_yaml(file, chunk, wrap_bytes, bytes_fmt, indp=""):
    ind = indp + ("- " if indp else "")
    if isinstance(chunk.data, RiffList):
        file.write("%s%s: %s\n" % (ind, chunk.header, chunk.data.type))
        for sub in chunk.data.children:
            chunk_to_yaml(file, sub, wrap_bytes, bytes_fmt, indp + "    ")
    else:
        structured_value_to_yaml(file, chunk.header, chunk.data, wrap_bytes, bytes_fmt, indp)


def structured_value_to_yaml(file, title, value, wrap_bytes, bytes_fmt, indp):
    ind = indp + ("- " if indp else "")
    items = []

    if isinstance(value, dict):
        print_data = ""
        items = value.items()
    elif isinstance(value, StructuredData):
        print_data = ""
        items = [(k, v) for k, v in vars(value).items() if k != "raw_bytes"]
    elif isinstance(value, (list, tuple)):
        if len(value) < 10 and len(value) > 0 and isinstance(value[0], (int, float)):
            print_data = value
        else:
            print_data = ""
            items = [("", it) for it in value]
    else:
        print_data = value

    if title:
        file.write("%s%s: %s\n" % (ind, title, value_to_yaml(print_data, wrap_bytes, bytes_fmt, indp + " " * (4+len(title)))))
    else:
        file.write("%s%s\n" % (ind, value_to_yaml(print_data, wrap_bytes, bytes_fmt, indp + "  ")))

    for k, v in items:
        structured_value_to_yaml(file, "" if k.startswith("_") else k, v, wrap_bytes, bytes_fmt, indp + "    ")


class ByteOutputMode(enum.Enum):
    String = "string"
    Hex = "hex"
    HexChar = "hex-char"


parser = argparse.ArgumentParser(
    description="Dump an AEP file into sort of readable Yaml"
)
parser.add_argument(
    "infile",
    help="Input file"
)
parser.add_argument(
    "--wrap-bytes",
    "-w",
    default=4,
    type=int,
    help="When to wrap long sequences of bytes"
)
parser.add_argument(
    "--xmp",
    action="store_true",
    help="If present, dump the XMP data after the RIFX data"
)
parser.add_argument(
    "--bytes", "-b",
    choices=ByteOutputMode.__members__.values(),
    help="Raw data mode",
    default=ByteOutputMode.HexChar,
    type=ByteOutputMode,
)

parser.add_argument(
    "--output", "-o",
    help="Output file name"
)

args = parser.parse_args()

with open(args.infile, "rb") as f:
    head = f.read(3)
    f.seek(0)

    if head == b'RIF':
        aep_parser = AepParser(f)
        root = aep_parser.parse()
    else:
        dom = ElementTree.parse(f)
        aep_parser = AepParser(None)
        root = aepx_to_chunk(dom.getroot(), aep_parser)

    with open(args.output or os.path.splitext(args.infile)[0]+".yml", "w") as of:
        for chunk in root.data.children:
            chunk_to_yaml(of, chunk, args.wrap_bytes, args.bytes)

        if args.xmp:
            of.write("ProjectXMPMetadata: _\n")
            of.write(f.read().decode("utf8"))
