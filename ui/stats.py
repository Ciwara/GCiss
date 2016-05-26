#!/usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: Fad
import peewee
from datetime import datetime, timedelta
from PyQt4 import QtGui, QtCore

from configuration import Config
from peewee import fn
from Common.ui.common import FWidget, FPeriodHolder, FPageTitle, BttExportXLS
from models import Report, Store, Product
from Common.ui.table import FTableWidget, TotalsWidget
from Common.ui.util import formatted_number, date_on_or_end


class StatViewWidget(FWidget, FPeriodHolder):

    def __init__(self, parent=0, *args, **kwargs):

        super(StatViewWidget, self).__init__(
            parent=parent, *args, **kwargs)
        FPeriodHolder.__init__(self, *args, **kwargs)

        self.title = u"     Les Activités"
        self.parentWidget().setWindowTitle(Config.NAME_ORGA + self.title)
        self.parent = parent

        self.table_rpt = ReportTableWidget(
            parent=self, main_date=self.main_date)

        self.btt_export = BttExportXLS(u"Exporter")
        self.btt_export.clicked.connect(self.export_xls)

        gridbox = QtGui.QGridLayout()
        gridbox.addWidget(self.btt_export, 0, 3)
        gridbox.setColumnStretch(0, 2)

        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(FPageTitle(self.title))
        vbox.addLayout(gridbox)
        vbox.addWidget(self.periods_bar)
        vbox.addWidget(self.table_rpt)
        self.setLayout(vbox)

    def refresh(self):
        self.table_rpt.refresh()

    def export_xls(self):
        from Common.exports_xlsx import export_dynamic_data

        dict_data = {
            'file_name': "Semaine.xlsx",
            'headers': self.table_rpt.hheaders,
            'data': self.table_rpt.data,
            "extend_rows": [(0, "Totaux"),
                            (1, self.table_rpt.total_sum_d1),
                            (2, self.table_rpt.total_sum_d2),
                            (3, self.table_rpt.total_sum_d3),
                            (4, self.table_rpt.total_sum_d4),
                            (5, self.table_rpt.total_sum_d5),
                            (6, self.table_rpt.total_sum_d6),
                            (7, self.table_rpt.totals), ],
            'sheet': self.title,
            'title': self.title,
            'widths': self.table_rpt.stretch_columns,
            "date": self.table_rpt.date_on.strftime(u"%x") + " au " + self.table_rpt.date_end.strftime(u"%x")
        }
        export_dynamic_data(dict_data)

    def change_period(self, main_date):
        self.table_rpt.refresh_period(main_date)


class ReportTableWidget(FTableWidget):

    def __init__(self, parent, main_date, *args, **kwargs):

        FTableWidget.__init__(self, parent=parent, *args, **kwargs)

        self.hheaders = ["Modeles", u"Lundi", u"Mardi", u"Mercredi",
                         u"Jeudi", u"Vendredi", u"Samedi", u"Total"]
        self.parent = parent

        self.sorter = True
        self.stretch_columns = [0]
        self.align_map = {
            0: 'l', 1: 'r', 2: 'r', 3: 'r', 4: 'r', 5: 'r', 6: 'r', 7: 'r'}
        self.display_vheaders = False
        self.refresh_period(main_date)

    def refresh_period(self, main_date):
        """ """
        self._reset()
        self.set_data_for(main_date)
        self.refresh()

        pw = self.parent.parent.page_width() / 10
        self.setColumnWidth(0, pw * 2)
        self.setColumnWidth(1, pw)
        self.setColumnWidth(2, pw)
        self.setColumnWidth(3, pw)
        self.setColumnWidth(4, pw)
        self.setColumnWidth(5, pw)
        self.setColumnWidth(6, pw)
        self.setColumnWidth(7, pw)

    def set_data_for(self, main_date):

        reports = []
        self.totals = 0
        self.total_sum_d1 = 0
        self.total_sum_d2 = 0
        self.total_sum_d3 = 0
        self.total_sum_d4 = 0
        self.total_sum_d5 = 0
        self.total_sum_d6 = 0
        try:
            self.date_on, self.date_end = main_date.current.current
        except Exception as e:
            self.date_on, self.date_end = main_date.current
        products = [(Product.get(id=rpt.product_id).name) for rpt in
                    Report.select(fn.Distinct(Report.product)).where(
            Report.date >= self.date_on, Report.date <= self.date_end,
            Report.type_ == Report.S)]

        products_ = [(prod.name) for prod in Product.select().where(
            Product.name << products).order_by(Product.name.desc())]
        for prod_name in products_:
            on = date_on_or_end(self.date_on)
            end = date_on_or_end(self.date_end, on=False)
            dict_store = {}
            repts = Report.select().where(Report.type_ == Report.S,
                                          Report.product == Product.get(
                                              name=prod_name))
            dict_store["product"] = prod_name

            dict_store["sum_week"] = repts.select(
                peewee.fn.SUM(Report.qty)).where(Report.date >= on,
                                                 Report.date <= end).scalar() or 0

            self.totals += (dict_store["sum_week"])
            end = on + timedelta(days=1, seconds=-1)
            dict_store["sum_d1"] = repts.select(
                peewee.fn.SUM(Report.qty)).where(Report.date >= on,
                                                 Report.date <= end).scalar() or 0
            self.total_sum_d1 += dict_store["sum_d1"]
            on += timedelta(1)
            end = on + timedelta(days=1, seconds=-1)
            dict_store["sum_d2"] = repts.select(
                peewee.fn.SUM(Report.qty)).where(Report.date >= on,
                                                 Report.date <= end).scalar() or 0
            self.total_sum_d2 += dict_store["sum_d2"]
            on += timedelta(1)
            end = on + timedelta(days=1, seconds=-1)
            dict_store["sum_d3"] = repts.select(
                peewee.fn.SUM(Report.qty)).where(Report.date >= on,
                                                 Report.date <= end).scalar() or 0
            self.total_sum_d3 += dict_store["sum_d3"]
            on += timedelta(1)
            end = on + timedelta(days=1, seconds=-1)
            dict_store["sum_d4"] = repts.select(
                peewee.fn.SUM(Report.qty)).where(Report.date >= on,
                                                 Report.date <= end).scalar() or 0
            self.total_sum_d4 += dict_store["sum_d4"]
            on += timedelta(1)
            end = on + timedelta(days=1, seconds=-1)
            dict_store["sum_d5"] = repts.select(
                peewee.fn.SUM(Report.qty)).where(Report.date >= on,
                                                 Report.date <= end).scalar() or 0
            self.total_sum_d5 += dict_store["sum_d5"]
            on += timedelta(1)
            end = on + timedelta(days=1, seconds=-1)
            dict_store["sum_d6"] = repts.select(
                peewee.fn.SUM(Report.qty)).where(Report.date >= on,
                                                 Report.date <= end).scalar() or 0
            self.total_sum_d6 += dict_store["sum_d6"]
            reports.append(dict_store)

        self.data = [(rep.get('product'), rep.get('sum_d1'), rep.get('sum_d2'),
                      rep.get('sum_d3'), rep.get('sum_d4'), rep.get('sum_d5'),
                      rep.get('sum_d6'), rep.get('sum_week')) for rep in reports]

    def extend_rows(self):

        self.nb_rows = self.rowCount()
        self.setRowCount(self.nb_rows + 1)
        self.setItem(self.nb_rows, 0, TotalsWidget(u"Totaux: "))
        self.setItem(
            self.nb_rows, 7, TotalsWidget(formatted_number(self.totals)))
        self.setItem(
            self.nb_rows, 1, TotalsWidget(formatted_number(self.total_sum_d1)))
        self.setItem(
            self.nb_rows, 2, TotalsWidget(formatted_number(self.total_sum_d2)))
        self.setItem(
            self.nb_rows, 3, TotalsWidget(formatted_number(self.total_sum_d3)))
        self.setItem(
            self.nb_rows, 4, TotalsWidget(formatted_number(self.total_sum_d4)))
        self.setItem(
            self.nb_rows, 5, TotalsWidget(formatted_number(self.total_sum_d5)))
        self.setItem(
            self.nb_rows, 6, TotalsWidget(formatted_number(self.total_sum_d6)))

    def _item_for_data(self, row, column, data, context=None):
        return super(ReportTableWidget, self)._item_for_data(row, column,
                                                             data, context)
