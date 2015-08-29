#!/usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: fad

import os
from PyQt4 import QtGui, QtCore

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


class HTMLEditor(QtGui.QDialog):

    def __init__(self, parent=None):
        super(HTMLEditor, self).__init__(parent)

        self.setWindowTitle(u"Aide")
        # try:
        #     import PyQt4.QtWebKit
        #     view = PyQt4.QtWebKit.QWebView(parent)

        #     view.load(QtCore.QUrl("file://%s" % os.path.join(ROOT_DIR,
        #                                                      'help.html')))
        #     layout = QtGui.QVBoxLayout(self)
        #     layout.addWidget(view)
        # except:
        #     pass
