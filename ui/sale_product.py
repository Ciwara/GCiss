#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
# maintainer: Fad

from PyQt4.QtGui import (QVBoxLayout, QIcon, QTableWidgetItem, QGridLayout)

# from Common.tabpane import tabbox
from datetime import datetime
from Common.ui.common import FWidget, Button, LineEdit
from Common.ui.table import FTableWidget
from Common.ui.util import is_int, date_on_or_end

from models import Invoice, ProviderOrClient
from configuration import Config


class SaleProducteWidget(FWidget):

    """ Shows the home page  """

    def __init__(self, parent=0, *args, **kwargs):
        super(SaleProducteWidget, self).__init__(
            parent=parent, *args, **kwargs)

        self.parentWidget().setWindowTitle(
            Config.APP_NAME + u"    TABLEAU DE BORD")

        self.parent = parent
        self.now = datetime.now()
        self.today = datetime(self.now.year, self.now.month, self.now.day)

        vbox = QVBoxLayout()
        table_invoice = QVBoxLayout()
        editbox = QGridLayout()

        self.add_invoice = Button(u"+ &Nouvel Vente")
        self.add_invoice.clicked.connect(self.goto_add)
        self.add_invoice.setFixedWidth(300)
        self.search_field = LineEdit()
        self.search_field.setPlaceholderText(
            "Taper un nom client ou num. facture")
        self.search_field.setMinimumSize(
            500, self.search_field.maximumSize().height())
        self.search_field.textChanged.connect(self.all_finder)

        self.date_on = self.today
        self.date_end = self.today

        self.this_day = Button(u"&Aujord'hui")
        self.this_day.clicked.connect(self.today_finder)
        self.this_week = Button(u"&Cette semaine")
        self.this_week.clicked.connect(self.week_finder)
        self.this_month = Button(u"&Ce mois")
        self.this_month.clicked.connect(self.month_finder)
        self.this_year = Button(u"&Cette année")
        self.this_year.clicked.connect(self.year_finder)
        self.all = Button(u"&Tous")
        self.all.clicked.connect(self.all_finder)

        editbox.addWidget(self.add_invoice, 0, 0)
        editbox.addWidget(self.search_field, 0, 1)
        editbox.setColumnStretch(2, 3)
        # editbox.addWidget(self.this_day, 1, 0)
        # editbox.addWidget(self.this_week, 1, 1)
        # editbox.addWidget(self.this_month, 1, 2)
        # editbox.addWidget(self.this_year, 1, 3)
        # editbox.addWidget(self.all, 1, 4)

        self.table_invoice = InvoiceTableWidget(parent=self)
        table_invoice.addWidget(self.table_invoice)
        vbox.addLayout(editbox)
        vbox.addLayout(table_invoice)
        self.setLayout(vbox)

    def goto_add(self):
        from ui.invoice import InvoiceViewWidget
        self.change_main_context(InvoiceViewWidget)

    def today_finder(self):
        self.table_invoice.refresh_(self.search_field.text())

    def week_finder(self):
        self.table_invoice.refresh_(self.search_field.text())

    def month_finder(self):
        self.table_invoice.refresh_(self.search_field.text())

    def year_finder(self):
        self.table_invoice.refresh_(self.search_field.text())

    def all_finder(self):
        self.table_invoice.refresh_(self.search_field.text())


class InvoiceTableWidget(FTableWidget):

    def __init__(self, parent):
        FTableWidget.__init__(self, parent=parent)
        self.hheaders = [u"Facture N°", u"Date", u"Doit", u"Consulter"]

        self.parent = parent

        self.sorter = True
        self.stretch_columns = [1, 2]
        # self.display_fixed = True
        self.display_vheaders = False
        self.align_map = {0: 'r', 1: 'r', 2: 'l', }
        self.refresh_()

    def refresh_(self, value=None):
        """ """
        self._reset()
        self.set_data_for(value)
        self.refresh()

        pw = self.parent.parent.page_width() / 5
        self.setColumnWidth(0, pw)
        self.setColumnWidth(1, pw)
        self.setColumnWidth(2, pw)

    def set_data_for(self, value):

        # qs = ((Invoice.date > date_on_or_end(self.parent.date_on)),
        #       (Invoice.date < date_on_or_end(self.parent.date_end, on=False)))
        # print(Invoice.where(qs))

        invoices = Invoice.select()
        # invoices = Invoice()
        # print(invoices)
        if value:
            value = str(value)
            if is_int(value):
                print("Num Facture")
                qs = ((Invoice.number == int(value)))
                invoices = invoices.where(qs)
                # invoices = Invoice.select().where(
                #     qs, Invoice.date >= date_on, Invoice.date < date_end)
            else:
                invoices = []
                for clt in ProviderOrClient.select().where(
                        ProviderOrClient.name.contains(value)).iterator():
                    for invoice in clt.invoices().iterator():
                        invoices.append(invoice)
        else:
            invoices = invoices.order_by(Invoice.number.desc()).iterator()

        try:
            self.data = [(
                invoice.number, invoice.date,
                invoice.client, "") for invoice in invoices]
            # self.data = [(
            #     invoice.number, invoice.date,
            #     invoice.client, "") for invoice in invoices if (
            #     invoice.date > date_on_or_end(
            #         self.parent.date_on) and invoice.date < date_on_or_end(
            #         self.parent.date_end, on=False))]
        except Exception as e:
            print("Exception ", e)

    def _item_for_data(self, row, column, data, context=None):
        if column == self.data[0].__len__() - 1:
            return QTableWidgetItem(
                QIcon(u"{img_media}{img}".format(img_media=Config.img_cmedia,
                                                 img="find.png")), (u"voir"))

        return super(InvoiceTableWidget, self)._item_for_data(row, column,
                                                              data, context)

    def click_item(self, row, column, *args):
        last_column = self.hheaders.__len__() - 1
        if column != last_column:
            return

        from ui.show_invoice import ShowInvoiceViewWidget
        try:
            self.parent.open_dialog(
                ShowInvoiceViewWidget, modal=True, opacity=100,
                table_p=self, invoice_num=self.data[row][0])
        except Exception as e:
            print(e)
