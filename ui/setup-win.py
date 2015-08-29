#!/usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: Fad
from __future__ import (unicode_literals, absolute_import, division, print_function)

import os
import py2exe

from distutils.core import setup

try:
    target = os.environ['PY2EXE_MODE']
except KeyError:
    target = 'multi'

if target == 'single':
    ZIPFILE = None
    BUNDLES = 1
else:
    ZIPFILE = 'shared.lib'
    BUNDLES = 1

includes = ['sip']
packages = ['sqlalchemy.dialects.sqlite']

setup(windows=[{'script': 'bmain.py', \
                'icon_resources': [(0, 'images\logo.ico')]}],
      options={'py2exe': {
                    'includes': includes,
                    'packages': packages,
                    'compressed': True,
                    'bundle_files': BUNDLES,
                    },
               },
      zipfile=ZIPFILE,
)
