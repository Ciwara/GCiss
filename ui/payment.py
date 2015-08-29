#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
# maintainer: Fad

from __future__ import (
    unicode_literals, absolute_import, division, print_function)

from datetime import datetime

from PyQt4.QtGui import (QVBoxLayout, QGridLayout, QIcon)
from PyQt4.QtCore import Qt

from configuration import Config
from Common.ui.common import (
    FWidget, FPeriodHolder, FPageTitle, Button, BttExportXLS)
from Common.ui.table import FTableWidget, TotalsWidget
from Common.ui.util import formatted_number, is_int, show_date
from models import Invoice, Report, Payment
from ui.payment_edit_add import EditOrAddPaymentrDialog
from Common.exports_xls import export_dynamic_data


try:
    unicode
except:
    unicode = str


class PaymentViewWidget(FWidget, FPeriodHolder):

    def __init__(self, parent=0, *args, **kwargs):

        super(PaymentViewWidget, self).__init__(
            parent=parent, *args, **kwargs)
        FPeriodHolder.__init__(self, *args, **kwargs)

        self.parentWidget().setWindowTitle(
            Config.APP_NAME + u"    TOUS LES RAPPORTS")
        self.parent = parent

        self.title = u"Movements"
        self.table = RapportTableWidget(parent=self)

        self.btt_export = BttExportXLS(u"Exporter")
        self.btt_export.clicked.connect(self.export_xls)
        self.add_btt = Button("Créditer")
        self.add_btt.setIcon(QIcon(u"{img_media}{img}".format(img_media=Config.img_media,
                                                              img="in.png")))
        self.add_btt.clicked.connect(self.add_payment)
        self.sub_btt = Button("Débiter")
        self.sub_btt.setIcon(QIcon(u"{img_media}{img}".format(img_media=Config.img_media,
                                                              img="out.png")))
        self.sub_btt.clicked.connect(self.sub_payment)

        editbox = QGridLayout()
        editbox.addWidget(self.add_btt, 0, 2)
        editbox.addWidget(self.sub_btt, 0, 3)
        editbox.addWidget(self.btt_export, 0, 6)
        editbox.setColumnStretch(5, 5)
        vbox = QVBoxLayout()
        vbox.addWidget(FPageTitle(self.title))
        vbox.addLayout(editbox)
        vbox.addWidget(self.table)
        self.setLayout(vbox)

    def refresh(self):
        self.table.refresh_()

    def export_xls(self):
        dict_data = {
            'file_name': "versement.xls",
            'headers': self.table.hheaders,
            'data': self.table.data,
            "extend_rows": [(1, self.table.label_mov_tt),
                            (2, self.table.totals_debit),
                            (3, self.table.totals_credit), ],
            "footers": [
                (0, 2, 3, self.table.label_balance),
                (0, 4, 4, self.table.balance_tt), ],
            'sheet': self.title,
            'title': self.title,
            'widths': self.table.stretch_columns,
            # "date": self.table.date.strftime(u"%x")
        }
        export_dynamic_data(dict_data)

    def add_payment(self):
        self.open_dialog(EditOrAddPaymentrDialog, modal=True,
                         payment=None, type_=Payment.CREDIT, table_p=self)

    def sub_payment(self):
        self.open_dialog(EditOrAddPaymentrDialog, modal=True,
                         payment=None, type_=Payment.DEBIT, table_p=self)


class RapportTableWidget(FTableWidget):

    def __init__(self, parent, *args, **kwargs):

        FTableWidget.__init__(self, parent=parent, *args, **kwargs)

        self.hheaders = [
            u"Date", u"Libelle opération", u"débit", u"Crédit", u"Solde"]

        self.parent = parent

        self.sorter = True
        self.stretch_columns = [0, 1, 4]
        self.align_map = {0: 'l', 1: 'l', 2: 'r', 3: 'r', 4: 'r'}
        self.ecart = -5
        self.display_vheaders = False
        self.set_data_for()
        self.refresh()

    def refresh_(self):
        """ """
        self._reset()
        self.set_data_for()
        self.refresh()

    def set_data_for(self):

        self.data = [(show_date(pay.date), pay.libelle, pay.debit, pay.credit,
                      pay.balance) for pay in Payment.select().order_by(Payment.date.asc())]

    def click_item(self, row, column, *args):
        product_column = 1

    def extend_rows(self):

        nb_rows = self.rowCount()
        self.setRowCount(nb_rows + 2)
        self.setSpan(nb_rows + 2, 2, 2, 4)
        self.totals_debit = 0
        self.totals_credit = 0
        self.balance_tt = 0
        for row_num in xrange(0, self.data.__len__()):
            mtt_debit = is_int(unicode(self.item(row_num, 2).text()))
            mtt_credit = is_int(unicode(self.item(row_num, 3).text()))
            self.totals_debit += mtt_debit
            self.totals_credit += mtt_credit

        self.balance_tt = self.totals_debit - self.totals_credit

        self.label_mov_tt = u"Total general mouvements: "
        self.setItem(nb_rows, 1, TotalsWidget(self.label_mov_tt))
        self.setItem(
            nb_rows, 2, TotalsWidget(formatted_number(self.totals_debit)))
        self.setItem(
            nb_rows, 3, TotalsWidget(formatted_number(self.totals_credit)))

        self.label_balance = u"Solde au {} ".format(
            datetime.now().strftime("%x"))
        self.setItem(
            nb_rows + 1, 1, TotalsWidget(self.label_balance))
        self.setItem(
            nb_rows + 1, 2, TotalsWidget(formatted_number(self.balance_tt)))
