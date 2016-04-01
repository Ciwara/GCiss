#!/usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: fad

from __future__ import (unicode_literals, absolute_import, division,
                        print_function)

from PyQt4.QtGui import (QMessageBox, QIcon, QAction, QPixmap)
from PyQt4.QtCore import SIGNAL

from configuration import Config
from Common.exports import export_database_as_file
from Common.ui.common import FWidget
from Common.ui.cmenubar import FMenuBar
from ui.dashboard import DashbordViewWidget
from ui.inventory import InventoryViewWidget
from ui.order_view import OrderViewWidget
from ui.help import HTMLEditor
from ui.period_by import PeriodByViewWidget
from GCommon.ui.products import ProductsViewWidget
from ui.invoice import InvoiceViewWidget
from ui.apricot import ApricotsViewWidget
from ui.buy import BuyViewWidget
from ui.providers import ProvidersViewWidget
from ui.debt_manager import DebtsViewWidget


class MenuBar(FMenuBar, FWidget):

    def __init__(self, parent=None, admin=False, *args, **kwargs):
        FMenuBar.__init__(self, parent=parent, *args, **kwargs)

        self.setWindowIcon(QIcon(QPixmap("{}".format(Config.APP_LOGO))))
        self.parent = parent

        menu = [{"name": u"Tableau de bord", "icon": 'dashboard', "admin":
                 False, "shortcut": "Ctrl+T", "goto": DashbordViewWidget},
                {"name": u"Articles", "admin": True,  "icon": 'product',
                 "shortcut": "Ctrl+P", "goto": ProductsViewWidget},
                # {"name": u"Commande", "admin": True,  "icon": 'order',
                #  "shortcut": "Ctrl+O", "goto": OrderViewWidget},
                {"name": u"Inventaire", "admin": True,  "icon": 'inventory',
                 "shortcut": "Ctrl+I", "goto": InventoryViewWidget},
                # {"name": u"Rapport périodique", "admin": True,  "icon":
                #  'period', "shortcut": "Ctrl+K", "goto": PeriodByViewWidget},
                {"name": u"Caise", "admin": False,  "icon": 'apricots',
                 "shortcut": "Ctrl+C", "goto": ApricotsViewWidget},
                {"name": u"Vente", "admin": False,  "icon": 'invoice',
                 "shortcut": "Ctrl+V", "goto": InvoiceViewWidget},
                {"name": u"Arrivage", "admin": True,  "icon": 'buy',
                 "shortcut": "Ctrl+A", "goto": BuyViewWidget},
                {"name": u"Dettes", "admin": True, "icon": 'debt',
                 "shortcut": "Ctrl+D", "goto": DebtsViewWidget},
                {"name": u"Clients", "admin": True, "icon": '',
                 "shortcut": "Alt+C", "goto": ProvidersViewWidget},
                ]

        # Menu aller à
        goto_ = self.addMenu(u"&Aller a")

        for m in menu:
            el_menu = QAction(
                QIcon("{}{}.png".format(Config.img_media, m.get('icon'))), m.get('name'), self)
            el_menu.setShortcut(m.get("shortcut"))
            self.connect(
                el_menu, SIGNAL("triggered()"), lambda m=m: self.goto(m.get('goto')))
            goto_.addSeparator()
            goto_.addAction(el_menu)

        # if admin:
        # all report
        #     all_report = QAction(u"Tous les rapports", self)
        #     all_report.setShortcut("Ctrl+T")
        #     self.connect(all_report, SIGNAL("triggered()"),
        #                                         self.all_report)
        #     goto_.addAction(all_report)

        # Menu Aide
        help_ = self.addMenu(u"Aide")
        help_.addAction(QIcon("{}help.png".format(Config.img_cmedia)),
                        "Aide", self.goto_help)
        help_.addAction(QIcon("{}info.png".format(Config.img_cmedia)),
                        u"À propos", self.goto_about)

    def goto(self, goto):
        self.change_main_context(goto)

    # Aide
    def goto_help(self):
        self.open_dialog(HTMLEditor, modal=True)
