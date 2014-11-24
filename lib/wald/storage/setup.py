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
import rdflib.plugin
import rdflib.store
import re
import ConfigParser
from collections import namedtuple
from os.path import join


class InvalidDatasetName(Exception):
    pass


class EditableDataset (namedtuple("EditableDataset", "dataset edits setup")):
    pass


def config_ini(project_root):
    return join(project_root, 'etc', 'config.ini')


def config(project_root):
    config_parser = ConfigParser.SafeConfigParser()
    config_parser.read(config_ini(project_root))

    setup = { 'config_parser': config_parser, 'project_root': project_root }
    for (name, value) in config_parser.items('storage'):
        if name == 'datasets':
            setup['datasets'] = value.split(',')
        if name in [ 'dburi', 'base_url' ]:
            setup[name] = value

    return namedtuple("Setup", setup)(**setup)


def save(setup, base_url, dataset):
    name_constraints = re.compile("^[a-zA-Z][a-zA-Z0-9.-]*$")

    datasets = { 'meta': True }
    for name in [ s.strip() for s in dataset.split(',') ]:
        if name_constraints.match(name):
            datasets[name] = True
        else:
            raise InvalidDatasetName("Invalid name: " + name)

    base_url = base_url.rstrip('/') + '/'

    setup.config_parser.set('storage', 'datasets', ','.join(datasets))
    setup.config_parser.set('storage', 'base_url', base_url)

    with open(config_ini(setup.project_root), "wb") as f:
        setup.config_parser.write(f)


def graphs(setup, create=False):
    all_graphs = {}

    for dataset in setup.datasets:
        graphs = {}

        for suffix in [ 'dataset', 'edits' ]:
            identifier = setup.base_url + dataset + '/' + suffix
            print ("Initializing", identifier)
            store = rdflib.plugin.get("SQLAlchemy", rdflib.store.Store)(identifier=identifier)
            graphs[suffix] = rdflib.Graph(store, identifier=identifier)
            graphs[suffix].open(setup.dburi, create=create)

        all_graphs[dataset] = EditableDataset(graphs['dataset'], graphs['edits'], setup)

    return all_graphs


def initialize(project_root, base_url, dataset):
    setup = config(project_root)
    save(setup, base_url, dataset)

    # reload configuration
    setup = config(project_root)
    graphs(setup, create=True)


def load(project_root):
    return graphs(config(project_root))
