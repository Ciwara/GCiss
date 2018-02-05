#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
# maintainer: Fad
from __future__ import (
    unicode_literals, absolute_import, division, print_function)

# from datetime import datetime

from peewee import fn

from PyQt4.QtCore import QDate
from PyQt4.QtGui import QVBoxLayout, QGridLayout

from models import Report, Refund
from configuration import Config

from Common.ui.common import FWidget, FPageTitle, FormatDate, BttExportXLSX
from Common.ui.util import formatted_number, date_on_or_end, is_int
from Common.ui.table import FTableWidget, TotalsWidget


try:
    unicode
except:
    unicode = str


class ApricotsViewWidget(FWidget):

    def __init__(self, parent=0, *args, **kwargs):
        super(ApricotsViewWidget, self).__init__(
            parent=parent, *args, **kwargs)
        self.parentWidget().setWindowTitle(Config.APP_NAME + u"    La Caise")

        self.parent = parent

        vbox = QVBoxLayout()
        tablebox = QVBoxLayout()
        gridbox = QGridLayout()
        self.title = "La caise"
        tablebox.addWidget(FPageTitle(self.title))
        self.date_ = FormatDate(QDate.currentDate())
        self.btt_export = BttExportXLSX(u"Exporter")
        self.btt_export.setEnabled(False)
        self.btt_export.clicked.connect(self.export_xls)

        self.table_op = ApricotsTableWidget(parent=self)
        tablebox.addWidget(self.table_op)
        # self.date_.setFont(QFont("Courier New", 10, True))
        self.date_.dateChanged.connect(self.table_op.refresh_)

        gridbox.addWidget(self.date_, 0, 0)
        gridbox.addWidget(self.btt_export, 0, 2)
        gridbox.setColumnStretch(1, 5)

        vbox.addLayout(gridbox)
        vbox.addLayout(tablebox)
        self.setLayout(vbox)

    def export_xls(self):
        from Common.exports_xlsx import export_dynamic_data
        dict_data = {
            'file_name': "caise",
            'headers': self.table_op.hheaders,
            'data': self.table_op.get_table_items(),
            "extend_rows": [(3, self.table_op.amount_ht), ],
            'sheet': self.title,
            'title': self.title,
            'format_money': ["C:C", "D:D", ],
            'widths': self.table_op.stretch_columns,
            "date": self.date_.text()
        }
        export_dynamic_data(dict_data)

    # def refresh(self):
    #     self.table_op.refresh_()


class ApricotsTableWidget(FTableWidget):

    def __init__(self, parent, *args, **kwargs):
        FTableWidget.__init__(self, parent=parent, *args, **kwargs)

        self.parent = parent

        self.hheaders = [u"models", u"Quantité", u"P Vente", u"Montant"]

        self.stretch_columns = [0, 1, 2, 5]
        self.align_map = {1: "r", 2: "r", 3: "r", 4: "r"}
        self.sorter = True
        self.display_vheaders = False
        self.display_fixed = True
        self.refresh_()

    def refresh_(self):
        """ """
        # je cache la 6 eme colonne
        self._reset()
        self.set_data_for()
        self.refresh()
        pw = self.parent.parent.page_width() / 5
        self.setColumnWidth(1, pw)
        self.setColumnWidth(2, pw)
        self.setColumnWidth(3, pw)

    def set_data_for(self):
        date = self.parent.date_.text()
        self.data = [(rap.product.name,
                      formatted_number(rap.qty),
                      formatted_number(rap.selling_price),
                      rap.qty * rap.selling_price)
                     for rap in Report.select().where(
            Report.type_ == Report.S,
            Report.date < date_on_or_end(date, on=False),
            Report.date > date_on_or_end(date)
        ).order_by(Report.id.desc())]
        self.refresh()

    def extend_rows(self):

        self.parent.btt_export.setEnabled(True)
        self.nb_rows = self.rowCount()
        date = self.parent.date_.text()

        self.setRowCount(self.nb_rows + 4)

        self.amount_ht = 0
        for row_num in range(0, self.data.__len__()):
            mtt = is_int(self.item(row_num, 3).text())
            self.amount_ht += mtt

        row_num += 1
        self.setItem(row_num, 2, TotalsWidget(u"Total vente : "))
        self.amount_apricot = self.amount_ht
        self.setItem(row_num, 3, TotalsWidget(
            formatted_number(formatted_number(self.amount_ht))))
        row_num += 1
        self.setItem(row_num, 2, TotalsWidget(u"Dette du jour : "))
        self.total_debt = Refund.select(fn.SUM(Refund.amount)).where(
            Refund.type_ == Refund.DT, Refund.date < date_on_or_end(
                date, on=False), Refund.date > date_on_or_end(date)).scalar() or 0
        if self.total_debt:
            self.amount_apricot -= self.total_debt
        self.setItem(row_num, 3, TotalsWidget(
            formatted_number(formatted_number(self.total_debt))))
        row_num += 1
        self.setItem(row_num, 2, TotalsWidget(u"Dette reglée : "))
        self.total_refund = Refund.select(fn.SUM(Refund.amount)).where(
            Refund.type_ == Refund.RB, Refund.date < date_on_or_end(
                date, on=False), Refund.date > date_on_or_end(date)).scalar() or 0
        if self.total_refund:
            self.amount_apricot += self.total_refund
        self.setItem(row_num, 3, TotalsWidget(
            formatted_number(formatted_number(self.total_refund))))
        row_num += 1
        self.setItem(row_num, 2, TotalsWidget(u"Caise : "))
        self.setItem(row_num, 3, TotalsWidget(
            formatted_number(formatted_number(self.amount_apricot))))
        self.setSpan(self.nb_rows, 0, 4, 2)

    def _item_for_data(self, row, column, data, context=None):

        return super(ApricotsTableWidget, self)._item_for_data(
            row, column, data, context)

    def click_item(self, row, column, *args):
        pass
        self.setSpan(self.nb_rows, 0, 2, 2)

    def get_table_items(self):
        """ Recupère les elements du tableau """
        list_invoice = []
        for i in range(self.rowCount() - 1):
            liste_item = []
            try:
                liste_item.append(unicode(self.item(i, 0).text()))
                liste_item.append(is_int(self.item(i, 1).text()))
                liste_item.append(is_int(self.item(i, 2).text()))
                liste_item.append(is_int(self.item(i, 3).text()))
                list_invoice.append(liste_item)
            except Exception as e:
                print(e)
                liste_item.append("")
        return list_invoice
