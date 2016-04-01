#!/usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: Fadiga


from PyQt4.QtGui import (QSplitter, QHBoxLayout, QVBoxLayout, QPushButton,
                         QTableWidgetItem, QPixmap, QFont, QListWidget, QMenu,
                         QListWidgetItem, QIcon, QFormLayout, QGridLayout)
from PyQt4.QtCore import Qt, SIGNAL, SLOT, QSize

from Common.peewee import fn
from models import ProviderOrClient, Invoice, Refund

from Common.ui.common import FWidget, FBoxTitle, Button, LineEdit, FLabel
from Common.ui.table import FTableWidget, TotalsWidget
from Common.ui.util import formatted_number, is_int

from configuration import Config

ALL_CONTACTS = "TOUS"


class DebtsViewWidget(FWidget):

    """ Shows the home page  """

    def __init__(self, parent=0, *args, **kwargs):
        super(DebtsViewWidget, self).__init__(parent=parent,
                                              *args, **kwargs)
        self.parent = parent
        self.parentWidget().setWindowTitle(
            Config.NAME_ORGA + u"Gestion des dettes")

        hbox = QHBoxLayout(self)
        # self.balace_box = QGridLayout(self)
        # self.balace_box.addWidget(FLabel(u"Reste à payer :"), 0, 2)
        # self.balace_box.setRowStretch(1, 2)
        self.remaining_box = FLabel()
        self.remaining_box.setMaximumHeight(40)

        self.table_debt = DebtsTableWidget(parent=self)
        self.table_provid_clt = ProviderOrClientTableWidget(parent=self)

        self.search_field = LineEdit()
        self.search_field.textChanged.connect(self.search)
        self.search_field.setPlaceholderText(u"Nom ou  numéro tel")
        self.search_field.setMaximumHeight(40)
        splitter = QSplitter(Qt.Horizontal)

        self.splitter_left = QSplitter(Qt.Vertical)
        self.splitter_left.addWidget(self.search_field)
        self.splitter_left.addWidget(self.table_provid_clt)

        splt_clt = QSplitter(Qt.Vertical)
        splt_clt.addWidget(self.remaining_box)
        splt_clt.addWidget(self.table_debt)
        splt_clt.resize(900, 1000)
        splitter.addWidget(self.splitter_left)
        splitter.addWidget(splt_clt)

        hbox.addWidget(splitter)
        self.setLayout(hbox)

    def search(self):
        self.table_provid_clt.refresh_(self.search_field.text())

    def new_refund(self, provid_clt):
        from ui.refund_edit_add import RefundEditAddDialog
        self.parent.open_dialog(
            RefundEditAddDialog, modal=True, type_=Refund.RB, provid_clt=provid_clt, table_p=self.table_debt)


class ProviderOrClientTableWidget(QListWidget):

    """affiche tout le nom de tous les provid_cltes"""

    def __init__(self, parent, *args, **kwargs):
        super(ProviderOrClientTableWidget, self).__init__(parent)

        self.parent = parent
        self.setAutoScroll(True)
        # self.setAutoFillBackground(True)
        self.itemSelectionChanged.connect(self.handleClicked)
        self.refresh_()
        # self.setStyleSheet("QListWidget::item { border-bottom: 1px; }")

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.popup)

    def popup(self, pos):
        row = self.selectionModel().selection().indexes()[0].row()
        if row < 1:
            return
        menu = QMenu()
        refund = menu.addAction("Reglement")
        editaction = menu.addAction("Modifier")
        action = menu.exec_(self.mapToGlobal(pos))

        provid_clt = ProviderOrClient.get(
            ProviderOrClient.phone == self.item(row).text().split(",")[1])
        if action == refund:
            if provid_clt.is_indebted():
                self.parent.new_refund(provid_clt)
            else:
                self.parent.parent.Notify(
                    "Le client {} n'est pas endetté".format(self.item(row).text()), "error")
        if action == editaction:
            from GCommon.ui.provider_client_edit_add import EditOrAddClientOrProviderDialog
            self.parent.open_dialog(EditOrAddClientOrProviderDialog, modal=True,
                                    prov_clt=provid_clt, table_p=self)

    def refresh_(self, provid_clt=None):
        """ Rafraichir la liste des provid_cltes"""
        self.clear()
        self.addItem(ProviderOrClientQListWidgetItem(ALL_CONTACTS))
        qs = ProviderOrClient.select().where(
            ProviderOrClient.type_ == ProviderOrClient.CLT)
        if provid_clt:
            qs = qs.where(ProviderOrClient.name.contains(provid_clt))
        for provid_clt in qs:
            self.addItem(ProviderOrClientQListWidgetItem(provid_clt))

    def handleClicked(self):
        self.provid_clt = self.currentItem()
        self.parent.table_debt.refresh_(
            provid_clt_id=self.provid_clt.provid_clt_id)


class ProviderOrClientQListWidgetItem(QListWidgetItem):

    def __init__(self, provid_clt):
        super(ProviderOrClientQListWidgetItem, self).__init__()

        self.provid_clt = provid_clt
        self.setSizeHint(QSize(0, 30))
        icon = QIcon()

        if not isinstance(self.provid_clt, str):
            icon.addPixmap(QPixmap("{}.png".format(
                Config.img_media + "debt" if self.provid_clt.is_indebted() else Config.img_cmedia + "user_active")),
                QIcon.Normal, QIcon.Off)

        self.setIcon(icon)
        self.init_text()

    def init_text(self):
        try:
            self.setText(
                "{}, {}".format(self.provid_clt.name, self.provid_clt.phone))
        except AttributeError:
            font = QFont()
            font.setBold(True)
            self.setFont(font)
            self.setTextAlignment(Qt.AlignCenter)
            self.setText(u"Tous")

    @property
    def provid_clt_id(self):
        try:
            return self.provid_clt.id
        except AttributeError:
            return self.provid_clt


class DebtsTableWidget(FTableWidget):

    """ Reçoit un provid_clte et affiche ses dettes et affiche tous les
        dettes par defaut"""

    def __init__(self, parent, *args, **kwargs):
        FTableWidget.__init__(self, parent=parent, *args, **kwargs)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.popup)

        self.parent = parent
        self.hheaders = [
            "", "type", u"Date", u"Numéro", u"Montant", u"Reste à payé"]

        self.setDragEnabled(True)
        self.stretch_columns = [0, 1]
        self.align_map = {0: 'l', 1: "l", 2: "l", 3: "r", 4: "r", 5: "r"}
        self.display_vheaders = True
        self.display_fixed = True
        self.refresh_()

    def popup(self, pos):
        row = self.selectionModel().selection().indexes()[0].row()
        if (len(self.data) - 1) < row:
            return
        refund = Refund.get(id=self.data[row][0])
        # if refund.type_ != Refund.RB:
        #     return
        menu = QMenu()
        edit_refund = menu.addAction("Modification")
        del_refund = menu.addAction("Suprimer")
        action = menu.exec_(self.mapToGlobal(pos))

        if action == del_refund:
            from ui.deleteview import DeleteViewWidget
            self.parent.open_dialog(DeleteViewWidget, modal=True, obj=refund,
                                    table_p=self)
        if action == edit_refund:
            from ui.refund_edit_add import RefundEditAddDialog
            self.parent.open_dialog(RefundEditAddDialog, modal=True,
                                    type_=Refund.RB, refund=refund, table_p=self)

    def refresh_(self, provid_clt_id=None, search=None):
        self._reset()
        self.set_data_for(provid_clt_id=provid_clt_id, search=search)
        self.refresh()

        pw = self.parent.parent.page_width() / 8
        self.setColumnWidth(0, 40)
        self.setColumnWidth(1, 40)
        self.setColumnWidth(2, pw * 2)
        self.setColumnWidth(3, pw)
        self.setColumnWidth(4, pw)
        self.setColumnWidth(5, pw)

    def set_data_for(self, provid_clt_id=None, search=None):
        self.provid_clt_id = provid_clt_id
        qs = Refund.select().where(
            Refund.status == False).order_by(Refund.date.desc())

        self.remaining = 0
        if isinstance(provid_clt_id, int):
            qs = qs.select().where(
                Refund.provider_client == ProviderOrClient.get(id=provid_clt_id))
        else:
            for prov in ProviderOrClient.select().where(
                    ProviderOrClient.type_ == ProviderOrClient.CLT):
                self.remaining += prov.last_remaining()
        self.parent.remaining_box.setText(
            self.display_remaining(formatted_number(self.remaining)))

        self.data = [(ref.id, ref.type_, ref.date, ref.invoice.number,
                      ref.amount, ref.remaining) for ref in qs.iterator()]

    def extend_rows(self):
        if isinstance(self.provid_clt_id, int):
            self.remaining = is_int(self.item(0, 5).text())
            self.parent.remaining_box.setText(
                self.display_remaining(formatted_number(self.remaining)))

    def _item_for_data(self, row, column, data, context=None):
        if column == 0:
            return QTableWidgetItem(QIcon(u"{}find.png".format(Config.img_cmedia)), "")
        if column == 1 and self.data[row][1] == Refund.RB:
            return QTableWidgetItem(QIcon(u"{img_media}{img}".format(img_media=Config.img_media,
                                                                     img="in.png")), u"")
        if column == 1 and self.data[row][1] == Refund.DT:
            return QTableWidgetItem(QIcon(u"{img_media}{img}".format(img_media=Config.img_media,
                                                                     img="out.png")), u"")
        return super(DebtsTableWidget, self)._item_for_data(row, column,
                                                            data, context)

    def click_item(self, row, column, *args):
        if column != 0:
            return

        from ui.invoice_show import ShowInvoiceViewWidget
        try:
            self.parent.open_dialog(ShowInvoiceViewWidget, modal=True, opacity=100,
                                    invoice_num=self.data[row][3])
        except Exception as e:
            print(e)

    def display_remaining(self, text):
        return """
        <h2>Dette restante: <b>{}</b> Fcfa </h2>
        """.format(text)
