#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
# maintainer: Fad
from __future__ import (
    unicode_literals, absolute_import, division, print_function)

from PyQt4.QtCore import QDate

from PyQt4.QtGui import (
    QVBoxLayout, QIcon, QTableWidgetItem, QGridLayout)

from datetime import date
from Common.ui.common import FWidget, LineEdit, Button, FormatDate, FormLabel
from Common.ui.table import FTableWidget
from Common.ui.util import is_int, date_on_or_end

from models import Invoice, Buy, ProviderOrClient
from configuration import Config


class PurchaseInvoiceWidget(FWidget):

    """ Shows the home page  """

    def __init__(self, parent=0, *args, **kwargs):
        super(PurchaseInvoiceWidget, self).__init__(
            parent=parent, *args, **kwargs)

        self.parentWidget().setWindowTitle(
            Config.APP_NAME + u"    TABLEAU DE BORD")

        self.parent = parent

        # self.now = datetime.now()
        # self.today = datetime(self.now.year, self.now.month, self.now.day)
        vbox = QVBoxLayout()
        table_buy = QVBoxLayout()

        self.on_date = FormatDate(QDate(date.today().year, 1, 1))
        self.on_date.dateChanged.connect(self.finder_date)
        self.end_date = FormatDate(QDate.currentDate())
        self.end_date.dateChanged.connect(self.finder_date)
        self.search_field = LineEdit()
        self.search_field.setPlaceholderText(
            "Taper un nom client ou num. facture")
        self.search_field.setMinimumSize(
            500, self.search_field.maximumSize().height())
        self.search_field.textChanged.connect(self.finder)

        self.add_buy = Button(u"+ &Nouvel Achat")
        self.add_buy.clicked.connect(self.goto_add)
        self.add_buy.setFixedWidth(300)

        editbox = QGridLayout()
        editbox.addWidget(self.add_buy, 0, 0)
        editbox.addWidget(self.search_field, 0, 1)
        editbox.setColumnStretch(2, 2)
        editbox.addWidget(FormLabel(u"Date debut"), 0, 3)
        editbox.addWidget(self.on_date, 0, 4)
        editbox.addWidget(FormLabel(u"Date fin"), 0, 5)
        editbox.addWidget(self.end_date, 0, 6)

        self.table_buy = BuyTableWidget(parent=self)
        table_buy.addWidget(self.table_buy)
        vbox.addLayout(editbox)
        vbox.addLayout(table_buy)
        self.setLayout(vbox)

    def goto_add(self):
        from ui.buy import BuyViewWidget
        self.change_main_context(BuyViewWidget)

    def finder_date(self):
        print("finder_date")
        self.table_buy.refresh_()

    def finder(self):
        self.table_buy.refresh_(self.search_field.text())


class BuyTableWidget(FTableWidget):

    def __init__(self, parent, *args, **kwargs):
        FTableWidget.__init__(self, parent=parent, *args, **kwargs)
        self.hheaders = [u"Numéro", u"Date", "fourmisseur", "Afficher"]

        self.parent = parent
        self.sorter = True

        self.stretch_columns = [0, 1, 2, 3]
        self.ecart = -15
        self.display_vheaders = False
        # self.align_map = {0: 'r', 1: 'l', 2: 'r'}
        self.refresh_()

    def refresh_(self, value=None):
        """ """
        self._reset()
        self.set_data_for(value)
        self.refresh()

    def set_data_for(self, value):
        if value:
            value = str(value)
            if is_int(value):
                qs = ((Buy.id == int(value)))
                buys = Buy.select().where(qs)
            else:
                buys = []
                for clt in ProviderOrClient.select().where(
                        ProviderOrClient.name.contains(value)).iterator():
                    for buy in clt.buys().iterator():
                        buys.append(buy)
        else:
            buys = Buy.select().order_by(Buy.id.desc()).iterator()

        try:
            self.data = [(
                buy.id, buy.date, buy.provd_or_clt, "") for buy in buys]
            # self.data = [(
            #     buy.id, buy.date, buy.provd_or_clt, "") for buy in buys if (
            #     buy.date > date_on_or_end(
            #         self.parent.on_date) and buy.date < date_on_or_end(
            #         self.parent.end_date, on=False))]
        except Exception as e:
            print("Exception ", e)

    def _item_for_data(self, row, column, data, context=None):
        if column == self.data[0].__len__() - 1:
            return QTableWidgetItem(
                QIcon(u"{img_media}{img}".format(img_media=Config.img_cmedia,
                                                 img="find.png")), (u"voir"))

        return super(BuyTableWidget, self)._item_for_data(row, column,
                                                          data, context)

    def click_item(self, row, column, *args):
        last_column = self.hheaders.__len__() - 1
        if column != last_column:
            return

        from ui.buy_show import BuyShowViewWidget
        try:
            self.parent.open_dialog(
                BuyShowViewWidget, modal=True, opacity=100,
                table_p=self, buy=Buy.get(id=self.data[row][0]))
        except Exception as e:
            print(e)
