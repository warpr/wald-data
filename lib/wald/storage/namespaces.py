#!/usr/bin/env python

#   This file is part of wald:meta
#   Copyright (C) 2014  Kuno Woudt <kuno@frob.nl>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of copyleft-next 0.3.1.  See copyleft-next-0.3.1.txt.

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import rdflib
from rdflib.namespace import RDF

a = RDF.type

CC = rdflib.Namespace ('http://creativecommons.org/ns#')
CS = rdflib.Namespace ('http://purl.org/vocab/changeset/schema#')
DC = rdflib.Namespace ('http://purl.org/dc/elements/1.1/')
FUSEKI = rdflib.Namespace ('http://jena.apache.org/fuseki#')
JASM = rdflib.Namespace ('http://jena.hpl.hp.com/2005/11/Assembler#')
LI = rdflib.Namespace ('https://licensedb.org/ns#')
TDB = rdflib.Namespace ('http://jena.hpl.hp.com/2008/tdb#')
WALD = rdflib.Namespace ('http://waldmeta.org/ontology/#')
