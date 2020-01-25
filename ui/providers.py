#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
# maintainer: Fad

from __future__ import (
    unicode_literals, absolute_import, division, print_function)

from datetime import datetime, date

from PyQt4.QtGui import (QVBoxLayout, QGridLayout,
                         QIcon, QMenu, QTableWidgetItem)
from PyQt4.QtCore import Qt, QDate

from configuration import Config
from Common.ui.common import (FormLabel, FWidget, FPeriodHolder, FPageTitle,
                              Button, BttExportXLSX, FormatDate, ExtendedComboBox)
from Common.ui.table import FTableWidget, TotalsWidget
from Common.ui.util import device_amount, is_int, date_to_datetime
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
            QDate(date.today().year, 1, 1))
        self.end_date = FormatDate(QDate.currentDate())
        # self.now = datetime.now().strftime("%x")
        self.soldeField = FormLabel("{}".format(device_amount(0)))
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

        self.btt_export = BttExportXLSX(u"Exporter")
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
            'file_name': "versements",
            'headers': self.table.hheaders[:-1],
            'data': self.table.data,
            "extend_rows": [(1, self.table.label_mov_tt),
                            (3, self.table.balance_tt), ],
            # "footers": [],
            'sheet': self.title,
            # 'title': self.title,
            'widths': self.table.stretch_columns,
            'exclude_row': len(self.table.data) - 1,
            'format_money': ["D:D", ],
            'others': [("A7", "B7", "Compte : {}".format(self.table.provider_clt)),
                       ("A8", "B8", "Du {} au {} : {}".format(
                        date_to_datetime(self.on_date.text()).strftime(
                            Config.DATEFORMAT),
                        date_to_datetime(self.end_date.text()).strftime(
                            Config.DATEFORMAT),
                        device_amount(self.table.balance_tt))), ],
        }
        export_dynamic_data(dict_data)

    def display_remaining(self, amount_text):
        return """ <h2>Solde du {} au {} : <b>{}</b></h2>
               """.format(date_to_datetime(
            self.on_date.text()).strftime(Config.DATEFORMAT),
            date_to_datetime(
            self.end_date.text()).strftime(Config.DATEFORMAT), amount_text)


class RapportTableWidget(FTableWidget):

    def __init__(self, parent, *args, **kwargs):

        FTableWidget.__init__(self, parent=parent, *args, **kwargs)

        self.hheaders = [
            u"Date", "Num. Facture", u"Client", u"Montant Facture", ""]

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
        self.d_star = date_to_datetime(self.parent.on_date.text())
        self.d_end = date_to_datetime(self.parent.end_date.text())
        l_date = [self.d_star, self.d_end]
        self._reset()
        self.set_data_for(l_date, provid_clt_id=provid_clt_id, search=search)
        self.refresh()

        pw = self.parent.parent.page_width() / 6
        self.setColumnWidth(0, pw)
        self.setColumnWidth(1, pw)
        self.setColumnWidth(2, pw * 2)
        self.setColumnWidth(3, pw)

        self.parent.soldeField.setText(
            self.parent.display_remaining(device_amount(self.balance_tt)))

        # self.hideColumn(len(self.hheaders) - 1)

    def set_data_for(self, date_, provid_clt_id=None, search=None):
        self.provid_clt_id = provid_clt_id
        qs = Invoice.select().order_by(Invoice.number.asc())
        if isinstance(self.provid_clt_id, int):
            self.provider_clt = ProviderOrClient.get(id=self.provid_clt_id)
            qs = qs.select().where(Invoice.client == self.provider_clt)
        else:
            self.provider_clt = "Tous"

        self.data = [(vl.date, vl.number, vl.client.name, vl.amount_ivoice, "")
                     for vl in qs if (vl.date > date_[0] and vl.date < date_[1])]

    def _item_for_data(self, row, column, data, context=None):
        if column == self.data[0].__len__() - 1:
            return QTableWidgetItem(
                QIcon(u"{img_media}{img}".format(img_media=Config.img_cmedia,
                                                 img="find.png")), (u"voir"))

        return super(RapportTableWidget, self)._item_for_data(row, column,
                                                              data, context)

    def click_item(self, row, column, *args):
        last_column = self.hheaders.__len__() - 1
        if column != last_column:
            return

        from ui.invoice_show import ShowInvoiceViewWidget
        try:
            self.parent.open_dialog(ShowInvoiceViewWidget, modal=True, opacity=100,
                                    table_p=self, invoice_num=self.data[row][1])
        except Exception as e:
            print(e)

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
            nb_rows, 3, TotalsWidget(device_amount(self.balance_tt)))
