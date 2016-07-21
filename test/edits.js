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
    const testData = require ('./test-data');

    const a = find.a;
    const cs = find.namespaces.cs;
//    const rdf = find.namespaces.rdf;
//    const wm = find.namespaces.wm;

    function tests () {
        let minter = false;

        test ('edits', function (done) {
            find.tools.parseTurtle (testData.entities).then (function (datastore) {
                const cfg = edit.entityConfiguration (datastore);

                assert.deepEqual ({
                    baseUri: 'https://test.waldmeta.org/',
                    entities: {
                        artist: 'ar',
                        song: 'so'
                    },
                    classes: {
                        'http://schema.org/MusicGroup': 'artist',
                        'http://schema.org/MusicRecording': 'song',
                    }
                }, cfg);

                minter = mint.factory (cfg);

                done ();
            }).catch (done);
        });

        test ('process ChangeSet document', function (done) {
            before (_ => minter);

            edit.parseChangeSet (testData.newArtist).then (function (datastore) {
                const c = find.factory (datastore);
                const id = c.firstSubject (a, cs.ChangeSet);

                assert.match (id, /^_:/);

                done ();
            }).catch (done);
        });
    }

    return { tests: tests };
}));

// -*- mode: web -*-
// -*- engine: jsx -*-
