#!/usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: Fadiga


from PyQt4.QtGui import (QSplitter, QHBoxLayout, QVBoxLayout, QGridLayout,
                         QTableWidgetItem, QPixmap, QFont, QListWidget,
                         QListWidgetItem, QIcon, QMenu)
from PyQt4.QtCore import Qt, SIGNAL, SLOT

from models import ProviderOrClient, Invoice, Refund

from Common.ui.common import FWidget, FBoxTitle, Button, LineEdit
from Common.ui.table import FTableWidget
from Common.ui.util import formatted_number

from configuration import Config

ALL_CONTACTS = "TOUS"


class DebtsViewWidget(FWidget):

    """ Shows the home page  """

    def __init__(self, parent=0, *args, **kwargs):
        super(DebtsViewWidget, self).__init__(parent=parent,
                                              *args, **kwargs)
        self.parent = parent
        self.parentWidget().setWindowTitle(
            Config.NAME_ORGA + u"Carnet d'adresse")

        hbox = QHBoxLayout(self)

        self.table_contact = DebtsTableWidget(parent=self)
        self.table_provid_clt = ProviderOrClientTableWidget(parent=self)
        self.table_transf = TransfTableWidget(parent=self)
        # self.operation = OperationWidget(parent=self)

        splitter = QSplitter(Qt.Horizontal)

        self.splitter_left = QSplitter(Qt.Vertical)
        self.splitter_left.addWidget(FBoxTitle(u"Les provid_cltes"))
        self.splitter_left.addWidget(self.table_provid_clt)

        splitter_details = QSplitter(Qt.Horizontal)

        splitter_down = QSplitter(Qt.Vertical)
        # splitter_down.addWidget(self.operation)

        splitter_transf = QSplitter(Qt.Horizontal)
        # splitter_transf.addWidget(self.table_transf)

        splt_contact = QSplitter(Qt.Vertical)
        splt_contact.addWidget(FBoxTitle(u"Les clients"))
        splt_contact.addWidget(self.table_contact)
        splt_contact.resize(900, 1000)

        self.splitter_left.addWidget(splitter_down)
        splitter_details.addWidget(splitter_transf)
        splt_contact.addWidget(splitter_details)
        splitter.addWidget(self.splitter_left)
        splitter.addWidget(splt_contact)

        hbox.addWidget(splitter)
        self.setLayout(hbox)


class OperationWidget(FWidget):

    """docstring for OperationWidget"""

    def __init__(self, parent, *args, **kwargs):
        super(FWidget, self).__init__(parent=parent, *args, **kwargs)

        self.parent = parent
        vbox = QVBoxLayout()
        editbox = QGridLayout()

        self.search_field = LineEdit()
        # self.search_field.textChanged.connect(self.search)
        self.search_field.setToolTip(u"Taper le nom ou le numéro de "
                                     u"téléphone à chercher")
        editbox.addWidget(self.search_field, 0, 0)

        search_but = Button("")
        search_but.setIcon(QIcon.fromTheme('search', QIcon('')))
        search_but.clicked.connect(self.search)
        editbox.addWidget(search_but, 0, 1)
        # self.empty = FLabel(u"")
        # editbox.addWidget(self.empty, 1, 0)

        addprovid_clt_but = Button(u"Nouveau provid_clte")
        addprovid_clt_but.setIcon(QIcon.fromTheme('document-new', QIcon('')))
        addprovid_clt_but.clicked.connect(self.addprovid_clt)

        self.contact_grp = Button(u"Envoyer à provid_clte")
        self.contact_grp.setIcon(QIcon.fromTheme('document-new', QIcon('')))
        self.contact_grp.clicked.connect(self.contact_provid_clt)
        self.contact_grp.setEnabled(False)

        editbox.addWidget(addprovid_clt_but, 2, 0)
        editbox.addWidget(self.contact_grp, 1, 0)

        vbox.addLayout(editbox)
        self.setLayout(vbox)

    def search(self):

        search_term = self.search_field.text()
        self.search_field.setStyleSheet("")
        self.search_field.setText(u"")

        self.parent.table_contact.refresh_(search=search_term)
        self.search_field.clear()
        # self.search_field.setStyleSheet("font-size:20px; color: red")
        # self.search_field.setToolTip(u"{} n'existe pas".format(search_term))

    def addprovid_clt(self):
        """ Affiche un QDialog qui permet d'ajouter un nouveau provid_clte """
        self.parent.open_dialog(ProviderOrClientViewWidget, modal=True,
                                table_provid_clt=self.parent)

    def contact_provid_clt(self):
        self.parent.open_dialog(SendProviderOrClientViewWidget, modal=True,
                                table_provid_clt=self.parent)


class ProviderOrClientTableWidget(QListWidget):

    """affiche tout le nom de tous les provid_cltes"""

    def __init__(self, parent, *args, **kwargs):
        super(ProviderOrClientTableWidget, self).__init__(parent)
        self.parent = parent
        self.setAutoScroll(True)
        self.setAutoFillBackground(True)
        self.itemSelectionChanged.connect(self.handleClicked)
        self.refresh_()

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.popup)

    def popup(self, pos):
        row = self.selectionModel().selection().indexes()[0].row()
        if row < 1:
            return
        menu = QMenu()
        delaction = menu.addAction("Supprimer")
        action = menu.exec_(self.mapToGlobal(pos))

        if action == delaction:
            ProviderOrClient.get(
                ProviderOrClient.name == self.item(row).text()).delete_instance()
            self.refresh_()

    def refresh_(self):
        """ Rafraichir la liste des provid_cltes"""
        self.clear()
        self.addItem(ProviderOrClientQListWidgetItem(ALL_CONTACTS))
        for provid_clt in ProviderOrClient.select():
            self.addItem(ProviderOrClientQListWidgetItem(provid_clt))

    def handleClicked(self):
        self.provid_clt = self.currentItem()
        # self.parent.operation.contact_grp.setEnabled(True)
        self.parent.table_contact.refresh_(
            provid_clt_id=self.provid_clt.provid_clt_id)


class ProviderOrClientQListWidgetItem(QListWidgetItem):

    def __init__(self, provid_clt):
        super(ProviderOrClientQListWidgetItem, self).__init__()

        self.provid_clt = provid_clt
        icon = QIcon()
        icon.addPixmap(
            QPixmap("{}provid_clt.png".format(Config.img_media)),
            QIcon.Normal, QIcon.Off)
        self.setIcon(icon)
        self.init_text()

    def init_text(self):
        try:
            self.setText(self.provid_clt.name)
        except AttributeError:
            font = QFont()
            font.setBold(True)
            self.setFont(font)
            self.setTextAlignment(
                Qt.AlignHCenter | Qt.AlignVCenter)
            self.setText(u"Tous")

    @property
    def provid_clt_id(self):
        try:
            return self.provid_clt.id
        except AttributeError:
            return self.provid_clt


class DebtsTableWidget(FTableWidget):

    """ Reçoit un provid_clte et affiche ses contactes et affiche tous les
        contactes par defaut"""

    def __init__(self, parent, *args, **kwargs):
        FTableWidget.__init__(self, parent=parent, *args, **kwargs)

        self.parent = parent
        self.hheaders = [u'', u"Nom", u"Numéro"]
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.popup)

        # self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.stretch_columns = [1]
        self.align_map = {0: 'l'}
        self.display_vheaders = True
        self.display_fixed = True
        self.refresh_()

    def refresh_(self, provid_clt_id=None, search=None):
        self._reset()
        self.set_data_for(provid_clt_id=provid_clt_id, search=search)
        self.refresh()
        pw = 100
        self.setColumnWidth(0, 20)
        self.setColumnWidth(1, pw * 2)
        self.setColumnWidth(2, pw)

    def set_data_for(self, provid_clt_id=None, search=None):
        if isinstance(provid_clt_id, int):
            qs = ProviderOrClient.select().where(
                ProviderOrClient == ProviderOrClient.get(id=provid_clt_id))
            self.data = [("", contact_gp.contact.name, contact_gp.contact.number)
                         for contact_gp in qs]
        else:
            qs = ProviderOrClient.select()
            if search:
                print(search)
                qs = qs.where(
                    ProviderOrClient.phone.contains(search) | ProviderOrClient.name.contains(search))
                print(qs)
            self.data = [("", contact.name, contact.phone) for contact in qs]

    def popup(self, pos):
        row = self.selectionModel().selection().indexes()[0].row()
        if (len(self.data) - 1) < row:
            return False
        self.contact = ProviderOrClient.get(
            ProviderOrClient.phone == int(self.data[row][2]))

        menu = QMenu()
        menu.addAction(QIcon("{}transfer.png".format(Config.img_media)),
                       u"Faire un envoi", lambda: self.send_money(self.contact))
        menu.addAction(QIcon("{}edit_contact.png".format(Config.img_media)),
                       u"modifier le contact", lambda: self.edit_contacts(self.contact))
        addprovid_clt = menu.addMenu(u"Ajouter au provid_clte")
        delprovid_clt = menu.addMenu(u"Enlever du provid_clte")
        # Enlever du provid_clte
        no_select = ProviderOrClient.filter(
            contact__number=int(self.data[row][2]))
        [delprovid_clt.addAction(u"{}".format(grp_ct.provid_clt.name), lambda grp_ct=grp_ct: self.del_grp(
            grp_ct)) for grp_ct in no_select]
        # Ajout au provid_clte
        lt_grp_select = [(i.provid_clt.name) for i in no_select]
        [addprovid_clt.addAction(u"{}".format(grp.name), lambda grp=grp: self.add_grp(grp))
         for grp in ProviderOrClient.select() if not grp.name in lt_grp_select]
        self.action = menu.exec_(self.mapToGlobal(pos))
        self.refresh()

    def del_grp(self, grp_ct):
        provid_clt = ProviderOrClient.get(
            ProviderOrClient.name == grp_ct.provid_clt.name)
        contactgrp = ProviderOrClient.select().where(
            ProviderOrClient.provid_clt == provid_clt, ProviderOrClient.contact == self.contact).get()
        contactgrp.delete_instance()
        self.refresh()

    def add_grp(self, grpname):
        provid_clt = ProviderOrClient.get(
            ProviderOrClient.name == grpname.name)
        ProviderOrClient.get_or_create(
            provid_clt=provid_clt, contact=self.contact)
        self.refresh()

    def edit_contacts(self, ctct):
        print("edit_contacts ", ctct)

    def send_money(self, ctct):
        print("send_money ", ctct)
        # self.parent.parent.open_dialog(
        #     SendByCtViewWidget, modal=True, ctct_id=ctct)

    def _item_for_data(self, row, column, data, context=None):
        if column == 0:
            return QTableWidgetItem(QIcon(u"{}user.png".format(Config.img_media)), "")
        return super(DebtsTableWidget, self)._item_for_data(row, column,
                                                            data, context)

    def click_item(self, row, column, *args):
        contact_number = self.data[row][2]
        self.parent.table_transf.refresh_(contact_number)


class TransfTableWidget(FTableWidget):

    """ Reçoit un numero de telephone et Affiche dans un tableau tout
       les transfers effectué par ce numero """

    def __init__(self, parent, *args, **kwargs):
        FTableWidget.__init__(self, parent=parent, *args, **kwargs)

        self.hheaders = [u"Numéro", u"Date du transfert", u"Montant(FCFA)",
                         u"Reponse"]
        self.align_map = {0: 'l', 1: 'l', 2: 'r', 3: 'l'}
        self.display_vheaders = True
        self.display_fixed = True
        self.refresh_(None)

    def refresh_(self, number):
        self._reset()
        self.set_data_for(number)
        self.refresh()
        pw = 100
        self.setColumnWidth(0, pw)
        self.setColumnWidth(1, pw * 2)
        self.setColumnWidth(2, pw + 10)
        self.setColumnWidth(3, pw * 2)

    def set_data_for(self, number):
        if not number:
            return

        try:
            self.data = [(transf.contact.number, transf.date.strftime(u"%c"),
                          formatted_number(transf.amount), transf.response)
                         for transf in Refund.filter(contact__number=number).order_by(Refund.date.desc())]
        except AttributeError:
            raise
            self.hheaders = [u"Vide", ]
            self.data = ["", "Aucun transfers", "", ]
