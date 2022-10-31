#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from base64 import b64encode;
from base64 import b64decode;
from getpass import getpass;
from glob import glob;
from hashlib import sha256;
from lazy_load import lazy;
from shutil import make_archive;
from zlib import compress as zlib_compress;
from zlib import decompress as zlib_decompress;

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MODIFICATIONS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def read_file(path: str) -> str:
    with open(path, 'r') as fp:
        lines = ''.join(fp.readlines());
    return lines;

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [
    'b64decode',
    'b64encode',
    'getpass',
    'glob',
    'lazy',
    'make_archive',
    'read_file',
    'sha256',
    'zlib_compress',
    'zlib_decompress',
];
