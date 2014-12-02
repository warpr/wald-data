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
import wald.storage.mint

from rdflib.namespace import FOAF, RDF
from rdflib.term import BNode, Literal, URIRef

class Dataset(object):

    def __init__(self, name, setup):
        self._setup = setup
        self.edit_graph = URIRef(setup.base_iri + name + '/edits')
        self.data_graph = URIRef(setup.base_iri + name + '/dataset')
        self.sparql_query = setup.sparql + name + '/query'
        self.sparql_update = setup.sparql + name + '/update'
        self.minter = wald.storage.mint.load(setup)

    def mint_edit(self):
        return self.minter.sequential(self.edit_graph + '/')

    def mint(self, entity, opaque=True):
        entity_iri = self.data_graph + '/' + entity + '/'

        if opaque:
            return self.minter.opaque(entity_iri)
        else:
            return self.minter.sequential(entity_iri)


def load(setup):
    return { ds: Dataset(ds, setup) for ds in setup.datasets }

