#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
# maintainer: Fadiga

from __future__ import (
    unicode_literals, absolute_import, division, print_function)

from datetime import datetime

from peewee import (DateTimeField, CharField, IntegerField, BooleanField,
                    ForeignKeyField, TextField)
from GCommon.models import (BaseModel, Version, FileJoin,
                            Organization, Owner, Category, Store)

FDATE = u"%c"
NOW = datetime.now()


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
        except peewee.ReportDoesNotExist as e:
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
        return remaining, prod.number_parts_box


class Category(Category):

    def all_prod(self):
        return Product.select().where(Product.category == self)


class Product(BaseModel):

    # class Meta:
    #     ordering = (('name', 'desc'))

    date = DateTimeField(default=NOW)
    code = CharField(max_length=30, unique=True, null=True)
    name = CharField(max_length=50, unique=True)
    number_parts_box = IntegerField(default=1)
    category = ForeignKeyField(
        Category, related_name='category_products')
    file_join = ForeignKeyField(
        FileJoin, null=True, related_name='file_joins_products')

    def __str__(self):
        return u"{}".format(self.name)

    def __unicode__(self):
        return u"{}".format(self.name)

    def display_name(self):
        return "{}".format(self.name)

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

    def last_price(self):
        try:
            last_selling_price = Report.select().where(
                Report.product == self,
                Report.type_ == Report.E,
                Report.deleted == False).order_by(Report.date.desc()).get().selling_price
        except Exception as e:
            print("last_price", e)
            last_selling_price = 0

        return last_selling_price


class Payment(BaseModel):

    """ docstring for Payment """

    class Meta:
        order_by = ('date',)

    DEBIT = "Debit"
    CREDIT = "Credit"

    DC = [DEBIT, CREDIT]

    owner = ForeignKeyField(Owner, verbose_name=("Utilisateur"))
    date = DateTimeField(verbose_name=("Date"))
    debit = IntegerField(verbose_name=("Débit"))
    credit = IntegerField(verbose_name=("Crédit"))
    libelle = CharField(verbose_name=("Libelle"), null=True)
    balance = IntegerField(verbose_name=("Solde"))
    type_ = CharField(choices=DC)
    deleted = BooleanField(default=False)

    def __unicode__(self):
        return "Le {date} {type_} d'un montant de {amount} Fcfa".format(
            date=self.date.strftime(FDATE), type_=self.type_,
            amount=self.credit if self.type_ == self.CREDIT else self.debit, lib=self.libelle)

    def __str__(self):
        return self.__unicode__()

    def display_name(self):
        return self.__unicode__()

    def save(self):
        """
        Calcul du balance en stock après une operation."""
        self.owner = Owner.get(Owner.islog == True)
        print("SAVE BEGIN")
        previous_balance = int(
            self.last_balance_payment().balance if self.last_balance_payment() else 0)
        if self.type_ == self.CREDIT:
            self.balance = previous_balance + int(self.credit)
            self.debit = 0
        if self.type_ == self.DEBIT:
            self.balance = previous_balance - int(self.debit)
            self.credit = 0

        super(Payment, self).save()

        if self.next_rpt():
            self.next_rpt().save()

    def next_rpt(self):
        try:
            return self.next_rpts().get()
        except:
            return None

    def next_rpts(self):
        try:
            return Payment.select().where(Payment.date > self.date,
                                          Payment.deleted == False).order_by(Payment.date.asc())
        except Exception as e:
            return None
            print("next_rpt", e)

    def deletes_data(self):
        last = self.last_balance_payment()
        next_ = self.next_rpt()
        self.delete_instance()
        if last:
            last.save()
        else:
            if next_:
                next_.save()
        return

    def last_balance_payment(self):
        try:
            return Payment.select().where(
                Payment.deleted == False, Payment.date < self.date).order_by(Payment.date.desc()).get()
        except Exception as e:
            print("last_balance_payment", e)
            return None


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

    def invoices(self):
        return Invoice.select().where(Invoice.client == self)

    def buys(self):
        return Buy.select().where(Buy.provd_or_clt == self)

    def invoices_items(self):
        return Report.select().where(Report.type_ == Report.S,
                                     Report.invoice.client == self)

    def is_indebted(self):
        flag = False
        if self.last_remaining() > 0:
            flag = True
        return flag

    def last_refund(self):
        try:
            return Refund.select().where(Refund.provider_client == self).order_by(
                Refund.date.desc()).get()
        except Exception as e:
            return None

    def last_remaining(self):
        last_r = self.last_refund()
        return last_r.remaining if last_r else 0

    def __str__(self):
        return u"{}, {}".format(self.name, self.phone)

    def __unicode__(self):
        return self.__str__()

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
        order_by = ('-number',)

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
        return "{num}/{client}/{owner}".format(num=self.number,
                                               owner=self.owner, client=self.client)

    def __unicode__(self):
        return self.__str__()

    def save(self):
        self.owner = Owner.get(Owner.islog == True)
        super(Invoice, self).save()

    # @property
    # def clt_name(self):
    #     return self.client.name

    @property
    def get_next_number(self):
        """ Get a valid number automatically incremented from
            the higher one.
        """
        number = 1
        if Invoice.select().count() > 1:
            number = int(Invoice.select().order_by(Invoice.number.desc()
                                                   ).get().number) + 1
        return str(number)

    @property
    def items(self):
        return Report.select().filter(Report.invoice == self)

    @property
    def amount_ivoice(self):
        return sum([(val.selling_price * val.qty) for val in self.items])

    @property
    def debts(self):
        return Refund.select().filter(Refund.invoice == self)

    @property
    def date(self):
        # print(self.number)
        try:
            # print('DATE ', self.items.first().date)
            return self.items.first().date
        except Exception as e:
            print(e, "  ", self.number)
            return NOW

    def deletes_data(self):
        print("deletes data")
        for rep in self.items:
            print("d rep ", self.items)
            rep.deletes_data()
        for debt in self.debts:
            print("d debt ", self.debts)
            debt.deletes_data()
        self.delete_instance()
        print('Done d invoice')

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

    @property
    def items(self):
        try:
            return Report.select().where(Report.buy == self)
        except:
            pass

    def save(self):
        self.owner = Owner.get(Owner.islog == True)
        super(Buy, self).save()

    @property
    def date(self):
        try:
            return self.items.first().date
        except Exception as e:
            print(e)

    @classmethod
    def last_prod_buy(cls, product=None):
        return Report.filter(invoice=False,
                             product=product).order_by(Report.date.desc()).get()

    def deletes_data(self):
        for rep in self.items:
            rep.deletes_data()
        self.delete_instance()


class Report(BaseModel):

    class Meta:
        order_by = ('date',)

    E = u"Entrée"
    S = u"Sortie"

    date = DateTimeField(verbose_name=("Fait le"), default=NOW)
    registered_on = CharField(default=NOW)
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
        return self.__str__()

    def display_name(self):
        return u"Le porduit {product} enregistré le {date}".format(
            product=self.product.name, date=self.date.strftime(FDATE))

    def save(self):
        """
        Calcul du restant en stock après une operation."""

        prev_remaining = int(
            self.last_report.remaining) if self.last_report else 0
        if not self.is_out_rpt:
            self.remaining = prev_remaining + int(self.qty)
        else:
            self.remaining = prev_remaining - int(self.qty)
            self.cost_buying = self.last_selling_price()
            if self.remaining < 0:
                return ValueError(
                    u"On peut pas utilisé {} puis qu'il ne reste que {}".format(self.qty, prev_remaining))
        super(Report, self).save()

        if self.next_rpt():
            self.next_rpt().save()

    def next_rpt(self):
        try:
            return self.next_rpts().get()
        except:
            return None

    def next_rpts(self):
        return Report.select().filter(Report.product == self.product,
                                      Report.store == self.store,
                                      Report.date > self.date,
                                      Report.deleted == False).order_by(Report.date.asc())

    def deletes_data(self):
        last = self.last_report
        next_ = self.next_rpt()
        self.delete_instance()
        if last:
            last.save()
        else:
            if next_:
                next_.save()
        return

    @property
    def last_report(self):
        try:
            return Report.select().where(Report.product == self.product,
                                         Report.store == self.store,
                                         Report.date < self.date,
                                         Report.deleted == False).order_by(Report.date.desc()).get()
        except:
            return None

    @property
    def is_out_rpt(self):
        return self.type_ == self.S

    def last_selling_price(self):
        try:
            last_selling_price = Report.select().where(Report.product == self.product,
                                                       Report.type_ == Report.E,
                                                       Report.store == self.store,
                                                       Report.date < self.date,
                                                       Report.deleted == False).order_by(Report.date.desc()).get().selling_price
        except Exception as e:
            print(e)
            last_selling_price = 0
        return int(last_selling_price)


class Refund(BaseModel):

    class Meta:
        order_by = ('date',)

    """docstring for ClassName"""
    DT = "D"
    RB = "R"

    owner = ForeignKeyField(Owner, verbose_name=("Utilisateur"))
    provider_client = ForeignKeyField(ProviderOrClient)
    date = DateTimeField(default=NOW)
    invoice = ForeignKeyField(Invoice, null=True)
    amount = IntegerField(verbose_name="Montant")
    remaining = IntegerField(verbose_name="Reste à payer")
    type_ = CharField(verbose_name="Type d'opération")
    # "fin de payement"
    status = BooleanField(default=False)
    deleted = BooleanField(default=False)

    def __str__(self):
        return "{owner}{amount}{date}".format(
            owner=self.owner, date=self.date, amount=self.amount)

    def __unicode__(self):
        return self.__str__()

    def display_name(self):
        return self.__str__()

    def save(self):
        """
        Calcul du remaining en stock après une operation."""
        self.owner = Owner.get(Owner.islog == True)
        print("SAVE BEGIN")
        previous_remaining = int(
            self.last_refund().remaining if self.last_refund() else 0)
        if self.type_ == self.RB:
            self.remaining = previous_remaining - int(self.amount)
        if self.type_ == self.DT:
            self.remaining = previous_remaining + int(self.amount)

        super(Refund, self).save()

        if self.next_rpt():
            self.next_rpt().save()

    def next_rpt(self):
        try:
            return self.next_rpts().get()
        except:
            return None

    def next_rpts(self):
        try:
            return Refund.select().where(
                Refund.date > self.date,
                Refund.provider_client == self.provider_client,
                Refund.deleted == False).order_by(Refund.date.asc())
        except Exception as e:
            return None
            print("next_rpt", e)

    def deletes_data(self):
        last = self.last_refund()
        next_ = self.next_rpt()
        self.delete_instance()
        if last:
            last.save()
        else:
            if next_:
                next_.save()
        return

    def last_refund(self):
        try:
            return self.all_refund_by_clt_prov().where(
                Refund.date < self.date).order_by(Refund.date.desc()).get()
        except Exception as e:
            print("last_balance_payment", e)
            return None

    def all_refund_by_clt_prov(self):
        return Refund.select().where(
            Refund.deleted == False,
            Refund.provider_client == self.provider_client)

    def refund_remaing(self):
        return self.all_refund_by_clt_prov().order_by(Refund.date.desc()).get().remaining
