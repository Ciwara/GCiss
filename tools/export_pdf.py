#!/usr/bin/env python
# -*- coding= UTF-8 -*-
# Fad

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

from models import Report
from num2words import num2words
from configuration import Config
from Common.ui.util import get_temp_filename, formatted_number


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
    PDFSOURCE = 'fact_source.pdf'
    TMP_FILE = 'tmp.pdf'
    DATE_FORMAT = u"%d/%m/%Y"

    DEFAULT_FONT_SIZE = 11
    FONT = 'Courier-Bold'
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
    input1 = PdfFileReader(file(PDFSOURCE, "rb"))

    # PDF en sortie
    output = PdfFileWriter()
    # Récupération du nombre de pages
    n_pages = input1.getNumPages()
    # Pour chaque page
    for i in range(n_pages):
        # Récupération de la page du doc initial (input1)
        page = input1.getPage(i)

        p = canvas.Canvas(TMP_FILE, pagesize=A4)
        p.setFont(FONT, DEFAULT_FONT_SIZE)
        p.drawString(130, 694, str(invoice.number))
        p.drawString(105, 666, (invoice.client.name))
        p.drawString(465, 694, str(invoice.date.strftime(DATE_FORMAT)))
        # On ecrit les invoiceitem
        x, y = 54, 597
        for i in items_invoice:
            p.drawString(x, y, str(i.qty).rjust(11, ' '))
            p.drawString(x + 78, y, str(i.product.name))
            p.drawString(x + 340, y,
                         str(formatted_number(i.selling_price)).rjust(10, ' '))
            p.drawString(x + 430, y, str(formatted_number(
                i.selling_price * i.qty)).rjust(10, ' '))
            y -= 23
        # on teste le type
        if invoice.type_ == "Proforma":
            p.drawString(59, 80, "Acceptation")
        else:
            p.drawString(59, 80, "Acquit")

        p.drawString(435, 80, "Fournisseur")
        # On calcul le montant total hors taxe et sa conversion en lettre
        ht = 0
        for i in items_invoice:
            montant = i.selling_price * i.qty
            ht += montant

        ht_en_lettre = num2words(ht, lang="fr")

        p.drawString(x + 430, 160, str(formatted_number(ht)).rjust(10, ' '))
        ht_en_lettre1, ht_en_lettre2 = controle_caratere(ht_en_lettre +
                                                         " FCFA", 40, 40)
        # p.drawString(260, 119, (ht_en_lettre + " FCFA"))
        p.drawString(272, 126, (ht_en_lettre1))
        p.drawString(53, 102, (ht_en_lettre2))

        # legal_infos, legal_infos1 = controle_caratere(Config.BP, 55, 55)
        # p.drawString(90, 14, legal_infos)
        # p.drawString(90, 6, legal_infos1)
        p.showPage()
        # Sauvegarde de la page
        p.save()
        # Création du watermark
        watermark = PdfFileReader(file(TMP_FILE, "rb"))
        # Création page_initiale+watermark
        page.mergePage(watermark.getPage(0))
        # Création de la nouvelle page
        output.addPage(page)
    # Nouveau pdf
    file_dest = filename + ".pdf"
    try:
        outputStream = file(file_dest, u"wb")
        output.write(outputStream)
        outputStream.close()
        return file_dest
    except OSError:
        from Common.ui.util import raise_error
        raise_error(u"Impossible de lancer le PDF", """
                    Car un autre en cours d'utilistation. Kill le""")
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
