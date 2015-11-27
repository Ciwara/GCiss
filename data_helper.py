#!/usr/bin/env python
# -*- encoding: utf-8
# vim: ai ts=4 sts=4 et sw=4 nu
# maintainer: Fad
from __future__ import (
    unicode_literals, absolute_import, division, print_function)

from datetime import datetime

from models import Report, Product, Store, Payment
from configuration import Config


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


def check_befor_update_data(reports):
    print("check_befor_update_data")
    for report in reports:
        list_error = []
        if report.last_report:
            remaining = report.last_report.remaining
        else:
            remaining = 0
        for rpt in report.next_rpts():
            print(rpt.product.name, "=", rpt.qty)
            if rpt.type_ == Report.E:
                remaining += rpt.qty
            if rpt.type_ == Report.S:
                remaining -= rpt.qty
            if remaining < 0:
                print(remaining)
                return rpt, remaining
                break
    return None, ""


def check_befor_update_payment(pay):
    balance = pay.balance
    lt = []
    for rpt in pay.next_rpts():
        previous_balance = int(rpt.last_balance_payment())
        print(rpt)
        if rpt.type_ == Payment.CREDIT:
            balance = previous_balance + int(rpt.credit)
            lt.append(
                "{} = last {} + {}".format(balance, previous_balance, rpt.credit))
        if rpt.type_ == Payment.DEBIT:
            balance = previous_balance - int(rpt.debit)
            lt.append(
                "{} = last {} - {}".format(balance, previous_balance, rpt.debit))
        # if balance < 0:
        #     return False
    print(lt)
    return True
