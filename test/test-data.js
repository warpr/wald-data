/**
 *   This file is part of wald:data.
 *   Copyright (C) 2016  Kuno Woudt <kuno@frob.nl>
 *
 *   This program is free software: you can redistribute it and/or modify
 *   it under the terms of copyleft-next 0.3.1.  See copyleft-next-0.3.1.txt.
 */

'use strict';

/* eslint  max-len:0 */

(function (factory) {
    const imports = [
        'require',
    ];

    if (typeof define === 'function' && define.amd) {
        define (imports, factory);
    } else if (typeof module === 'object' && module.exports) {
        module.exports = factory (require);
    } else {
        console.log ('Module system not recognized, please use AMD or CommonJS');
    }
} (function (require) {
    return {
        insertCommand: `
INSERT DATA
{
    GRAPH <https://test.waldmeta.org/music/dataset>
    {
        <http://musicbrainz.org/artist/45a663b5-b1cb-4a91-bff6-2bef7bbfdd76#_>
        <http://xmlns.com/foaf/0.1/name> "Brittaney Spears"
    }
}
`,
        // FIXME: is the WHERE clause neccesary?
        editCommand: `
DELETE
{
    GRAPH <https://test.waldmeta.org/music/dataset>
    {
        <http://musicbrainz.org/artist/45a663b5-b1cb-4a91-bff6-2bef7bbfdd76#_> <http://xmlns.com/foaf/0.1/name> "Brittaney Spears"
    }
}
INSERT
{
    GRAPH <https://test.waldmeta.org/music/dataset>
    {
        <http://musicbrainz.org/artist/45a663b5-b1cb-4a91-bff6-2bef7bbfdd76#_> <http://rdfs.org/sioc/types#Microblog> <https://twitter.com/britneySPEARS> .
        <http://musicbrainz.org/artist/45a663b5-b1cb-4a91-bff6-2bef7bbfdd76#_> <http://xmlns.com/foaf/0.1/name> "Britney Spears"
    }

    GRAPH <https://test.waldmeta.org/music/edits>
    {
        <https://test.waldmeta.org/music/edits/2> <http://xmlns.com/foaf/0.1/name> "test edit 2"
    }
}
WHERE
{
    GRAPH <https://test.waldmeta.org/music/dataset>
    {
        FILTER EXISTS
        {
            <http://musicbrainz.org/artist/45a663b5-b1cb-4a91-bff6-2bef7bbfdd76#_> <http://xmlns.com/foaf/0.1/name> "Brittaney Spears"
        }
        FILTER NOT EXISTS
        {
            <http://musicbrainz.org/artist/45a663b5-b1cb-4a91-bff6-2bef7bbfdd76#_> <http://rdfs.org/sioc/types#Microblog> <https://twitter.com/britneySPEARS> .
            <http://musicbrainz.org/artist/45a663b5-b1cb-4a91-bff6-2bef7bbfdd76#_> <http://xmlns.com/foaf/0.1/name> "Britney Spears"
        }
    }
}
`
    };
}));

// -*- mode: web -*-
// -*- engine: jsx -*-

