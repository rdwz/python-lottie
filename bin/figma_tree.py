#!/usr/bin/env python3
import os
import sys
import json
import enum
import pathlib
import argparse
sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "lib"
))
from lottie.parsers.figma.file import FigmaFile


def id_tuple(guid):
    return (guid.localID, guid.sessionID)


class NodeLink:
    nodes = {}

    def __init__(self, id):
        self.changes = None
        self.id = id
        self.children = []

    @classmethod
    def node(cls, guid):
        id = id_tuple(guid)
        if id in cls.nodes:
            return cls.nodes[id]

        node = cls(id)
        cls.nodes[id] =  node
        return node

    def print(self, indent):
        print("%s%s %s" % (indent, self.changes.type, self.changes.name))
        self.print_children(" " * 4 + indent)

    def print_children(self, indent):
        for child in self.children:
            child.print(indent)


parser = argparse.ArgumentParser(
    description="Show tree structure of a figma file"
)
parser.add_argument(
    "file",
    type=pathlib.Path,
    help="Path to the figma file",
)

args = parser.parse_args()

with open(args.file, "rb") as f:
    file = FigmaFile()
    file.load(f)


global_node = NodeLink(None)

for change in file.data.nodeChanges:
    if change.parentIndex:
        parent = NodeLink.node(change.parentIndex.guid)
    else:
        parent = global_node

    node = NodeLink.node(change.guid)
    node.changes = change
    parent.children.append(node)

global_node.print_children("")
