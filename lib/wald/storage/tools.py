#!/usr/bin/env python

#   This file is part of wald:meta
#   Copyright (C) 2014  Kuno Woudt <kuno@frob.nl>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of copyleft-next 0.3.0.  See LICENSE.txt.

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import codecs
import os
import re
import json
import rdflib

from os.path import join

has_suffix = re.compile('\\.[a-z0-9]{2,32}$')

def iri_join (*args):
    parts = list (args)
    if len(parts) < 2:
        return parts[0]

    ret = [ unicode (parts.pop (0)).rstrip ("/") ]

    fragment = False
    for p in parts:
        p = unicode (p)
        if p[0] == '#':
            fragment = True
            ret.append (p)
        elif p[0] == '/':
            ret.append (p)
        else:
            ret.append ('/' + p)

    trailing_slash = '/'
    if fragment or has_suffix.search(parts[-1]):
        trailing_slash = ''

    return "".join (ret) + trailing_slash


def replace_bnode(graph, old, new):
    for p, o in graph[old::]:
        graph.remove((old, p, o))
        graph.add((new, p, o))

    for s, p in graph[::old]:
        graph.remove((s, p, old))
        graph.add((s, p, new))

    return graph


def graph(project_root):
    """ Prepare an rdflib.Graph with prefixes loaded. """

    # FIXME: update this to also load website specific prefixes from site_root

    with open(join (project_root, 'etc', 'context.json'), "rb") as f:
        context = json.loads (f.read())

    g = rdflib.Graph()
    for prefix, iri in context["@context"].items():
        g.namespace_manager.bind(prefix, iri)

    return g


def parse_file (project_root, filename):
    with open (filename, "rb") as f:
        data = f.read ()

    format = None
    if filename.endswith('.nt') or filename.endswith('.ntriples'):
        format = 'nt'
    elif filename.endswith('.json') or filename.endswith('.jsonld'):
        format = 'json-ld'
    elif filename.endswith('.ttl') or filename.endswith('.turtle'):
        format = 'turtle'
    elif filename.endswith('.rdf') or filename.endswith('.xml'):
        # FIXME: untested
        format = 'rdfxml'

    return parse(project_root, data, format)


def parse(project_root, str, format='nt'):
    """ Parse an RDF document.

    Supports any RDFLib supported formats, see
    https://rdflib.readthedocs.org/en/latest/plugin_parsers.html .

    """

    g = graph(project_root)
    return g.parse(data=str, format=format)


def trimlines (str):
    return "\n".join ([ l.rstrip () for l in str.split ("\n") ])

def save_json (target, data):
    with codecs.open(target, "wb", "UTF-8") as f:
        f.write(trimlines (json.dumps (data, indent=4, ensure_ascii=False)) + "\n")
