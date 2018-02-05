#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
# maintainer: Fad
from __future__ import (
    unicode_literals, absolute_import, division, print_function)

from datetime import date

from PyQt4.QtGui import (QGridLayout, QVBoxLayout)
from PyQt4.QtCore import QDate, Qt

from configuration import Config
from database import Report, Product

from Common.ui.common import (FWidget, FPageTitle, FormLabel, BttExportXLSX,
                              Button, FormatDate, IntLineEdit)
from Common.ui.table import FTableWidget, TotalsWidget
from Common.ui.util import formatted_number, is_int, date_to_datetime


class InventoryViewWidget(FWidget):

    def __init__(self, parent=0, *args, **kwargs):
        super(InventoryViewWidget, self).__init__(
            parent=parent, *args, **kwargs)

        self.parentWidget().setWindowTitle(
            Config.APP_NAME + u"     INVENTAIRE")

        self.parent = parent

        self.title = u"Inventaire"

        self.on_date = FormatDate(QDate(date.today().year, 1, 1))
        self.end_date = FormatDate(QDate.currentDate())
        self.button = Button(u"Ok")
        self.button.clicked.connect(self.rapport_filter)
        self.btt_export = BttExportXLSX(u"Exporter")
        self.btt_export.clicked.connect(self.export_xls)

        self.invent_table = InventaireTableWidget(parent=self)
        # Grid
        gridbox = QGridLayout()
        gridbox.addWidget(FormLabel(u"Date debut"), 0, 1)
        gridbox.addWidget(self.on_date, 0, 2)
        gridbox.addWidget(FormLabel(u"Date fin"), 1, 1)
        gridbox.addWidget(self.end_date, 1, 2)
        gridbox.addWidget(self.button, 1, 3)
        gridbox.addWidget(self.btt_export, 1, 6)
        gridbox.setColumnStretch(4, 5)
        vbox = QVBoxLayout()
        vbox.addWidget(FPageTitle(self.title))
        vbox.addLayout(gridbox)
        vbox.addWidget(self.invent_table)
        self.setLayout(vbox)
        self.refresh()

    def refresh(self):
        self.l_date = [
            date_to_datetime(self.on_date.text()), date_to_datetime(self.end_date.text())]
        self.invent_table.refresh_period(self.l_date)

    def rapport_filter(self):
        self.refresh()

    def export_xls(self):
        from Common.exports_xlsx import export_dynamic_data
        table = self.invent_table
        hheaders = table.hheaders
        dict_data = {
            'file_name': "Inventaire",
            'headers': hheaders,
            'data': table.data,
            "extend_rows": [(3, table.sum_totals), ],
            'sheet': self.title,
            # 'title': self.title,
            'format_money': ["C:C", "D:D", ],
            'widths': table.stretch_columns,
            "date": "Du {} au {}".format(
                date_to_datetime(self.on_date.text()).strftime(u'%d/%m/%Y'),
                date_to_datetime(self.end_date.text()).strftime(u'%d/%m/%Y'))
        }
        export_dynamic_data(dict_data)


class InventaireTableWidget(FTableWidget):

    def __init__(self, parent, *args, **kwargs):
        FTableWidget.__init__(self, parent=parent, *args, **kwargs)

        self.hheaders = [
            u"Désignation", u"Qtité restante", u"P.U. vente", u"Montant"]

        self.parent = parent

        self.stretch_columns = [0, 3]
        self.align_map = {0: 'l', 1: 'r', 2: 'r', 3: 'r'}
        self.display_fixed = True
        self.set_data_for()
        self.refresh()

    def refresh_period(self, l_date):
        self._reset()
        self.set_data_for(l_date)
        self.refresh()

        pw = self.parent.parent.page_width() / 5
        self.setColumnWidth(0, pw)
        self.setColumnWidth(1, pw)
        self.setColumnWidth(2, pw)
        self.setColumnWidth(3, pw)

    def set_data_for(self, *args):

        if args:
            reports = []
            for prod in Product.all():
                try:
                    reports.append(
                        Report.filter(Report.product == prod, Report.date > args[0][
                            0], Report.date < args[0][1]).order_by(Report.date.desc()).get())
                except:
                    pass
            self.data = [(rap.product.name, rap.remaining,
                          rap.selling_price, rap.remaining * rap.selling_price)
                         for rap in reports]

    def get_table_items(self):
        """  """
        list_invoice = []
        for i in range(self.rowCount() - 1):
            liste_item = []
            try:
                liste_item.append(unicode(self.item(i, 0).text()))
                liste_item.append(is_int(self.item(i, 1).text()))
                liste_item.append(is_int(self.item(i, 2).text()))
                liste_item.append(is_int(self.item(i, 3).text()))
                list_invoice.append(liste_item)
            except:
                liste_item.append("")

        return list_invoice

    def extend_rows(self):

        nb_rows = self.rowCount()
        self.setRowCount(nb_rows + 2)
        self.setSpan(nb_rows, 0, 2, 2)
        self.setItem(nb_rows + 1, 2, TotalsWidget(u"TOTAUX: "))

        self.sum_totals = 0
        for row_num in range(0, self.data.__len__()):
            self.sum_totals += is_int(self.item(row_num, 3).text())
        self.setItem(
            row_num + 2, 3, TotalsWidget(formatted_number(self.sum_totals)))

    # def changed_value(self, refresh=False):

    #     self.sum_totals = 0
    #     for row_num in xrange(0, self.data.__len__()):
    #         total = (is_int(self.item(row_num, 1).text()) *
    #                  is_int(self.cellWidget(row_num, 2).text()))
    #         self.sum_totals += total
    #         ui_item_ = TotalsWidget(formatted_number(total))
    #         self.setItem(row_num, 3, ui_item_)
    #     row_num += 1
    #     self.setItem(
    #         row_num + 1, 3, TotalsWidget(formatted_number(self.sum_totals)))

    # def _item_for_data(self, row, column, data, context=None):
    #     if column == 2:
    #         line_edit = IntLineEdit("")
    #         line_edit.textChanged.connect(self.changed_value)
    # return line_edit
    #     return super(InventaireTableWidget, self)._item_for_data(row,
    #                                                              column, data,
    #                                                              context)
