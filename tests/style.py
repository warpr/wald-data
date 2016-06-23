#!/usr/bin/env python

#   This file is part of wald:meta
#   Copyright (C) 2014  Kuno Woudt <kuno@frob.nl>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of copyleft-next 0.3.1.  See copyleft-next-0.3.1.txt.

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import sys
import unittest
from os.path import abspath, dirname, isdir, isfile, join

import wald.style

class TestFrobStyle (unittest.TestCase):

    def _check_succeeds(self, input):
        r = list (wald.style.whitespace_before_parentheses (input))
        self.assertEqual([], r)

    def _check_fails(self, input):
        r = list (wald.style.whitespace_before_parentheses (input))
        self.assertTrue(len(r) > 0)

        return r.pop()

    def test_whitespace_before_parentheses (self):
        self._check_succeeds('def foo (ham, egg):')

        (found, message) = self._check_fails ('def foo(ham, egg):')
        self.assertEqual(7, found)
        self.assertEqual("E281 no whitespace before '('", message)

        self._check_succeeds('x = computation ((ham, egg))')

        (found, message) = self._check_fails ('x = computation((ham, egg))')
        self.assertEqual(15, found)
        self.assertEqual("E281 no whitespace before '('", message)

        (found, message) = self._check_fails ('x = computation( (ham, egg))')
        self.assertEqual(15, found)
        self.assertEqual("E281 no whitespace before '('", message)
