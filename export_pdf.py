#!/usr/bin/env python
# -*- coding= UTF-8 -*-
# Fad

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

from num2words import num2words
# from configuration import Config

from Common.ui.util import formatted_number


def pdf_view(invoice):
    """
        cette views est cree pour la generation du PDF
    """
    # print(filename)
    # on recupere les items de la facture
    items_invoice = invoice.get("data")
    file_name = invoice.get("file_name")
    # title = invoice.get("title")

    # Static source pdf to be overlayed
    template_pdf = 'templates/fact_source.pdf'
    tmp_file = 'tmp.pdf'
    # DATE_FORMAT = u"%d/%m/%Y"

    # DEFAULT_FONT_SIZE = 11
    # FONT = 'Courier-Bold'
    # A simple function to return a leading 0 on any single digit int.

    def double_zero(value):
        try:
            return '%02d' % value
        except TypeError:
            return value

    # setup the empty canvas
    from io import FileIO as file
    # from Common.pyPdf import PdfFileWriter, PdfFileReader
    from PyPDF2 import PdfFileWriter, PdfFileReader

    # PDF en entrée
    input1 = PdfFileReader(file(template_pdf, "rb"))

    # PDF en sortie
    output = PdfFileWriter()
    # Récupération du nombre de pages
    n_pages = input1.getNumPages()
    # Pour chaque page
    for i in range(n_pages):
        # Récupération de la page du doc initial (input1)
        page = input1.getPage(i)

        p = canvas.Canvas(tmp_file, pagesize=A4)
        # p.setFont(FONT, DEFAULT_FONT_SIZE)

        p.drawString(50, 683, invoice.get("invoice_type") +
                     " N° : " + str(invoice.get("number")))
        p.drawString(50, 667, "Doit à :" +
                     str(invoice.get("name_client")))
        p.drawString(450, 683, "Date : " + str(invoice.get("invoice_date")))
        # On ecrit les invoiceitem
        x, y = 20, 625
        cpt = 1
        ht = 0
        print(items_invoice)
        for qtty, designation, amount, montant in items_invoice:
            # montant = qtty * amount
            p.drawRightString(x + 50, y, str(cpt))
            p.drawString(x + 55, y, str(designation))
            p.drawRightString(
                x + 378, y, str(formatted_number(qtty)))
            p.drawRightString(
                x + 452, y, str(formatted_number(amount)))
            p.drawRightString(
                x + 535, y, str(formatted_number(montant)))
            y -= 20
            ht += montant
            cpt += 1

        ht_en_lettre = num2words(ht, lang='fr')
        p.drawRightString(555, 223, str(formatted_number(ht)))
        ht_en_lettre1, ht_en_lettre2 = controle_caratere(
            "Arrêté la présente facture à la somme de : " + ht_en_lettre.title() +
            " francs CFA", 10, 90)
        p.drawString(50, 176, (ht_en_lettre1))
        p.drawString(55, 160, (ht_en_lettre2))
        p.drawString(450, 120, ('Le Fournisseur'))

        p.showPage()
        # Sauvegarde de la page
        p.save()
        # Création du watermark
        watermark = PdfFileReader(file(tmp_file, "rb"))
        # Création page_initiale+watermark
        page.mergePage(watermark.getPage(0))
        # Création de la nouvelle page
        output.addPage(page)
    file_dest = file_name
    output_stream = file(file_dest, u"wb")
    output.write(output_stream)
    output_stream.close()

    return file_dest


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
