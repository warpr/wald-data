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
            plurals: {},
            types: {},
        };

        const shortUri = c.firstObject (id, wm.shortUri);
        if (shortUri != rdf.nil) {
            ret.shortUri = shortUri;
        }

        c.allObjects (id, wm.entity).map (node => {
            const cls = c.firstObject (node, wm.class);
            const name = N3.Util.getLiteralValue (c.firstObject (node, wm.name));
            const plural = N3.Util.getLiteralValue (c.firstObject (node, wm.plural));
            const prefix = N3.Util.getLiteralValue (c.firstObject (node, wm.prefix));
            ret.types[cls] = name;
            ret.entities[name] = prefix;
            ret.plurals[name] = plural;
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

    function wrapSection (before, lines, after) {
        return before.concat (lines.map (line => {
            return line === '' ? '' : '    ' + line;
        }), after);
    }

    function tripleToSparql (triple) {
        // FIXME: probably shouldn't rely on internal functions of a third-party library
        return [
            N3.Writer.prototype._encodeObject (triple.subject),
            N3.Writer.prototype._encodeObject (triple.predicate),
            N3.Writer.prototype._encodeObject (triple.object)
        ].join (' ');
    }

    function toSparqlUpdate (datasetGraph, editsGraph, changeSet) {
        const c = find.factory (changeSet);
        const id = c.firstSubject (a, cs.ChangeSet);

        const addedIds = c.allObjects (id, cs.addition);
        const removedIds = c.allObjects (id, cs.removal);

        let added = [];
        addedIds.map (id => {
            find.tools.dereify (c.all (id, null, null)).map (triple => added.push (triple));
        });

        let removed = [];
        removedIds.map (id => {
            find.tools.dereify (c.all (id, null, null)).map (triple => removed.push (triple));
        });

        // We sort these so that the output is predictable, this is useful during
        // development and testing.  If neccesary for performance this can be made
        // optional later.
        const addedLines = find.tools.sortQuads (added).map (tripleToSparql);
        const removedLines = find.tools.sortQuads (removed).map (tripleToSparql);
        const editLines = find.tools.sortQuads (c.all (null, null, null)).map (tripleToSparql);

        let deleteFromDataset = [];
        let filterExists = [];
        if (removedLines.length) {
            deleteFromDataset = wrapSection (
                [ `GRAPH <${datasetGraph}>`, '{' ],
                removedLines,
                [ '}' ]
            );

            filterExists = wrapSection (
                [ 'FILTER EXISTS', '{' ],
                removedLines,
                [ '}' ]
            );
        }

        let insertIntoDataset = [];
        let insertEdits = [];
        let filterNotExists = [];
        if (addedLines.length) {
            insertIntoDataset = wrapSection (
                [ `GRAPH <${datasetGraph}>`, '{' ],
                addedLines,
                [ '}' ]
            );

            insertEdits = wrapSection (
                [ `GRAPH <${editsGraph}>`, '{' ],
                editLines,
                [ '}' ]
            );

            filterNotExists = wrapSection (
                [ 'FILTER NOT EXISTS', '{' ],
                addedLines,
                [ '}' ]
            );
        }

        let deleteBlock = !deleteFromDataset.length ? [] : wrapSection (
            [ 'DELETE', '{' ],
            deleteFromDataset,
            [ '}' ]
        );

        let insertBlock = wrapSection (
            [ 'INSERT', '{' ],
            insertIntoDataset.concat ('', insertEdits),
            [ '}' ]
        );

        let where = wrapSection (
            [ 'WHERE', '{' ],
            wrapSection (
                [ `GRAPH <${datasetGraph}>`, '{' ],
                filterExists.concat ('', filterNotExists),
                [ '}' ]
            ),
            [ '}' ]
        );

        return deleteBlock.join ('\n') + '\n'
             + insertBlock.join ('\n') + '\n'
             + where.join ('\n') + '\n';
    }

    function processChangeSet (entities, changeSet) {
        const cfg = entityConfiguration (entities);
        const minter = mint.factory (cfg);

        // FIXME: hardcode graphs for now, they may need to be more flexible later.
        const datasetGraph = cfg.baseUri + 'dataset';
        const editsGraph = cfg.baseUri + 'edits';

        return mintIdentifiers (minter, changeSet)
            .then (datastore => toSparqlUpdate (datasetGraph, editsGraph, datastore));
    }

    return {
        allBlankNodes: allBlankNodes,
        entityConfiguration: entityConfiguration,
        mintIdentifiers: mintIdentifiers,
        processChangeSet: processChangeSet,
        wrapSection: wrapSection
    };
}));
