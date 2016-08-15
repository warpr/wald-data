/**
 *   This file is part of wald:data - the storage back-end of wald:meta.
 *   Copyright (C) 2016  Kuno Woudt <kuno@frob.nl>
 *
 *   This program is free software: you can redistribute it and/or modify
 *   it under the terms of copyleft-next 0.3.1.  See copyleft-next-0.3.1.txt.
 */

'use strict';

const edit = require ('./edit');
const find = require ('wald-find');
const fs = require ('fs');
const httpinvoke = require ('httpinvoke');
const when = require ('when');

// FIXME: don't hardcode this
const configFile = __dirname + '/../test/test-config.ttl';
const configBody = fs.readFileSync (configFile, 'UTF-8');

const fuseki = find.namespaces.fuseki;
const jasm = find.namespaces.jasm;
const rdf = find.namespaces.rdf;
const rdfs = find.namespaces.rdfs;
const tdb = find.namespaces.tdb;

function verifyDatasetExists (dataset) {
    // FIXME: use superagent?
    return (when (httpinvoke ('http://localhost:3030/$/datasets/' + dataset, 'GET'))
        .then (data => {
            // 200 OK if the dataset exists
            // 404 Not Found if it does not
            if (data.statusCode !== 200) {
                throw new Error('dataset "' + dataset + '" does not exist');
            }
        }));
}

function createDataset (dataset) {
    // FIXME: generate fuseki dataset configuration from wald:meta entity configuration

/*
    return when (httpinvoke ('http://localhost:3030/$/datasets/', 'POST', {
        headers: { 'Content-Type': 'text/turtle' },
        input: testData.metaDataset
}));
*/
}

function initDataset (dataset) {
    return verifyDatasetExists (dataset).then (() => {
        console.log ('Dataset "' + dataset + '" verified.');
    }).catch (err => console.log (err));
}

find.tools.parseTurtle (configBody).then (function (datastore) {
    const cfg = edit.entityConfiguration (datastore);

    initDataset (cfg.dataset);
    initDataset ('meta');
});
