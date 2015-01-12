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
import urlparse

from collections import namedtuple
from os.path import join

has_suffix = re.compile ('\\.[a-z0-9]{2,32}$')

# http://www.w3.org/2008/01/rdf-media-types
#  var DEFAULT_ACCEPT = 'text/turtle;q=1.0,application/n-triples;q=0.7,text/n3;q=0.6';
# https://github.com/LinkedDataFragments/Client.js/blob/master/lib/triple-pattern-fragments/FragmentsClient.js#L16
formats = {
    'application/json': 'json-ld',
    'application/ld+json': 'json-ld',
    'application/rdf+xml': 'rdfxml',
    'application/x-turtle': 'turtle',
    'application/xml': 'rdfxml',
    'json': 'json-ld',
    'json-ld': 'json-ld',
    'jsonld': 'json-ld',
    'nt': 'nt',
    'ntriples': 'nt',
    'rdf': 'rdfxml',
    'rdfxml': 'rdfxml',
    'text/turtle': 'turtle',
    'ttl': 'turtle',
    'turtle': 'turtle',
    'xml': 'rdfxml',
}


class LinkedData (object):
    def __init__ (self, project_root, site_root=None):
        with open (join (project_root, 'etc', 'context.json'), "rb") as f:
            self.context = json.loads (f.read ())

    def graph (self, triples=None):
        # FIXME: update this to also load website specific prefixes from site_root

        if not triples:
            triples = []

        g = rdflib.Graph ()
        for prefix, iri in self.context["@context"].items ():
            g.namespace_manager.bind (prefix, iri)

        [ g.add (t) for t in triples ]

        return g

    def parse_file (self, filename):
        with open (filename, "rb") as f:
            data = f.read ()

        basename, suffix = os.path.splitext (filename)
        if suffix:
            suffix = suffix[1:]

        return self.parse (data, formats.get (suffix, 'nt'))

    def parse (self, str, content_type=None):
        """ Parse an RDF document.

        Supports any RDFLib supported formats, see
        https://rdflib.readthedocs.org/en/latest/plugin_parsers.html .

        """

        return self.graph ().parse (data=str, format=formats.get (content_type, 'nt'))


def iri_join (*args):
    parts = list (args)
    if len (parts) < 2:
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
    if fragment or has_suffix.search (parts[-1]):
        trailing_slash = ''

    return "".join (ret) + trailing_slash


def iri_parse (iri):
    parts = urlparse.urlparse (iri)

    if parts.scheme == 'https':
        if not parts.port:
            port = 443
            display_port = ''
        else:
            port = parts.port
            display_port = ':' + unicode (port)
    else:
        if not parts.port:
            port = 80
            display_port = ''
        else:
            port = parts.port
            display_port = ':' + unicode (port)

    PI = namedtuple (
        'ParsedIRI',
        'scheme netloc path params query fragment username password hostname port display_port')

    return PI (parts.scheme, parts.netloc, parts.path, parts.params, parts.query, parts.fragment,
               parts.username, parts.password, parts.hostname, port, display_port)


def replace_bnode (graph, old, new):
    for p, o in graph[old::]:
        graph.remove ( (old, p, o))
        graph.add ( (new, p, o))

    for s, p in graph[::old]:
        graph.remove ( (s, p, old))
        graph.add ( (s, p, new))

    return graph


def trimlines (str):
    return "\n".join ([ l.rstrip () for l in str.split ("\n") ])


def save_json (target, data):
    with codecs.open (target, "wb", "UTF-8") as f:
        f.write (trimlines (json.dumps (data, indent=4, ensure_ascii=False)) + "\n")
