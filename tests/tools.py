#!/usr/bin/env python

#   This file is part of wald:meta
#   Copyright (C) 2014  Kuno Woudt <kuno@frob.nl>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of copyleft-next 0.3.0.  See LICENSE.txt.

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import unittest

from wald.storage.tools import iri_join, iri_parse

class TestTools (unittest.TestCase):

    def test_iri_join (self):
        self.assertEqual ("https://example.com/foo/bar/",
                          iri_join ('https://example.com', 'foo', 'bar'))

        self.assertEqual ("https://example.com/foo/bar.html",
                          iri_join ('https://example.com', 'foo', 'bar.html'))

    def test_iri_parse (self):

        parts = iri_parse ('https://example.com:80/foo')
        self.assertEqual (80, parts.port)
        self.assertEqual (':80', parts.display_port)

        parts = iri_parse ('http://example.com:80/foo')
        self.assertEqual (80, parts.port)
        self.assertEqual (':80', parts.display_port)

        parts = iri_parse ('http://example.com/foo')
        self.assertEqual (80, parts.port)
        self.assertEqual ('', parts.display_port)

        parts = iri_parse ('http://example.com:443/foo')
        self.assertEqual (443, parts.port)
        self.assertEqual (':443', parts.display_port)

        parts = iri_parse ('https://example.com/foo')
        self.assertEqual (443, parts.port)
        self.assertEqual ('', parts.display_port)

        parts = iri_parse ('https://example.com:443/foo')
        self.assertEqual (443, parts.port)
        self.assertEqual (':443', parts.display_port)
