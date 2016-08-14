/**
 *   This file is part of wald:data - the storage back-end of wald:meta.
 *   Copyright (C) 2016  Kuno Woudt <kuno@frob.nl>
 *
 *   This program is free software: you can redistribute it and/or modify
 *   it under the terms of copyleft-next 0.3.1.  See copyleft-next-0.3.1.txt.
 */

'use strict';

const express = require ('express');
const edit = require ('./edit');
const find = require ('wald-find');
const fs = require ('fs');
const bodyParser = require ('body-parser');

// FIXME: don't hardcode this
const configFile = __dirname + '/../test/test-config.ttl';

// const a = find.a;
const cs = find.namespaces.cs;
// const rdf = find.namespaces.rdf;

class Edits {
    constructor (entities) {
        this.entities = entities;
        this.fetch = this.fetch.bind (this);
        this.create = this.create.bind (this);
    }

    fetch (request, response) {
        response.send ('Hello!\n');
    }

    create (request, response) {
        edit.processChangeSet (this.entities, request.body).then (sparqlUpdate => {
            // console.log (sparqlUpdate);
            response.send ('should submit the update to fuseki');
        });
    }
}

function buildRoutes (datastore) {
    const cfg = edit.entityConfiguration (datastore);

    const editResource = cfg.types[cs.ChangeSet];
    if (!editResource) {
        throw new Error ('No type cs:ChangeSet type specified');
    }

    const editCollection = cfg.plurals[editResource];
    if (!editCollection) {
        throw new Error ('No plural specified for ', editResource);
    }

    const edits = new Edits (datastore);

    const routes = { GET: {}, POST: {} };
    // FIXME: add content-negotation based on suffix (e.g. /edit/ed123.json, /edit/ed123.ttl)
    routes.GET['/' + editResource + '/:id'] = edits.fetch;
    routes.POST['/' + editCollection + '/?'] = edits.create;

    return routes;
}

function factory () {
    const configBody = fs.readFileSync (configFile, 'UTF-8');

    return find.tools.parseTurtle (configBody).then (function (datastore) {
        const routes = buildRoutes (datastore);

        const app = express ();

        app.use (bodyParser.text ({limit: '1024kb', type: 'text/*'}));

        Object.keys (routes).forEach (method => {
            Object.keys (routes[method]).forEach (path => {
                app[method.toLowerCase ()] (path, routes[method][path]);
            });
        });

        return app;
    });
}

module.exports = {
    buildRoutes: buildRoutes,
    Edits: Edits,
    factory: factory,
};
