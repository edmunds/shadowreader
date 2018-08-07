"""
Copyright 2018 Edmunds.com, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import zlib
import base64


def compress(*, data: str) -> str:
    """ Given a string, compress it, encode it in base64, decode it to string and return it"""
    zipped = _compress_str_to_bytes(data=data)
    zipped = base64.b64encode(zipped)
    zipped = zipped.decode()
    return zipped


def _compress_str_to_bytes(*, data: str) -> bytes:
    """ Compress a string using zlib, returning a bytes object """
    data = data.encode()
    compressed = zlib.compress(data)
    return compressed


def decompress(*, data: str) -> str:
    """ First decode Base64 byte object then decompress it using zlib """
    data = data.encode()
    data = base64.b64decode(data)
    unzipped = _decompress_base64_to_str(data=data)
    return unzipped


def _decompress_base64_to_str(*, data: bytes) -> str:
    """ Decompress a bytes object using zlib """
    decompressed = zlib.decompress(data)
    decompressed = decompressed.decode()
    return decompressed
