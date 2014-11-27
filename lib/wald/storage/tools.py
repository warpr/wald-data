#!/usr/bin/env python

#   This file is part of wald:meta
#   Copyright (C) 2014  Kuno Woudt <kuno@frob.nl>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of copyleft-next 0.3.0.  See LICENSE.txt.

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import rdflib

def parse(str, format='nt'):
    """ Parse an RDF document.

    Supports any RDFLib supported formats, see
    https://rdflib.readthedocs.org/en/latest/plugin_parsers.html .

    """

    return rdflib.Graph().parse(data=str, format=format)
