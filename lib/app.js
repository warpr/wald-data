/**
 *   This file is part of wald:data - the storage back-end of wald:meta.
 *   Copyright (C) 2016  Kuno Woudt <kuno@frob.nl>
 *
 *   This program is free software: you can redistribute it and/or modify
 *   it under the terms of copyleft-next 0.3.1.  See copyleft-next-0.3.1.txt.
 */

'use strict';

const express = require ('express');
const app = express ();

const config = {
    baseUrl: 'https://test.waldmeta.org/',
    datasets: ['music', 'meta'],
};

app.get ('/', (req, res) => {
    res.send ('hello!');
});

module.exports = app;
