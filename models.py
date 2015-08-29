#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
# maintainer: Fadiga

from __future__ import (
    unicode_literals, absolute_import, division, print_function)

from datetime import datetime

from Common.peewee import (DateTimeField, CharField, IntegerField, BooleanField,
                           ForeignKeyField, TextField)
from GCommon.models import (BaseModel, SettingsAdmin, Version, FileJoin,
                            Organization, Owner, Category, Store)

FDATE = u"%c"
now = datetime.now()


class Store(Store):

    def last_report(self):
        return self.get_or_none(Report.select().where(Report.store == self).order_by(Report.date.desc()))

    def lasts_reports(self):
        try:
            return Report.select().where(Report.store == self).order_by(Report.date.desc()).all()
        except Exception as e:
            # print("lasts_reports ", e)
            raise

    def get_reports(self):

        try:
            return Report.select().where(Report.store == self)
        except Common.peewee.ReportDoesNotExist as e:
            print("get_reports ", e)

    def get_report_or_none(self):
        return self.get_or_none(Report.select().where(Report.store == self))

    def get_remaining_and_nb_parts(self, prod):

        remaining = 0

        rpt = self.get_or_none(
            self.get_reports()
                  .where(Report.product == prod)
                  .order_by(Report.date.desc()))
        if rpt:
            remaining = rpt.remaining
            # print(rpt.product.name)
        return remaining, prod.number_parts_box


class Category(Category):

    def all_prod(self):
        return Product.select().where(Product.category == self)


class Product(BaseModel):

    # class Meta:
    #     ordering = (('name', 'desc'))

    date = DateTimeField(default=now)
    code = CharField(max_length=30, unique=True, null=True)
    name = CharField(max_length=50, unique=True)
    number_parts_box = IntegerField(default=1)
    category = ForeignKeyField(
        Category, related_name='category_products')
    file_join = ForeignKeyField(
        FileJoin, null=True, related_name='file_joins_products')

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

    def save(self):
        self.code = self.code if self.code else self.name.lower().replace(
            " ", "")
        super(Product, self).save()

    def display_name(self):
        return u"{}".format(self.name)

    def get_report_or_none(self):
        return self.get_or_none(Report.select().where(Report.product == self))

    @property
    def image_link(self):
        try:
            return self.file_join.get_file
        except Exception as e:
            return None

    @property
    def last_report(self):
        try:
            last = Report.select().where(
                Report.product == self).order_by(Report.date.desc()).get()
        except Exception as e:
            print(e)
            last = None
        return last

    def reports(self):
        try:
            return Report.select().where(Report.product == self).order_by(Report.date.desc())
        except Exception as e:
            # print(e)
            pass


class Payment(BaseModel):

    """ docstring for Payment """

    class Meta:
        order_by = ('date',)

    DEBIT = "Débit"
    CREDIT = "Crédit"

    DC = [DEBIT, CREDIT]

    owner = ForeignKeyField(Owner, verbose_name=("Utilisateur"))
    date = DateTimeField(verbose_name=("Date"), default=now)
    debit = IntegerField(verbose_name=("Débit"))
    credit = IntegerField(verbose_name=("Crédit"))
    libelle = CharField(verbose_name=("Libelle"), null=True)
    balance = IntegerField(verbose_name=("Solde"))
    type_ = CharField(choices=DC)
    deleted = BooleanField(default=False)

    def __str__(self, arg):
        return "{libelle} {date} {type_} de {balance}".format(
            date=self.date.strftime(FDATE), type_=self.type_,
            balance=self.balance, libelle=self.libelle)

    def save(self):
        """
        Calcul du balance en stock après une operation."""
        self.owner = Owner.get(Owner.islog == True)
        print("SAVE BEGIN")
        previous_balance = int(self.last_balance_payment())
        print("previous_balance: ", previous_balance)
        # amount = int(self.amount)
        print("type :", self.type_)
        if self.type_ == self.CREDIT:
            print("credit")
            self.balance = previous_balance + int(self.credit)
            self.debit = 0
        if self.type_ == self.DEBIT:
            print("debit")
            self.balance = previous_balance - int(self.debit)
            self.credit = 0

        super(Payment, self).save()
        try:
            next_rpt = Payment.select().where(Payment.date > self.date,
                                              Payment.deleted == False).order_by(Payment.date.asc()).get()
            next_rpt.save()
        except Exception as e:
            # print("next_rpt", e)
            pass

    def last_balance_payment(self):
        try:
            return Payment.select().where(Payment.deleted == False).order_by(Payment.date.desc()).get().balance
        except Exception as e:
            print("last_balance_payment", e)
            return 0


class ProviderOrClient(BaseModel):

    """ Represents the company emmiting the invoices
    """
    # class Meta:
    #     order_by = ('name',)

    CLT = 'Client'
    FSEUR = 'Fournisseur'
    TYPES = [CLT, FSEUR]

    name = CharField(verbose_name=("Nom de votre entreprise"))
    address = TextField(
        null=True, verbose_name=("Adresse principale de votre société"))
    phone = IntegerField(
        unique=True, verbose_name=("Numero de téléphone de votre entreprise"))
    email = CharField(
        null=True, verbose_name=("Adresse électronique de votre entreprise"))
    legal_infos = TextField(
        null=True, verbose_name=("Informations légales"))
    type_ = CharField(max_length=30, choices=TYPES, default=CLT)
    picture = ForeignKeyField(
        FileJoin, null=True, related_name='file_joins_pictures', verbose_name=("image de la societe"))

    def __str__(self):
        return u"{}".format(self.name)

    @classmethod
    def get_or_create(cls, name, phone, typ):
        try:
            ctct = cls.get(name=name, phone=phone, type_=typ)
        except cls.DoesNotExist:
            ctct = cls.create(name=name, phone=phone, type_=typ)
        return ctct


class Invoice(BaseModel):

    """ Represents an invoices """

    class Meta:
        order_by = ('number',)

    TYPE_FACT = 'Facture'
    TYPE_PROF = 'Proforma'
    TYPE_BON = 'Bon'

    TYPES = [TYPE_BON, TYPE_FACT, TYPE_PROF]

    owner = ForeignKeyField(Owner, verbose_name=("Utilisateur"))
    number = IntegerField(verbose_name=("Numero"), unique=True)
    client = ForeignKeyField(
        ProviderOrClient, null=True, verbose_name=("Doit"))
    location = CharField(max_length=50, null=True, verbose_name=("A"))
    type_ = CharField(max_length=30, default=TYPE_PROF)
    subject = CharField(max_length=100, verbose_name=("Objet"))
    tax = BooleanField(default=False)
    tax_rate = IntegerField(
        null=True, verbose_name=("Taux"), default=18)
    paid_amount = IntegerField(verbose_name="Reste à payer")

    def __str__(self):
        return "{num}/{client}/{owner}".format(num=self.number, owner=self.owner,
                                               client=self.client)

    @classmethod
    def get_next_number(cls, org):
        """ Get a valid number automatically incremented from
            the higher one.
        """
        number = 1
        if Invoice.select().count():
            number += int(Invoice.latest('number').number)
        return number

    @property
    def items(self):
        return Report.select().filter(Report.invoice == self)

    @property
    def date(self):
        return self.items.first().date

    def deletes(self):
        self.delete_instance()
        for rep in self.items:
            rep.delete()
            rep.delete_instance()

    def display_name(self):
        return u"Facture N: {num} de {client} au {date}".format(num=self.number,
                                                                client=self.client, date=self.date.strftime("%c"))


class Buy(BaseModel):

    """docstring for Buy"""

    class Meta:
        order_by = ('provd_or_clt',)

    owner = ForeignKeyField(Owner, verbose_name=("Utilisateur"))
    provd_or_clt = ForeignKeyField(ProviderOrClient,
                                   verbose_name=("Proprietaire"))

    def __str__(self):
        return u"{owner}/{provd_or_clt}".format(owner=self.owner,
                                                provd_or_clt=self.provd_or_clt)

    def items(self):
        try:
            return Report.select().where(Report.buy == self)
        except:
            pass

    @property
    def date(self):
        return self.items().first().date

    @classmethod
    def last_prod_buy(cls, product=None):
        return Report.filter(invoice=False,
                             product=product).order_by(Report.date.desc()).get()


class Refund(BaseModel):

    class Meta:
        order_by = ('date',)

    """docstring for ClassName"""

    owner = ForeignKeyField(Owner, verbose_name=("Utilisateur"))
    provider_client = ForeignKeyField(ProviderOrClient)
    date = DateTimeField(default=now)
    amount = IntegerField(verbose_name="Montant")

    def save(self):
        """Calcul du remboursement après une operation."""
        # print("SAVE BEGIN")
        previous_balance = int(last_balance_payment())
        amount = int(self.amount)
        if self.type_ == self.CREDIT:
            self.balance = previous_balance + amount
        if self.type_ == self.DEBIT:
            self.balance = previous_balance - amount
            if self.balance < 0:
                raise_error(u"Erreur",
                            u"On peut pas utilisé %d puis qu'il ne reste que %d"
                            % (self.amount, previous_balance))
                return False

        super(Refund, self).save()
        try:
            next_rpt = Refund.select().where(Refund.date > self.date,
                                             Refund.deleted == False).order_by(Refund.date.asc()).get()
            next_rpt.save()
        except Exception as e:
            # print("next_rpt", e)
            pass

    def last_balance_payment(self):
        try:
            return Refund.select().where(Refund.deleted == False).order_by(Refund.date.desc()).get().balance
        except Exception as e:
            print("last_balance_payment", e)
            return 0

    @property
    def payment(self):
        return Refund.select().where(Refund.deleted == False)
        super(save, self).save()

    def __str__(self):
        return "{owner}{amount}{date}".format(
            owner=self.owner, date=self.date, amount=self.amount)

    def __unicode__(self):
        return "{owner}{amount}{date}".format(
            owner=self.owner, date=self.date, amount=self.amount)


class Report(BaseModel):

    class Meta:
        order_by = ('date',)

    E = u"Entrée"
    S = u"Sortie"

    date = DateTimeField(verbose_name=("Fait le"), default=now)
    registered_on = CharField(default=now)
    store = ForeignKeyField(Store, related_name='stores')
    product = ForeignKeyField(Product, related_name='product_reports')
    buy = ForeignKeyField(Buy, null=True)
    cost_buying = IntegerField(verbose_name="Prix de revient")
    invoice = ForeignKeyField(Invoice, null=True)
    selling_price = IntegerField(default=1, verbose_name="Prix de vente")
    type_ = CharField(default=E)
    qty = IntegerField(default=1)
    remaining = IntegerField(default=0)
    deleted = BooleanField(default=False)

    def __str__(self):
        return u"{product}/{store}/{type_}".format(type_=self.type_,
                                                   store=self.store,
                                                   product=self.product)

    def __unicode__(self):
        return u"{product}/{store}/{type_}".format(type_=self.type_,
                                                   store=self.store,
                                                   product=self.product)

    def save(self):
        """
        Calcul du restant en stock après une operation."""

        prev_remaining = int(
            self.last_report.remaining) if self.last_report else 0
        if not self.is_out_rpt:
            self.remaining = prev_remaining + int(self.qty)
        else:
            self.remaining = prev_remaining - int(self.qty)
            self.selling_price = self.last_price()
            if self.remaining < 0:
                return ValueError(
                    u"On peut pas utilisé {} puis qu'il ne reste que {}".format(self.qty, prev_remaining))
        super(Report, self).save()

        try:
            self.next_rpts().get().save()
        except:
            pass

    def next_rpts(self):
        return Report.select().filter(Report.product == self.product,
                                      Report.store == self.store,
                                      Report.date > self.date,
                                      Report.deleted == False).order_by(Report.date.asc())

    @property
    def last_report(self):
        last_reports = Report.select().where(Report.product == self.product,
                                             Report.store == self.store,
                                             Report.date < self.date,
                                             Report.deleted == False).order_by(Report.date.desc())
        try:
            return last_reports.get()
        except:
            return None

    @property
    def is_out_rpt(self):
        return self.type_ == self.S

    def last_price(self):
        if self.is_out_rpt and self.last_report:
            return int(self.last_report.selling_price)
