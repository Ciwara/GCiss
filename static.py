#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
# Maintainer: Fad

import os

from Common.cstatic import CConstants


class Constants(CConstants):

    def __init__(self):
        CConstants.__init__(self)

    # des_image_record = "static/img_prod"

    ROOT_DIR = os.path.dirname(os.path.abspath('__file__'))
    ARMOIRE = "img_prod"
    des_image_record = os.path.join(ROOT_DIR, ARMOIRE)
    PEEWEE_V = 224
    credit = 17
    tolerance = 50
    nb_warning = 5
    # type_period = W
    # type_period = M

    DOC_SUPPORT = "*.gif *.png *.jpg *.doc *.docx *.pdf *.jpeg"
    # -------- Application -----------#

    NAME_MAIN = "bmain.py"
    M_GESTION = u"Gestion de Stock"
    B_GESTION = "Gestion de Boutique"
    P_GESTION = u"Gestion d'achat"
    pdf_source = "pdf_source.pdf"
    # APP_NAME = P_GESTION
    # APP_NAME = B_GESTION
    APP_NAME = M_GESTION

    APP_VERSION = u"6.0.0"
    APP_DATE = u"02/2013"
    img_media = os.path.join(ROOT_DIR, "static", "images/")
    APP_LOGO = os.path.join(img_media, "logo.png")
    APP_LOGO_ICO = os.path.join(img_media, "logo.ico")

    INV_TEMPLATE_XLSX = os.path.join(ROOT_DIR, "templates", "t_invoice.xls")
    INV_TEMPLATE_PDF = os.path.join(ROOT_DIR, "templates", "t_invoice.pdf")
