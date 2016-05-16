#!usr/bin/env python
# -*- encoding: utf-8 -*-
# maintainer: Fad
from __future__ import (
    unicode_literals, absolute_import, division, print_function)

from PyQt4.QtGui import (QVBoxLayout, QHBoxLayout, QWidget, QDialog,
                         QIcon, QGridLayout, QSplitter, QFrame, QMessageBox,
                         QPushButton, QMenu, QCompleter, QPixmap)
from PyQt4.QtCore import Qt

from configuration import Config
from models import Invoice, Report
# from tools.export_pdf import pdf_view
from GCommon.tools.pdf_invoice import pdf_view
# from tools.pdf import draw_pdf

from Common.ui.util import formatted_number, is_int, uopen_file, show_date
from Common.ui.common import FWidget, FPageTitle, FLabel, LineEdit, Deleted_btt
from Common.ui.table import FTableWidget, TotalsWidget

try:
    unicode
except:
    unicode = str


class ShowInvoiceViewWidget(QDialog, FWidget):

    def __init__(self, invoice_num, parent=0, *args, **kwargs):
        # super(ShowInvoiceViewWidget, self).__init__(
        #     parent=parent, *args, **kwargs)
        QDialog.__init__(self, parent, *args, **kwargs)

        self.invoice = Invoice.get(number=invoice_num)
        self.parentWidget().setWindowTitle(Config.NAME_ORGA +
                                           u"  CONSULTATION DE FACTURE")

        self.parent = parent

        vbox = QVBoxLayout()
        self.title = self.invoice.type_

        self.table_show = ShowOrderTableWidget(parent=self)

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
        self.button_dl = Deleted_btt(u"Annuler la facture")
        self.button_dl.released.connect(self.cancellation)

        editbox.addWidget(FLabel(u"{typ} N°: {num}".format(
            num=self.invoice.number, typ=self.invoice.type_)), 0, 0)
        editbox.addWidget(FLabel(u"%s le %s" % (self.invoice.location,
                                                show_date(self.invoice.date))), 1, 4)
        editbox.addWidget(FLabel(u"Doit: %s " % self.invoice.client), 1, 0)
        editbox.addWidget(self.button_pdf, 1, 5)
        editbox.addWidget(self.button_dl, 0, 4)
        editbox.addWidget(self.button_xls, 1, 6)

        vbox.addLayout(editbox)
        vbox.addWidget(self.table_show)
        self.setLayout(vbox)

    def export_xls(self):
        # TODO A
        from Common.exports_xlsx import export_dynamic_data
        from num2words import num2words
        table = self.table_show
        hheaders = table.hheaders[:-1]
        data = table.data
        endrowx = len(hheaders) - 1
        dict_data = {
            'file_name': "facture.xlsx",
            'headers': hheaders,
            'data': data,
            "extend_rows": [(3, table.montant_ht), ],
            'sheet': self.title,
            # 'title': self.title,
            'widths': table.stretch_columns,
            "date": show_date(self.invoice.date),
            "others": [
                ("A7", "B7", "FACTURE N° : {}".format(self.invoice.number)),
                ("A8", "B8", "Doit: {}".format(self.invoice.client.name)),
                ("A35", "D35", "Arrêté la présente facture à la somme de : {} FCFA".format(
                    num2words(table.montant_ht, lang="fr"))),
                ("A38", "B38", "Pour acquit"),
                ("C38", "D38", "Le fournisseur"),
            ],
            # 'exclude_row': len(data) - 2,
        }
        export_dynamic_data(dict_data)

    def printer_pdf(self):
        # pdf_report = draw_pdf(self.invoice)
        pdf_report = pdf_view("invoice", self.invoice)
        uopen_file(pdf_report)

    def cancellation(self):
        reply = QMessageBox.question(self, 'Confirmation',
                                     u"<h2 style='color:red;'>Voulez vous vraiment annuler cette"
                                     u" facture?</h2>",
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)

        if reply == QMessageBox.Yes:
            from ui.dashboard import DashbordViewWidget
            self.invoice.deletes_data()
            self.change_main_context(DashbordViewWidget)


class ShowOrderTableWidget(FTableWidget):

    def __init__(self, parent, *args, **kwargs):
        FTableWidget.__init__(self, parent=parent, *args, **kwargs)

        self.parent = parent

        self.hheaders = [
            u"Quantité", u"Désignation", u"Prix Unitaire", u"Montant", ""]

        # self.setContextMenuPolicy(Qt.CustomContextMenu)
        # self.customContextMenuRequested.connect(self.popup)

        self.stretch_columns = [1, 3]
        self.align_map = {2: 'r', 3: 'r'}
        self.max_rows = 100
        # self.display_vheaders = False
        self.display_fixed = True
        self.refresh_()
        self.hideColumn(len(self.hheaders) - 1)

    def refresh_(self):
        """ """
        self._reset()
        self.set_data_for()
        self.refresh()

        # pw = (self.parent.parent.page_width() / 5) - 20
        # self.setColumnWidth(0, pw)
        # self.setColumnWidth(1, pw * 2)
        # self.setColumnWidth(2, pw)
        # self.setColumnWidth(3, pw)

    def set_data_for(self):

        items = self.parent.invoice.items if self.parent.invoice.items else []
        self.data = [(item.qty, item.product.name, item.selling_price,
                      item.qty * item.selling_price, item.id) for item in items]

    def popup(self, pos):

        from ui.ligne_edit import EditLigneViewWidget
        from ui.deleteview import DeleteViewWidget
        from data_helper import check_befor_update_data
        row = self.selectionModel().selection().indexes()[0].row()
        if (len(self.data) - 1) < row:
            return False
        menu = QMenu()
        editaction = menu.addAction("Modifier cette ligne")
        delaction = menu.addAction("Supprimer cette ligne")
        action = menu.exec_(self.mapToGlobal(pos))
        report = Report.get(id=self.data[row][-1])
        if action == editaction:
            try:
                self.parent.open_dialog(EditLigneViewWidget, modal=True,
                                        table_p=self, report=report)
            except IndexError:
                pass
        if action == delaction:
            list_error = check_befor_update_data(report)
            if list_error == []:
                if len(self.data) < 2:
                    self.parent.cancellation()
                else:
                    self.parent.open_dialog(
                        DeleteViewWidget, modal=True, obj=report, table_p=self,)
            else:
                from Common.ui.util import raise_error
                raise_error(u"Impossible de supprimer", """<h3>L'article {} :</h3>
                        Aura <b>{}</b> comme dernier restant.""".format(
                    report.product.name, list_error[-1]))

    def extend_rows(self):

        nb_rows = self.rowCount()
        self.setRowCount(nb_rows + 2)

        self.montant_ht = 0
        for row_num in xrange(0, self.data.__len__()):
            self.montant_ht += (is_int(self.item(row_num, 0).text())
                                * is_int(self.item(row_num, 2).text()))
        row_num += 1
        self.setItem(row_num, 2, TotalsWidget(u"Totaux : "))
        self.setItem(
            row_num, 3, TotalsWidget(formatted_number(self.montant_ht)))
        row_num += 1
        self.setItem(row_num, 2, TotalsWidget(u"Montant payé : "))
        self.setItem(row_num, 3, TotalsWidget(
            formatted_number(self.montant_ht - self.parent.invoice.paid_amount)))
        self.setSpan(nb_rows, 0, 2, 2)

    def get_table_items(self):
        """ Recupère les elements du tableau """
        list_invoice = []
        for i in range(self.rowCount() - 1):
            liste_item = []
            try:
                liste_item.append(is_int(self.item(i, 0).text()))
                liste_item.append(unicode(self.item(i, 1).text()))
                liste_item.append(is_int(self.item(i, 2).text()))
                liste_item.append(is_int(self.item(i, 3).text()))
                list_invoice.append(liste_item)
            except Exception as e:
                print(e)
                liste_item.append("")
        return list_invoice
