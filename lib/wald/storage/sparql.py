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

def query(dataset, query):
    print ("send query to sparql query endpoint", dataset.sparql_query)

def update(dataset, update):
    print (update)

    response = requests.post(dataset.sparql_update, data={ 'update': update })
    import pprint
    pprint.pprint(response)

    if response.status_code != 204:
        print ("---------------\n", response.text)

