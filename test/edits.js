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
    const testData = require ('./test-data');
    const edit = require ('../lib/edit');
    const find = require ('wald-find');

    function tests () {
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

                done ();
            }).catch (done);
        });
    }

    return { tests: tests };
}));

// -*- mode: web -*-
// -*- engine: jsx -*-
