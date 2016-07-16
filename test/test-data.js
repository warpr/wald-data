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
        metaDataset: `
@prefix config: <http://kuno.link/meta/fuseki/> .
@prefix fuseki: <http://jena.apache.org/fuseki#> .
@prefix jasm: <http://jena.hpl.hp.com/2005/11/Assembler#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix tdb: <http://jena.hpl.hp.com/2008/tdb#> .

tdb:DatasetTDB rdfs:subClassOf jasm:RDFDataset .

tdb:GraphTDB rdfs:subClassOf jasm:Model .

config:metaDataGraph a tdb:GraphTDB ;
    tdb:dataset config:metaDataset ;
    tdb:graphName <https://test.waldmeta.org/meta/dataset> .

config:metaEditsGraph a tdb:GraphTDB ;
    tdb:dataset config:metaDataset ;
    tdb:graphName <https://test.waldmeta.org/meta/edits> .

config:metaService a fuseki:Service ;
    fuseki:dataset config:metaDataset ;
    fuseki:name "meta" ;
    fuseki:serviceQuery "query", "sparql" ;
    fuseki:serviceReadWriteGraphStore "data" ;
    fuseki:serviceUpdate "update" ;
    fuseki:serviceUpload "upload" .

config:metaDataset a tdb:DatasetTDB ;
    tdb:location "../test/store/meta.tdb" .

`,
        musicDataset: `
@prefix config: <http://kuno.link/meta/fuseki/> .
@prefix fuseki: <http://jena.apache.org/fuseki#> .
@prefix jasm: <http://jena.hpl.hp.com/2005/11/Assembler#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix tdb: <http://jena.hpl.hp.com/2008/tdb#> .

tdb:DatasetTDB rdfs:subClassOf jasm:RDFDataset .

tdb:GraphTDB rdfs:subClassOf jasm:Model .

config:musicDataGraph a tdb:GraphTDB ;
    tdb:dataset config:musicDataset ;
    tdb:graphName <https://test.waldmeta.org/music/dataset> .

config:musicEditsGraph a tdb:GraphTDB ;
    tdb:dataset config:musicDataset ;
    tdb:graphName <https://test.waldmeta.org/music/edits> .

config:musicService a fuseki:Service ;
    fuseki:dataset config:musicDataset ;
    fuseki:name "music" ;
    fuseki:serviceQuery "query", "sparql" ;
    fuseki:serviceReadWriteGraphStore "data" ;
    fuseki:serviceUpdate "update" ;
    fuseki:serviceUpload "upload" .

config:musicDataset a tdb:DatasetTDB ;
    tdb:location "../test/store/music.tdb" .

`,
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
`,
        edit1: `
@prefix cs: <http://purl.org/vocab/changeset/schema#>.
@prefix dc: <http://purl.org/dc/elements/1.1/>.
@prefix foaf: <http://xmlns.com/foaf/0.1/>.
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>.
@prefix sioc: <http://rdfs.org/sioc/types#>.

[]  a cs:ChangeSet;
    dc:creator <https://example.com/user/456>;
    dc:date "2014-09-16T23:59:01Z";
    cs:addition [
        a rdf:Statement;
        rdf:subject <http://musicbrainz.org/artist/45a663b5-b1cb-4a91-bff6-2bef7bbfdd76>;
        rdf:predicate foaf:name;
        rdf:object "ブリトニー・スピアーズ"
    ], [
        a rdf:Statement;
        rdf:subject <http://musicbrainz.org/artist/45a663b5-b1cb-4a91-bff6-2bef7bbfdd76>;
        rdf:predicate sioc:Microblog;
        rdf:object <https://twitter.com/britneySPEARS>
    ];
    cs:removal [
        a rdf:Statement;
        rdf:subject <http://musicbrainz.org/artist/45a663b5-b1cb-4a91-bff6-2bef7bbfdd76>;
        rdf:predicate foaf:name;
        rdf:object "Britney Spears"
    ];
    cs:subjectOfChange <http://musicbrainz.org/artist/45a663b5-b1cb-4a91-bff6-2bef7bbfdd76>;
    cs:changeReason "prefer japanese name".
`
    };
}));

// -*- mode: web -*-
// -*- engine: jsx -*-

