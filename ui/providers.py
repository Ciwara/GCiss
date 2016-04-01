#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
# maintainer: Fad

from __future__ import (
    unicode_literals, absolute_import, division, print_function)

from datetime import datetime, date

from PyQt4.QtGui import (QVBoxLayout, QGridLayout, QIcon, QMenu)
from PyQt4.QtCore import Qt, QDate

from configuration import Config
from Common.ui.common import (FormLabel, FWidget, FPeriodHolder, FPageTitle,
                              Button, BttExportXLS, FormatDate, ExtendedComboBox)
from Common.ui.table import FTableWidget, TotalsWidget
from Common.ui.util import formatted_number, is_int, show_date, date_to_datetime
from models import Invoice, ProviderOrClient
from ui.payment_edit_add import EditOrAddPaymentrDialog


try:
    unicode
except:
    unicode = str


class ProvidersViewWidget(FWidget):

    def __init__(self, parent=0, *args, **kwargs):

        super(ProvidersViewWidget, self).__init__(
            parent=parent, *args, **kwargs)

        self.parent = parent

        self.title = u"Movements"

        self.on_date = FormatDate(
            QDate(date.today().year, date.today().month, 1))
        self.end_date = FormatDate(QDate.currentDate())
        self.now = datetime.now().strftime("%x")
        self.soldeField = FormLabel("0 {}".format(Config.DEVISE))
        balanceBox = QGridLayout()
        balanceBox.addWidget(self.soldeField, 0, 3)
        balanceBox.setColumnStretch(0, 1)

        self.string_list = [""] + ["{},{}".format(clt.name, clt.phone)
                                   for clt in ProviderOrClient.select().where(
            ProviderOrClient.type_ == ProviderOrClient.CLT).order_by(ProviderOrClient.name.desc())]

        self.name_client_field = ExtendedComboBox()
        self.name_client_field.addItems(self.string_list)
        self.name_client_field.setMaximumSize(
            200, self.name_client_field.maximumSize().height())
        self.name_client_field.setToolTip("Nom, numero du client")

        self.table = RapportTableWidget(parent=self)
        self.button = Button(u"Ok")
        self.button.clicked.connect(self.refresh_prov_clt)

        self.btt_export = BttExportXLS(u"Exporter")
        self.btt_export.clicked.connect(self.export_xls)

        editbox = QGridLayout()
        editbox.addWidget(FormLabel(u"Date debut"), 0, 1)
        editbox.addWidget(self.on_date, 0, 2)
        editbox.addWidget(FormLabel(u"Date fin"), 1, 1)
        editbox.addWidget(self.end_date, 1, 2)
        editbox.addWidget(self.name_client_field, 0, 3)
        editbox.addWidget(self.button, 1, 3)

        editbox.addWidget(self.btt_export, 1, 7)
        editbox.setColumnStretch(4, 2)
        vbox = QVBoxLayout()
        vbox.addWidget(FPageTitle(self.title))
        vbox.addLayout(editbox)
        vbox.addWidget(self.table)
        vbox.addLayout(balanceBox)
        self.setLayout(vbox)

    def refresh_prov_clt(self):

        try:
            self.name_client, self.phone = self.name_client_field.lineEdit().text().split(",")
            clt = ProviderOrClient.get(phone=int(self.phone.replace(" ", "")))
            self.table.refresh_(provid_clt_id=clt.id)
        except Exception as e:
            self.table.refresh_()
            print(" ", e)

    def export_xls(self):
        from Common.exports_xlsx import export_dynamic_data
        dict_data = {
            'file_name': "versements.xlsx",
            'headers': self.table.hheaders,
            'data': self.table.data,
            "extend_rows": [(1, self.table.label_mov_tt),
                            (3, self.table.balance_tt), ],
            "footers": [
                ("C", "E", "Solde au {} = {}".format(self.now, self.table.balance_tt)), ],
            'sheet': self.title,
            # 'title': self.title,
            'widths': self.table.stretch_columns,
            'format_money': ["D:D", ],
            'others': [("A7", "C7", "Compte : {}".format(self.table.provider_clt)), ],
            "date": "Du {} au {}".format(
                date_to_datetime(
                    self.on_date.text()).strftime(Config.DATEFORMAT),
                date_to_datetime(
                    self.end_date.text()).strftime(Config.DATEFORMAT))
        }
        export_dynamic_data(dict_data)

    def display_remaining(self, text):
        return """ <h2>Solde au {} : <b>{}</b> {} </h2>
               """.format(self.now,  text, Config.DEVISE)


class RapportTableWidget(FTableWidget):

    def __init__(self, parent, *args, **kwargs):

        FTableWidget.__init__(self, parent=parent, *args, **kwargs)

        self.hheaders = [
            u"Date", "Num Facture", u"Client", u"Solde", ]

        # self.setContextMenuPolicy(Qt.CustomContextMenu)
        # self.customContextMenuRequested.connect(self.popup)

        self.parent = parent

        self.sorter = True
        self.stretch_columns = [0, 2, 3]
        self.align_map = {0: 'l', 1: 'r', 3: 'r'}
        self.ecart = -400
        self.display_vheaders = False
        self.display_fixed = True
        self.refresh_()

    def refresh_(self, provid_clt_id=None, search=None):
        """ """

        self.totals_debit = 0
        self.totals_credit = 0
        self.balance_tt = 0

        l_date = [date_to_datetime(self.parent.on_date.text()),
                  date_to_datetime(self.parent.end_date.text())]
        self._reset()
        self.set_data_for(l_date, provid_clt_id=provid_clt_id, search=search)
        self.refresh()

        pw = self.parent.parent.page_width() / 6
        self.setColumnWidth(0, pw)
        self.setColumnWidth(1, pw)
        self.setColumnWidth(2, pw * 2)
        self.setColumnWidth(3, pw)

        self.parent.soldeField.setText(
            self.parent.display_remaining(formatted_number(self.balance_tt)))

        # self.hideColumn(len(self.hheaders) - 1)

    def set_data_for(self, date_, provid_clt_id=None, search=None):
        self.provid_clt_id = provid_clt_id
        qs = Invoice.select().order_by(Invoice.number.asc())
        if isinstance(self.provid_clt_id, int):
            self.provider_clt = ProviderOrClient.get(id=self.provid_clt_id)
            qs = qs.select().where(Invoice.client == self.provider_clt)
        else:
            self.provider_clt = "Tous"

        # self.data = [(show_date(pay.date), pay.libelle, pay.debit, pay.credit,
        #               pay.balance, pay.id) for pay in qs.filter(Invoice.date > date_[
        # 0], Invoice.date < date_[1]).order_by(Invoice.number.asc())]
        self.data = [(vl.date, vl.number, vl.client.name, vl.amount_ivoice,)
                     for vl in qs]

    def extend_rows(self):
        nb_rows = self.rowCount()
        self.setRowCount(nb_rows + 2)
        self.setSpan(nb_rows + 2, 2, 2, 4)
        cp = 0
        self.balance_tt = sum([is_int(unicode(self.item(row_num, 3).text()))
                               for row_num in range(0, self.data.__len__())])
        self.label_mov_tt = u"Totals "
        self.setItem(nb_rows, 2, TotalsWidget(self.label_mov_tt))
        self.setItem(
            nb_rows, 3, TotalsWidget(formatted_number(self.balance_tt)))
