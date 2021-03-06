#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from django.utils.encoding import python_2_unicode_compatible

@python_2_unicode_compatible
class BankAccount(models.Model):
    user = models.ForeignKey(User)
    description = models.CharField(max_length=256, blank=True, null=True)
    btc_address = models.CharField(max_length=1024, blank=True, null=True)

    def __str__(self):
        if self.description and self.btc_address:
            return '{} ({})'.format(self.description, self.btc_address)
        elif not self.description and self.btc_address:
            return self.btc_address
        elif self.description and not self.btc_address:
            return self.description
        else:
            return _('Unnamed account')


class Activity(models.Model):
    CURRENCY_EUR = (0, _('EUR'))
    CURRENCY_USD = (1, _('USD'))
    CURRENCY_BITCOIN = (2, _('BTC'))

    CURRENCIES = (
        CURRENCY_EUR,
        CURRENCY_USD,
        CURRENCY_BITCOIN
    )

    user = models.ForeignKey(User, null=True, blank=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    currency = models.IntegerField(choices=CURRENCIES)
    goal = models.DecimalField(max_digits=10, decimal_places=8)
    pledge_value = models.DecimalField(max_digits=10, decimal_places=8)
    min_people = models.IntegerField()
    max_people = models.IntegerField(blank=True, null=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    target_account = models.ForeignKey('BankAccount', null=True)

    completed = models.BooleanField(default=False)

    @property
    def days_left(self):
        now = timezone.now()
        if now >= self.end_date:
            return 0

        delta = self.end_date - now
        return delta.days

    def get_number_of_participants(self):
        return Transaction.objects.filter(state=Transaction.STATE_PAYMENT_CONFIRMED).count()

    def get_total_pledge_amount(self):
        return Transaction.objects.filter(activity=self,
            state=Transaction.STATE_PAYMENT_CONFIRMED).aggregate(Sum('amount'))['amount__sum']


class Transaction(models.Model):
    STATE_ABORTED = -1
    STATE_PLEDGED = 0
    STATE_PAYMENT_RECEIVED = 1
    STATE_PAYMENT_CONFIRMED = 2

    STATES = (
        (STATE_PLEDGED, _("pledged")),
        (STATE_PAYMENT_RECEIVED, _('payment received')),
        (STATE_PAYMENT_CONFIRMED, _('payment confirmed'))
    )
    amount = models.DecimalField(max_digits=10, decimal_places=8, null=True)
    activity = models.ForeignKey('Activity')
    state = models.IntegerField(choices=STATES)

    btc_address = models.CharField(max_length=1024, blank=True, null=True)
    return_btc_address = models.CharField(max_length=1024, blank=True, null=True)

    email = models.EmailField(max_length=1024, blank=True, null=True)