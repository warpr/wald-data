#!/usr/bin/env python

#   This file is part of wald:meta
#   Copyright (C) 2014  Kuno Woudt <kuno@frob.nl>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of copyleft-next 0.3.0.  See LICENSE.txt.

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import requests

import wald.storage.tools

class Sparql(object):

    def __init__ (self, sparql_base, identifier):
        self.query_iri = wald.storage.tools.iri_join(sparql_base, identifier, 'query')
        self.update_iri = wald.storage.tools.iri_join(sparql_base, identifier, 'update')

    def clear(self, are_you_sure=False):
        if not are_you_sure:
            return False

        return self.update('CLEAR ALL')

    def query(self, query):
        response = requests.post(self.query_iri, data={ 'query': query, 'output': 'tsv' })
        if response.status_code == 200:
            return response.text

        # FIXME: raise exception
        print ("STATUS:", response.status_code)
        if response.status_code != 204:
            print ("---------------\n", response.text)

    def update(self, update):
        response = requests.post(self.update_iri, data={ 'update': update })
        if response.status_code == 200:
            return True

        # FIXME: raise exception
        print ("STATUS:", response.status_code)
        if response.status_code != 204:
            print ("---------------\n", response.text)
