#!/usr/bin/env python

#   This file is part of wald:meta
#   Copyright (C) 2014  Kuno Woudt <kuno@frob.nl>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of copyleft-next 0.3.1.  See copyleft-next-0.3.1.txt.

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

from colorama import Fore, Style
from wald.storage.namespaces import *
from wald.storage.tools import iri_join
from werkzeug.routing import Map
from werkzeug.utils import cached_property
from werkzeug.wrappers import Request


class Rule (werkzeug.routing.Rule):

    def description (self):
        if self.map is None or self.methods is None:
            return self.__repr__ ()

        tmp = []
        for is_dynamic, data in self._trace:
            if is_dynamic:
                tmp.append (u'<%s>' % data)
            else:
                tmp.append (data)

        route = ''.join (tmp).lstrip ('|')
        methods = ', '.join (self.methods)
        endpoint = self.endpoint

        pad0 = ' ' * (16 - len (methods))
        pad1 = ' ' * (32 - len (route))
        return ''.join ((
            Fore.GREEN, '  ', methods, pad0,
            Fore.WHITE, route, pad1,
            Fore.BLACK, Style.BRIGHT, endpoint, Style.RESET_ALL
        ))


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


def patch_endpoint (setup_graph, ld, dataset):

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

        try:
            edit_id = edit.apply (request_graph)
        except Exception as e:
            raise werkzeug.exceptions.UnprocessableEntity (e)

        return werkzeug.utils.redirect (edit_id, code=303)

    return endpoint


def redirect_endpoint (location):

    def endpoint (request):
        return werkzeug.utils.redirect (location, code=303)

    return endpoint


def make_application (setup_graph):

    site_config = setup_graph.value (None, a, WALD.SiteConfig)
    project_root = setup_graph.value (site_config, WALD.projectRoot)
    site_root = setup_graph.value (site_config, WALD.siteRoot)

    base = setup_graph.value (site_config, WALD.base)

    ld = wald.storage.tools.LinkedData (project_root, site_root)

    endpoints = {}

    rules = []
    for dataset in setup_graph[:a:WALD.Dataset]:
        name = setup_graph.value (dataset, DC.identifier)

        readOnly = bool (setup_graph.value (dataset, WALD.readOnly))
        if not readOnly:
            # The following sets up the edit endpoint for a dataset.
            endpoints['edit ' + name] = patch_endpoint (setup_graph, ld, dataset)
            rules.append (Rule ('/' + name + '/', methods=[ 'PATCH', 'POST' ],
                                endpoint='edit ' + name))

        data_graph = setup_graph.value (dataset, WALD.dataGraph)
        edit_graph = setup_graph.value (dataset, WALD.editGraph)

        ldf_base = iri_join (base, 'fragments', name).rstrip ('/')
        for g, ldf in [ (data_graph, ldf_base),
                        (edit_graph, iri_join (ldf_base, 'edit').rstrip ('/')) ]:
            path = '/' + g.replace (base, '').lstrip ('/').rstrip ('/') + '/'
            endpoint = 'named graph redirect ' + g
            endpoints[endpoint] = redirect_endpoint (ldf)
            rules.append (Rule (path, methods=[ 'GET' ], endpoint=endpoint))

    routing_map = Map (rules)

    for rule in routing_map.iter_rules ():
        print (rule.description ())

    @LimitedRequest.application
    def application (request):
        adapter = routing_map.bind_to_environ (request.environ)
        try:
            endpoint, values = adapter.match ()
            return endpoints[endpoint] (request, **values)
        except werkzeug.exceptions.HTTPException as e:
            return e

    return application
