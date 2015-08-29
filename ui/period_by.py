#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
# maintainer: Fad
from __future__ import (
    unicode_literals, absolute_import, division, print_function)

from datetime import date
from PyQt4.QtGui import (QVBoxLayout, QTableWidgetItem, QGridLayout)
from PyQt4.QtCore import QDate, Qt

from Common.ui.table import FTableWidget
from Common.ui.util import formatted_number, is_int, date_on_or_end
from Common.ui.common import (FWidget, FPageTitle, FormLabel, FLabel,
                              Button, FormatDate)
from models import Report


class PeriodByViewWidget(FWidget):

    def __init__(self, parent=0, *args, **kwargs):
        super(PeriodByViewWidget, self).__init__(
            parent=parent, *args, **kwargs)
        self.parent = parent
        self.title = FPageTitle(_(u"Periodic report"))

        self.on_date = FormatDate(QDate(date.today().year, 1, 1))
        self.end_date = FormatDate(QDate.currentDate())
        self.Button = Button(u"OK")
        self.Button.clicked.connect(self.rapport_filter)
        self.current_period = FLabel(self.format_period(self.on_date.text(),
                                                        self.end_date.text()))
        vbox = QVBoxLayout()
        # Grid
        gridbox = QGridLayout()
        gridbox.addWidget(FormLabel(u"Date debut"), 0, 0)
        gridbox.addWidget(self.on_date, 0, 1)
        gridbox.addWidget(FormLabel(u"Date fin"), 1, 0)
        gridbox.addWidget(self.end_date, 1, 1)
        gridbox.addWidget(self.Button, 1, 2)
        gridbox.setColumnStretch(3, 1)

        gridbox.addWidget(self.current_period, 1, 4)

        self.table = By_periodTableWidget(parent=self)

        vbox.addWidget(self.title)
        vbox.addLayout(gridbox)
        vbox.addWidget(self.table)
        self.setLayout(vbox)

    def format_period(self, on, end):
        return u"<h3>Rapport: <i style='color:LimeGreen'>%s</i>" \
               u" Au <i style='color:LimeGreen'>%s</i><h3>" \
            % (date_on_or_end(on).strftime(u"%A le %d/%m/%Y"),
               date_on_or_end(end, on=False).strftime(u"%A le %d/%m/%Y"))

    def refresh(self):

        self.table.refresh()

    def rapport_filter(self):
        self.table.refresh_(on=self.on_date.text(), end=self.end_date.text())


class By_periodTableWidget(FTableWidget):

    """ """

    def __init__(self, parent, *args, **kwargs):

        FTableWidget.__init__(self, parent=parent, *args, **kwargs)

        self.hheaders = [u"Désignation", u"Qtité restante", u"Prix U. achat",
                         u"Montant", u"Bénéfice"]
        self.stretch_columns = [0]
        self.align_map = {0: 'l', 1: 'r', 2: 'r', 3: 'r', 4: 'r'}
        self.ecart = -5
        # self.display_vheaders = False
        self.refresh_()

    def refresh_(self, on=None, end=None):
        self._reset()
        self.set_data_for(on, end)
        self.refresh()

    def set_data_for(self, on, end):
        reports = []
        if end:
            # self.parent.current_period.setText(self.parent.format_period(on,
            # end))
            reports = Report.filter(date__gte=date_on_or_end(on),
                                    date__lte=date_on_or_end(end, on=False)).order_by(Report.date.desc())

        self.data = [(rap.product, rap.remaining, rap.selling_price,
                      rap.remaining * rap.selling_price,
                      rap.qty * (rap.selling_price - rap.selling_price))
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

        pw = (self.parentWidget().width()) / (len(self.hheaders) + 2)
        # if pw == 14:
        #     pw = 125
        self.setColumnWidth(0, pw * 3)
        self.setColumnWidth(1, pw)
        self.setColumnWidth(2, pw)
        self.setColumnWidth(3, pw)
        self.setColumnWidth(4, pw)

        nb_rows = self.rowCount()
        self.setRowCount(nb_rows + 2)
        self.setSpan(nb_rows, 0, 2, 2)
        mtt_ttc = QTableWidgetItem(u"TOTAUX: ")
        mtt_ttc.setTextAlignment(Qt.AlignRight)
        self.setItem(nb_rows + 1, 2, mtt_ttc)

        self.montant_ht = 0
        self.montant_b = 0
        for row_num in xrange(0, self.data.__len__()):
            mtt = is_int(self.item(row_num, 3).text())
            mttb = is_int(self.item(row_num, 4).text())
            self.montant_ht += mtt
            self.montant_b += mttb
        # Montant TTC
        montant_t = QTableWidgetItem(formatted_number(self.montant_ht))
        montant_t.setTextAlignment(Qt.AlignRight)
        montant_tb = QTableWidgetItem(formatted_number(self.montant_b))
        montant_tb.setTextAlignment(Qt.AlignRight)
        self.setItem(row_num + 2, 3, montant_t)
        self.setItem(row_num + 2, 4, montant_tb)

    def changed_value(self, refresh=False):

        some = 0
        for row_num in xrange(0, self.data.__len__()):
            ui_item = (is_int(self.item(row_num, 1).text()) *
                       is_int(self.cellWidget(row_num, 2).text()))
            some += ui_item
            ui_item_ = QTableWidgetItem(formatted_number(ui_item))
            ui_item_.setTextAlignment(Qt.AlignRight)
            self.setItem(row_num, 3, ui_item_)
        row_num += 1
        som_val = QTableWidgetItem(formatted_number(some))
        som_val.setTextAlignment(Qt.AlignRight)
        self.setItem(row_num + 1, 2, QTableWidgetItem(u"%s" % u"TOTAUX"))
        self.setItem(row_num + 1, 3, som_val)
