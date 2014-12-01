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
import rdflib.term
import re
import sqlalchemy
import sqlalchemy.exc
import sqlalchemy.types

from collections import OrderedDict, namedtuple
import wald.storage.zbase32

class InvalidEntityName(Exception):
    pass


def schema(metadata):
    prefix = sqlalchemy.Column('prefix', sqlalchemy.types.String(4096), primary_key = True)
    id = sqlalchemy.Column('id', sqlalchemy.types.BigInteger, nullable = False, default = 0)

    # Start the sequence at 0x400.  Because we zbase32 the identifiers the first series of
    # identifiers would be just one or two characters.  The identifiers should have at least
    # three characters to appear like "real" identifiers, and the first three character value
    # is 0x400 (or "yyb").


    return sqlalchemy.Table('identifiers', metadata, prefix, id)


class EntityMinter(object):

    _mint = None
    _prefix = None

    def __init__(self, mint, prefix):
        self._mint = mint
        self._prefix = prefix

    def __getattr__(self, name):
        if '--' in name:
            raise InvalidEntityName("Invalid entity name")

        name_constraints = re.compile("^[a-z][a-z0-9-]*[a-z0-9]$")
        if not name_constraints.match(name):
            raise InvalidEntityName("Invalid entity name")

        prefix = self._prefix + name + '/'

        return namedtuple("EntityMinterIdentifier", "opaque sequential")(
            lambda: self._mint.opaque(prefix), lambda: self._mint.sequential(prefix))


class Mint(object):

    connection = None
    identifiers = None

    OPAQUE = "OPAQUE"
    SEQUENTIAL = "SEQUENTIAL"

    _seen = {}

    def __init__(self, setup):
        engine = sqlalchemy.create_engine(setup.dburi)
        metadata = sqlalchemy.MetaData()
        self.identifiers = schema(metadata)
        self.connection = engine.connect()

        # Create identifier database if it doesn't exist yet.
        metadata.create_all(engine)


    def _insert(self, prefix, default):
        try:
            self.connection.execute(self.identifiers.insert().values(prefix=prefix, id=default))
        except sqlalchemy.exc.IntegrityError as e:
            # duplicate key, that's fine.
            pass


    def increment(self, prefix, start=0):
        if not prefix in self._seen:
            self._insert(prefix, start)
            self._seen[prefix] = True

        result = self.connection.execute(
            self.identifiers
            .update()
            .values(id=self.identifiers.c.id + 1)
            .where(self.identifiers.c.prefix==prefix)
            .returning(self.identifiers.c.id))

        return list(result)[0][0]


    def sequential(self, prefix):
        """
        Returns a sequential identifier.  This is implemented as a sequential integer
        starting at 1. (0 is avoided because it is often considered false-y).
        """

        return rdflib.term.URIRef(prefix + unicode(self.increment(prefix)))


    def opaque(self, prefix):
        """
        Returns an opaque identifier.  This is implemented as a sequential integer
        starting at 0x400, returned as a zbase32 encoded string.
        """

        iri = prefix + wald.storage.zbase32.b2a(self.increment(prefix, 0x3ff))
        return rdflib.term.URIRef (iri)


    def entity(self, prefix):
        return EntityMinter(self, prefix)


def initialize(setup):
    print ("ERROR: implement redis backed minter")
    # return Mint(setup)

def load(setup):
    print ("ERROR: implement redis backed minter")
    # return Mint(setup)

