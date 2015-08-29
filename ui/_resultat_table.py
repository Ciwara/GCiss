#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
# maintainer: Fad
from __future__ import (
    unicode_literals, absolute_import, division, print_function)


from PyQt4.QtGui import QTableWidgetItem, QIcon

from models import (Product)
from configuration import Config
from Common.ui.table import FTableWidget


class ResultatTableWidget(FTableWidget):

    """docstring for ResultatTableWidget"""

    def __init__(self, parent, *args, **kwargs):
        FTableWidget.__init__(self, parent=parent, *args, **kwargs)

        self.parent = parent
        self.hheaders = [u"Produits", u"Ajouter"]
        self.stretch_columns = [0]
        self.align_map = {0: 'l', 1: 'r'}
        # self.display_fixed = True
        self.refresh_()

    def refresh_(self, value=None):

        self._reset()
        self.set_data_for(value)
        self.refresh()
        pw = (self.width()) * 2 - 20
        self.setColumnWidth(0, pw)
        self.setColumnWidth(1, 20)

    def set_data_for(self, prod_find):

        products = Product.select().order_by(Product.name.asc())
        if prod_find:
            products = products.where(Product.name.contains(prod_find))

        self.data = [(prod.name, "") for prod in products]

    def _item_for_data(self, row, column, data, context=None):
        if column == 1:
            return QTableWidgetItem(QIcon(u"{img_media}{img}".format(img_media=Config.img_cmedia,
                                                                     img="go-next.png")), "")
        return super(ResultatTableWidget, self)._item_for_data(row, column,
                                                               data, context)

    def click_item(self, row, column, *args):
        self.choix = Product.filter(name=self.data[row][0]).get()
        self.parent.table_info.refresh_(self.choix.id)
        if column == 1:
            self.parent.table_buy.refresh_(self.choix)
