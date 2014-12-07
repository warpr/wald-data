#!/usr/bin/env python

#   This file is part of wald:meta
#   Copyright (C) 2014  Kuno Woudt <kuno@frob.nl>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of copyleft-next 0.3.0.  See LICENSE.txt.

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import json
import os
import rdflib
import rdflib.collection
import rdflib.plugin
import rdflib.store
import re
import requests
import sys
import wald.storage.mint
import wald.storage.tools

from collections import namedtuple, OrderedDict
from os.path import join
from rdflib.namespace import RDF, RDFS, XSD
from rdflib.term import BNode, Literal, URIRef
from wald.storage.tools import iri_join

CC = rdflib.Namespace('http://creativecommons.org/ns#')
DC = rdflib.Namespace('http://purl.org/dc/elements/1.1/')
LI = rdflib.Namespace('https://licensedb.org/ns#')
FUSEKI = rdflib.Namespace('http://jena.apache.org/fuseki#')
JASM = rdflib.Namespace('http://jena.hpl.hp.com/2005/11/Assembler#')
TDB = rdflib.Namespace('http://jena.hpl.hp.com/2008/tdb#')
WALD = rdflib.Namespace('http://waldmeta.org/ontology/#')

a = RDF.type

class InvalidDatasetName(Exception):
    pass

class SiteTitleNotFound(Exception):
    pass


def load_site_config(project_root, site_root):
    errors = []

    # FIXME: I should have a general RDF file loader which itself tries to
    # find .ttl, .json, etc.. variants when loading an RDF file.

    try:
        return wald.storage.tools.parse_file(project_root, join(site_root, 'waldmeta.json'))
    except Exception as e:
        errors.append(unicode(e))

    try:
        return wald.storage.tools.parse_file(project_root, join(site_root, 'waldmeta.ttl'))
    except Exception as e:
        errors.append(unicode(e))

    print ("\n".join (errors))
    print ("ERROR: could not load wald:meta configuration")
    sys.exit(1)


def load_license_details(graph, dataset):
    license_id = graph[dataset:CC.license:].next()
    if (license_id.startswith('https://licensedb.org/id/')):
        response = requests.get(license_id.rstrip('/') + '.json')
        if response.status_code == 200:
            license_graph = rdflib.Graph().parse(data=response.text, format='json-ld')

            license_iri = license_graph.value(None, a, CC.License)
            license_name = None
            if license_iri:
                license_name = license_graph.value(license_iri, LI.name)
                graph.add((license_id, CC.legalcode, license_iri))

            if license_name:
                graph.add((license_id, LI.name, license_name))

    license_name = graph.value(license_id, LI.name)
    if not license_name:
        title = graph.value(license_id, DC.title)
        if title:
            graph.add((license_id, LI.name, title))
        license_name = title

    license_iri = graph.value(license_id, CC.legalcode)
    return license_name, license_iri


def process_config(graph):
    # FIXME: bail out if required properties are missing.

    document, base = graph[:WALD.base:].next()
    graph.add((document, a, WALD.SiteConfig))

    print ("")
    print ("# Site configuration")
    print ("")
    print ("base:        ", base)
    print ("sparql:      ", graph[document:WALD.sparql:].next())
    print ("redis:       ", graph[document:WALD.redis:].next())

    print ("")
    print ("# Datasets:")
    print ("")

    meta = list(graph[:DC.identifier:Literal("meta")])
    has_meta_dataset = False
    for node in meta:
        # we have a node with identifier "meta", let's check if it is a dataset in our document.
        if graph[document:WALD.dataset:node]:
            has_meta_dataset = True

    if not has_meta_dataset:
        dataset = URIRef(iri_join(base, 'meta'))
        graph.add((document, WALD.dataset, dataset))
        graph.add((dataset, DC.identifier, Literal("meta")))
        graph.add((dataset, DC.title, Literal("wald:meta site metadata", lang="en")))
        graph.add((dataset, DC.description, Literal("This dataset contains metadata for a wald:meta website", lang="en")))
        graph.add((dataset, CC.license, URIRef("https://licensedb.org/id/CC-BY-NC-ND-4.0")))
        graph.add((dataset, WALD.readOnly, Literal("false", datatype=XSD.boolean)))

    for dataset in graph[document:WALD.dataset:]:
        # give the dataset a real identifier.
        if isinstance(dataset, BNode):
            identifier = graph[dataset:DC.identifier:].next()
            dataset_new = URIRef(iri_join(base, identifier))
            wald.storage.tools.replace_bnode(graph, dataset, dataset_new)

    for dataset in graph[document:WALD.dataset:]:
        print ("title:        %s (%s)" % (graph.value(dataset, DC.title), dataset))
        print ("read-only:   ", graph.value(dataset, WALD.readOnly))
        print ("")

        graph.add((dataset, a, WALD.Dataset))
        graph.add((dataset, WALD.editGraph, dataset + 'edits'))
        graph.add((dataset, WALD.dataGraph, dataset + 'dataset'))
        load_license_details(graph, dataset)


def fuseki_config(site_root, graph):
    fuseki_graph = rdflib.Graph()

    document, base_iri = graph[:WALD.base:].next()

    CONFIG = rdflib.Namespace(base_iri + 'meta/fuseki/')

    fuseki_graph.namespace_manager.bind('tdb', TDB)
    fuseki_graph.namespace_manager.bind('jasm', JASM)
    fuseki_graph.namespace_manager.bind('fuseki', FUSEKI)
    fuseki_graph.namespace_manager.bind('config', CONFIG)

    fuseki_graph.add((TDB.DatasetTDB, RDFS.subClassOf, JASM.RDFDataset))
    fuseki_graph.add((TDB.GraphTDB, RDFS.subClassOf, JASM.Model))

    fuseki_graph.add((CONFIG.Server, a, FUSEKI.Server))
    fuseki_graph.add((CONFIG.Server, JASM.loadClass, Literal("com.hp.hpl.jena.tdb.TDB")))

    server_context = BNode()
    fuseki_graph.add((CONFIG.Server, JASM.context, server_context))
    fuseki_graph.add((server_context, JASM.cxtName, Literal("arq:queryTimeout")))
    fuseki_graph.add((server_context, JASM.cxtValue, Literal("1000")))

    services = []
    for dataset_node in graph[document:WALD.dataset]:
        dataset = graph.value(dataset_node, DC.identifier)
        service = CONFIG[dataset + 'Service']
        rdf_dataset = CONFIG[dataset + 'Dataset']
        services.append(service)
        fuseki_graph.add((service, a, FUSEKI.Service))
        fuseki_graph.add((service, FUSEKI.name, Literal(dataset)))
        fuseki_graph.add((service, FUSEKI.serviceQuery, Literal("query")))
        fuseki_graph.add((service, FUSEKI.serviceQuery, Literal("sparql")))
        fuseki_graph.add((service, FUSEKI.serviceUpdate, Literal("update")))
        fuseki_graph.add((service, FUSEKI.serviceUpload, Literal("upload")))
        # FIXME: should have a read-only one for ldf-server
        fuseki_graph.add((service, FUSEKI.serviceReadWriteGraphStore, Literal("data")))
        fuseki_graph.add((service, FUSEKI.dataset, rdf_dataset))

        fuseki_graph.add((rdf_dataset, a, TDB.DatasetTDB))
        fuseki_graph.add((rdf_dataset, TDB.location, Literal('../store/' + dataset + ".tdb")))

        edits_graph = CONFIG[dataset + 'EditsGraph']
        fuseki_graph.add((edits_graph, a, TDB.GraphTDB))
        fuseki_graph.add((edits_graph, TDB.dataset, rdf_dataset))
        fuseki_graph.add((edits_graph, TDB.graphName, URIRef(base_iri + dataset + '/edits')))

        data_graph = CONFIG[dataset + 'DataGraph']
        fuseki_graph.add((data_graph, a, TDB.GraphTDB))
        fuseki_graph.add((data_graph, TDB.dataset, rdf_dataset))
        fuseki_graph.add((data_graph, TDB.graphName, URIRef(base_iri + dataset + '/dataset')))

    servicesName = BNode()
    servicesList = rdflib.collection.Collection(fuseki_graph, servicesName, services)
    fuseki_graph.add((CONFIG.Server, FUSEKI.services, servicesName))

    target = join('etc', 'fuseki.ttl')
    filename = join(site_root, target)
    with open(filename, "wb") as f:
        f.write(fuseki_graph.serialize(format='turtle'))

    print ("Fuseki configuration saved to %s" % (target))


def ldf_config(site_root, graph):
    document, base_iri = graph[:WALD.base:].next()
    fuseki_base = 'http://localhost:3030/'

    title = graph.value(document, DC.title)
    if not title:
        # There is no main title for the service.  That's OK if there is only one dataset,
        # we can use the dataset title in that case.

        main_dataset = None
        for dataset in graph[document:WALD.dataset]:
            name = graph.value(dataset, DC.identifier)
            if unicode(name) == 'meta':
                continue

            if main_dataset:
                print (main_dataset, dataset, name)
                raise SiteTitleNotFound("Site has multiple datasets, no main title found")
            else:
                main_dataset = dataset

        if not main_dataset:
            raise SiteTitleNotFound("Site has no datasets")

        title = graph.value(main_dataset, DC.title)
        if not title:
            raise SiteTitleNotFound("Dataset %s is missing a title" % (main_dataset))

    output = OrderedDict()
    output['title'] = title
    output['datasources'] = OrderedDict()

    for dataset_node in graph[document:WALD.dataset]:
        dataset_name = graph.value(dataset_node, DC.identifier)
        dataset = OrderedDict()
        edit_dataset = None
        dataset["title"] = graph.value(dataset_node, DC.title)
        dataset["description"] = graph.value(dataset_node, DC.description)

        license_node = graph.value(dataset_node, CC.license)
        if license_node:
            dataset["license"] = graph.value(license_node, LI.name)
            dataset["licenseUrl"] = graph.value(license_node, CC.legalcode)
        dataset["copyright"] = None
        dataset["homepage"] = base_iri

        attribution = graph.value(dataset_node, CC.attributionName)
        if not attribution:
            attribution = graph.value(document, CC.attributionName)

        if attribution:
            # NOTE: The following is correct for an empty database, but if a database has been
            # collecting edits for some time it should be updated to include the range of years
            # from the first to the most recent edit.
            # FIXME: include a bin/copyright tool or something to update these copyright notices
            # based on dataset edit data.
            dataset["copyright"] = "copyright %s %s" % (
                datetime.datetime.now().year, attribution)

        if graph.value(dataset_node, WALD.readOnly):
            # FIXME: untested, undocumented
            dataset['type'] = 'HdtDatasource'
            dataset['settings'] = {
                'file': join('store', dataset_name + '.hdt')
            }
        else:
            dataset['type'] = 'FusekiDatasource'
            dataset['settings'] = {
                'endpoint': iri_join(fuseki_base, dataset_name, 'query'),
                'defaultGraph': iri_join(base_iri, dataset_name, 'dataset')
            }

            edit_dataset = OrderedDict()
            edit_dataset['title'] = dataset['title'] + ' edit history'
            edit_dataset['description'] = None
            for key in ['license', 'licenseUrl', 'copyright', 'homepage', 'type']:
                edit_dataset[key] = dataset[key]
            edit_dataset['settings'] = {
                'endpoint': dataset['settings']['endpoint'],
                'defaultGraph': iri_join(base_iri, dataset_name, 'edits')
            }

        output["datasources"][dataset_name] = dataset
        if edit_dataset:
            output["datasources"][dataset_name + '/edits'] = edit_dataset


    target = join('etc', 'ldf-server.json')
    filename = join(site_root, target)
    wald.storage.tools.save_json(target, output)

    print ("Linked Data Fragments server configuration saved to %s" % (target))


def initialize(project_root, site_root):
    try:
        os.makedirs(join(site_root, 'etc'))
    except OSError as e:
        pass # already exists, that's fine.

    graph = load_site_config(project_root, site_root)
    process_config(graph)
    fuseki_config(site_root, graph)
    ldf_config(site_root, graph)

    target = join('etc', 'waldmeta.ttl')
    filename = join(site_root, target)
    with open(filename, "wb") as f:
        f.write(graph.serialize(format='turtle'))

    print ("wald:meta configuration saved to %s" % (target))
    print ("")

    return graph


def load(project_root):
    return config(project_root)
