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
        'supertest',
        'wald-find',
        './test-data',
        '../lib/app',
    ];

    if (typeof define === 'function' && define.amd) {
        define (imports, factory);
    } else if (typeof module === 'object' && module.exports) {
        module.exports = factory (require);
    } else {
        console.log ('Module system not recognized, please use AMD or CommonJS');
    }
} (function (require) {
    const app = require ('../lib/app');
    const assert = require ('chai').assert;
    const supertest = require ('supertest');
    const find = require ('wald-find');
    const testData = require ('./test-data');

    function tests () {
        test ('routes', function (done) {
            return find.tools.parseTurtle (testData.entities).then (datastore => {
                const routes = app.buildRoutes (datastore);
                assert.isFunction (routes.GET['/edit/:id']);
                assert.isFunction (routes.POST['/edits/?']);
                done ();
            });
        });

        test ('create edit', function (done) {
            app.factory ().then (app => {
                supertest (app)
                    .post ('/edits')
                    .set ('Content-Type', 'text/turtle')
                    .send (testData.newArtist)
                    .expect (200, done);
            });
        });

        test ('hello', function (done) {
            app.factory ().then (app => {
                supertest (app)
                    .get ('/edit/ed123')
                    .set ('Accept', 'application/json')
                    .expect ('Content-Type', 'text/html; charset=utf-8')
                    .expect (200, 'Hello!\n', done)
            });
        });
    }

    return { tests: tests };
}));

// -*- mode: web -*-
// -*- engine: jsx -*-
