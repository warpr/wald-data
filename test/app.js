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
    // const assert = require ('chai').assert;
    const supertest = require ('supertest');

    function tests () {
        test ('hello', function (done) {
            supertest (app)
                .get ('/')
                .set ('Accept', 'application/json')
                .expect ('Content-Type', 'text/html; charset=utf-8')
                .expect (200, 'Hello!\n', done)
        });
    }

    return { tests: tests };
}));

// -*- mode: web -*-
// -*- engine: jsx -*-
