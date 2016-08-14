/**
 *   This file is part of wald:data - the storage back-end of wald:meta.
 *   Copyright (C) 2016  Kuno Woudt <kuno@frob.nl>
 *
 *   This program is free software: you can redistribute it and/or modify
 *   it under the terms of copyleft-next 0.3.1.  See copyleft-next-0.3.1.txt.
 */

'use strict';

const app = require ('express') ();
const edit = require ('./edit');
const find = require ('wald-find');
const fs = require ('fs');

// FIXME: don't hardcode this
const configFile = __dirname + '/../test/test-config.ttl';

// const a = find.a;
const cs = find.namespaces.cs;
// const rdf = find.namespaces.rdf;

function buildRoutes (entityConfiguration) {
    const editResource = entityConfiguration.types[cs.ChangeSet];
    if (!editResource) {
        throw new Error ('No type cs:ChangeSet type specified');
    }

    const editCollection = entityConfiguration.plurals[editResource];
    if (!editCollection) {
        throw new Error ('No plural specified for ', editResource);
    }

    const routes = { GET: {}, POST: {} };
    // FIXME: use function instead of string for getEdit?
    // FIXME: add content-negotation based on suffix (e.g. /edit/ed123.json, /edit/ed123.ttl)
    routes.GET['/' + editResource + '/:id'] = 'getEdit';
    routes.POST['/' + editCollection + '/?'] = 'createEdit';

    return routes;
}

function factory () {
    const configBody = fs.readFileSync (configFile, 'UTF-8');

    return find.tools.parseTurtle (configBody).then (function (datastore) {
        const cfg = edit.entityConfiguration (datastore);

        app.get ('/', (req, res) => {
            res.send ('Hello!\n');
        });

        return app;
    });
}

module.exports = {
    buildRoutes: buildRoutes,
    factory: factory
};
