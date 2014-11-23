#!/usr/bin/env python

#   This file is part of wald:meta
#   Copyright (C) 2014  Kuno Woudt <kuno@frob.nl>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of copyleft-next 0.3.0.  See LICENSE.txt.

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import os
import sys
from os.path import abspath, dirname, isdir, isfile, join


def uninstalled ():
    """ This will look for ../lib and include it in the sys.path if present,
    this is allows uninstalled applications to find their modules. """

    lib = join (dirname (dirname (abspath (__file__))), 'lib')
    if isdir (lib):
        sys.path[0] = lib


def virtualenv (appname):
    """ This will look for an application specific virtualenv in
    $XDG_DATA_HOME/<appname>/virtualenv and activate it if present. """

    data_home = os.getenv ('XDG_DATA_HOME')
    if not data_home:
        home = os.getenv ('HOME')
        if not home:
            print ('ERROR: $HOME environment variable not set')
            sys.exit (1)

        data_home = join (home, '.local', 'share')

    ve_activate = join (data_home, appname, 'virtualenv',
                        'bin', 'activate_this.py')

    if isfile (ve_activate):
        execfile (ve_activate, dict (__file__=ve_activate))
