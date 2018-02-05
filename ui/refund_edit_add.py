#!/usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: Fad


from PyQt4.QtCore import QDate
from PyQt4.QtGui import (QVBoxLayout, QDialog, QFormLayout)

# from configuration import Config

from Common.ui.util import (check_is_empty, is_valide_codition_field,
                            date_to_datetime, formatted_number)
from Common.ui.common import (
    FWidget, Button_save, FormLabel, IntLineEdit, FormatDate)

from models import Refund


class RefundEditAddDialog(QDialog, FWidget):

    def __init__(self, table_p, parent, provid_clt=None, type_=None, refund=None, *args, **kwargs):
        QDialog.__init__(self, parent, *args, **kwargs)

        self.type_ = type_
        self.refund = refund
        self.parent = parent
        self.table_p = table_p
        self.provid_clt = provid_clt
        self.new = True
        if self.refund:
            self.new = False
            self.last_r = self.refund
            self.type_ = refund.type_
            self.refund_date_field = FormatDate(self.refund.date)
            self.refund_date_field.setEnabled(False)
            self.title = u"Modification de {} {}".format(
                self.refund.type_, self.refund.invoice.client)
            self.succes_msg = u"{} a été bien mise à jour".format(
                self.refund.type_)
            self.amount = refund.amount
            self.provid_clt = refund.provider_client
        else:
            self.refund_date_field = FormatDate(QDate.currentDate())
            self.succes_msg = u"Client a été bien enregistré"
            self.title = u"Création d'un nouvel client"
            self.amount = ""
            self.refund = Refund()
            self.last_r = Refund.select().where(
                Refund.provider_client == provid_clt).order_by(
                Refund.date.desc()).get()

        self.setWindowTitle(self.title)
        self.amount_field = IntLineEdit(str(self.amount))

        vbox = QVBoxLayout()
        self.last_remaining = self.last_r.refund_remaing()
        # try:
        #     self.last_r.refund_remaing()
        # self.remaining = self.last_r.remaining
        # except Exception as e:
        #     self
        #     print("last_r except ", e)
        #     self.last_r = None
        # self.close()

        formbox = QFormLayout()
        formbox.addRow(FormLabel("Client :"),
                       FormLabel(self.provid_clt.name))
        formbox.addRow(FormLabel("Dette restante :"),
                       FormLabel(str(formatted_number(self.last_remaining))))
        formbox.addRow(FormLabel(u"Date : *"), self.refund_date_field)
        formbox.addRow(FormLabel(u"Montant : *"), self.amount_field)

        butt = Button_save(u"Enregistrer")
        butt.clicked.connect(self.save_edit)
        formbox.addRow("", butt)
        # formbox.addRow("", "Le client {} n'est pas endetté")

        vbox.addLayout(formbox)
        self.setLayout(vbox)

    def save_edit(self):
        ''' add operation '''

        if check_is_empty(self.amount_field):
            return

        amount = int(self.amount_field.text())
        refund_date = str(self.refund_date_field.text())

        # self.remaining = self.last_r.remaining
        if is_valide_codition_field(
                self.amount_field, "Ce montant ne peut être supperieur au dettes restante {}.".format(
                self.last_remaining), amount > self.last_remaining):
            return
        refund = self.refund
        refund.type_ = self.type_
        refund.invoice = self.last_r.invoice
        refund.amount = amount
        if self.new:
            refund.provider_client = self.provid_clt
            refund.date = date_to_datetime(refund_date)
        try:
            refund.save()
            self.close()
            self.parent.Notify(u"le {type} {lib} à été enregistré avec succès".format(
                type=self.type_, lib=amount), "success")
            self.table_p.refresh_(provid_clt_id=self.provid_clt.id)
        except Exception as e:
            self.parent.Notify(e, "error")
