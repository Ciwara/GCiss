#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
# maintainer: Fad
from __future__ import (unicode_literals, absolute_import, division,
                        print_function)
import os
# from static import Constants
from Common.cstatic import CConstants
# import peewee


class Config(CConstants):

    """ docstring for Config
                            """

    DATEFORMAT = u'%d/%m/%Y'

    ROOT_DIR = os.path.dirname(os.path.abspath('__file__'))

    def __init__(self):
        CConstants.__init__(self)

    # ------------------------- Organisation --------------------------#

    # from Common.models import Organization, Version

    # try:
    #     DB_VERS = Version().get(Version.number == 1)
    # except Exception as e:
    #     print(e)
    #     DB_VERS = 1
    # try:
    #     sttg = Organization().get(Organization.id == 1)
    #     # LOGIN = sttg.login
    #     NAME_ORGA = sttg.name_orga
    #     TEL_ORGA = sttg.phone
    #     ADRESS_ORGA = sttg.adress_org
    #     BP = sttg.bp
    #     EMAIL_ORGA = sttg.email_org
    #     # DEBUG = True
    # except peewee.OperationalError:
    #     pass
    DEBUG = True
    # ORG_LOGO = "org_logo.png"
    ORG_LOGO = None

    APP_NAME = "GCISS"
    APP_VERSION = 1
    APP_DATE = u"02/2016"

    SERV = None

    img_media = os.path.join(os.path.join(ROOT_DIR, "static"), "images/")
    APP_LOGO = os.path.join(img_media, "logo.png")
    APP_LOGO_ICO = os.path.join(img_media, "logo.ico")

    NAME_MAIN = "main.py"
    OUT = os.path.join(ROOT_DIR, 'Out')
    INV_TEMPLATE_PDF = os.path.join(
        os.path.join(ROOT_DIR, "template"), "t_invoice.pdf")
