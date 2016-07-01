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
        //        'n3',
        'when',
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
    const httpinvoke = require ('httpinvoke');
    const URI = require ('urijs');
//    const N3 = require ('n3');
    const when = require ('when');
    const find = require ('wald-find');
    const testData = require ('./test-data');

    suite ('fuseki', function () {
        let resultClear = false;
        let resultLoad = false;
        let resultVerifyInitial = false;
        let resultEdit = false;

        test ('clear', function (done) {
            return when (httpinvoke ('http://localhost:3030/music/update', 'POST', {
                headers: { 'Content-Type': 'application/sparql-update' },
                input: 'CLEAR ALL'
            })).then (function (data) {
                // check that data was cleared
                assert.equal (data.statusCode, 204);
                resultClear = true;
                done ();
            }).catch (done);
        });

        test ('load', function (done) {
            before (_ => resultClear);

            // load initial data
            return when (httpinvoke ('http://localhost:3030/music/update', 'POST', {
                headers: { 'Content-Type': 'application/sparql-update' },
                input: testData.insertCommand
            })).then (function (data) {
                // initial data was loaded
                assert.equal (data.statusCode, 204);
                resultLoad = true;
                done ();
            }).catch (done);
        });

        test ('verify initial data', function (done) {
            before (_ => resultLoad);

            var listUri = new URI ('http://localhost:3030/music/data');
            listUri.addQuery ('graph', 'https://test.waldmeta.org/music/dataset');
            return when (httpinvoke (listUri.toString (), 'GET', {
                headers: { Accept: 'text/turtle' }
            })).then (function (data) {
                assert.equal (data.statusCode, 200);
                return find.tools.parseTurtle (data.body);
            }).then (function (datastore) {
                // we've inserted one triple, so only one should be in the result
                assert.equal (datastore.find ().length, 1);

                const mbid = 'http://musicbrainz.org/artist/'
                           + '45a663b5-b1cb-4a91-bff6-2bef7bbfdd76#_';
                const triples = datastore.find (mbid, find.namespaces.foaf.name);
                assert.equal (triples.length, 1);
                assert.equal (triples[0].object, '"Brittaney Spears"');

                resultVerifyInitial = true;
                done ();
            }).catch (done);
        });

        test ('edit data', function (done) {
            before (_ => resultVerifyInitial);

            // edit initial data
            return when (httpinvoke ('http://localhost:3030/music/update', 'POST', {
                headers: { 'Content-Type': 'application/sparql-update' },
                input: testData.editCommand
            })).then (function (data) {
                // update processed correctly
                assert.equal (data.statusCode, 204);
                resultEdit = true;
                done ();
            }).catch (done);
        });

        test ('verify edited data', function (done) {
            before (_ => resultEdit);

            var listUri = new URI ('http://localhost:3030/music/data');
            listUri.addQuery ('graph', 'https://test.waldmeta.org/music/dataset');
            return when (httpinvoke (listUri.toString (), 'GET', {
                headers: { Accept: 'text/turtle' }
            })).then (function (data) {
                assert.equal (data.statusCode, 200);
                return find.tools.parseTurtle (data.body);
            }).then (function (datastore) {
                // we've replaced one triple with two
                assert.equal (datastore.find ().length, 2);

                const sioc = find.prefix ('sioc', 'http://rdfs.org/sioc/types#', []);

                const mbid = 'http://musicbrainz.org/artist/'
                           + '45a663b5-b1cb-4a91-bff6-2bef7bbfdd76#_';
                const name = datastore.find (mbid, find.namespaces.foaf.name);
                assert.equal (name.length, 1);
                assert.equal (name[0].object, '"Britney Spears"');

                const blog = datastore.find (mbid, sioc.Microblog);
                assert.equal (blog.length, 1);
                assert.equal (blog[0].object, 'https://twitter.com/britneySPEARS');

                done ();
            }).catch (done);
        });

        test ('verify edit', function (done) {
            before (_ => resultEdit);

            var listUri = new URI ('http://localhost:3030/music/data');
            listUri.addQuery ('graph', 'https://test.waldmeta.org/music/edits');
            return when (httpinvoke (listUri.toString (), 'GET', {
                headers: { Accept: 'text/turtle' }
            })).then (function (data) {
                assert.equal (data.statusCode, 200);
                return find.tools.parseTurtle (data.body);
            }).then (function (datastore) {
                // verify that there is one triple describing the edit
                assert.equal (datastore.find ().length, 1);

                const editId = 'https://test.waldmeta.org/music/edits/2';

                const name = datastore.find (editId, find.namespaces.foaf.name);
                assert.equal (name.length, 1);
                assert.equal (name[0].object, '"test edit 2"');

                done ();
            }).catch (done);
        });

    });
}));

// -*- mode: web -*-
// -*- engine: jsx -*-
