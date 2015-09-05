#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
# maintainer: Fad
from __future__ import (
    unicode_literals, absolute_import, division, print_function)

from PyQt4.QtCore import QDate, Qt
from PyQt4.QtGui import (QVBoxLayout, QHBoxLayout, QGridLayout,
                         QIcon, QSplitter, QFrame, QPushButton, QMenu,
                         QCompleter)

from models import Product, Report, Buy, ProviderOrClient, Owner
from configuration import Config

from Common.ui.table import FTableWidget, TotalsWidget
from Common.ui.common import (FWidget, IntLineEdit, FBoxTitle, FLabel,
                              FormLabel, FormatDate, Button, LineEdit)
from Common.ui.util import (raise_error, formatted_number, is_int,  raise_success,
                            date_to_datetime, check_is_empty, field_error)

from GCommon.ui.product_edit_or_add import EditOrAddProductsDialog
from GCommon.ui._product_detail import InfoTableWidget
from ui._resultat_table import ResultatTableWidget
from ui.buy_show import BuyShowViewWidget


try:
    unicode
except:
    unicode = str


class BuyViewWidget(FWidget):

    def __init__(self, parent=0, *args, **kwargs):
        super(BuyViewWidget, self).__init__(parent=parent, *args, **kwargs)
        self.parentWidget().setWindowTitle(
            Config.APP_NAME + u"    Arrivage d'article")
        self.parent = parent

        vbox = QVBoxLayout(self)
        hbox = QHBoxLayout(self)
        editbox = QGridLayout()

        self.date = FormatDate(QDate.currentDate())
        self.name_client = LineEdit()
        self.search_field = LineEdit()
        self.search_field.setPlaceholderText("Rechercher un article")
        # self.search_field.setMaximumSize(350,
        # self.search_field.maximumSize().height())
        self.search_field.textChanged.connect(self.finder)
        self.search_field.setFixedWidth(200)

        self.add_prod = Button(u"+ &Article")
        self.add_prod.clicked.connect(self.add_product)
        self.add_prod.setFixedWidth(80)
        # self.add_prod.setFixedHeight(20)
        self.add_prod.setStyleSheet("Text-align:botton")
        self.add_prod.setToolTip("Ajouter un nouvel article")

        self.table_buy = BuyTableWidget(parent=self)
        self.table_resultat = ResultatTableWidget(parent=self)
        self.table_info = InfoTableWidget(parent=self)

        # editbox.addWidget(self.search_field, 0, 0)
        editbox.addWidget(self.add_prod, 0, 1)
        editbox.addWidget(FormLabel(u"Date d'achat:"), 0, 4)
        editbox.addWidget(self.date, 0, 5)

        editbox.setColumnStretch(3, 3)
        splitter = QSplitter(Qt.Horizontal)

        splitter_left = QSplitter(Qt.Vertical)
        splitter_down = QSplitter(Qt.Vertical)
        # splitter_left.addWidget(FBoxTitle(u"Les produits"))
        splitter_left.addWidget(self.search_field)
        splitter_left.addWidget(self.table_resultat)
        splitter_down.resize(35, 20)
        splitter_down.addWidget(self.table_info)

        splitter_rigth = QSplitter(Qt.Vertical)
        # splitter_rigth.addWidget(FBoxTitle(u"Les produits achetés"))
        splitter_rigth.addWidget(self.table_buy)
        splitter_rigth.resize(800, 900)

        splitter_left.addWidget(splitter_down)
        splitter.addWidget(splitter_left)
        splitter.addWidget(splitter_rigth)

        hbox.addWidget(splitter)
        vbox.addLayout(editbox)
        vbox.addLayout(hbox)
        self.setLayout(vbox)

    def add_product(self):
        """ """
        self.open_dialog(EditOrAddProductsDialog, modal=True,
                         product=None, table_p=self.table_resultat)

    def finder(self):
        search_term = str(self.search_field.text())
        self.table_resultat.refresh_(search_term)

    def save_b(self):
        ''' add operation '''
        # entete de la facture
        if not self.table_buy.isvalid:
            return False
        owner = Owner.get(Owner.islog == True)
        date = str(self.date.text())
        values_t = self.table_buy.get_table_items()
        buy = Buy()
        # buy.date = datetime_
        buy.provd_or_clt = \
            ProviderOrClient.get_or_create(
                "Fournisseur", 000000, ProviderOrClient.FSEUR)
        buy.owner = owner
        try:
            buy.save()
            err = False
        except:
            raise
            raise_error(
                "Erreur", u"Impossible d'enregistrer l'entête de la facture")
            return False
        for name, qty, cost_buying, selling_price in values_t:
            rep = Report()
            rep.buy = buy
            rep.type_ = Report.E
            rep.store = 1
            rep.date = date_to_datetime(date)
            rep.product = Product.get(name=name)
            rep.qty = int(qty)
            rep.cost_buying = int(cost_buying)
            rep.selling_price = int(selling_price)
            try:
                rep.save()
            except Exception as e:
                print(e)
                err = True
        if err:
            buy.delete_instance()
            raise_error("Erreur", u"Ce mouvement n'a pas pu etre "
                        u"enregistré dans les rapports")
            return False
        else:
            self.parent.Notify(u"L'entrée des articles avec succès", "success")
        self.change_main_context(BuyShowViewWidget, buy=buy)


class BuyTableWidget(FTableWidget):

    def __init__(self, parent, *args, **kwargs):
        FTableWidget.__init__(self, parent=parent, *args, **kwargs)

        self.parent = parent

        self.hheaders = [u"Modeles", u"Qte", u"P Revient", u"P Vente",
                         u"Montant", "BF Unitaire", "BF"]

        # self.setSelectionMode(QAbstractItemView.NoSelection)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.popup)

        self.stretch_columns = [0]
        self.align_map = {3: 'r'}
        self.display_vheaders = False
        self.display_fixed = True
        self.refresh_()
        self.isvalid = False

    def refresh_(self, choix=None):
        if choix:
            self.row = ["%s" % choix.name, "", "", "", "", "", ""]
            if not [row for row in self.data if self.row[0] in row]:
                self.set_data_for()
                self.refresh()

    def set_data_for(self):

        self._reset()
        self.data.extend([self.row])
        self.refresh()

    def popup(self, pos):
        if (len(self.data) - 1) < self.selectionModel().selection().indexes()[0].row():
            return False
        menu = QMenu()
        quitAction = menu.addAction("Supprimer cette ligne")
        action = menu.exec_(self.mapToGlobal(pos))
        if action == quitAction:
            try:
                self.data.pop(self.selectionModel()
                                  .selection().indexes()[0].row())
            except IndexError:
                pass
            self.refresh()
            self.changed_value(self)

    def extend_rows(self):
        nb_rows = self.rowCount()
        self.setRowCount(nb_rows + 1)
        self.setSpan(nb_rows, 0, 1, 2)
        self.setItem(nb_rows, 3, TotalsWidget(u"Montant"))
        self.setItem(nb_rows, 6, TotalsWidget(formatted_number(u"%d" % 0)))

        nb_rows += 1
        self.setRowCount(nb_rows + 1)
        self.setSpan(nb_rows, 0, 1, 6)
        bicon = QIcon.fromTheme('', QIcon(u"{}".format(Config.img_cmedia)))
        self.button = QPushButton(bicon, u"Enregistrer")
        self.button.released.connect(self.parent.save_b)
        self.setCellWidget(nb_rows, 6, self.button)

        # pw = (self.parentWidget().width()) / 5
        # self.setColumnWidth(0, pw)
        # self.setColumnWidth(1, pw * 2)
        # self.setColumnWidth(2, pw)
        # self.setColumnWidth(3, pw)

    def _item_for_data(self, row, column, data, context=None):
        if column == 1 or column == 2 or column == 3:
            self.line_edit = IntLineEdit(u"%s" % data)
            self.line_edit.textChanged.connect(self.changed_value)
            return self.line_edit
        return super(BuyTableWidget, self)._item_for_data(row, column, data,
                                                          context)

    def _update_data(self, row_num, new_data):
        self.data[row_num] = (self.data[row_num][0], new_data[0], new_data[1],
                              new_data[2], new_data[3], new_data[4],
                              new_data[5])

    def get_table_items(self):
        """ Recupère les elements du tableau """

        list_invoice = []
        for i in range(self.rowCount() - 2):
            liste_item = []
            row_data = self.data[i]
            try:
                liste_item.append(str(row_data[0]))
                liste_item.append(int(row_data[1]))
                liste_item.append(int(row_data[2]))
                liste_item.append(int(row_data[3]))
                list_invoice.append(liste_item)
            except AttributeError:
                raise
                liste_item.append("")

        return list_invoice

    def changed_value(self, refresh=False):
        """ Calcule les Resultat """
        b_f_tt = 0
        v_amount_tt = 0
        for row_num in xrange(0, self.data.__len__()):

            qtsaisi = is_int(self.cellWidget(row_num, 1).text()) or 1
            cost_buying = is_int(self.cellWidget(row_num, 2).text())
            selling_price = is_int(self.cellWidget(row_num, 3).text())

            self.isvalid = True
            # if not selling_price:
            #     return
            if (selling_price and check_is_empty(self.cellWidget(row_num, 1))):
                self.isvalid = False
            if (selling_price and check_is_empty(self.cellWidget(row_num, 2))):
                self.isvalid = False
            if (check_is_empty(self.cellWidget(row_num, 3))):
                self.isvalid = False

            r_amount = qtsaisi * cost_buying
            v_amount = qtsaisi * selling_price
            b_f = v_amount - r_amount
            b_f_u = b_f / qtsaisi

            b_f_tt += b_f
            v_amount_tt += v_amount
            # montt.setTextAlignment(Qt.AlignRight)
            self.setItem(row_num, 4, TotalsWidget(formatted_number(v_amount)))
            self.setItem(row_num, 5, TotalsWidget(formatted_number(b_f_u)))
            self.setItem(row_num, 6, TotalsWidget(formatted_number(b_f)))
            # Mise à jour
            self._update_data(
                row_num, [qtsaisi, cost_buying, selling_price, v_amount, b_f_u, b_f])
        row_num += 1
        self.setItem(row_num, 4, TotalsWidget(formatted_number(v_amount_tt)))
        self.setItem(row_num, 6, TotalsWidget(formatted_number(b_f_tt)))
