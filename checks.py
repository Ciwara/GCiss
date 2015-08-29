#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
# maintainer: Fadiga

from __future__ import (unicode_literals, absolute_import, division,
                        print_function)

try:
    unicode
except NameError:
    unicode = str


class SharedChecks(object):

    def __init__(self):

        self.color_waring = ""
        self.color_error = "background-color: rgba(255, 107, 107, 150);"

    def is_empty(self, field):
        field.setToolTip("")
        field.setStyleSheet("")
        if unicode(field.text()) == "":
            field.setStyleSheet(self.color_error)
            field.setToolTip(u"Ce champs est obligatoire.")
            return True
        return False
