/**
 *   This file is part of wald:data - the storage back-end of wald:meta.
 *   Copyright (C) 2016  Kuno Woudt <kuno@frob.nl>
 *
 *   This program is free software: you can redistribute it and/or modify
 *   it under the terms of copyleft-next 0.3.1.  See copyleft-next-0.3.1.txt.
 */

'use strict';

(function (factory) {
    const imports = [
        'require',
        'n3',
        'wald-find',
        'wald-mint',
        'when',
    ];

    if (typeof define === 'function' && define.amd) {
        define (imports, factory);
    } else if (typeof module === 'object' && module.exports) {
        module.exports = factory (require);
    } else {
        console.log ('Module system not recognized, please use AMD or CommonJS');
    }
} (function (require) {
    const find = require ('wald-find');
    const mint = require ('wald-mint');
    const when = require ('when');
    // const nodefn = require ('when/node');
    const N3 = require ('n3');

    const a = find.a;
    const cs = find.namespaces.cs;
    const rdf = find.namespaces.rdf;
    const wm = find.namespaces.wm;

    /*
    class Edit {
        constructor (cfg) {
            this._config = cfg;
            this._minter = mint.factory (cfg);
        }
    }
    */

    function entityConfiguration (datastore) {
        const c = find.factory (datastore);
        const id = c.firstSubject (a, wm.Configuration);

        const ret = {
            baseUri: c.firstObject (id, wm.baseUri),
            entities: {},
            types: {}
        };

        const shortUri = c.firstObject (id, wm.shortUri);
        if (shortUri != rdf.nil) {
            ret.shortUri = shortUri;
        }

        c.allObjects (id, wm.entity).map (node => {
            const cls = c.firstObject (node, wm.class);
            const name = N3.Util.getLiteralValue (c.firstObject (node, wm.name));
            const prefix = N3.Util.getLiteralValue (c.firstObject (node, wm.prefix));
            ret.types[cls] = name;
            ret.entities[name] = prefix;
        });

        const finalChar = ret.baseUri.slice (-1);
        if (finalChar !== '/' && finalChar !== '#') {
            ret.baseUri += '/';
        }

        return ret;
    }

    function allBlankNodes (datastore) {
        const nodes = {};

        datastore.find (null, null, null).map (triple => {
            if (N3.Util.isBlank (triple.subject)) {
                nodes[triple.subject] = true;
            }

            if (N3.Util.isBlank (triple.object)) {
                nodes[triple.object] = true;
            }
        });

        return Object.keys (nodes);
    }

    function mintIdentifiers (minter, changeSet) {
        return find.tools.parseTurtle (changeSet).then (function (datastore) {
            const replacingIds = allBlankNodes (datastore).map (oldId => {
                return minter.newId (oldId, datastore).then (newId => {
                    find.tools.replaceId (oldId, newId.uri, datastore);
                    return datastore;
                });
            });

            return when.all (replacingIds).then (_ => datastore);
        });
    }

    function tripleToSparql (triple) {
        // FIXME: probably shouldn't rely on internal functions of a third-party library
        return [
            N3.Writer.prototype._encodeObject (triple.subject),
            N3.Writer.prototype._encodeObject (triple.predicate),
            N3.Writer.prototype._encodeObject (triple.object)
        ].join (' ');
    }

    function toSparqlUpdate (changeSet) {
        const c = find.factory (datastore);

        const added = c.allObjects (id, cs.addition);
        const removed = c.allObjects (id, cs.removal);

        let deleteStr = '';
        let insertStr = '';
        // let filterExists = '';
        // let filterNotExists = '';

        deleteStr = removed.map (tripleToSparql).join ('.\n') + '\n';
        insertStr = added.map (tripleToSparql).join ('.\n') + '\n';

        return [ deleteStr, insertStr ].join ('\n    ---\n');
    }

    function processChangeSet (entities, changeSet) {
        const cfg = edit.entityConfiguration (entities);
        const minter = mint.factory (cfg);

        // FIXME: hardcode graphs for now, they may need to be more flexible later.
        const datasetGraph = cfg.baseUri + 'dataset';
        const editsGraph = cfg.baseUri + 'edits';

        return mintIdentifiers (minter, changeSet)
            .then (toSparqlUpdate (datasetGraph, editsGraph, changeSet));
    }

    return {
        allBlankNodes: allBlankNodes,
        entityConfiguration: entityConfiguration,
        mintIdentifiers: mintIdentifiers,
        processChangeSet: processChangeSet,
    };
}));
