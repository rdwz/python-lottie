import io
import re
import zlib
import json
import struct
import base64
import zipfile
import PIL.Image

from .kiwi import Schema, module_to_schema
from . import schema


def read_uint32le(file):
    return struct.unpack("<i", file.read(4))[0]


def write_uint32le(file, v):
    file.write(struct.pack("<i", v))


def inflate_raw(data):
    decompress = zlib.decompressobj(-15)
    decompressed_data = decompress.decompress(data)
    decompressed_data += decompress.flush()
    return decompressed_data


def deflate_raw(data):
    compress = zlib.compressobj(
        zlib.Z_DEFAULT_COMPRESSION,
        zlib.DEFLATED,
        -15,
        memLevel=8,
        strategy=zlib.Z_DEFAULT_STRATEGY
    )
    compressed_data = compress.compress(data)
    compressed_data += compress.flush()
    return compressed_data


class FigmaFile:
    default_gray_value = 0.9607843160629272
    _default_schema = None

    @classmethod
    def default_schema(cls):
        if cls._default_schema is None:
            cls._default_schema = module_to_schema(schema)
        return cls._default_schema

    def __init__(self):
        self.schema = Schema()
        self.data = None
        self.assets = {}
        self.version = 30
        self.meta = {
            "client_meta": {
                "background_color": {
                    "r": self.default_gray_value,
                    "g": self.default_gray_value,
                    "b": self.default_gray_value,
                    "a": 1
                },
                "thumbnail_size": {
                    "width": 512,
                    "height": 512
                },
                "render_coordinates": {
                    "x": 0,
                    "y": 0,
                    "width": 512,
                    "height": 512
                }
            },
            "file_name": "Untitled",
            "developer_related_links": []
        }
        self.thumbnail = None
        self._schema_root = None

    @property
    def schema_root(self):
        if self._schema_root is None:
            self._schema_root = self.schema["Message"]
        return self._schema_root

    def load_data(self, file):
        header = file.read(8)
        if header != b'fig-kiwi':
            raise Exception("Could not load %s" % header)
        self.version = read_uint32le(file)
        schema = self._read_chunk(file)
        self.schema.read_binary_schema(schema)
        data = self._read_chunk(file)
        self.data = self.schema_root.read_data(data, self.schema)

    def _read_chunk(self, file):
        size = read_uint32le(file)
        data = file.read(size)
        if data.startswith(b'\x28\xb5\x2f\xfd'):
            raise Exception("ZSTDDecoder not supported")
        return io.BytesIO(inflate_raw(data))

    def load_zip(self, file):
        with zipfile.ZipFile(file) as zf:
            for info in zf.infolist():
                if info.filename == "canvas.fig":
                    with zf.open(info) as f:
                        self.load_data(f)
                elif info.filename == "meta.json":
                    with zf.open(info) as f:
                        self.meta = json.load(f)
                elif info.filename == "thumbnail.png":
                    with zf.open(info) as f:
                        self.thumbnail = PIL.Image.open(f)
                elif info.filename.startswith("images/") and not info.is_dir():
                    with zf.open(info) as f:
                        self.assets[info.filename.split("/", 1)[1]] = PIL.Image.open(f)

    def load(self, file):
        header = file.read(4)
        file.seek(0)
        if header == b'PK\3\4':
            self.load_zip(file)
        else:
            self.load_data(file)

    def write_data(self, file):
        file.write(b'fig-kiwi')

        write_uint32le(file, self.version)

        schema = io.BytesIO()
        self.schema.write_binary_schema(schema)
        self._write_chunk(file, schema)

        data = io.BytesIO()
        self.schema_root.write_data(data, self.schema, self.data)
        self._write_chunk(file, data)

    def _write_chunk(self, file, bio):
        data = deflate_raw(bio.getvalue())
        write_uint32le(file, len(data))
        file.write(data)

    def write_zip(self, file):
        with zipfile.ZipFile(file, "w") as zf:
            zf.writestr("meta.json", json.dumps(self.meta))

            if self.thumbnail:
                with zf.open("thumbnail.png", "w") as f:
                    self.thumbnail.save(f, "PNG")

            # f = io.BytesIO()
            # self.write_data(f)
            # zf.writestr("canvas.fig", f.getvalue())
            with zf.open("canvas.fig", "w") as f:
                self.write_data(f)

    def load_clipboard_data(self, html):
        match = re.search(r'\(figma\)(.*)\(/figma\)', html)
        if not match:
            return False

        base_encoded = match.group(1)
        data = base64.b64decode(base_encoded)
        self.load_data(io.BytesIO(data))
        return True
