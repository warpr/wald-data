#!/usr/bin/env python

#   This file is part of wald:meta
#   Copyright (C) 2014  Kuno Woudt <kuno@frob.nl>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of copyleft-next 0.3.0.  See LICENSE.txt.

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import StringIO
import wald.storage.edit
import wald.storage.sparql
import wald.storage.tools
import werkzeug
import werkzeug.exceptions
import werkzeug.utils

from wald.storage.namespaces import *
from werkzeug.routing import Map, Rule
from werkzeug.utils import cached_property
from werkzeug.wrappers import Request, Response


class LimitedRequest (Request):
    # accept up to 32MB of transmitted data.
    max_content_length = 1024 * 1024 * 32

    @cached_property
    def body (self):
        content_length = int (self.headers.get ('content-length'))
        if not content_length:
            raise werkzeug.exceptions.LengthRequired ()

        if content_length > self.max_content_length:
            raise werkzeug.exceptions.RequestEntityTooLarge ()

        body_io = StringIO.StringIO (self.environ['wsgi.input'].read (content_length))
        self.environ['wsgi.input'] = body_io

        request_body = body_io.getvalue ()
        if len (request_body) != content_length:
            raise werkzeug.exceptions.BadRequest (
                "Request truncated. Received %d bytes, expected %d." % (
                    len (request_body), content_length))

        return request_body.decode ('UTF-8')


def make_endpoint (setup_graph, ld, dataset):

    site_config = setup_graph.value (None, a, WALD.SiteConfig)
    sparql_base = setup_graph.value (site_config, WALD.sparql)

    identifier = setup_graph.value (dataset, DC.identifier)
    sparql = wald.storage.sparql.Sparql (sparql_base, identifier)
    edit = wald.storage.edit.Edit (setup_graph, dataset, ld, sparql)

    def endpoint (request):
        content_type = request.headers.get ('content-type')
        if content_type not in wald.storage.tools.formats:
            raise werkzeug.exceptions.UnsupportedMediaType ()

        try:
            request_graph = ld.parse (request.body, content_type)
        except Exception as e:
            raise werkzeug.exceptions.BadRequest (e)

        edit_id = edit.apply (request_graph)
        return werkzeug.utils.redirect(edit_id, code=303)

    return endpoint


def make_application (setup_graph):

    site_config = setup_graph.value (None, a, WALD.SiteConfig)
    project_root = setup_graph.value (site_config, WALD.projectRoot)
    site_root = setup_graph.value (site_config, WALD.siteRoot)

    ld = wald.storage.tools.LinkedData (project_root, site_root)

    endpoints = {}

    rules = []
    for dataset in setup_graph[:a:WALD.Dataset]:
        name = setup_graph.value (dataset, DC.identifier)
        endpoints['edit_' + name] = make_endpoint (setup_graph, ld, dataset)
        rules.append (Rule ('/' + name + '/', methods=[ 'PATCH', 'POST' ], endpoint='edit_' + name))

    routing_map = Map (rules)

    @LimitedRequest.application
    def application (request):
        adapter = routing_map.bind_to_environ (request.environ)
        try:
            endpoint, values = adapter.match ()
            return endpoints[endpoint] (request, **values)
        except werkzeug.exceptions.HTTPException as e:
            return e

    return application
