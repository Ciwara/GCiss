#!/usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: Fad
from __future__ import (unicode_literals, absolute_import, division,
                        print_function)

from PyQt4.QtGui import QIcon
from PyQt4.QtCore import Qt

from Common.ui.common import FMainWindow

from models import Owner
from configuration import Config

from ui.menutoolbar import MenuToolBar
from ui.menubar import MenuBar
from ui.statusbar import GStatusBar
from ui.dashboard import DashbordViewWidget


class MainWindow(FMainWindow):

    def __init__(self):
        FMainWindow.__init__(self)

        self.setWindowIcon(QIcon.fromTheme('logo',
                                           QIcon(u"{}".format(Config.APP_LOGO))))
        self.menubar = MenuBar(self)
        self.setMenuBar(self.menubar)
        self.toolbar = MenuToolBar(self)
        self.addToolBar(Qt.LeftToolBarArea, self.toolbar)

        self.statusbar = GStatusBar(self)
        self.setStatusBar(self.statusbar)

        if Config.APP_NAME == Config.P_GESTION:
            self.page = PriceViewWidget
        else:
            self.page = DashbordViewWidget

        self.change_context(self.page)

    def page_width(self):
        return self.width() - 100

    def exit(self):
        self.logout()
        self.close()
