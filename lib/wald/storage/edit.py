#!/usr/bin/env python

#   This file is part of wald:meta
#   Copyright (C) 2014  Kuno Woudt <kuno@frob.nl>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of copyleft-next 0.3.1.  See copyleft-next-0.3.1.txt.

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import wald.storage.mint

from collections import OrderedDict
from rdflib.namespace import RDF
from rdflib.term import BNode, URIRef
from wald.storage.namespaces import *


class Edit  (object):

    def __init__ (self, setup_graph, dataset, linkeddata, sparql):
        self.setup_graph = setup_graph
        self.dataset = dataset
        self.sparql = sparql
        self.ld = linkeddata
        self.minter = wald.storage.mint.Mint (setup_graph)

        self.data_graph = setup_graph.value (dataset, WALD.dataGraph)
        self.edit_graph = setup_graph.value (dataset, WALD.editGraph)

    def apply (self, changeset):
        """ wald.storage.edit.appy will apply the specified changeset at the
        specified sparql endpoint.

        The sparql argument should be an initialized Sparql object as provided
        by wald.storage.sparql. The changeset argument should be a parsed graph
        of a changeset described using http://vocab.org/changeset/schema.html .
        """

        # This needs some kind of complicated double transaction which:

        # 1. Validate if the changeset can be applied:
        #     1.1 Verify that triples which are removed by the changeset exist
        #     1.2 Verify that triples added by the changeset do not exist yet
        # 2. Give the changeset an identifier
        # 3. Record the changeset in the edit graph
        # 4. Apply the changeset to the data graph
        # 5. Record  (in the edit graph) that the changeset has been applied or failed to apply

        # validate will raise an exception if the changeset is not valid
        validate (self.sparql, changeset)

        edit_graph = self.setup_graph.value (self.dataset, WALD.editGraph)
        edit_id = self.minter.sequential (edit_graph)

        edit_as_sparql = sparql_update (self.data_graph, self.edit_graph,
                                        self.ld.graph (normalize (edit_id, changeset)))

        if self.sparql.update (edit_as_sparql):
            # FIXME: verify that the id exists, if it doesn't the edit wasn't applied.
            return edit_id
        else:
            return False


def validate (sparql, changeset):
    """ Validate the changeset.

    This verifies that no changes would be ignored if the changeset is applied to the
    current data.

    A changeset consists of a set of triples to be added to the graph, and a set of triples
    to be removed from the graph.

    For additions this function will validate that those triples do not exist yet, and for
    removals this function will validate that those triples still exist in the database.

    Raises an exception if the changeset is not valid.

    """

    return True


def normalize (edit_id, triples):
    """ Normalize the changeset.

    This replaces all blank nodes in the changeset with #addN and #delN identifiers
    relative to the edit.  If there are any blank nodes which are not additions or
    removals they get a #genN identifier.

    FIXME: at some point I need to do unicode normalization as well.

    """

    changeset = []

    seen_changeset = False
    replacements = {}
    bnodes = { "add": OrderedDict (), "del": OrderedDict (), "gen": OrderedDict () }

    for s, p, o in triples:
        assert isinstance (p, URIRef)

        if o == CS.ChangeSet:
            if seen_changeset:
                # FIXME: raise exception, multiple changesets in the dataset?
                assert False
            seen_changeset = True
            replacements[s] = edit_id

        if isinstance (o, BNode):
            if p == CS.addition:
                bnodes['add'][o] = True
            elif p == CS.removal:
                bnodes['del'][o] = True
            else:
                bnodes['gen'][o] = True

    for kind in [ 'add', 'del', 'gen' ]:
        for i, bnode in enumerate (bnodes[kind]):
            replacements[bnode] = edit_id + '#' + kind + unicode (i)

    for s, p, o in triples:
        triple = [s, p, o]
        if s in replacements:
            triple[0] = replacements[s]
        if o in replacements:
            triple[2] = replacements[o]

        changeset.append (triple)

    return changeset


def unreify (graph, iri):
    # FIXME: Is there a good antonym for reify?

    return (graph.value (iri, RDF.subject),
            graph.value (iri, RDF.predicate),
            graph.value (iri, RDF.object))


def triple_to_n3 (triple):
    return "        " + " ".join ([ term.n3 () for term in triple ])


def triples_clause (graph_iri, triples):
    terms = " .\n".join ([ triple_to_n3 (triple) for triple in triples ])

    if not graph_iri:
        return terms

    return "    GRAPH %s\n    {\n%s\n    }" % (graph_iri.n3 (), terms)


def filter_clause (filter, triples):
    terms = " .\n".join ([ "    " + triple_to_n3 (triple) for triple in triples ])
    return "        %s\n        {\n%s\n        }" % (filter, terms)


def where_clause (graph_iri, removals, additions):
    exists = ''
    not_exists = ''

    # For those triples we want to DELETE, verify that they exist
    if removals:
        exists = filter_clause ("FILTER EXISTS", removals)

    # For those triples we want to INSERT, verify that they do not exist
    if additions:
        not_exists = filter_clause ("FILTER NOT EXISTS", additions)

    return ("    GRAPH %s\n    {\n%s\n%s\n    }" % (graph_iri.n3 (), exists, not_exists))


def sparql_update (data_graph, edit_graph, changeset):

    removal_ids = []
    for s, o in changeset[:CS.removal:]:
        removal_ids.append (o)

    addition_ids = []
    for s, o in changeset[:CS.addition:]:
        addition_ids.append (o)

    removals = [ unreify (changeset, iri) for iri in removal_ids ]
    additions = [ unreify (changeset, iri) for iri in addition_ids ]

    if not removals and not additions:
        return False

    parts = []
    if removals:
        parts.append ("DELETE\n{\n%s\n}\n" % (triples_clause (data_graph, removals)))

    insert_additions = ''
    if additions:
        insert_additions = triples_clause (data_graph, additions)

    parts.append ("INSERT\n{\n%s\n%s\n}\n" % (
        insert_additions, triples_clause (edit_graph, changeset)))

    parts.append ("WHERE\n{\n%s\n}\n" % (
        where_clause (data_graph, removals, additions)))

    return "".join (parts)
