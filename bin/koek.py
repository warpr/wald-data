#!/usr/bin/env python

#   This file is part of wald:meta
#   Copyright (C) 2014  Kuno Woudt <kuno@frob.nl>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of copyleft-next 0.3.0.  See LICENSE.txt.

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import os
import sys
import activate
from os.path import abspath, dirname

activate.uninstalled ()
activate.virtualenv ('waldmeta')

import rdflib
from rdflib.term import Literal, URIRef
from rdflib.namespace import RDFS

SCHEMA = rdflib.Namespace(u'http://schema.org/')

from py2neo import Graph, Node, Relationship
graph = Graph()

def add(db, triples):
    rels = []

    objs = {}
    for (s, p, o) in triples:
        # FIXME: raise exception
        assert isinstance(s, URIRef)
        assert isinstance(p, URIRef)

        iri = unicode(s)
        objs[iri] = objs.get(iri, graph.merge_one(RDFS.Resource, "id", iri))

    for (s, p, o) in triples:
        subject = objs[unicode(s)]
        if isinstance(o, URIRef):
            iri = unicode(o)
            objs[iri] = objs.get(iri, graph.merge_one(RDFS.Resource, "id", iri))
            rels.append(Relationship(subject, unicode(p), objs[iri]))
        elif isinstance(o, Literal):
            subject.properties[unicode(p)] = o.n3()
        else:
            # FIXME: raise exception
            assert False

    import pprint
    pprint.pprint(rels)

    lijst = objs.items()
    import pprint
    pprint.pprint(lijst)



if __name__ == '__main__':

    # graph.schema.create_uniqueness_constraint("http://www.w3.org/2000/01/rdf-schema#Resource", "id")

    kuno = URIRef("https://frob.nl/#me")

    triples = [
        (kuno, SCHEMA.email, Literal("kuno@frob.nl")),
        (kuno, SCHEMA.telephone, Literal("+31 651 255 985")),
        (kuno, SCHEMA.familyName, Literal("Woudt", datatype=RDFS.Literal)),
        (kuno, SCHEMA.givenName, Literal("Kuno", lang="en-GB")),
        (kuno, SCHEMA.image, URIRef("https://frob.nl/me.png"))
    ]

    add(graph, triples)


    # kuno = graph.merge_one("http://www.w3.org/2000/01/rdf-schema#Resource", "id", "https://frob.nl/#me")
    # kuno.properties["http://schema.org/telephone"] = '"+31 651 255 985"'
    # kuno.properties["http://schema.org/email"] = '"kuno@frob.nl"'
    # kuno.properties["http://schema.org/familyName"] = '"Woudt"^^<http://www.w3.org/2000/01/rdf-schema#Literal>'
    # kuno.properties["http://schema.org/givenName"] = '"Kuno"@en'
    # kuno.push()

    # avatar = graph.merge_one("http://www.w3.org/2000/01/rdf-schema#Resource", "id", "https://frob.nl/me.png")
    # avatar.push()


    # rels = list(graph.match(start_node=kuno, rel_type="http://schema.org/image", end_node=avatar))
    # if len(rels) == 0:
    #     graph.create(Relationship(kuno, "http://schema.org/image", avatar))
    #     print ("Created relationship")
    # else:
    #     graph.delete(rels[0])
    #     print ("Deleted relationship")
