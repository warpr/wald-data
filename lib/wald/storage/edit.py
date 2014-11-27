#!/usr/bin/env python

#   This file is part of wald:meta
#   Copyright (C) 2014  Kuno Woudt <kuno@frob.nl>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of copyleft-next 0.3.0.  See LICENSE.txt.

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import rdflib

def apply(dataset, triples):
    """ wald.storage.edit.appy will apply the specified changeset to the specified graph.

    The dataset argument should be an EditableDataset as provided by wald.storage.setup.
    The triples argument should be a list of (subject, predicate, object) tuples which
    describe a changeset using http://vocab.org/changeset/schema.html .
    """

    # This needs some kind of complicated double transaction which:

    # 1. Validate if the changeset can be applied:
    #     1.1 Verify that triples which are removed by the changeset exist
    #     1.2 Verify that triples added by the changeset do not exist yet
    # 2. Give the changeset an identifier
    # 3. Record the changeset in the edits graph
    # 4. Apply the changeset to the dataset graph
    # 5. Record (in the edits graph) that the changeset has been applied or failed to apply

    # Perhaps move to neo4j.  As far as I can tell none of the RDFLib stores do ACID.


    # if not valid(triples):
    #     raise some exception
    # triples = normalize(dataset.mint.edit.sequential(), triples)

    pass





test_changeset = """
{
  "@context": {
    "@base": "urn:uuid:9561f858-75e8-11e4-8574-fb90dd581502",
    "cs": "http://purl.org/vocab/changeset/schema#",
    "dc": "http://purl.org/dc/terms/",
    "foaf": "http://xmlns.com/foaf/0.1/",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "sioc": "http://rdfs.org/sioc/types#",
    "wald": "https://waldmeta.org/ns#",
    "xsd": "http://www.w3.org/2001/XMLSchema#",
    "cs:addition": {
      "@type": "@id"
    },
    "cs:removal": {
      "@type": "@id"
    },
    "cs:subjectOfChange": {
      "@type": "@id"
    },
    "dc:creator": {
      "@type": "@id"
    },
    "s": {
      "@id": "rdf:subject",
      "@type": "@id"
    },
    "p": {
      "@id": "rdf:predicate",
      "@type": "@id"
    },
    "o": {
      "@id": "rdf:object"
    }
  },
  "@id": "urn:uuid:9561f858-75e8-11e4-8574-fb90dd581502",
  "@type": "cs:ChangeSet",
  "dc:creator": "https://example.com/user/CallerNo6",
  "dc:date": "2014-09-16T23:59:01Z",
  "cs:changeReason": "fix typo",
  "cs:subjectOfChange": "http://musicbrainz.org/artist/45a663b5-b1cb-4a91-bff6-2bef7bbfdd76#_",
  "cs:removal": [
    {
      "@type": "rdf:Statement",
      "s": "http://musicbrainz.org/artist/45a663b5-b1cb-4a91-bff6-2bef7bbfdd76#_",
      "p": "foaf:name",
      "o": "Brittaney Spears"
    }
  ],
  "cs:addition": [
    {
      "@type": "rdf:Statement",
      "s": "http://musicbrainz.org/artist/45a663b5-b1cb-4a91-bff6-2bef7bbfdd76#_",
      "p": "foaf:name",
      "o": "Britney Spears"
    },
    {
      "@type": "rdf:Statement",
      "s": "http://musicbrainz.org/artist/45a663b5-b1cb-4a91-bff6-2bef7bbfdd76#_",
      "p": "sioc:Microblog",
      "o": {
        "@id": "https://twitter.com/britneySPEARS"
      }
    }
  ]
}
"""
