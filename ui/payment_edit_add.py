#!/usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: Fad
from __future__ import (
    unicode_literals, absolute_import, division, print_function)

import os

from PyQt4.QtCore import Qt, QDate
from PyQt4.QtGui import (QIcon, QVBoxLayout, QFileDialog, QDialog, QTextEdit,
                         QIntValidator, QFormLayout, QPushButton, QCompleter)

from configuration import Config

from Common.ui.util import check_is_empty, field_error, date_to_datetime
from Common.ui.common import (FWidget, FPageTitle, Button_save, FormLabel,
                              FLabel, LineEdit, IntLineEdit, Warning_btt,
                              FormatDate)
from Common import peewee
from models import Payment


try:
    unicode
except:
    unicode = str


class EditOrAddPaymentrDialog(QDialog, FWidget):

    def __init__(self, table_p, parent, type_=None, payment=None, *args, **kwargs):
        FWidget.__init__(self, parent, *args, **kwargs)

        self.table_p = table_p
        self.type_ = type_
        print("EEEEEEEEEEE", self.type_)
        self.payment = payment
        self.parent = parent
        if self.payment:
            self.new = False
            self.title = u"Modification de {} {}".format(self.payment.type_,
                                                         self.payment.libelle)
            self.succes_msg = u"{} a été bien mise à jour".format(
                self.payment.type_)

            if self.type_ == Payment.CREDIT:
                amount = payment.credit
            elif self.type_ == Payment.DEBIT:
                amount = payment.debit
        else:
            self.new = True
            self.succes_msg = u"Client a été bien enregistré"
            self.title = u"Création d'un nouvel client"
            self.payment = Payment()
            amount = ""
        self.setWindowTitle(self.title)

        vbox = QVBoxLayout()

        self.payment_date_field = FormatDate(QDate.currentDate())
        self.amount_field = IntLineEdit(amount)
        self.libelle_field = QTextEdit(self.payment.libelle)

        formbox = QFormLayout()
        formbox.addRow(FormLabel(u"date: *"), self.payment_date_field)
        formbox.addRow(FormLabel(u"Libelle : *"), self.libelle_field)
        formbox.addRow(FormLabel(u"Montant: *"), self.amount_field)

        butt = Button_save(u"Enregistrer")
        butt.clicked.connect(self.save_edit)
        formbox.addRow("", butt)

        vbox.addLayout(formbox)
        self.setLayout(vbox)

    def save_edit(self):
        ''' add operation '''
        libelle = unicode(self.libelle_field.toPlainText())
        amount = unicode(self.amount_field.text())
        payment_date = unicode(self.payment_date_field.text())
        # if check_is_empty(self.libelle_field):
        #     return
        if check_is_empty(self.amount_field):
            return

        payment = self.payment
        payment.type_ = self.type_
        payment.date = date_to_datetime(payment_date)
        payment.libelle = libelle
        if self.type_ == Payment.CREDIT:
            payment.credit = amount
        elif self.type_ == Payment.DEBIT:
            payment.debit = amount
        try:
            payment.save()
            self.close()
            self.parent.Notify(u"le {type} {lib} à été enregistré avec succès".format(
                type=payment.type_, lib=payment.libelle), "success")
            self.table_p.refresh()
        except Exception as e:
            self.parent.Notify(e, "error")
