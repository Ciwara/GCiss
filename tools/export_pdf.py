#!/usr/bin/env python
# -*- coding= UTF-8 -*-

# from reportlab.lib.units import inch
# from reportlab.lib import colors
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    # from subprocess import Popen, PIPE
    # from reportlab. platypus import Table
    # from reportlab.lib.styles import ParagraphStyle
except:
    pass

from models import Report
from Common.cel import cel
from configuration import Config
from Common.ui.util import get_temp_filename


def pdf_view(filename, order):
    """
        cette views est cree pour la generation du PDF
    """

    if not filename:
        filename = get_temp_filename('pdf')
    # on recupere la facture a afficher
    invoice = order
    # on recupere les items de la facture
    items_invoice = Report.filter(invoice=invoice)

    # Static source pdf to be overlayed
    PDF_SOURCE = 'tools/fact_source.pdf'
    TMP_FILE = 'tools/tmp.pdf'
    DATE_FORMAT = u"%d/%m/%Y"

    DEFAULT_FONT_SIZE = 10
    FONT = 'Courier-Bold'
    # A simple function to return a leading 0 on any single digit int.

    def double_zero(value):
        try:
            return '%02d' % value
        except TypeError:
            return value

    # setup the empty canvas

    from pyPdf import PdfFileWriter, PdfFileReader
    # PDF en entrée
    input1 = PdfFileReader(file(PDF_SOURCE, "rb"))
    # PDF en sortie
    output = PdfFileWriter()
    # Récupération du nombre de pages
    n_pages = input1.getNumPages()
    # Pour chaque page
    for i in range(n_pages):
        # Récupération de la page du doc initial (input1)
        page = input1.getPage(i)

        # p = canvas.Canvas(buffer, pagesize=A4)
        p = canvas.Canvas(TMP_FILE, pagesize=A4)
        p.setFont(FONT, DEFAULT_FONT_SIZE)

        # Création de l'objet PDF, en utilisant l'objet de réponse comme "fichier"
        # on afffiche l'image de l'orgamisation
        try:
            p.drawImage(u'%s' % Config.APP_LOGO, 60, 740)
        except:
            print(u"logo non disponible!")
            pass

        p.drawString(370, 735, unicode(Config.NAME_ORGA))
        # On trace Une ligne horizontale
        p.line(60, 730, 535, 730)

        p.drawString(59, 25, Config.NAME_ORGA + " - tel : " +
                     str(Config.TEL_ORGA) + " - " + unicode(Config.ADRESS_ORGA))

        legal_infos, legal_infos1 = controle_caratere(Config.BP, 55, 55)

        p.drawString(90, 14, legal_infos)
        p.drawString(90, 6, legal_infos1)
        p.drawString(
            60, 706, str(invoice.type_) + " N°: " + str(invoice.number))
        p.drawString(370, 706, "Date: " + str(invoice.date.strftime(DATE_FORMAT)) +
                     " à " + str(invoice.location))
        p.drawString(60, 690, "Doit: " + (invoice.client))

        if invoice.subject:
            p.drawString(60, 664, "Objet: " + str(invoice.subject))

        # On ecrit les invoiceitem
        x, y = 40, 600
        for i in items_invoice:
            p.drawString(x, y, str(i.qty).rjust(10, ' '))
            p.drawString(x + 75, y, (i.product.__str__()))
            p.drawString(x + 340, y, str(i.selling_price).rjust(10, ' '))
            p.drawString(
                x + 435, y, str(i.selling_price * i.qty).rjust(10, ' '))
            y -= 20
        # on teste le type
        if invoice.type_ == "Facture":
            p.drawString(59, 95, "Pour acquit: ")
        else:
            p.drawString(59, 95, "Pour acceptation: ")

        p.drawString(435, 95, "Le Providers: ")
        # On calcul le montant total hors taxe et sa conversion en lettre
        ht = 0
        for i in items_invoice:
            montant = i.selling_price * i.qty
            ht += montant
        p.drawString(476, 204, str(ht).rjust(10, ' '))
        ht_en_lettre = cel(ht)
        # Calcul du TTC avec le TVA s'il existe
        if invoice.tax:
            TVA = (invoice.tax_rate * ht) / 100
            p.drawString(476, 183.5, str(TVA).rjust(10, ' '))
            TTC = ht + TVA
            p.drawString(476, 164, str(TTC).rjust(10, ' '))
            ht_en_lettre = cel(TTC)
            ht_en_lettre1, ht_en_lettre2 = controle_caratere(
                ht_en_lettre + " FCFA", 46, 40)
            p.drawString(263.8, 133, (ht_en_lettre1))
            p.drawString(53, 120, (ht_en_lettre2))

            p.drawString(415, 183.5, str(invoice.tax_rate))

        else:
            TTC = ht
            p.drawString(476, 164, str(TTC).rjust(10, ' '))
            ht_en_lettre1, ht_en_lettre2 = controle_caratere(
                ht_en_lettre + " FCFA", 46, 40)
            p.drawString(263.8, 133, (ht_en_lettre1))
            p.drawString(53, 120, (ht_en_lettre2))
            p.drawString(415, 183.5, str(0))
            p.drawString(476, 183.5, str(0).rjust(10, ' '))
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
    file_dest = filename + u".pdf"
    outputStream = file(file_dest, u"wb")
    output.write(outputStream)
    outputStream.close()

    return file_dest


def controle_caratere(lettre, nb_controle, nb_limite):
    """
        cette fonction decoupe une chaine de caratere en fonction
        du nombre de caratere donnée et conduit le reste à la ligne
    """
    lettre = lettre
    if len(lettre) <= nb_controle:
        ch = lettre
        ch2 = ""
        return ch, ch2
    else:
        ch = ch2 = ""
        for n in lettre.split(" "):
            if len(ch) <= nb_limite:
                ch = ch + " " + n
            else:
                ch2 = ch2 + " " + n
        return ch, ch2
