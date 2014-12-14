#!/usr/bin/env python

#   This file is part of wald:meta
#   Copyright (C) 2014  Kuno Woudt <kuno@frob.nl>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of copyleft-next 0.3.0.  See LICENSE.txt.

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import re

WHITESPACE_BEFORE_PAREN_REGEX = re.compile (r'[^\s\t\(]\(')


def whitespace_before_parentheses (logical_line):
    r"""Require whitespace before open parentheses

    Require whitespace before open parentheses unless preceded by another open paren.
    Okay: def foo (ham, egg):
    E281: def foo(ham, egg):
    Okay: x = computation ((ham, egg))
    E281: x = computation((ham, egg))
    E281: x = computation( (ham, egg))
    """

    line = logical_line
    for match in WHITESPACE_BEFORE_PAREN_REGEX.finditer (line):
        found = match.start ()
        yield found + 1, "E281 no whitespace before '('"
