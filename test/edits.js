/**
 *   This file is part of wald:data.
 *   Copyright (C) 2016  Kuno Woudt <kuno@frob.nl>
 *
 *   This program is free software: you can redistribute it and/or modify
 *   it under the terms of copyleft-next 0.3.1.  See copyleft-next-0.3.1.txt.
 */

'use strict';

(function (factory) {
    const imports = [
        'require',
        'chai',
        'httpinvoke',
        'n3',
        'urijs',
        'wald-find',
        'wald-mint',
        'when',
        '../lib/edit',
        './test-data'
    ];

    if (typeof define === 'function' && define.amd) {
        define (imports, factory);
    } else if (typeof module === 'object' && module.exports) {
        module.exports = factory (require);
    } else {
        console.log ('Module system not recognized, please use AMD or CommonJS');
    }
} (function (require) {
    const assert = require ('chai').assert;
    const edit = require ('../lib/edit');
    const find = require ('wald-find');
    const mint = require ('wald-mint');
    const N3 = require ('n3');
    const testData = require ('./test-data');

    const a = find.a;
    const cs = find.namespaces.cs;
    const rdf = find.namespaces.rdf;
//    const wm = find.namespaces.wm;

    function tests () {
        let minter = false;

        test ('all blank nodes', function () {
            const datastore = new N3.Store ();

            datastore.addTriple ('_:b0', a, cs.ChangeSet);
            datastore.addTriple ('_:b0', cs.addition, '_:b1');
            datastore.addTriple ('_:b1', a, rdf.Statement);
            datastore.addTriple ('_:b1', rdf.subject, '_:artist');
            datastore.addTriple ('_:b4', a, '_:b5');

            const all = edit.allBlankNodes (datastore);
            all.sort ();

            assert.deepEqual (['_:artist', '_:b0', '_:b1', '_:b4', '_:b5'], all);
        });

        test ('edits', function (done) {
            find.tools.parseTurtle (testData.entities).then (function (datastore) {
                const cfg = edit.entityConfiguration (datastore);

                assert.deepEqual ({
                    baseUri: 'https://test.waldmeta.org/',
                    entities: {
                        artist: 'ar',
                        song: 'so',
                        edit: 'ed',
                    },
                    types: {
                        'http://schema.org/MusicGroup': 'artist',
                        'http://schema.org/MusicRecording': 'song',
                        'http://purl.org/vocab/changeset/schema#ChangeSet': 'edit',
                    }
                }, cfg);

                minter = mint.factory (cfg);

                done ();
            }).catch (done);
        });

        test ('mint identifiers for ChangeSet', function (done) {
            before (_ => minter);

            const skolemizedBlankNode = new RegExp (
                '^https://test.waldmeta.org/.well-known/genid/_b');

            minter
                .reset ('edit')
                .then (_ => edit.mintIdentifiers (minter, testData.newArtist))
                .then (function (datastore) {
                    const c = find.factory (datastore);
                    const id = c.firstSubject (a, cs.ChangeSet);

                    assert.equal (id, 'https://test.waldmeta.org/edit/edyb');

                    const additions = c.allObjects (id, cs.addition);
                    assert.equal (2, additions.length);

                    assert.match (additions[0], skolemizedBlankNode);
                    assert.match (additions[1], skolemizedBlankNode);

                    assert.notEqual (additions[0], additions[1]);

                    assert.isOk (c.has (additions[0], a, rdf.Statement));
                    assert.isOk (c.has (additions[0], rdf.subject, null));
                    assert.isOk (c.has (additions[0], rdf.predicate, null));
                    assert.isOk (c.has (additions[0], rdf.object, null));
                    assert.isOk (c.has (additions[1], a, rdf.Statement));
                    assert.isOk (c.has (additions[1], rdf.subject, null));
                    assert.isOk (c.has (additions[1], rdf.predicate, null));
                    assert.isOk (c.has (additions[1], rdf.object, null));

                    done ();
                }).catch (done);
        });

        test ('wrap section', function () {
            const before = ['GRAPH <https://example.org>', '{'];
            const after = ['}'];
            const lines = [
                '_:b0 rdf:type rdf:Statement.',
                '_:b0 rdf:subject _:b1'
            ];

            const expected = [
                'GRAPH <https://example.org>',
                '{',
                '    _:b0 rdf:type rdf:Statement.',
                '    _:b0 rdf:subject _:b1',
                '}',
            ].join ('\n');

            const result = edit.wrapSection (before, lines, after).join ('\n');
            assert.equal (expected, result);
        });

        test ('process ChangeSet document', function (done) {
            find.tools.parseTurtle (testData.entities).then (entities => {
                return edit.processChangeSet (entities, testData.edit1);
            }).then (output => {
                console.log (output);
                assert.equal (1, 2);
            }).catch (done);
        });
    }

    return { tests: tests };
}));

// -*- mode: web -*-
// -*- engine: jsx -*-
