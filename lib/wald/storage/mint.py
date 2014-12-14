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
import redis
import wald.storage.zbase32

from collections import OrderedDict, namedtuple
from wald.storage.namespaces import *

class Mint(object):

    def __init__(self, setup_graph):
        site_config = setup_graph.value(None, a, WALD.SiteConfig)
        host, port = setup_graph.value(site_config, WALD.redis).split(':')
        self._Redis = redis.Redis(host=host, port=port)

    def increment(self, prefix):
        return self._Redis.incr('wald:meta:mint:' + unicode(prefix))

    def sequential(self, prefix):
        """
        Returns a sequential identifier.  This is implemented as a sequential integer
        starting at 1. (0 is avoided because it is often considered false-y).
        """

        return rdflib.term.URIRef(prefix + unicode(self.increment(prefix)))

    def opaque(self, prefix):
        """
        Returns an opaque identifier.  This is implemented as a sequential integer
        starting at 1, but 0x3ff is added and the result returned as a zbase32 encoded
        string. (0x3ff is added to ensure a minimum string length for the return value).
        """

        iri = prefix + wald.storage.zbase32.b2a(0x3ff + self.increment(prefix))
        return rdflib.term.URIRef (iri)
