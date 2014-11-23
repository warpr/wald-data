#!/usr/bin/env python

#   This file is part of wald:meta
#   Copyright (C) 2014  Kuno Woudt <kuno@frob.nl>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of copyleft-next 0.3.0.  See LICENSE.txt.

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import ConfigParser
from os.path import join

dburi = None

def init(project_root):
    global dburi

    config_ini = join(project_root, 'etc', 'config.ini')
    config = ConfigParser.SafeConfigParser()
    config.read(config_ini)
    dburi = config.get('storage', 'dburi')




