#!/usr/bin/env python

#   This file is part of wald:meta
#   Copyright (C) 2014  Kuno Woudt <kuno@frob.nl>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of copyleft-next 0.3.0.  See LICENSE.txt.

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from collections import OrderedDict

import rdflib
from rdflib.namespace import FOAF, RDF, RDFS
from rdflib.term import BNode, Literal, URIRef

CS = rdflib.Namespace('http://purl.org/vocab/changeset/schema#')

def apply(dataset, triples):
    """ wald.storage.edit.appy will apply the specified changeset to the specified graph.

    The dataset argument should be an EditableDataset as provided by wald.storage.setup.
    The triples argument should be a list of (subject, predicate, object) tuples which
    describe a changeset using http://vocab.org/changeset/schema.html .
    """

    # This needs some kind of complicated double transaction which:

    # 1. Validate if the changeset can be applied:
    #     1.1 Verify that triples which are removed by the changeset exist
    #     1.2 Verify that triples added by the changeset do not exist yet
    # 2. Give the changeset an identifier
    # 3. Record the changeset in the edits graph
    # 4. Apply the changeset to the dataset graph
    # 5. Record (in the edits graph) that the changeset has been applied or failed to apply

    # Perhaps move to neo4j.  As far as I can tell none of the RDFLib stores do ACID.


    # if not valid(triples):
    #     raise some exception
    # triples = normalize(dataset.mint.edit.sequential(), triples)

    triple = (
        URIRef("http://musicbrainz.org/artist/45a663b5-b1cb-4a91-bff6-2bef7bbfdd76#_"),
        FOAF.name,
        Literal("Brittaney Spears")
    )


    # DELETE { GRAPH <g1> { a b c } } INSERT { GRAPH <g1> { x y z } } USING <g1> WHERE { ... }

# INSERT
#   { GRAPH <http://example/addresses>
#     {
#       ?person  foaf:name  ?name .
#       ?person  foaf:mbox  ?email
#     } }
# WHERE
#   { GRAPH  <http://example/people>
#     {
#       ?person  foaf:name  ?name .
#       OPTIONAL { ?person  foaf:mbox  ?email }
#     } }


def validate(graph, triples):
    """ Validate the changeset.

    This verifies that no changes would be ignored if the changeset is applied to the
    current data.

    A changeset consists of a set of triples to be added to the graph, and a set of triples
    to be removed from the graph.

    For additions this function will validate that those triples do not exist yet, and for
    removals this function will validate that those triples still exist in the database.



    """



def normalize(edit_id, triples):
    """ Normalize the changeset.

    This replaces all blank nodes in the changeset with #addN and #delN identifiers
    relative to the edit.  If there are any blank nodes which are not additions or
    removals they get a #genN identifier.

    """

    changeset = rdflib.Graph()

    seen_changeset = False
    replacements = {}
    bnodes = { "add": OrderedDict(), "del": OrderedDict(), "gen": OrderedDict() }

    for s, p, o in triples:
        assert isinstance(p, URIRef)

        if o == CS.ChangeSet:
            if seen_changeset:
                # FIXME: raise exception, multiple changesets in the dataset?
                assert False
            seen_changeset = True
            replacements[s] = edit_id

        if isinstance(o, BNode):
            if p == CS.addition:
                bnodes['add'][o] = True
            elif p == CS.removal:
                bnodes['del'][o] = True
            else:
                bnodes['gen'][o] = True

    for kind in [ 'add', 'del', 'gen' ]:
        for i, bnode in enumerate(bnodes[kind]):
            replacements[bnode] = edit_id + '#' + kind + unicode(i)

    for s, p, o in triples:
        triple = [s, p, o]
        if s in replacements:
            triple[0] = replacements[s]
        if o in replacements:
            triple[2] = replacements[o]

        changeset.add(triple)

    return changeset


def unreify(graph, iri):
    # FIXME: Is there a good antonym for reify?

    return (next(graph[iri:RDF.subject:]),
            next(graph[iri:RDF.predicate:]),
            next(graph[iri:RDF.object:]))

def triple_to_n3(triple):
    return "        " + " ".join([ term.n3() for term in triple ])

def triples_clause(graph_iri, triples):

    terms = " .\n".join([ triple_to_n3(triple) for triple in triples ])

    if not graph_iri:
        return terms;

    return "    GRAPH %s\n    {\n%s\n    }" % (graph_iri.n3(), terms)


def filter_clause (filter, triples):
    terms = " .\n".join([ "    " + triple_to_n3(triple) for triple in triples ])
    return "        %s\n        {\n%s\n        }" % (filter, terms)


def where_clause (graph_iri, removals, additions):

    # For those triples we want to DELETE, verify that they exist
    exists = filter_clause("FILTER EXISTS", removals)

    # For those triples we want to INSERT, verify that they do not exist
    not_exists = filter_clause("FILTER NOT EXISTS", additions)

    return ("    ?subject ?predicate ?object\n"
            "    GRAPH %s\n    {\n%s\n%s\n    }" % (graph_iri.n3(), exists, not_exists))


def sparql_update(dataset, changeset):

    edit_graph = URIRef('http://kuno.link/music/edits')
    data_graph = URIRef('http://kuno.link/music/dataset')

    import pprint

    removal_ids = []
    for s,o in changeset[:CS.removal:]:
        removal_ids.append(o)

    addition_ids = []
    for s,o in changeset[:CS.addition:]:
        addition_ids.append(o)

    removals = [ unreify(changeset, iri) for iri in removal_ids ]
    additions = [ unreify(changeset, iri) for iri in addition_ids ]


    return "".join([
        "DELETE\n{\n%s\n}\n" % (triples_clause(data_graph, removals)),
        "INSERT\n{\n%s\n}\n" % (triples_clause(data_graph, additions)),
        "WHERE\n{\n%s\n}\n" % (where_clause(data_graph, removals, additions))
    ])


def tmp():

    update_url = 'http://fub.frob.mobi:8080/marmotta/sparql/update'

    t = """
INSERT DATA
{
    GRAPH <http://kuno.link/music/dataset>
    {
        <http://musicbrainz.org/artist/45a663b5-b1cb-4a91-bff6-2bef7bbfdd76#_>
        <http://xmlns.com/foaf/0.1/name>
        "Brittaney Spears"
    }
}
"""
    example = """
DELETE DATA
{
    GRAPH <http://example/bookStore>
    { <http://example/book1>  <http://purl.org/dc/elements/1.1/title>  "Fundamentals of Compiler Desing" }
};

INSERT DATA
{
    GRAPH <http://example/bookStore>
    { <http://example/book1>  <http://purl.org/dc/elements/1.1/title>  "Fundamentals of Compiler Design" }
}
"""


test_changeset = """
{
  "@context": {
    "@base": "urn:uuid:9561f858-75e8-11e4-8574-fb90dd581502",
    "cs": "http://purl.org/vocab/changeset/schema#",
    "dc": "http://purl.org/dc/terms/",
    "foaf": "http://xmlns.com/foaf/0.1/",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "sioc": "http://rdfs.org/sioc/types#",
    "wald": "https://waldmeta.org/ns#",
    "xsd": "http://www.w3.org/2001/XMLSchema#",
    "cs:addition": {
      "@type": "@id"
    },
    "cs:removal": {
      "@type": "@id"
    },
    "cs:subjectOfChange": {
      "@type": "@id"
    },
    "dc:creator": {
      "@type": "@id"
    },
    "s": {
      "@id": "rdf:subject",
      "@type": "@id"
    },
    "p": {
      "@id": "rdf:predicate",
      "@type": "@id"
    },
    "o": {
      "@id": "rdf:object"
    }
  },
  "@id": "urn:uuid:9561f858-75e8-11e4-8574-fb90dd581502",
  "@type": "cs:ChangeSet",
  "dc:creator": "https://example.com/user/CallerNo6",
  "dc:date": "2014-09-16T23:59:01Z",
  "cs:changeReason": "fix typo",
  "cs:subjectOfChange": "http://musicbrainz.org/artist/45a663b5-b1cb-4a91-bff6-2bef7bbfdd76#_",
  "cs:removal": [
    {
      "@type": "rdf:Statement",
      "s": "http://musicbrainz.org/artist/45a663b5-b1cb-4a91-bff6-2bef7bbfdd76#_",
      "p": "foaf:name",
      "o": "Brittaney Spears"
    }
  ],
  "cs:addition": [
    {
      "@type": "rdf:Statement",
      "s": "http://musicbrainz.org/artist/45a663b5-b1cb-4a91-bff6-2bef7bbfdd76#_",
      "p": "foaf:name",
      "o": "Britney Spears"
    },
    {
      "@type": "rdf:Statement",
      "s": "http://musicbrainz.org/artist/45a663b5-b1cb-4a91-bff6-2bef7bbfdd76#_",
      "p": "sioc:Microblog",
      "o": {
        "@id": "https://twitter.com/britneySPEARS"
      }
    }
  ]
}
"""
