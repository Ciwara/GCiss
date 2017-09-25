#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
# maintainer: Fad
from __future__ import (unicode_literals, absolute_import, division,
                        print_function)

from Common.models import migrator, dbh, SettingsAdmin, Version, FileJoin, Organization, Owner
from models import (Store, Product, Report, Category, Invoice, Buy, Payment,
                    Refund, ProviderOrClient)


def setup(drop_tables=False):
    """ create tables if not exist """
    did_create = False

    for model in [Owner, Store, Product, Report, Category, Invoice, Buy,
                  Payment, SettingsAdmin, Organization, Version, Refund,
                  ProviderOrClient, FileJoin]:
        if drop_tables:
            model.drop_table()
        if not model.table_exists():
            model.create_table()
            did_create = True

    if did_create:
        from fixture import FixtInit
        FixtInit().create_all_or_pass()

setup()

# with dbh.transaction():

#     migrate(
#         migrator.rename_column('story', 'pub_date', 'publish_date'),
#         migrator.rename_column('story', 'mod_date', 'modified_date'),
#     )
