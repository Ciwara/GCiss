#!usr/bin/env python
# -*- encoding: utf-8 -*-
# maintainer: Fad
from __future__ import (
    unicode_literals, absolute_import, division, print_function)

from PyQt4.QtGui import (QVBoxLayout, QHBoxLayout,
                         QIcon, QGridLayout, QSplitter, QFrame, QMessageBox,
                         QPushButton, QMenu, QCompleter, QPixmap)
from PyQt4.QtCore import Qt

from configuration import Config
from models import Invoice, Report
from tools.export_pdf import pdf_view
from tools.export_xls import write_invoice_xls
from Common.ui.util import formatted_number, is_int, uopen_file
from Common.ui.common import FWidget, FPageTitle, FLabel, LineEdit
from Common.ui.table import FTableWidget, TotalsWidget

from Common.exports_xls import export_dynamic_data


class ShowInvoiceViewWidget(FWidget):

    def __init__(self, invoice_num, parent=0, *args, **kwargs):
        super(ShowInvoiceViewWidget, self).__init__(
            parent=parent, *args, **kwargs)
        self.invoice = Invoice.get(number=invoice_num)
        self.parentWidget().setWindowTitle(Config.NAME_ORGA +
                                           u"  CONSULTATION DE FACTURE")

        self.parent = parent

        vbox = QVBoxLayout()
        self.title = u"Facture"

        tablebox = QVBoxLayout()
        self.table_show = ShowOrderTableWidget(parent=self)
        tablebox.addWidget(self.table_show)

        formbox = QVBoxLayout()
        editbox = QGridLayout()
        xls_bicon = QIcon.fromTheme(
            'document-del', QIcon(u"{}xls.png".format(Config.img_cmedia)))
        pdf_icon = QIcon.fromTheme(
            'document-del', QIcon(u"{}pdf.png".format(Config.img_cmedia)))
        self.button_pdf = QPushButton(pdf_icon, u"")
        self.button_pdf.setFixedWidth(30)
        self.button_pdf.setFixedHeight(30)
        self.button_xls = QPushButton(xls_bicon, u"")
        self.button_xls.setFixedWidth(30)
        self.button_xls.setFixedHeight(30)
        self.button_pdf.released.connect(self.printer_pdf)
        self.button_xls.released.connect(self.export_xls)

        editbox.addWidget(FLabel(u"Facture N°: %s"
                                 % self.invoice.number), 0, 0)
        editbox.addWidget(FLabel(u"%s le %s" % (self.invoice.location,
                                                self.invoice.date.strftime(u'%x'))), 1, 4)
        editbox.addWidget(FLabel(u"Doit: %s " % self.invoice.client), 1, 0)
        editbox.addWidget(self.button_pdf, 1, 5)
        editbox.addWidget(self.button_xls, 1, 6)

        formbox.addLayout(editbox)
        vbox.addLayout(formbox)
        vbox.addLayout(tablebox)
        self.setLayout(vbox)

    def export_xls(self):

        from Common.cel import cel
        table = self.table_show
        endrowx = len(table.hheaders) - 1
        dict_data = {
            'file_name': "facture.xls",
            'headers': table.hheaders,
            'data': table.data,
            "extend_rows": [(3, table.montant_ht)],
            'sheet': self.title,
            'title': self.title,
            'widths': table.stretch_columns,
            "date": self.invoice.date.strftime(u'%x'),
            "others": [
                (5, 5, 0, 2, "Doit: {}".format(self.invoice.client)),
                (45, 45, 0, endrowx,
                 "Arrêté la présente facture à la somme de : {} FCFA".format(cel(table.montant_ht))),
                (50, 50, 0, 0, "Pour acquit"),
                (50, 50, endrowx, endrowx, "Le fournisseur")]
        }
        export_dynamic_data(dict_data)
    # def printer_xls(self):
    #     write_invoice_xls("invoice.xls", self.invoice)

    def printer_pdf(self):
        pdf_report = pdf_view("invoice.pdf", self.invoice)
        uopen_file(pdf_report)

    def annulation(self):
        reply = QMessageBox.question(self, 'Confirmation',
                                     u"<h2 style='color:red;'>Voulez vous vraiment annuler cette"
                                     u" facture?</h2>",
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)

        if reply == QMessageBox.Yes:
            from ui.dashboard import DashbordViewWidget
            rep = Report()
            rep.store = 1
            for item in Report.filter(invoice=self.invoice):
                item.delete_instance()
            self.invoice.delete_instance()
            self.change_main_context(DashbordViewWidget)


class ShowOrderTableWidget(FTableWidget):

    def __init__(self, parent, *args, **kwargs):
        FTableWidget.__init__(self, parent=parent, *args, **kwargs)

        self.parent = parent

        self.hheaders = [_(u"Quantité"), _(u"Désignation"), _(u"Prix Unitaire"),
                         _(u"Montant")]
        self.stretch_columns = [1, 3]
        self.align_map = {2: 'r', 3: 'r'}
        self.max_rows = 100
        # self.display_vheaders = False
        self.display_fixed = True
        self.refresh_()

    def refresh_(self):
        """ """
        self._reset()
        self.set_data_for()
        self.refresh()

        pw = self.parent.parent.page_width() / 5
        self.setColumnWidth(0, pw)
        self.setColumnWidth(1, pw * 2)
        self.setColumnWidth(2, pw)
        self.setColumnWidth(3, pw)

    def set_data_for(self):

        items = self.parent.invoice.items if self.parent.invoice.items else []

        self.data = [(item.qty, item.product.name, item.selling_price,
                      item.qty * item.selling_price) for item in items]

    def extend_rows(self):

        nb_rows = self.rowCount()
        self.setRowCount(nb_rows + 3)
        self.setSpan(nb_rows, 0, 3, 2)
        mtt_ttc = TotalsWidget(u"Total: ")
        mtt_ttc.setTextAlignment(Qt.AlignRight)
        self.setItem(nb_rows + 1, 2, mtt_ttc)

        self.montant_ht = 0
        for row_num in xrange(0, self.data.__len__()):
            qty = is_int(self.item(row_num, 0).text())
            pu = is_int(self.item(row_num, 2).text())
            self.montant_ht += (qty * pu)
        # Montant TTC
        montant_ttc_item = TotalsWidget(formatted_number(self.montant_ht))
        montant_ttc_item.setTextAlignment(Qt.AlignRight)
        self.setItem(row_num + 2, 3, montant_ttc_item)

        # bicon = QIcon.fromTheme(
        #     'document-del', QIcon(u"{}del.png".format(Config.img_media)))
        # self.button = QPushButton(bicon, u"Annuler la facture")
        # self.button.released.connect(self.parent.annulation)
        # self.setCellWidget(nb_rows + 2, 3, self.button)

        # self.setColumnWidth(1, 250)
