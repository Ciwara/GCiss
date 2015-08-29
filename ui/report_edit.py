#!/usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: Fad
from __future__ import (
    unicode_literals, absolute_import, division, print_function)

from PyQt4.QtGui import (QDialog, QVBoxLayout, QIntValidator,
                         QComboBox, QGridLayout, )
from PyQt4.QtCore import QDate, QVariant

from Common.ui.common import (FWidget, FBoxTitle, FPageTitle, Button,
                              FormatDate, FormatDate, QGridLayout
from Common.ui.util import raise_success
from models import Report, Product
from data_helper import date_to_datetime


class EditReportViewWidget(QDialog, FWidget):

    def __init__(self, report, parent, *args, **kwargs):
        QDialog.__init__(self, parent, *args, **kwargs)
        self.setWindowTitle(u"Modification")
        self.title=FPageTitle(u"Vous le vous modifié ?")

        self.report=report
        vbox=QVBoxLayout()

        self.qty=LineEdit(str(self.report.qty))
        self.qty.setValidator(QIntValidator())

        self.date_=FormatDate(QDate(self.report.date_rep))

        self.time=FormatDate(QTime.currentTime())
        formbox=QVBoxLayout()
        editbox=QGridLayout()
        formbox.addWidget(FBoxTitle(u"Modification"))
        # Combobox widget

        i=0
        self.liste_type=Report.TYPES
        self.box_type=QComboBox()
        for index in xrange(0, len(self.liste_type)):
            ty=self.liste_type[index]
            if ty == self.report.type_:
                i=index
            sentence=u"%(type_)s" % {'type_': ty}
            self.box_type.addItem(sentence, QVariant(ty))
            self.box_prod.setCurrentIndex(i)
        # Combobox widget
        # self.liste_store = Store.order_by(desc(Store.id)).all()
        # self.box_mag = QComboBox()
        # for index in xrange(0, len(self.liste_store)):
        #     report = self.liste_store[index]
        #     sentence = _(u"%(name)s") % {'name': report.name}
        #     self.box_mag.addItem(sentence, QVariant(report.id))
        # Combobox widget

        self.liste_product=Product.all()
        self.box_prod=QComboBox()

        for index in xrange(0, len(self.liste_product)):
            report=self.liste_product[index]
            if report == self.report.product.name:
                i=index
            sentence=u"%(name)s" % {'name': report.name}
            self.box_prod.addItem(sentence, QVariant(report.id))
            self.box_prod.setCurrentIndex(i)

        editbox.addWidget(FLabel(u"Type"), 0, 0)
        editbox.addWidget(self.box_type, 1, 0)
        # editbox.addWidget(FLabel((_(u"Store"))), 0, 1)
        # editbox.addWidget(self.box_mag, 1, 1)
        editbox.addWidget(FLabel(u"Produit"), 0, 2)
        editbox.addWidget(self.box_prod, 1, 2)
        editbox.addWidget(FLabel(u"Quantité"), 0, 3)
        editbox.addWidget(self.qty, 1, 3)
        editbox.addWidget(FLabel((u"Date")), 0, 4)
        editbox.addWidget(self.date_, 1, 4)
        butt=Button(u"Enregistrer")
        butt.clicked.connect(self.report_edit)
        cancel_but=Button(u"Annuler")
        cancel_but.clicked.connect(self.cancel)
        editbox.addWidget(butt, 2, 3)
        editbox.addWidget(cancel_but, 2, 4)
        formbox.addLayout(editbox)
        vbox.addLayout(formbox)
        self.setLayout(vbox)

    def cancel(self):
        self.close()

    def report_edit(self):

        type_=self.box_type.currentIndex()
        product=self.liste_product[self.box_prod.currentIndex()]
        qty=unicode(self.nbr_carton.text())
        date_=self.date_.text()
        datetime_=date_to_datetime(date_)

        report=self.report
        report.type_=type_
        report.product=product
        report.qty=qty
        report.remaining=0
        report.date=datetime_
        report.save()
        self.cancel()
        raise_success(u"Confirmation", u"Votre rapport a été modifié")
