#!/usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: Fad
from __future__ import (
    unicode_literals, absolute_import, division, print_function)

import json

from PyQt4 import QtGui, QtCore

from Common.ui.common import (FWidget, FPageTitle, Button)
from Common.ui.util import raise_success


class OrderRemoveWidget(QtGui.QDialog, FWidget):

    def __init__(self, parent, *args, **kwargs):
        QtGui.QDialog.__init__(self, parent, *args, **kwargs)
        super(OrderRemoveWidget, self).__init__(parent=parent, *args, **kwargs)

        self.setWindowTitle(u"Confirmation de le suppression")
        self.title = FPageTitle(u"Voulez vous vraiment supprimer"
                                u" de la sauvegarde?")

        self.title.setAlignment(QtCore.Qt.AlignHCenter)
        title_hbox = QtGui.QHBoxLayout()
        title_hbox.addWidget(self.title)
        report_hbox = QtGui.QGridLayout()

        # delete and cancel hbox
        Button_hbox = QtGui.QHBoxLayout()

        # Delete Button widget.
        delete_but = Button(u"Supprimer")
        Button_hbox.addWidget(delete_but)
        delete_but.clicked.connect(self.delete)
        # Cancel Button widget.
        cancel_but = Button(u"Annuler")
        Button_hbox.addWidget(cancel_but)
        cancel_but.clicked.connect(self.cancel)

        # Create the QVBoxLayout contenaire.
        vbox = QtGui.QVBoxLayout()
        vbox.addLayout(title_hbox)
        vbox.addLayout(report_hbox)
        vbox.addLayout(Button_hbox)
        self.setLayout(vbox)

    def cancel(self):
        self.close()

    def delete(self):
        from order_view import OrderViewWidget
        self.cancel()

        data = []
        # fichier.txt est un fichier déjà créé par toi-même
        obj_file = open('tmp_order.txt', 'w')
        # ecriture des données dans fichier.txt
        obj_file.write(json.dumps(data))
        obj_file.close()  # fermeture du fichier quand plus aucune utilité
        raise_success(
            u"", u"La sauvegarde de la commande à été supprimé avec succès")
        self.change_main_context(OrderViewWidget)
