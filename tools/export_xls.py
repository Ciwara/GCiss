#!usr/bin/env python
# -*- coding= UTF-8 -*-
# maintainer: Fadiga

import xlwt

from datetime import date

from Common.ui.util import openFile

from configuration import Config
from models import Report, Product

font_title = xlwt.Font()
font_title.name = 'Times New Roman'
font_title.bold = True
font_title.height = 19 * 0x14
font_title.underline = xlwt.Font.UNDERLINE_DOUBLE

borders = xlwt.Borders()
borders.left = 1
borders.right = 1
borders.top = 1
borders.bottom = 1

al_center = xlwt.Alignment()
al_center.horz = xlwt.Alignment.HORZ_CENTER
al_center.vert = xlwt.Alignment.VERT_CENTER

al_right = xlwt.Alignment()
al_right.horz = xlwt.Alignment.HORZ_RIGHT

color = xlwt.Pattern()
color.pattern = xlwt.Pattern.SOLID_PATTERN
color.pattern_fore_colour = 22

pat2 = xlwt.Pattern()
pat2.pattern = xlwt.Pattern.SOLID_PATTERN
pat2.pattern_fore_colour = 0x01F

# styles
style_title = xlwt.easyxf('font: name Cooper Black, height 250, bold on,'
                          'color blue')
style_title.alignment = al_center

style_ = xlwt.easyxf('font: name Centaur, height 250, bold on, color black')
style_.alignment = al_center

style_t_table = xlwt.easyxf('font: name Times New Roman, height 250, bold on')
style_t_table.pattern = color
style_t_table.alignment = al_center
style_t_table.borders = borders

style2 = xlwt.easyxf('font: name Times New Roman, height 250, bold on')
style2.borders = borders

style1 = xlwt.easyxf('font: name Times New Roman, height 250, bold on')
style1.pattern = pat2
style1.borders = borders

style = xlwt.easyxf('font: name Times New Roman, height 250, bold off')
style.borders = borders

style_mag = xlwt.easyxf('font: name Times New Roman, height 250, bold on')
style_mag.alignment = al_center
style_mag.borders = borders
style_mag.pattern = color

int_style = xlwt.easyxf('font: name Times New Roman, height 250, bold off')
int_style.borders = borders
int_style.alignment = al_right

style_code = xlwt.easyxf(
    'font: name Times New Roman, height 250, bold off, color blue')
style_code.borders = borders


def write_report_xls(file_name, data):
    ''' Export data '''
    # Principe
    # write((nbre ligne - 1), nbre colonne, "contenu", style(optionnel).
    # write_merge((nbre ligne - 1), (nbre ligne - 1) + nbre de ligne
    # à merger, (nbre de colonne - 1), (nbre de colonne - 1) + nbre
    # de colonne à merger, u"contenu", style(optionnel)).
    book = xlwt.Workbook(encoding='ascii')
    sheet = book.add_sheet(u"Rapports")
    rowx = 0
    sheet.write_merge(rowx, rowx + 1, 0, 3,
                      u"Rapports de gestion de stock %s" % Config.NAME_ORGA, style_title)
    rowx += 3
    sheet.write_merge(rowx, rowx, 1, 2, u"Date du rapport: ", style)
    date_com = "Bko le %s" % date.today().strftime(u"%d/%m/%Y")
    sheet.write_merge(rowx, rowx, 3, 3, date_com)

    sheet.col(1).width = 0x0d00 * 3
    sheet.col(2).width = 0x0d00 * 1.5
    sheet.col(4).width = 0x0d00 * 2
    # title = [u"Type", u"Produit", u"Nbre Carton", u"Restant", u"Date"]

    for rap in Report.all():
        if int(rowx) % 2 == 0:
            style_row_table = style1
        else:
            style_row_table = style2
        sheet.write(rowx, 0, rap.type_, style_row_table)
        sheet.write(rowx, 1, "%s (%s)" % (rap.product.name,
                                          rap.product.code), style_row_table)
        sheet.write(rowx, 2, rap.nbr_carton, style_row_table)
        sheet.write(rowx, 3, rap.remaining, style_row_table)
        sheet.write(
            rowx, 4, rap.date.strftime(u'%x %Hh:%Mmn'), style_row_table)
        rowx += 1
    book.save(file_name)
    return file_name


def write_product_xls(file_name, data):
    ''' Export data '''
    # Principe
    # write((nbre ligne - 1), nbre colonne, "contenu", style(optionnel).
    # write_merge((nbre ligne - 1), (nbre ligne - 1) + nbre de ligne
    # à merger, (nbre de colonne - 1), (nbre de colonne - 1) + nbre
    # de colonne à merger, u"contenu", style(optionnel)).
    book = xlwt.Workbook(encoding='ascii')
    sheet = book.add_sheet(u"Rapports")

    sheet.col(0).width = 0x0d00 * 2
    sheet.col(1).width = 0x0d00 * 4
    sheet.col(2).width = 0x0d00 * 2
    rowx = 0
    sheet.write_merge(rowx, rowx + 1, 0, 3,
                      u"Rapports de gestion de stock %s" % Config.NAME_ORGA, style_title)
    rowx += 3
    sheet.write_merge(rowx, rowx, 1, 2, u"Date du rapport: ", style)

    rowx += 1
    title = [u"Code", u"Article", u"Nombre de pièce", u""]
    for colx, val_center in enumerate(title):
        sheet.write(rowx, colx, val_center, style_t_table)
    rowx += 1
    for prod in Product.all():
        if int(rowx) % 2 == 0:
            style_row_table = style1
        else:
            style_row_table = style2
        sheet.write(rowx, 0, prod.code, style_row_table)
        sheet.write(rowx, 1, prod.name, style_row_table)
        sheet.write(rowx, 2, prod.number_parts_box, style_row_table)
        # sheet.write(rowx, 3, '[u"%s",u"%s"],' % (prod.code, prod.name))

        rowx += 1
    book.save(file_name)
    return file_name


# def write_xls(file_name):
#     ''' Export data '''
# Principe
# write((nbre ligne - 1), nbre colonne, "contenu", style(optionnel).
# write_merge((nbre ligne - 1), (nbre ligne - 1) + nbre de ligne
# à merger, (nbre de colonne - 1), (nbre de colonne - 1) + nbre
# de colonne à merger, u"contenu", style(optionnel)).
#     book = xlwt.Workbook(encoding='ascii')
#     sheet = book.add_sheet(u"Rapports")
#     rowx = 0
#     sheet.write_merge(rowx, rowx + 1, 0, 3,
#                       u"Rapports de gestion de stock %s" % Config.APP_NAME, style_title)
#     rowx += 3
#     sheet.write_merge(rowx, rowx, 1, 2, u"Date du rapport: ", style)
#     date_com = "Bko le %s" % date.today().strftime("%d/%m/%Y")
#     sheet.write_merge(rowx, rowx, 3, 3, date_com)

#     sheet.col(1).width = 0x0d00 * 3
#     sheet.col(2).width = 0x0d00 * 1.5
#     sheet.col(4).width = 0x0d00 * 2
# title = [u"Type", u"Produit", u"Nbre Carton", u"Restant", u"Date"]

#     for rap in Report.all():
#         if int(rowx) % 2 == 0:
#             style_row_table = style1
#         else:
#             style_row_table = style2
#         sheet.write(rowx, 0, rap.type_, style_row_table)
#         sheet.write(rowx, 1, "%s (%s)" % (rap.product.name,
#                                           rap.product.code), style_row_table)
#         sheet.write(rowx, 2, rap.nbr_carton, style_row_table)
#         sheet.write(rowx, 3, rap.remaining, style_row_table)
#         sheet.write(
#             rowx, 4, rap.date.strftime(u'%x %Hh:%Mmn'), style_row_table)
#         rowx += 1
#     book.save(file_name)
#     return file_name


# def write_inventory_xls(file_name, report):
#     period, report = report
#     book = xlwt.Workbook(encoding='ascii')
#     sheet = book.add_sheet(u"Inventaire %s" % Config.NAME_ORGA)
#     sheet.col(0).width = 0x0d00 * 3
#     sheet.protect = True
#     sheet.wnd_protect = True
#     sheet.obj_protect = True
#     sheet.scen_protect = True
#     sheet.password = "True"
#     rowx = 0
#     sheet.write_merge(rowx, rowx + 1, 0, 3,
#                       u"Inventaire de %s" % Config.NAME_ORGA, style_title)

#     rowx += 3
#     sheet.write_merge(rowx, rowx, 1, 3, u"Du %s au %s" %
#                       (period[0].strftime("%d/ %m/ %Y"), period[1].strftime("%d/ %m/ %Y")))

#     title = [u"Désignation", u"Quantité", u"Prix U.", u"Montant"]

#     rowx += 2
#     for colx, val_center in enumerate(title):
#         sheet.write(rowx, colx, val_center, style_t_table)
#     rowx += 1
#     totaux = 0
#     for prod in report:
#         col = 0
#         totaux += prod[3]
#         for val_center in prod:
#             if isinstance(val_center, unicode):
#                 style_ = style
#             else:
#                 style_ = int_style
#             sheet.write_merge(rowx, rowx, col, col, val_center, style_)
#             col += 1
#         rowx += 1

#     sheet.write_merge(rowx, rowx, 2, 2, "Totaux", style_)
#     sheet.write_merge(rowx, rowx, 3, 3, totaux, style_)
#     book.save(file_name)
#     openFile(file_name)
# return file_name


def write_order_xls(file_name, report):
    com_date, report = report
    book = xlwt.Workbook(encoding='ascii')
    sheet = book.add_sheet(u"%s COMMANDE" % Config.NAME_ORGA)
    sheet.col(0).width = 0x0d00 * 2
    sheet.col(1).width = 0x0d00 * 4
    sheet.col(2).width = 0x0d00 * 2
    rowx = 0
    sheet.write_merge(rowx, rowx + 1, 0, 2,
                      u"%s COMMANDE" % Config.NAME_ORGA, style_title)
    rowx += 2
    sheet.write_merge(rowx, rowx, 0, 2, u"DRAMANE KOUREKAMA ET FILS", style_)
    rowx += 1
    sheet.write_merge(rowx, rowx, 0, 2,
                      u"B.P.: 177–Tél. Bout. N°: 20229776/76429471/76422142",
                      style_)
    rowx += 1
    sheet.write_merge(rowx, rowx, 0, 2,
                      u"E-mail: ultimomalidk@yahoo.fr–Bamako-Rép. Du Mali",
                      style_)
    rowx += 2
    date_com = u"Bko le %s" % com_date.strftime("%d/%m/%Y")
    sheet.write_merge(rowx, rowx, 2, 2, date_com, style_)

    title = [u"QUANTITE", u"DESCRIPTION", u"ITEM NO"]

    rowx += 2
    for colx, val_center in enumerate(title):
        sheet.write(rowx, colx, val_center, style_t_table)
    rowx += 1
    for prod in report:
        col = 0
        sheet.write_merge(rowx, rowx, col, col, prod[0], int_style)
        col += 1
        sheet.write_merge(rowx, rowx, col, col, prod[1], style)
        col += 1
        sheet.write_merge(rowx, rowx, col, col, prod[2], style_code)
        rowx += 1
    book.save(file_name)
    openFile(file_name)
    # return file_name


def write_invoice_xls(file_name, invoice):

    book = xlwt.Workbook(encoding='ascii')
    sheet = book.add_sheet(u"Commande %s" % Config.NAME_ORGA)
    sheet.col(1).width = 0x0d00 * 3
    # sheet.col(4).width = 0x0d00 * 1.5
    rowx = 0
    sheet.write_merge(rowx, rowx + 1, 0, 3,
                      u"Facture de %s" % Config.NAME_ORGA, style_title)

    rowx += 3
    date = "Bko le %s" % invoice.date.strftime("%d/%m/%Y")
    sheet.write_merge(rowx, rowx, 2, 3, date)

    hheaders = [u"Quantité", u"Désignation", u"Prix Unitaire",
                u"Montant"]
    rowx += 2
    for colx, val_center in enumerate(hheaders):
        sheet.write(rowx, colx, val_center, style_t_table)
    rowx += 1

    data = [(item.qty, item.product.name, item.selling_price,
             item.qty * item.selling_price) for item in Report.filter(invoice=invoice)]

    for prod in data:
        col = 0
        for val_center in prod:
            if isinstance(val_center, str):
                style_ = style
            else:
                style_ = int_style
            sheet.write_merge(rowx, rowx, col, col, val_center, style_)
            col += 1
        rowx += 1
    book.save(file_name)
    openFile(file_name)
    # return file_name
