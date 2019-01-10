#!/usr/bin/env python
# -*- coding= UTF-8 -*-
# Fad

import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

# from reportlab.pdfbase import pdfmetrics
# from reportlab.pdfbase.ttfonts import TTFont

# setup the empty canvas
from io import FileIO as file
# from Common.pyPdf import PdfFileWriter, PdfFileReader
from PyPDF2 import PdfFileWriter, PdfFileReader
from models import Report
from num2words import num2words
from configuration import Config
from Common.ui.util import get_temp_filename, formatted_number, device_amount


def pdf_view(filename, invoice):
    """
        cette views est cree pour la generation du PDF
    """

    if not filename:
        filename = get_temp_filename('pdf')
        # print(filename)
    # on recupere les items de la facture
    items_invoice = Report.filter(invoice=invoice)
    # Static source pdf to be overlayed

    pdf_source = os.path.join(Config.ROOT_DIR, "templates", 't_invoice.pdf')
    tmp_file = os.path.join(Config.OUT, 'tmp.pdf')
    date_format = u"%d/%m/%Y"
    DEFAULT_FONT_SIZE = 11
    FONT = 'Times-Roman'

    # PDF en entrée
    input1 = PdfFileReader(file(pdf_source, "rb"))
    # PDF en sortie
    output = PdfFileWriter()
    # Récupération du nombre de pages
    n_pages = input1.getNumPages()
    # Pour chaque page

    for i in range(n_pages):
        # Récupération de la page du doc initial (input1)
        page = input1.getPage(i)
        p = canvas.Canvas(tmp_file, pagesize=A4)
        p.setFont(FONT, DEFAULT_FONT_SIZE)

        p.drawString(48, 685, "Facture N° : {}".format(invoice.number))
        p.drawString(48, 676, "Doit : {}".format(invoice.client.name))
        p.drawString(450, 676, "Bko, le {}".format(
            invoice.date.strftime(date_format)))
        # On ecrit les invoiceitem
        x, y = 120, 640
        x_qty = x
        x_description = x + 10
        x_price = x + 350
        x_amount = x + 435

        for i in items_invoice:
            p.drawRightString(x_qty, y, str(i.qty))
            p.drawString(x_description, y, str(i.product.name))
            p.drawRightString(x_price, y, str(
                formatted_number(i.selling_price)))
            p.drawRightString(x_amount, y, str(formatted_number(
                i.selling_price * i.qty)))
            y -= 17
        # On calcul le montant total hors taxe et sa conversion en lettre

        y = 150
        ht = sum([(val.selling_price * val.qty) for val in items_invoice])
        tax_rate = invoice.tax_rate if invoice.tax else 0
        mt_tax = int((ht * tax_rate) / 100)
        ttc = mt_tax + ht
        ht_en_lettre = num2words(ht, lang="fr")
        ht_en_lettre1, ht_en_lettre2 = controle_caratere(
            ht_en_lettre + " francs CFA", 50, y - 50)
        p.drawString(
            52, y - 55, "Arrêté la présente facture à la somme de :{}".format(
                ht_en_lettre1))
        p.drawString(50, y - 65, (ht_en_lettre2))
        p.setFont('Times-Bold', 11)

        tt_y = 155
        # Hors Taxe
        p.drawRightString(x_amount, tt_y, str(device_amount(ht)))
        p.drawString(x_price - 20, tt_y - 17, str(tax_rate) + "%")
        # TVA
        p.drawRightString(x_amount, tt_y - 17, device_amount(mt_tax))
        # Tout Taxe
        p.drawRightString(x_amount, tt_y - 34, str(device_amount(ttc)))
        x_foot = y - 90
        p.drawString(50, x_foot, "Acceptation" if invoice.type_ ==
                     "Proforma" else "Acquit")
        p.drawString(490, x_foot, "Fournisseur")
        p.showPage()
        # Sauvegarde de la page
        newpath = "Out"
        if not os.path.exists(newpath):
            os.makedirs(newpath)
        p.save()
        # Création du watermark
        watermark = PdfFileReader(file(tmp_file, "rb"))
        # Création page_initiale+watermark
        page.mergePage(watermark.getPage(0))
        # Création de la nouvelle page
        output.addPage(page)
    # Nouveau pdf
    file_dest = filename + ".pdf"
    try:
        outputStream = file(os.path.join(Config.OUT, file_dest), u"wb")
        output.write(outputStream)
        outputStream.close()
        return file_dest
    except OSError as e:
        from Common.ui.util import raise_error
        raise_error(u"Impossible de lancer le PDF", """
                    Car un autre en cours d'utilistation. Kill le \n{}""".format(e))
        return


def controle_caratere(lettre, nb_controle, nb_limite):
    """
        cette fonction decoupe une chaine de caratere en fonction
        du nombre de caratere donnée et conduit le reste à la ligne
    """
    lettre = lettre
    if len(lettre) <= nb_controle:
        ch = lettre
        ch2 = u""
        return ch, ch2
    else:
        ch = ch2 = u""
        for n in lettre.split(u" "):
            if len(ch) <= nb_limite:
                ch = ch + u" " + n
            else:
                ch2 = ch2 + u" " + n
        return ch, ch2
