#!/usr/bin/env python

#   This file is part of wald:meta
#   Copyright (C) 2014  Kuno Woudt <kuno@frob.nl>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of copyleft-next 0.3.0.  See LICENSE.txt.

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import ConfigParser
import rdflib
import rdflib.collection
import rdflib.plugin
import rdflib.store
import re
import wald.storage.mint

from collections import namedtuple
from os.path import join
from rdflib.namespace import RDF, RDFS
from rdflib.term import BNode, Literal, URIRef

TDB = rdflib.Namespace('http://jena.hpl.hp.com/2008/tdb#')
JASM = rdflib.Namespace('http://jena.hpl.hp.com/2005/11/Assembler#')
FUSEKI = rdflib.Namespace('http://jena.apache.org/fuseki#')

# class InvalidDatasetName(Exception):
#     pass


# class EditableDataset (namedtuple("EditableDataset", "dataset edits mint setup")):
#     pass


def config_ini(project_root):
    return join(project_root, 'etc', 'config.ini')


def config(project_root):
    config_parser = ConfigParser.SafeConfigParser()
    config_parser.read(config_ini(project_root))

    setup = { 'config_parser': config_parser, 'project_root': project_root }
    for (name, value) in config_parser.items('storage'):
        if name == 'datasets':
            setup['datasets'] = value.split(',')
        if name in [ 'sparql', 'redis', 'base_iri' ]:
            setup[name] = value

    return namedtuple("Setup", setup)(**setup)


def save(setup, base_iri, dataset):
    name_constraints = re.compile("^[a-zA-Z][a-zA-Z0-9.-]*$")

    datasets = { 'meta': True }
    for name in [ s.strip() for s in dataset.split(',') ]:
        if name_constraints.match(name):
            datasets[name] = True
        else:
            raise InvalidDatasetName("Invalid name: " + name)

    base_iri = base_iri.rstrip('/') + '/'

    setup.config_parser.set('storage', 'datasets', ','.join(datasets))
    setup.config_parser.set('storage', 'base_iri', base_iri)

    with open(config_ini(setup.project_root), "wb") as f:
        setup.config_parser.write(f)

    # Reload the configuration.
    return config(setup.project_root)

# def graphs(setup, create=False):
#     all_graphs = {}

#     mint = wald.storage.mint.initialize(setup)

#     for dataset in setup.datasets:
#         graphs = {}

#         dataset_identifier = setup.base_iri + dataset + '/'

#         for suffix in [ 'dataset', 'edits' ]:
#             identifier = dataset_identifier + suffix + '/'
#             print ("Initializing", identifier)
#             store = rdflib.plugin.get("SQLAlchemy", rdflib.store.Store)(identifier=identifier)
#             graphs[suffix] = rdflib.Graph(store, identifier=identifier)
#             graphs[suffix].open(setup.dburi, create=create)

#         all_graphs[dataset] = EditableDataset(
#             graphs['dataset'],
#             graphs['edits'],
#             mint.entity(dataset_identifier),
#             setup)

#     return all_graphs


# def initialize(project_root, base_iri, dataset):
#     setup = config(project_root)
#     save(setup, base_iri, dataset)

#     # reload configuration
#     setup = config(project_root)
#     return graphs(setup, create=True)


# def load(project_root):
#     return graphs(config(project_root))


# jena/jena-fuseki-1.1.1/s-update --service=http://localhost:3030/music/update --update=clear.dataset.sparql.txt

def assembly(setup):
    g = rdflib.Graph()

    CONFIG = rdflib.Namespace(setup.base_iri + 'meta/fuseki/')
    a = RDF.type

    g.namespace_manager.bind('tdb', TDB)
    g.namespace_manager.bind('jasm', JASM)
    g.namespace_manager.bind('fuseki', FUSEKI)
    g.namespace_manager.bind('config', CONFIG)

    g.add((TDB.DatasetTDB, RDFS.subClassOf, JASM.RDFDataset))
    g.add((TDB.GraphTDB, RDFS.subClassOf, JASM.Model))

    g.add((CONFIG.Server, a, FUSEKI.Server))
    g.add((CONFIG.Server, JASM.loadClass, Literal("com.hp.hpl.jena.tdb.TDB")))

    server_context = BNode()
    g.add((CONFIG.Server, JASM.context, server_context))
    g.add((server_context, JASM.cxtName, Literal("arq:queryTimeout")))
    g.add((server_context, JASM.cxtValue, Literal("1000")))

    services = []
    for dataset in setup.datasets:
        service = CONFIG[dataset + 'Service']
        rdf_dataset = CONFIG[dataset + 'Dataset']
        services.append(service)
        g.add((service, a, FUSEKI.Service))
        g.add((service, FUSEKI.name, Literal(dataset)))
        g.add((service, FUSEKI.serviceQuery, Literal("query")))
        g.add((service, FUSEKI.serviceQuery, Literal("sparql")))
        g.add((service, FUSEKI.serviceUpdate, Literal("update")))
        g.add((service, FUSEKI.serviceUpload, Literal("upload")))
        g.add((service, FUSEKI.serviceReadWriteGraphStore, Literal("data")))
        g.add((service, FUSEKI.dataset, rdf_dataset))

        g.add((rdf_dataset, a, TDB.DatasetTDB))
        g.add((rdf_dataset, TDB.location, Literal('../store/' + dataset + ".tdb")))

        edits_graph = CONFIG[dataset + 'EditsGraph']
        g.add((edits_graph, a, TDB.GraphTDB))
        g.add((edits_graph, TDB.dataset, rdf_dataset))
        g.add((edits_graph, TDB.graphName, URIRef(setup.base_iri + dataset + '/edits')))

        data_graph = CONFIG[dataset + 'DataGraph']
        g.add((data_graph, a, TDB.GraphTDB))
        g.add((data_graph, TDB.dataset, rdf_dataset))
        g.add((data_graph, TDB.graphName, URIRef(setup.base_iri + dataset + '/dataset')))

    servicesName = BNode()
    servicesList = rdflib.collection.Collection(g, servicesName, services)
    g.add((CONFIG.Server, FUSEKI.services, servicesName))

    target = 'etc/fuseki.ttl'
    filename = setup.project_root + '/' + target
    with open(filename, "wb") as f:
        f.write(g.serialize(format='turtle'))

    print ("Fuseki configuration saved to %s" % (target))


def initialize(project_root, base_iri, dataset):
    setup = config(project_root)
    setup = save(setup, base_iri, dataset)

    import pprint
    pprint.pprint(setup)

    print("--------------------------")
    assembly(setup)



#     # reload configuration
#     setup = config(project_root)
#     return graphs(setup, create=True)
