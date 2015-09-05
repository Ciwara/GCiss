#!/usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: Fadiga


from PyQt4.QtGui import (QSplitter, QHBoxLayout, QVBoxLayout, QPushButton,
                         QTableWidgetItem, QPixmap, QFont, QListWidget,
                         QListWidgetItem, QIcon, QMenu, QFormLayout)
from PyQt4.QtCore import Qt, SIGNAL, SLOT

from models import ProviderOrClient, Invoice, Refund

from Common.ui.common import FWidget, FBoxTitle, Button, LineEdit
from Common.ui.table import FTableWidget, TotalsWidget
from Common.ui.util import formatted_number, show_date, is_int

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

        self.table_debt = DebtsTableWidget(parent=self)
        self.table_provid_clt = ProviderOrClientTableWidget(parent=self)
        # self.table_refund = RefundTableWidget(parent=self)
        # self.operation = OperationWidget(parent=self)

        self.search_field = LineEdit()
        self.search_field.textChanged.connect(self.search)
        self.search_field.setPlaceholderText(u"Nom ou  numéro tel")

        splitter = QSplitter(Qt.Horizontal)

        self.splitter_left = QSplitter(Qt.Vertical)
        self.splitter_left.addWidget(self.search_field)
        self.splitter_left.addWidget(self.table_provid_clt)

        splitter_details = QSplitter(Qt.Horizontal)

        # splitter_down = QSplitter(Qt.Vertical)
        # splitter_down.addWidget(self.operation)

        # splitter_transf = QSplitter(Qt.Horizontal)
        # splitter_transf.addWidget(self.table_refund)

        splt_clt = QSplitter(Qt.Vertical)
        # splt_clt.addWidget(FBoxTitle(u"Les clients"))
        splt_clt.addWidget(self.table_debt)
        splt_clt.resize(900, 1000)

        # self.splitter_left.addWidget(splitter_down)
        # splitter_details.addWidget(splitter_transf)
        splt_clt.addWidget(splitter_details)
        splitter.addWidget(self.splitter_left)
        splitter.addWidget(splt_clt)

        hbox.addWidget(splitter)
        self.setLayout(hbox)

    def search(self):

        search_term = self.search_field.text()
        print(search_term)
        # self.search_field.setStyleSheet("")
        # self.search_field.setText(u"")

        # self.table_debt.refresh_(search=search_term)
        # self.search_field.clear()

    def new_refund(self):
        from ui.refund_edit_add import RefundEditAddDialog
        self.parent.open_dialog(
            RefundEditAddDialog, modal=True, table_p=self.table_debt)


# class OperationWidget(FWidget):

#     """docstring for OperationWidget"""

#     def __init__(self, parent, *args, **kwargs):
#         super(FWidget, self).__init__(parent=parent, *args, **kwargs)

#         self.parent = parent

#         self.search_field = LineEdit()
#         self.search_field.textChanged.connect(self.search)
#         self.search_field.setToolTip(u"Taper le nom ou le numéro de "
#                                      u"téléphone à chercher")

# btt_addprovid_clt = Button(u"Nouveau Reglement")
# btt_addprovid_clt.setIcon(QIcon.fromTheme('document-new', QIcon('')))
# btt_addprovid_clt.clicked.connect(self.new_refund)

#         formbox = QFormLayout()

# formbox.addWidget(self.search_field, 0, 0)
# formbox.addWidget(btt_addprovid_clt, 1, 0)
#         formbox.addRow("", self.search_field)
# formbox.addRow("", btt_addprovid_clt)
#         vbox = QVBoxLayout()
#         vbox.addLayout(formbox)
#         self.setLayout(vbox)

#     def search(self):

#         search_term = self.search_field.text()
#         self.search_field.setStyleSheet("")
#         self.search_field.setText(u"")

#         self.parent.table_debt.refresh_(search=search_term)
#         self.search_field.clear()

#     def add_provid_clt(self):
#         from provider_client_edit_add import EditOrAddClientOrProviderDialog
#         self.parent.open_dialog(EditOrAddClientOrProviderDialog, modal=True,
#                                 table_p=self.parent)


class ProviderOrClientTableWidget(QListWidget):

    """affiche tout le nom de tous les provid_cltes"""

    def __init__(self, parent, *args, **kwargs):
        super(ProviderOrClientTableWidget, self).__init__(parent)
        self.parent = parent
        self.setAutoScroll(True)
        self.setAutoFillBackground(True)
        self.itemSelectionChanged.connect(self.handleClicked)
        self.refresh_()

        # self.setContextMenuPolicy(Qt.CustomContextMenu)
        # self.customContextMenuRequested.connect(self.popup)

    def popup(self, pos):
        row = self.selectionModel().selection().indexes()[0].row()
        if row < 1:
            return
        menu = QMenu()
        delaction = menu.addAction("modifier")
        action = menu.exec_(self.mapToGlobal(pos))

        if action == delaction:
            ProviderOrClient.get(ProviderOrClient.type_ == ProviderOrClient.CLT,
                                 ProviderOrClient.name == self.item(row).text()).delete_instance()
            self.refresh_()

    def refresh_(self):
        """ Rafraichir la liste des provid_cltes"""
        self.clear()
        self.addItem(ProviderOrClientQListWidgetItem(ALL_CONTACTS))
        for provid_clt in ProviderOrClient.select().where(ProviderOrClient.type_ == ProviderOrClient.CLT):
            self.addItem(ProviderOrClientQListWidgetItem(provid_clt))

    def handleClicked(self):
        self.provid_clt = self.currentItem()
        # self.parent.operation.contact_grp.setEnabled(True)
        self.parent.table_debt.refresh_(
            provid_clt_id=self.provid_clt.provid_clt_id)


class ProviderOrClientQListWidgetItem(QListWidgetItem):

    def __init__(self, provid_clt):
        super(ProviderOrClientQListWidgetItem, self).__init__()

        self.provid_clt = provid_clt
        icon = QIcon()
        icon.addPixmap(
            QPixmap("{}user_active.png".format(Config.img_cmedia)),
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

    """ Reçoit un provid_clte et affiche ses dettes et affiche tous les
        dettes par defaut"""

    def __init__(self, parent, *args, **kwargs):
        FTableWidget.__init__(self, parent=parent, *args, **kwargs)

        self.parent = parent
        self.hheaders = ["", u"Date", u"Numéro", u"Montant", u"Reste à payé"]

        self.setDragEnabled(True)
        self.stretch_columns = [0, 1]
        self.align_map = {0: 'l', 1: "l", 2: "r", 3: "r", 4: "r"}
        self.display_vheaders = True
        self.display_fixed = True
        self.refresh_()

    def refresh_(self, provid_clt_id=None, search=None):
        self._reset()
        self.set_data_for(provid_clt_id=provid_clt_id, search=search)
        self.refresh()

        pw = self.parent.parent.page_width() / 7
        self.setColumnWidth(0, 40)
        self.setColumnWidth(1, pw * 2)
        self.setColumnWidth(2, pw)
        self.setColumnWidth(3, pw)
        self.setColumnWidth(4, pw)

    def set_data_for(self, provid_clt_id=None, search=None):

        qs = Refund.select().where(Refund.status == False)
        if isinstance(provid_clt_id, int):
            qs = qs.select().where(
                Refund.provider_client == ProviderOrClient.get(id=provid_clt_id))
        self.data = [
            ("", show_date(ref.date), ref.invoice.number, ref.amount, ref.remaining) for ref in qs]

    def extend_rows(self):

        nb_rows = self.rowCount()
        self.setRowCount(nb_rows + 2)
        self.setSpan(nb_rows, 0, 1, 5)
        nb_rows += 1
        self.setSpan(nb_rows, 0, 1, 2)
        self.setItem(nb_rows, 3, TotalsWidget(u"Dette: "))

        self.remaining = is_int(self.item(self.data.__len__() - 1, 4).text())
        self.setItem(
            nb_rows, 4, TotalsWidget(formatted_number(self.remaining)))
        self.btt_refund = QPushButton(u"Reglement")
        # self.btt_refund.released.connect(self.new_refund)
        # self.setCellWidget(nb_rows, 2, self.btt_refund)

    def new_refund(self):
        print("cool")

    def _item_for_data(self, row, column, data, context=None):
        if column == 0:
            return QTableWidgetItem(QIcon(u"{}find.png".format(Config.img_cmedia)), "")
        return super(DebtsTableWidget, self)._item_for_data(row, column,
                                                            data, context)

    def click_item(self, row, column, *args):
        if column != 0:
            return
        from ui.invoice_show import ShowInvoiceViewWidget
        try:
            self.parent.change_main_context(ShowInvoiceViewWidget,
                                            invoice_num=self.data[row][2])
        except IndexError:
            pass

        # inv_number = self.data[row][2]
        # self.parent.table_refund.refresh_(inv_number)


# class RefundTableWidget(FTableWidget):

#     """ Reçoit un numero de telephone et Affiche dans un tableau tout
#        les transfers effectué par ce numero """

#     def __init__(self, parent, *args, **kwargs):
#         FTableWidget.__init__(self, parent=parent, *args, **kwargs)

#         self.parent = parent
#         self.hheaders = [u"Date", u"Numéro", u"Montant", u"Reste à payé"]
#         self.align_map = {0: 'l', 1: 'l', 2: 'r', 3: 'r'}
#         self.display_vheaders = True
#         self.display_fixed = True
#         self.refresh_(None)

#     def refresh_(self, number):
#         self._reset()
#         self.set_data_for(number)
#         self.refresh()
#         pw = self.parent.parent.page_width() / 7
#         self.setColumnWidth(0, pw * 2)
#         self.setColumnWidth(1, pw)
#         self.setColumnWidth(2, pw)

#     def set_data_for(self, inv_number):
#         if not inv_number:
#             return

#         qs = Refund.select().where(
#             Refund.invoice == Invoice.get(id=inv_number))
#         self.data = [(show_date(refund.date), refund.invoice.number,
#                       refund.amount, refund.remaining) for refund in qs]
