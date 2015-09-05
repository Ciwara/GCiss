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
from models import Refund


try:
    unicode
except:
    unicode = str


class RefundEditAddDialog(QDialog, FWidget):

    def __init__(self, table_p, parent, type_=None, refund=None, *args, **kwargs):
        QDialog.__init__(self, parent, *args, **kwargs)

        self.type_ = type_
        self.refund = refund
        self.parent = parent
        self.table_p = table_p

        amount = ""
        if self.refund:
            self.new = False
            print("refund", self.refund)
            self.type_ = refund.type_
            self.refund_date_field = FormatDate(self.refund.date)
            self.refund_date_field.setEnabled(False)
            self.title = u"Modification de {} {}".format(self.refund.type_,
                                                         self.refund.libelle)
            self.succes_msg = u"{} a été bien mise à jour".format(
                self.refund.type_)
            self.amount = refund.amount
        else:
            self.new = True
            self.refund_date_field = FormatDate(QDate.currentDate())
            self.succes_msg = u"Client a été bien enregistré"
            self.title = u"Création d'un nouvel client"
            self.refund = Refund()
        self.setWindowTitle(self.title)

        self.amount_field = IntLineEdit(unicode(amount))
        self.libelle_field = QTextEdit(self.refund.libelle)

        vbox = QVBoxLayout()

        formbox = QFormLayout()
        formbox.addRow(FormLabel(u"date: *"), self.refund_date_field)
        formbox.addRow(FormLabel(u"Libelle :"), self.libelle_field)
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
        refund_date = unicode(self.refund_date_field.text())
        # if check_is_empty(self.libelle_field):
        #     return
        if check_is_empty(self.amount_field):
            return

        refund = self.refund
        refund.type_ = self.type_
        refund.libelle = libelle
        if self.new:
            print(date_to_datetime(refund_date))
            refund.date = date_to_datetime(refund_date)
        if self.type_ == Refund.CREDIT:
            refund.credit = amount
        elif self.type_ == Refund.DEBIT:
            refund.debit = amount
        try:
            refund.save()
            self.close()
            self.parent.Notify(u"le {type} {lib} à été enregistré avec succès".format(
                type=self.type_, lib=libelle), "success")
            self.table_p.refresh_()
        except Exception as e:
            self.parent.Notify(e, "error")
