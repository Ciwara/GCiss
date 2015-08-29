#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
# maintainer: Fad
from __future__ import (
    unicode_literals, absolute_import, division, print_function)

from PyQt4.QtGui import (QHBoxLayout, QGridLayout, QGroupBox, QIcon)

from models import Owner
from configuration import Config
from Common.ui.util import SystemTrayIcon
from Common.ui.common import (
    FWidget, PyTextViewer, Button_menu, FPageTitle, FLabel)
from ui.dashboard import DashbordViewWidget
from ui.invoice import InvoiceViewWidget
# from ui.admin import AdminViewWidget
from ui.buy import BuyViewWidget
from ui.M.state_stock import StateStockViewWidget
from ui.M.product_out import product_outViewWidget
from ui.order_view import OrderViewWidget
from ui.M.product_in import InViewWidget


class HomeViewWidget(FWidget):

    """ Shows the home page  """

    def __init__(self, parent=0, *args, **kwargs):
        super(HomeViewWidget, self).__init__(parent=parent, *args, **kwargs)
        self.parent = parent
        self.root_permission = [u"admin", u"superuser"]

        blanck = 3 * " "
        self.parentWidget().setWindowTitle(
            Config.APP_NAME + blanck + "MENU GENERAL")

        self.title = FPageTitle(u"{} MENU GENERAL {}".format(blanck, blanck))
        self.title.setStyleSheet("background: url(%s) no-repeat scroll 20px 50px #CCCCCC;"
                                 "border-radius: 14px 14px 4px 4px;"
                                 "font: 15pt 'URW Bookman L';" % Config.APP_LOGO)

        self.consultation = Button_menu(_("Consultation"))
        self.consultation.clicked.connect(self.goto_consultation)
        self.consultation.setIcon(
            QIcon.fromTheme('save', QIcon(u"{}dashboard.png".format(Config.img_media))))

        self.invoice = Button_menu(_("Facturation"))
        # Affiche sur le commentaire sur le status bar
        # invoice.setStatusTip("hhhhhh")
        self.invoice.setIcon(
            QIcon.fromTheme('save', QIcon(u"{}invoice.png".format(Config.img_media))))
        self.invoice.clicked.connect(self.goto_invoice)
        # self.admin = Button_menu(_("Administration"))
        # self.admin.clicked.connect(self.goto_admin)
        # self.admin.setIcon(QIcon.fromTheme('save', QIcon(u"{}admin.png".format(Config.img_media))))
        self.report = Button_menu(_("Rapports d'achats"))
        self.report.clicked.connect(self.goto_buy)
        self.report.setIcon(
            QIcon.fromTheme('save', QIcon(u"{}buy.png".format(Config.img_media))))
        self.label = FLabel(self)
        self.label.setStyleSheet("background: url('{}center.png') no-repeat scroll 0 0;"
                                 "height: 50px;width:50px; margin: 0; padding: 0;".format(Config.img_media))

        # editbox.setColumnStretch(50, 2)
        ########### Mstock ############

        self.state = Button_menu(_(u"État des stocks"))
        self.state.clicked.connect(self.goto_state)
        self.state.setIcon(
            QIcon.fromTheme('save', QIcon(u"{}state.png".format(Config.img_media))))

        self.output = Button_menu(_("Sortie"))
        # Affiche sur le commentaire sur le status bar
        # self.output.setStatusTip("hhhhhh")
        self.output.setIcon(
            QIcon.fromTheme('save', QIcon(u"{}out.png".format(Config.img_media))))
        self.output.clicked.connect(self.goto_output)

        self.order = Button_menu(_(u"Faire les commandes"))
        self.order.clicked.connect(self.goto_order)
        self.order.setIcon(
            QIcon.fromTheme('save', QIcon(u"{}order.png".format(Config.img_media))))
        self.inputs = Button_menu(_(u"Entrée"))
        self.inputs.clicked.connect(self.goto_inputs)
        self.inputs.setIcon(
            QIcon.fromTheme('save', QIcon(u"{}in.png".format(Config.img_media))))

        vbox = QHBoxLayout(self)
        vbox.addWidget(self.title)
        # vbox.addLayout(editbox)

        # if Owner.get(islog=True).login_count > Config.tolerance:
        #     if not is_valide_mac(Config().license):
        #         self.createErroMsGroupBox()
        #         vbox.addWidget(self.chow_ms_err)
        #         self.setLayout(vbox)
        #         return
        if Config.APP_NAME == Config.M_GESTION:
            self.createMenuMStockGroupBox()
            vbox.addWidget(self.mstockgbox)
            self.setLayout(vbox)
        if Config.APP_NAME == Config.B_GESTION:
            self.createMenuBStockGroupBox()
            vbox.addWidget(self.bstockgbox)
            self.setLayout(vbox)

    def createErroMsGroupBox(self):
        self.chow_ms_err = QGroupBox()

        ms_err = PyTextViewer(u"<h3>Vous n'avez pas le droit d'utiliser ce \
                              logiciel sur cette machine, veuillez me contacté \
                              </h3> <ul><li><b>Tel:</b> {phone}</li>\
                              <li><b>{adress}</b></li><li><b>E-mail:</b> \
                              {email}</li></ul></br></br>{mac} \
                              ".format(email=Config.EMAIL_AUT,
                                       adress=Config.ADRESS_AUT,
                                       phone=Config.TEL_AUT,
                                       mac=get_mac().replace(":", ":")))

        gridbox = QGridLayout()
        gridbox.addWidget(FPageTitle(_("Erreur de permission")), 0, 2)
        gridbox.addWidget(ms_err, 1, 2)
        self.chow_ms_err.setLayout(gridbox)

    def createMenuMStockGroupBox(self):
        self.mstockgbox = QGroupBox()

        editbox = QGridLayout()
        editbox.addWidget(self.state, 0, 1, 1, 1)
        editbox.addWidget(self.inputs, 1, 0, 1, 1)
        editbox.addWidget(self.label, 1, 1, 1, 1)
        editbox.addWidget(self.output, 1, 2, 1, 1)
        editbox.addWidget(self.order, 2, 1, 1, 1)
        self.mstockgbox.setLayout(editbox)

    def createMenuBStockGroupBox(self):
        self.bstockgbox = QGroupBox()

        editbox = QGridLayout()
        editbox.addWidget(self.consultation, 0, 1, 1, 1)
        editbox.addWidget(self.invoice, 1, 0, 1, 1)
        editbox.addWidget(self.label, 1, 1, 1, 1)
        editbox.addWidget(self.report, 2, 1, 1, 1)
        # editbox.addWidget(self.admin, 1, 2, 1, 1)
        self.bstockgbox.setLayout(editbox)

    def check_log(self, page, permiss=None):

        if not Config.LOGIN:
            self.parent.active_menu_ad()
            self.change_main_context(page)
            SystemTrayIcon((_(u"Avertissement de Securité"),
                            "({}) Il est vivement souhaité de securiser son \
                            application".format(Config.APP_NAME)), parent=self)
        else:
            try:
                owner = Owner.get(islog=True)
                self.parent.active_menu_ad(
                ) if owner.group in self.root_permission else self.parent.active_menu()
            except OwnerDoesNotExist:
                return False

    def goto_consultation(self):
        self.check_log(DashbordViewWidget, permiss=self.root_permission)

    def goto_invoice(self):
        self.root_permission.append("user")
        self.check_log(InvoiceViewWidget, permiss=self.root_permission)

    # def goto_admin(self):
        # self.check_log(AdminViewWidget, permiss=self.root_permission)

    def goto_buy(self):
        self.check_log(BuyViewWidget, permiss=self.root_permission)

    def goto_state(self):
        self.check_log(StateStockViewWidget, permiss=self.root_permission)

    def goto_output(self):
        self.root_permission.append("user")
        self.check_log(product_outViewWidget, permiss=self.root_permission)

    def goto_order(self):
        self.check_log(OrderViewWidget, permiss=self.root_permission)

    def goto_inputs(self):
        self.check_log(InViewWidget, permiss=self.root_permission)
