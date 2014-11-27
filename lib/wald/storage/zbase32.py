#!/usr/bin/env python

""" zbase32 provides a simple implementation of the zbase32
ascii encoding, with support for very large numbers. """

#   This file is part of wald:meta, a generic database for linked data.
#   Copyright (C) 2008-2013  Kuno Woudt <kuno@frob.nl>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of copyleft-next 0.3.0.  See LICENSE.txt.

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

# from http://zooko.com/repos/z-base-32/base32/DESIGN
_MNET32 = "ybndrfg8ejkmcpqxot1uwisza345h769"


def _shift5 (i):
    if not i:
        yield 0

    while i:
        yield i & 0x1f
        i = i >> 5


def b2a (integer):
    """ binary to ascii (zbase32) conversion. """
    return "".join ([_MNET32[x] for x in _shift5(integer)])


def a2b (string):
    """ ascii (zbase32) to binary conversion. """
    shift = 0
    ret = 0
    for x in string:
        ret |= _MNET32.find (x) << shift
        shift += 5

    return ret
