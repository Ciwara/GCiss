#!usr/bin/env python
# -*- encoding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
# maintainer: Fad
from PyQt4.QtCore import QDate, Qt
from PyQt4.QtGui import (
    QVBoxLayout, QComboBox, QIcon, QGridLayout, QSplitter, QPushButton, QMenu)

from Common.ui.util import (
    check_is_empty, is_valide_codition_field, is_int, field_error,
    date_to_datetime, formatted_number)
from Common.ui.table import FTableWidget, TotalsWidget
from Common.ui.common import (
    FWidget, IntLineEdit, LineEdit, FLabel, FormatDate, BttSmall,
    ExtendedComboBox)
from peewee import fn

from GCommon.ui._product_detail import InfoTableWidget
# from ui.invoice_show import ShowInvoiceViewWidget
from ui.sale_product import SaleProducteWidget
from configuration import Config
from models import (Product, Invoice, Owner, Report, ProviderOrClient, Refund)


class InvoiceViewWidget(FWidget):

    def __init__(self, product="", parent=0, *args, **kwargs):
        super(InvoiceViewWidget, self).__init__(parent=parent, *args, **kwargs)
        self.parentWidget().setWindowTitle(
            Config.APP_NAME + "      Ventes")
        self.parent = parent

        vbox = QVBoxLayout()
        # hbox = QHBoxLayout(self)
        editbox = QGridLayout()
        try:
            next_number = int(
                Invoice.select().order_by(Invoice.number.desc()).get(
                ).number) + 1
        except:
            next_number = 1
        self.num_invoice = IntLineEdit(str(next_number))
        self.num_invoice.setToolTip("Le numéro")
        self.num_invoice.setMaximumSize(
            40, self.num_invoice.maximumSize().height())
        self.invoice_date = FormatDate(QDate.currentDate())
        # self.name_client_field = LineEdit()

        self.string_list = [""] + ["{},{}".format(clt.name, clt.phone)
                                   for clt in ProviderOrClient.select().where(
            ProviderOrClient.type_ == ProviderOrClient.CLT).order_by(
            ProviderOrClient.name.desc())]

        # self.name_client_field_new = ""
        self.name_client_field = ExtendedComboBox()
        self.name_client_field.addItems(self.string_list)

        self.name_client_field.setMinimumSize(300, 30)
        # self.name_client_field.setMaximumSize(
        #     200, self.name_client_field.maximumSize().height())
        self.name_client_field.setToolTip("Nom, numero du client")

        self.add_clt_btt = BttSmall("+")
        self.add_clt_btt.clicked.connect(self.add_clt)
        self.add_clt_btt.setFixedWidth(300)

        # Combobox widget for add store
        self.liste_type_invoice = [Invoice.TYPE_FACT, Invoice.TYPE_BON,
                                   Invoice.TYPE_PROF]

        self.box_type_inv = QComboBox()
        for index in range(0, len(self.liste_type_invoice)):
            op = self.liste_type_invoice[index]
            sentence = "%(name)s" % {'name': op}
            self.box_type_inv.addItem(sentence, op)

        self.search_field = LineEdit()
        self.search_field.setPlaceholderText("Rechercher un article")
        self.search_field.textChanged.connect(self.finder)
        # self.search_field.setFixedWidth(250)
        self.search_field.setMaximumHeight(40)

        self.table_invoice = InvoiceTableWidget(parent=self)
        self.table_resultat = ResultatTableWidget(parent=self)
        self.table_info = InfoTableWidget(parent=self)

        self.name_client_field.currentIndexChanged.connect(
            self.table_invoice.changed_value)
        self.table_resultat.refresh_("")
        editbox.addWidget(self.box_type_inv, 0, 2)
        editbox.addWidget(self.num_invoice, 0, 3)
        editbox.addWidget(FLabel("Doit :"), 0, 5)
        editbox.addWidget(self.name_client_field, 0, 6)
        editbox.addWidget(self.invoice_date, 0, 7)
        editbox.setColumnStretch(0, 1)
        # editbox.setColumnStretch(4, 2)
        splitter = QSplitter(Qt.Horizontal)

        splitter_left = QSplitter(Qt.Vertical)
        splitter_left.addWidget(self.search_field)
        splitter_left.addWidget(self.table_resultat)
        # splitter_down.resize(15, 20)
        splitter_down = QSplitter(Qt.Vertical)
        splitter_down.addWidget(self.table_info)
        splitter_rigth = QSplitter(Qt.Vertical)

        # splitter_rigth.setLayout(editbox)
        splitter_rigth.addWidget(self.table_invoice)
        splitter_rigth.resize(800, 900)

        splitter_left.addWidget(splitter_down)
        splitter.addWidget(splitter_left)
        splitter.addWidget(splitter_rigth)

        vbox.addLayout(editbox)
        vbox.addWidget(splitter)
        self.setLayout(vbox)

    def add_clt(self):
        from GCommon.ui.provider_client_edit_add import EditOrAddClientOrProviderDialog
        self.open_dialog(EditOrAddClientOrProviderDialog, modal=True,
                         prov_clt=None, table_p=self)

    def finder(self):
        search_term = self.search_field.text()
        value = str(search_term)
        self.table_resultat.refresh_(value)

    def refresh_(self):
        pass

    def save_b(self):
        ''' add operation '''

        invoice_date = str(self.invoice_date.text())
        num_invoice = int(self.num_invoice.text())
        invoice_type = self.liste_type_invoice[
            self.box_type_inv.currentIndex()]
        lis_error = []
        invoice = Invoice()
        try:
            self.owner = Owner.get(Owner.islog == True)
        except:
            lis_error.append("Aucun utilisateur est connecté <br/>")
        paid_amount = int(self.table_invoice.paid_amount_field.text())
        try:
            self.name_client, self.phone = self.name_client_field.lineEdit(
            ).text().split(",")
            clt = ProviderOrClient.get_or_create(
                self.name_client, int(self.phone.replace(" ", "")),
                ProviderOrClient.CLT)
        except ValueError:
            field_error(self.name_client_field,
                        "Nom, numéro de téléphone du client")

        invoice.number = num_invoice
        invoice.owner = self.owner
        invoice.client = clt
        invoice.location = "Bamako"
        invoice.type_ = invoice_type
        invoice.subject = ""
        invoice.paid_amount = paid_amount
        invoice.tax = False
        try:
            invoice.save()
            if int(paid_amount) != 0 or invoice_type == Invoice.TYPE_BON:
                Refund(
                    type_=Refund.DT, owner=self.owner, amount=paid_amount,
                    date=date_to_datetime(invoice_date), provider_client=clt,
                    invoice=Invoice.get(number=num_invoice)).save()
        except Exception as e:
            invoice.deletes_data()
            lis_error.append(
                "Erreur sur l'enregistrement d'entête de facture<br/>")
            return False
        # Save invoiceitems
        invoice = Invoice.get(Invoice.number == num_invoice)
        for name, qty, price in self.table_invoice.get_table_items():
            rep = Report()
            product = Product.get(Product.name == name)
            rep.store = 1
            rep.product = product
            rep.invoice = invoice
            rep.type_ = Report.S
            rep.cost_buying = int(product.last_report.cost_buying)
            rep.date = date_to_datetime(invoice_date)
            rep.qty = int(qty)
            rep.selling_price = int(price)
            try:
                rep.save()
            except Exception as e:
                lis_error.append(e)
        if lis_error != []:
            invoice.delete_instance()
            self.parent.Notify(lis_error, "error")
            return False
        else:
            # self.table_invoice._reset()
            # try:
            #     self.parent.open_dialog(
            #         ShowInvoiceViewWidget, modal=True, opacity=100,
            #         table_p=self, invoice_num=invoice.number)
            # except Exception as e:
            #     print(e)

            self.change_main_context(SaleProducteWidget)
            self.parent.Notify("Facture Enregistrée avec succès", "success")


class ResultatTableWidget(FTableWidget):

    """docstring for ResultatTableWidget"""

    def __init__(self, parent, *args, **kwargs):
        FTableWidget.__init__(self, parent=parent, *args, **kwargs)

        self.parent = parent

        self.hheaders = ["Produits", "Ajouter"]
        self.stretch_columns = [0]
        self.align_map = {0: 'l', 1: 'r'}
        # self.display_fixed = True
        self.refresh_()

    def refresh_(self, value=None):

        self._reset()
        self.set_data_for(value)
        self.refresh()

    def set_data_for(self, value=None):
        products = [(Product.get(id=rpt.product_id).name) for rpt in
                    Report.select(fn.Distinct(Report.product))]
        if value:
            products = [(prod.name) for prod in Product.select(
            ).where(Product.name.contains(value))
                .where(Product.name << products).order_by(Product.name.desc())]
        self.data = [(prd, "") for prd in products]

    def _item_for_data(self, row, column, data, context=None):
        if column == 1:
            return TotalsWidget(QIcon("{img_media}{img}".format(
                img_media=Config.img_cmedia, img="go-next.png")), "")

        return super(ResultatTableWidget, self)._item_for_data(row, column,
                                                               data, context)

    def click_item(self, row, column, *args):
        self.choix = Product.filter(name=self.data[row][0]).get()
        self.parent.table_info.refresh_(self.choix.id)
        if column == 1:
            self.parent.table_invoice.refresh_(self.choix)


class InvoiceTableWidget(FTableWidget):

    def __init__(self, parent, *args, **kwargs):
        FTableWidget.__init__(self, parent=parent, *args, **kwargs)

        self.parent = parent
        self.pparent = parent.parent
        self.hheaders = ["Modeles", "Quantité", "Prix Unitaire", "Montant"]

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.popup)

        self.stretch_columns = [0, 2]
        self.align_map = {3: 'r'}
        self.display_vheaders = False
        # self.display_fixed = True
        self.refresh_()
        self.isvalid = False

    def refresh_(self, choix=None):
        if choix:
            self.row = ["%s" % choix.name, "", ""]
            if not [row for row in self.data if self.row[0] in row]:
                self.set_data_for()
                self.refresh()

    def set_data_for(self):

        self._reset()
        self.data.extend([self.row])
        self.refresh()

    def popup(self, pos):
        row = self.selectionModel().selection().indexes()[0].row()
        if (len(self.data) - 1) < row:
            return False
        menu = QMenu()
        quit_action = menu.addAction("Supprimer cette ligne")
        action = menu.exec_(self.mapToGlobal(pos))
        if action == quit_action:
            try:
                self.data.pop(row)
            except IndexError:
                pass
            self.refresh()

    def extend_rows(self):
        nb_rows = self.rowCount()
        self.setRowCount(nb_rows + 3)
        self.setItem(nb_rows, 2, TotalsWidget("Montant"))
        monttc = TotalsWidget(formatted_number("%d" % 0))
        self.setItem(nb_rows, 3, monttc)
        nb_rows += 1
        bicon = QIcon.fromTheme(
            '', QIcon("{}save.png".format(Config.img_media)))
        self.button = QPushButton(bicon, "Enregistrer")
        self.button.released.connect(self.parent.save_b)
        self.button.setEnabled(False)
        self.setItem(nb_rows, 2, TotalsWidget("Reste à payer"))
        self.paid_amount_field = IntLineEdit()
        self.setCellWidget(nb_rows, 3, self.paid_amount_field)
        self.setCellWidget(nb_rows + 1, 3, self.button)
        self.setSpan(nb_rows - 1, 0, 3, 2)

        pw = self.parent.parent.page_width() / 5
        self.setColumnWidth(0, pw * 2)
        self.setColumnWidth(1, pw)
        self.setColumnWidth(2, pw)

    def _update_data(self, row_num, new_data):
        self.data[row_num] = (self.data[row_num][0], new_data[0], new_data[1],
                              new_data[2])

    def _item_for_data(self, row, column, data, context=None):
        if column == 1 or column == 2:
            self.line_edit = IntLineEdit("%s" % data)
            self.line_edit.textChanged.connect(self.changed_value)
            self.line_edit.setAlignment(Qt.AlignRight)
            return self.line_edit
        return super(InvoiceTableWidget, self)._item_for_data(row, column,
                                                              data, context)

    def get_table_items(self):
        """ Recupère les elements du tableau """

        list_invoice = []
        for i in range(self.rowCount() - 3):
            liste_item = []
            row_data = self.data[i]
            try:
                liste_item.append(str(row_data[0]))
                liste_item.append(int(row_data[1]))
                liste_item.append(int(row_data[2]))
                list_invoice.append(liste_item)
            except AttributeError:
                raise
                liste_item.append("")

        return list_invoice

    def changed_value(self, refresh=False):
        """ Calcule les Resultat """
        self.mtt_ht = 0
        self.button.setEnabled(False)
        for row_num in range(0, self.data.__len__()):
            product = Product.get(
                Product.name == str(self.item(row_num, 0).text()))
            last_report = product.last_report
            last_price = product.last_price()
            qtremaining = last_report.remaining
            # selling_price = last_price
            # invoice_date = str(self.parent.invoice_date.text())
            qtsaisi = is_int(self.cellWidget(row_num, 1).text())
            pusaisi = is_int(self.cellWidget(row_num, 2).text())

            if check_is_empty(self.parent.num_invoice):
                return
            if check_is_empty(self.parent.name_client_field.lineEdit()):
                return
            # if is_valide_codition_field(self.parent.invoice_date,
            #                "Le {} est Inférieure à la date de la dernière rapport (<b>{}</b>)".format(date_to_datetime(invoice_date), last_report.date), (last_report.date > date_to_datetime(invoice_date))):
            #     return

            if (pusaisi and check_is_empty(self.cellWidget(row_num, 1))):
                return
            if (pusaisi and check_is_empty(self.cellWidget(row_num, 2))):
                return
            if is_valide_codition_field(
                self.cellWidget(row_num, 1),
                "<b>{}</b> est supérieur à la quantité restante (<b>{}</b>)".format(
                    qtsaisi, qtremaining), qtremaining < qtsaisi):
                return
            # if is_valide_codition_field(
            #     self.cellWidget(row_num, 2),
            #     "<b>{}</b> est inférieure au prix minimum de vente<b> {} CFA</b>".format(
            #         pusaisi, selling_price), pusaisi < selling_price):
            #     print("")

            montant = (qtsaisi * pusaisi)
            self.mtt_ht += montant
            self.setItem(row_num, 3, TotalsWidget(formatted_number(montant)))

            self._update_data(row_num, [qtsaisi, pusaisi, self.mtt_ht])

        self.setItem(
            row_num + 1, 3, TotalsWidget(formatted_number(self.mtt_ht)))

        typ = self.parent.liste_type_invoice[
            self.parent.box_type_inv.currentIndex()]
        self.paid_amount_field.setText(
            str(self.mtt_ht) if typ == Invoice.TYPE_BON else "0")
        self.button.setEnabled(True)
