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
import werkzeug.http

from wald.storage.tools import iri_join


class DatastoreException (Exception):

    def __init__ (self, response):
        status_name = ''
        if response.status_code in werkzeug.http.HTTP_STATUS_CODES:
            status_name = " " + werkzeug.http.HTTP_STATUS_CODES[response.status_code]

        msg = "Database Error: %d %s\n\n%s\n" % (
            response.status_code, status_name, response.text)

        return super (DatastoreException, self).__init__ (msg)


class Sparql (object):

    def __init__ (self, sparql_base, identifier):
        self.query_iri = iri_join (sparql_base, identifier, 'query').rstrip('/')
        self.update_iri = iri_join (sparql_base, identifier, 'update').rstrip('/')

    def clear (self, are_you_sure=False):
        if not are_you_sure:
            return False

        return self.update ('CLEAR ALL')

    def query (self, query):
        response = requests.post (self.query_iri, data={ 'query': query, 'output': 'tsv' })
        if response.status_code == 200:
            return response.text

        if response.status_code != 204:
            raise DatastoreException (response)

    def update (self, update):
        print ("POST:", self.update_iri)
        response = requests.post (self.update_iri, data={ 'update': update })
        if response.status_code == 200:
            return True

        raise DatastoreException (response)
