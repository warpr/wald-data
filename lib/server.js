/**
 *   This file is part of wald:data - the storage back-end of wald:meta.
 *   Copyright (C) 2016  Kuno Woudt <kuno@frob.nl>
 *
 *   This program is free software: you can redistribute it and/or modify
 *   it under the terms of copyleft-next 0.3.1.  See copyleft-next-0.3.1.txt.
 */

'use strict';

const app = require ('./app');
const port = 3000;

process.title = 'wald:data test server';

app.factory ().then (app => {
    app.listen (port, () => {
        console.log ('"' + process.title + '" listening on port ' + port);
    });
});


