#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
# maintainer: Fad
from __future__ import (
    unicode_literals, absolute_import, division, print_function)

from datetime import datetime

from PyQt4.QtCore import QDate, Qt
from PyQt4.QtGui import QIcon, QVBoxLayout, QGridLayout, QFont

from models import Report
from configuration import Config

from Common.exports_xls import export_dynamic_data
from Common.ui.common import FWidget, FPageTitle, FormatDate, BttExportXLS
from Common.ui.util import formatted_number, date_on_or_end, is_int
from Common.ui.table import FTableWidget, TotalsWidget


class ApricotsViewWidget(FWidget):

    def __init__(self, parent=0, *args, **kwargs):
        super(ApricotsViewWidget, self).__init__(
            parent=parent, *args, **kwargs)
        self.parentWidget().setWindowTitle(Config.APP_NAME + u"    La Caise")

        self.parent = parent

        tablebox = QVBoxLayout()
        gridbox = QGridLayout()
        self.title = "La caise"
        tablebox.addWidget(FPageTitle(self.title))

        self.date_ = FormatDate(QDate.currentDate())
        self.table_op = ApricotsTableWidget(parent=self)
        tablebox.addWidget(self.table_op)
        # self.date_.setFont(QFont("Courier New", 10, True))
        self.date_.dateChanged.connect(self.refresh)
        self.btt_export = BttExportXLS(u"Exporter")
        self.btt_export.clicked.connect(self.export_xls)

        gridbox.addWidget(self.date_, 0, 0)
        gridbox.addWidget(self.btt_export, 0, 2)
        gridbox.setColumnStretch(1, 5)

        vbox = QVBoxLayout()
        vbox.addLayout(gridbox)
        vbox.addLayout(tablebox)
        self.setLayout(vbox)

    def export_xls(self):
        dict_data = {
            'file_name': "arivage.xls",
            'headers': self.table_op.hheaders,
            'data': self.table_op.data,
            "extend_rows": [(3, self.table_op.amount_ht), ],
            'sheet': self.title,
            'title': self.title,
            'widths': self.table_op.stretch_columns,
            "date": self.date_.text()
        }
        export_dynamic_data(dict_data)

    def refresh(self):
        self.table_op.refresh_(self.date_.text())


class ApricotsTableWidget(FTableWidget):

    def __init__(self, parent, *args, **kwargs):
        FTableWidget.__init__(self, parent=parent, *args, **kwargs)

        self.parent = parent

        self.hheaders = [u"models", u"Quantité",
                         u"P Vente", u"Montant"]

        self.stretch_columns = [1, 2, 5]
        self.align_map = {1: "r", 2: "r", 3: "r", 4: "r"}
        self.sorter = True
        self.display_vheaders = False
        self.display_fixed = True
        self.refresh_(self.parent.date_.text())

    def refresh_(self, today):
        """ """
        # je cache la 6 eme colonne
        self._reset()
        self.set_data_for(today)
        self.refresh()
        # self.hideColumn(6)
        pw = self.parent.parent.page_width() / 5
        self.setColumnWidth(1, pw)
        self.setColumnWidth(2, pw)
        self.setColumnWidth(3, pw)

    def set_data_for(self, today):

        self.data = [(rap.product.name,
                      formatted_number(rap.qty),
                      formatted_number(rap.selling_price),
                      rap.qty * rap.selling_price)
                     for rap in Report.select().where(
            Report.type_ == Report.S,
            Report.date < date_on_or_end(today, on=False),
            Report.date > date_on_or_end(today)
        ).order_by(Report.id.desc())]

    def extend_rows(self):
        nb_rows = self.rowCount()
        self.setRowCount(nb_rows + 1)
        self.setSpan(nb_rows, 0, 1, 2)
        self.setItem(nb_rows, 2, TotalsWidget(u"Montant"))

        self.amount_ht = 0
        for row_num in xrange(0, self.data.__len__()):
            mtt = is_int(self.item(row_num, 3).text())
            self.amount_ht += mtt

        amount_ht_item = TotalsWidget(
            formatted_number(formatted_number(self.amount_ht)))
        amount_ht_item.setTextAlignment(Qt.AlignRight | Qt.AlignCenter)
        self.setItem(nb_rows, 3, amount_ht_item)

    def _item_for_data(self, row, column, data, context=None):

        return super(ApricotsTableWidget, self)._item_for_data(row, column,
                                                               data, context)

    def click_item(self, row, column, *args):
        pass
