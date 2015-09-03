#!usr/bin/env python
# -*- encoding: utf-8 -*-
# maintainer: Fad

from __future__ import (
    unicode_literals, absolute_import, division, print_function)

from PyQt4.QtGui import (QIcon, QVBoxLayout,
                         QGridLayout, QMenu, QPushButton, QMessageBox)
from PyQt4.QtCore import Qt

from Common.ui.util import formatted_number, is_int
from Common.ui.common import FWidget, FLabel, FPageTitle, BttExportXLS, Deleted_btt
from Common.ui.table import FTableWidget, TotalsWidget

from configuration import Config
from models import Buy, Report, Store

from Common.exports_xls import export_dynamic_data


class BuyShowViewWidget(FWidget):

    def __init__(self, buy="", parent=0, *args, **kwargs):
        super(BuyShowViewWidget, self).__init__(parent=parent,
                                                *args, **kwargs)
        self.buy = buy

        self.parentWidget().setWindowTitle(Config.APP_NAME +
                                           u"  CONSULTATION DES ACHAT")

        self.parent = parent
        self.title = "Arivage"
        vbox = QVBoxLayout()
        vbox.addWidget(FPageTitle(self.title))

        self.table_show = ShowBuyTableWidget(parent=self)

        editbox = QGridLayout()
        self.btt_export = BttExportXLS(u"Exporter")
        self.btt_export.clicked.connect(self.export_xls)
        self.button_dl = Deleted_btt(u"Annuler la facture")
        self.button_dl.released.connect(self.cancellation)

        editbox.addWidget(FLabel(u"<b>Achat N°: </b>%s" % self.buy.id), 0, 0)
        editbox.addWidget(FLabel(u"<b>Par:</b> %s " % self.buy.owner), 1, 0)
        editbox.addWidget(
            FLabel(u"<b>Fait le </b>%s" % (self.buy.date.strftime(u'%x'))), 1, 3)
        editbox.addWidget(self.button_dl, 0, 4)
        editbox.addWidget(self.btt_export, 1, 4)

        vbox.addLayout(editbox)
        vbox.addWidget(self.table_show)
        self.setLayout(vbox)

    def export_xls(self):
        table = self.table_show
        hheaders = table.hheaders[:-1]
        dict_data = {
            'file_name': "arivage.xls",
            'headers': hheaders,
            'data': self.table_show.data,
            "extend_rows": [(4, self.table_show.v_amount_tt),
                            (5, ""),
                            (6, self.table_show.b_f_tt)],
            'sheet': self.title,
            'title': self.title,
            'widths': self.table_show.stretch_columns,
            "date": self.buy.date.strftime(u'%x'),
            'exclude_row':  len(table.data) - 2,
        }
        export_dynamic_data(dict_data)

    def cancellation(self):

        buy = self.buy
        reports = Report.select().where(Report.buy == buy)
        list_err = []
        for report in reports:
            print(report)
            if not check_befor_update_data(report):
                print(report)
                list_err.append("<li><b>'%s'</b> aura <b style='color:red;'>%s</b> comme restant</li>" % (
                    report.product.name.title(), remaining))

        # if len(list_err) == 0:
        #     reply = QMessageBox.question(self, 'Confirmation',
        #                                  u"<h3 style='color:red;'>Voulez vous"
        #                                  u" vraiment annuler ce rapport"
        #                                  u" d'achat?</h3>",
        #                                  QMessageBox.Yes |
        #                                  QMessageBox.No,
        #                                  QMessageBox.No)

        #     if reply == QMessageBox.Yes:
        #         from admin import AdminViewWidget
        #         for rep in reports:
        #             suppression(rep)
        #         buy.delete_instance()
        #         self.change_main_context(AdminViewWidget)
        # else:
        #     QMessageBox.about(self, u"Alerte",
        #                       u"<h3>Vous ne pousez pas supprimer ce rapport car:</h3>"
        #                       u"<ul><li></li>"
        #                       u" %(err)s"
        #                       u"<li>Après la suppression</li></ul>"
        #                       % {"err": ' '.join(list_err)})


class ShowBuyTableWidget(FTableWidget):

    def __init__(self, parent, *args, **kwargs):
        FTableWidget.__init__(self, parent=parent, *args, **kwargs)

        self.parent = parent

        self.hheaders = [u"Modeles", u"Qte", u"P Revient", u"P Vente",
                         u"Montant", "BF Unitaire", "BF", ""]

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.popup)

        self.stretch_columns = [0, 4, 6]
        self.align_map = {1: "r", 2: 'r', 3: 'r', 4: 'r', 5: 'l', 6: 'r'}
        self.max_rows = 100
        self.display_vheaders = False
        self.refresh_()
        self.hideColumn(len(self.hheaders) - 1)

    def refresh_(self):
        """ """
        self._reset()
        self.set_data_for()
        self.refresh()

    def set_data_for(self):
        self.data = []
        self.b_f_tt = 0
        self.v_amount_tt = 0
        for item in self.parent.buy.items():
            r_amount = item.qty * item.cost_buying
            v_amount = item.qty * item.selling_price
            b_f = v_amount - r_amount
            b_f_u = b_f / item.qty

            self.b_f_tt += b_f
            self.v_amount_tt += v_amount
            self.data.append((
                item.product.name, item.qty, item.cost_buying, item.selling_price,
                v_amount, b_f_u, b_f, item.id))

    def popup(self, pos):

        from ui.ligne_edit import EditLigneViewWidget
        from ui.deleteview import DeleteViewWidget
        from data_helper import check_befor_update_data

        if (len(self.data) - 1) < self.selectionModel().selection().indexes()[0].row():
            return False
        menu = QMenu()
        editaction = menu.addAction("Modifier cette ligne")
        delaction = menu.addAction("Supprimer cette ligne")
        action = menu.exec_(self.mapToGlobal(pos))
        row = self.selectionModel().selection().indexes()[0].row()
        report = Report.get(id=self.data[row][-1])
        if action == editaction:
            try:
                self.parent.open_dialog(
                    EditLigneViewWidget, modal=True, table_p=self, report=report)
            except IndexError:
                pass

        if action == delaction:
            if check_befor_update_data(report):
                self.parent.open_dialog(
                    DeleteViewWidget, modal=True, table_p=self, report=report)
            else:
                from Common.ui.util import raise_error
                raise_error(u"Erreur", u"Impossible de supprimer ce rapport car"
                            u" le restant sera : <b>%s</b> qui est < 0" % remaining)

    def extend_rows(self):

        nb_rows = self.rowCount()
        self.setRowCount(nb_rows + 1)
        # self.setSpan(nb_rows, 0, 1, 3)
        mtt_ttc = TotalsWidget(u"Totaux: ")
        self.setItem(nb_rows, 3, mtt_ttc)

        v_amount_tt_item = TotalsWidget(formatted_number(self.v_amount_tt))
        b_f_tt_item = TotalsWidget(formatted_number(self.b_f_tt))
        self.setItem(nb_rows, 4, v_amount_tt_item)
        self.setItem(nb_rows, 6, b_f_tt_item)
        # nb_rows += 1
        # self.setRowCount(nb_rows + 1)
        # bicon = QIcon.fromTheme(
        #     '', QIcon(u"{img_media}{img}".format(img_media=Config.img_cmedia, img='del.png')))
        self.cancelbutton = Deleted_btt(u"Annuler l'achat")
        self.cancelbutton.released.connect(self.parent.cancellation)
        # self.setCellWidget(nb_rows + 1, 6, self.cancelbutton)

        # bicon = QIcon.fromTheme('document-pev',
        #                         QIcon(u"{img_media}{img}".format(img_media=Config.img_media,
        #                                                          img='de.png')))
        # self.pevbutton = Deleted_btt(bicon, u"Retour")
        # self.pevbutton.released.connect(self.parent.previews)
        # self.setCellWidget(nb_rows + 2, 2, self.pevbutton)

    def _item_for_data(self, row, column, data, context=None):
        return super(ShowBuyTableWidget, self)._item_for_data(row, column,
                                                              data, context)
