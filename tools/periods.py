#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
# Maintainer: Fad

from datetime import date, timedelta
from calendar import monthrange


def get_week_boundaries(year, week):
    """
        Retoure les date du premier et du dernier jour de la semaine dont
        on a le numéro.
    """
    d = date(year, 1, 1)

    if(d.weekday() > 3):
        d = d + timedelta(7 - d.weekday())
    else:
        d = d - timedelta(d.weekday())

    dlt = timedelta(days=(week - 1) * 7)
    return d + dlt,  d + dlt + timedelta(days=6)


class WeekPeriod(object):
    """docstring for WeekPeriod"""
    def __init__(self, year, duration, duration_number):
        super(WeekPeriod, self).__init__()
        self.year = year
        self.duration = duration
        self.duration_number = duration_number

    def __repr__(self):
        return ("<Period('%(start)s', '%(end)s')>") \
                 % {'start': self.current[0], 'end': self.current[1]}

    def __unicode__(self):
        return ("Semaine de:%(start)s") % {'start': self.current[0]}

    @property
    def current(self):
        return get_week_boundaries(self.year, self.duration_number)


    def display_name(self):
        return ("Semaine du: %(start)s") % {'start': self.current[0].strftime(u"%d %b %Y")}

    @property
    def next(self):
        # la date de la semaine avant celle qu'on affiche
        delta = timedelta(7)

        next_date = self.current[0] + delta
        next_week_number = next_date.isocalendar()[1]

        return next_date.year, next_week_number

    @property
    def previous(self):
        # la date de la semaine avant celle qu'on affiche
        delta = timedelta(7)

        previous_date = self.current[0] - delta
        previous_week_number = previous_date.isocalendar()[1]

        return previous_date.year, previous_week_number


class Period(object):
    """docstring for Period"""
    def __init__(self, year, duration,  duration_number):
        super(Period, self).__init__()

        self.year = year
        self.duration = duration
        self.duration_number = duration_number
        W = "week"
        # la date à afficher
        if duration == "week": # on recupere le premier jour
            self.current = WeekPeriod(self.year, W, self.duration_number)

            self.next = WeekPeriod(self.current.next[0], W, self.current.next[1])
            self.previous = WeekPeriod(self.current.previous[0], W,
                                       self.current.previous[1])
    #     if duration == "month":
    #         self.current = date(self.year, self.duration_number, 1)
    #         self.next = self.next_month()
    #         self.previous = self.previous_month()
    #     if duration == "year":
    #         self.current = date(self.year, 1, 1)
    #         self.next = self.next_year()
    #         self.previous = self.previous_year()

    # def next_week(self):
    #     # la date de la semaine avant celle qu'on affiche
    #     delta = timedelta(7)

    #     next_date = self.current[0] + delta
    #     next_week_number = next_date.isocalendar()[1]

    #     return next_week_number

    # def previous_week(self):
    #     # la date de la semaine avant celle qu'on affiche
    #     delta = timedelta(7)

    #     previous_date = self.current[0] - delta
    #     previous_week_number = previous_date.isocalendar()[1]

    #     return previous_week_number

    # def next_month(self):
    #     # la date du mois après celui qu'on affiche
    #     days_count = monthrange(self.current.year,
    #                             self.current.month)[1]
    #     delta = timedelta(days_count + 1)
    #     return self.current + delta

    # def previous_month(self):
    #      # la date du mois avant celui qu'on affiche
    #     delta = timedelta(1)
    #     previous_month = self.current - delta
    #     return date(previous_month.year, previous_month.month, 1)

    # def next_year(self):
    #     current_date = date(self.year, 1, 1)
    #     # la date de l'année après celle qu'on affiche
    #     return date(current_date.year + 1, current_date.month,
    #                                                         current_date.day)

    # def previous_year(self):
    #     current_date = date(self.year, 1, 1)
    #     # la date de l'année avant celle qu'on affiche
    #     return date(current_date.year - 1, current_date.month,
    #                                                         current_date.day)


# TODO:  faire de ce mamouth un middleware ou un context processor
def get_time_pagination(year, duration,  duration_number):

    """
    navigation entre les dates année, mois, week

    """

    todays_date_is_before = False
    todays_date_is_after = False

    # la date à afficher
    todays_date = date.today()

    if duration == "month":

        current_date = date(year, duration_number, 1)

         # la date du mois avant celui qu'on affiche
        delta = timedelta(1)
        previous_date = current_date - delta
        previous_date = date(previous_date.year, previous_date.month, 1)

        # la date du mois après celui qu'on affiche
        days_count = monthrange(current_date.year, current_date.month)[1]
        delta = timedelta(days_count + 1)
        next_date = current_date + delta

        # Vérification que la semaine d'aujourd'hui est à afficher ou non
        if todays_date < previous_date:
            todays_date_is_before = True

        if todays_date > next_date:
            todays_date_is_after = True

        # l'adresse pour afficher le mois d'ajourd'hui
        todays_date_url = (todays_date.year, duration, todays_date.month)

        # l'adresse pour afficher le mois précédent
        previous_date_url = (previous_date.year, duration, previous_date.month)

        # l'adresse pour afficher le mois suivant
        next_date_url = (next_date.year, duration, next_date.month)

        # formatage de l'affichage des mois en tenant compte de la
        # language code

        current_date_ = current_date.strftime(u'%b %Y')
        previous_date_ = previous_date.strftime(u'%b %Y')
        next_date_ = next_date.strftime(u'%b %Y')
        todays_date = "This month"

    else:

        current_date = date(year, 1, 1)

         # la date de l'année avant celle qu'on affiche
        previous_date = date(current_date.year - 1,
                             current_date.month,
                             current_date.day)

        # la date de l'année après celle qu'on affiche
        next_date = date(current_date.year + 1, current_date.month,
                                                        current_date.day)

        # Vérification que l'année d'aujourd'hui est à afficher ou non
        if todays_date.year < (current_date.year - 1):
            todays_date_is_before = True

        if todays_date.year > (current_date.year + 1):
            todays_date_is_after = True

        # l'adresse pour afficher l'année d'aujourd'hui
        todays_date_url = todays_date.year

        # l'adresse pour afficher l'année précédent
        previous_date_url = previous_date.year

        # l'adresse pour afficher l'année suivant
        next_date_url = next_date.year

        # formatage de l'affichage des années
        current_date_ = current_date.strftime(u"%Y")
        previous_date_ = previous_date.strftime(u"%Y")
        next_date_ = next_date.strftime(u"%Y")
        todays_date = "This year"

    return (previous_date_url, todays_date_url, next_date_url, previous_date_,
            current_date_, next_date_, todays_date, todays_date_is_before,
            todays_date_is_after)
