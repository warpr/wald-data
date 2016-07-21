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
    const N3 = require ('n3');

    const a = find.a;
    const wm = find.namespaces.wm;
    const rdf = find.namespaces.rdf;

    class Edit {
        constructor (cfg) {
            this._config = cfg;
            this._minter = mint.factory (cfg);
        }
    }

    function entityConfiguration (datastore) {
        const c = find.factory (datastore);
        const id = c.firstSubject (a, wm.Configuration);

        const ret = {
            baseUri: c.firstObject (id, wm.baseUri),
            entities: {},
            classes: {}
        };

        const shortUri = c.firstObject (id, wm.shortUri);
        if (shortUri != rdf.nil) {
            ret.shortUri = shortUri;
        }

        c.allObjects (id, wm.entity).map (node => {
            const cls = c.firstObject (node, wm.class);
            const name = N3.Util.getLiteralValue (c.firstObject (node, wm.name));
            const prefix = N3.Util.getLiteralValue (c.firstObject (node, wm.prefix));
            ret.classes[cls] = name;
            ret.entities[name] = prefix;
        });

        return ret;
    }

    /*
    function parseChangeSet (changeSet) {
        return find.tools.parseTurtle (changeSet).then (function (datastore) {
            const c = find.factory (datastore);

            const id = c.firstSubject (a, cs.ChangeSet);

            const added = c.allObjects (id, cs.addition);
            const removed = c.allObjects (id, cs.removal);

        });
    }
    */
    return {
        entityConfiguration: entityConfiguration,
//        parseChangeSet: parseChangeSet,
    };
}));
