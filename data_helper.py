#!/usr/bin/env python
# -*- encoding: utf-8
# vim: ai ts=4 sts=4 et sw=4 nu
# maintainer: Fad
from __future__ import (
    unicode_literals, absolute_import, division, print_function)

from datetime import datetime

from models import Report, Product, Store
from configuration import Config


def date_to_datetime(dat):
    "reçoit une date return une datetime"
    dat = str(unicode(dat))
    day, month, year = dat.split('/')
    dt = datetime.now()
    return datetime(int(year), int(month), int(day),
                    int(dt.hour), int(dt.minute),
                    int(dt.second), int(dt.microsecond))


def lastes_reports():
    list_rep = []
    for prod in Product.all():
        last_report_for_prod = prod.last_report()
        if last_report_for_prod:
            list_rep.append(last_report_for_prod)
    return list_rep


def warning_of_prod():
    """"""
    l = []
    for store in Store.all():
        for prod in Product.all():
            report = last_report_store_prod(store.name, prod.name)
            try:
                if report.remaining < Config.nb_warning:
                    l.append(report)
            except AttributeError:
                pass
    return l


def suppression(report):
    """ Supression  """
    try:
        p = Report.filter(date__gt=report.date).get()
    except:
        p = None
    report.delete_instance()
    if p:
        p.save()


def last_prod_buy(product):
    l_rap = Report.filter(invoice=None,
                          product__name=product).order_by(('date', 'desc'))
    try:
        return l_rap.get()
    except:
        raise
        return None


def date_end(dat):
    dat = str(unicode(dat))
    day, month, year = dat.split('/')
    return datetime(int(year), int(month), int(day), 23, 59, 59)


def date_on(dat):
    dat = str(unicode(dat))
    day, month, year = dat.split('/')
    return datetime(int(year), int(month), int(day), 0, 0, 0)


def show_date(dat):
    return dat.strftime(u"%A le %d %b %Y a %Hh:%Mmn")


def lastes_reports():
    list_rep = []
    for store in Store.all():
        for prod in Product.all():
            try:
                list_rep.append(Report.filter(deleted=False, store=store,
                                              product=prod)
                                .order_by(('date', 'desc')).get())
            except:
                pass
    return list_rep


def update_report(report):
    """ Supression  """
    try:
        p = Report.filter(deleted=False, date__gt=report.date).get()
        p.save()
    except:
        pass

    report.delete_instance()


def last_report_store_prod(store, prod):
    last_reports = Report.filter(deleted=False, store=store,
                                 product=prod).order_by(('date', 'desc'))
    try:
        return last_reports.get()
    except:
        raise
        return None
