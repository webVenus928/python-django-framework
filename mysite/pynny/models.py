#!/usr/bin/env python3
'''
File: models.py
Author: Zachary King
Created: 2017-06-29

Implements the models for the Pynny web app.
Django usese these models to automatically create
the necessary tables in the database.
'''

from django.db import models
from django.utils import timezone
from datetime import date
from django.contrib import auth
from django.utils.encoding import python_2_unicode_compatible

@python_2_unicode_compatible
class Wallet(models.Model):
    '''A source/destination for income and spending.
    For example, your checking account, credit card, or cash.
    `balance` uses the Python `decimal.Decimal` class.
    `created_time` is a `datetime.datetime` timestamp for
    when the Wallet was created. `created_time` defaults
    to the current timestamp.'''
    name = models.CharField(max_length=60)
    balance = models.DecimalField(max_digits=20, decimal_places=2, default=0, blank=True)
    created_time = models.DateTimeField(editable=False, blank=True, default=timezone.now)
    user = models.ForeignKey(auth.get_user_model(), on_delete=models.CASCADE)

    def __str__(self):
        '''Returns the string representation (`name`)'''
        return self.name


@python_2_unicode_compatible
class BudgetCategory(models.Model):
    '''A category to tag transactions and budgets with.
    The `is_income` field determines if the category
    denotes income or expenses. By default
    `is_income` is False.'''
    name = models.CharField(max_length=60)
    is_income = models.BooleanField(default=False)
    user = models.ForeignKey(auth.get_user_model(), on_delete=models.CASCADE)

    def __str__(self):
        '''Returns the string representation (`name`)'''
        return self.name


@python_2_unicode_compatible
class Transaction(models.Model):
    '''A record of income or an expense. `amount`
    uses the Python `decimal.Decimal` class.
    `category` refers to a BudgetCategory; this category
    determines whether the transaction was an expense or not.
    `description` is an optional human-readable description
    of the transaction (i.e. groceries @ Krogers).
    `created_time` is a `datetime.datetime` instance
    and defaults to the current timestamp.'''
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    category = models.ForeignKey(BudgetCategory, on_delete=models.CASCADE)
    description = models.CharField(max_length=150, blank=True, default='')
    created_time = models.DateField(blank=True, default=date.today)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    user = models.ForeignKey(auth.get_user_model(), on_delete=models.CASCADE)

    def __str__(self):
        '''Returns the string representation (`name`)'''
        return self.category.name


@python_2_unicode_compatible
class Budget(models.Model):
    '''A user-created budget that is applied to a
    particular Wallet. The Budget is categorized by
    a Category with `category`. `goal` is the user-defined
    goal for the budget, which is monthly-based.
    `month` is a `datetime.date` instance indicating what
    month the Budget applies to. `wallet` refers to the
    Wallet this Budget applies to.'''
    budget_id = models.PositiveIntegerField()
    category = models.ForeignKey(BudgetCategory, on_delete=models.CASCADE)
    goal = models.DecimalField(max_digits=20, decimal_places=2)
    month = models.DateField(default=date.today, blank=True)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=20, decimal_places=2, blank=True, default=0.0)
    user = models.ForeignKey(auth.get_user_model(), on_delete=models.CASCADE)

    def __str__(self):
        '''Returns the string representation (`name`)'''
        return self.category.name


@python_2_unicode_compatible
class Savings(models.Model):
    """Represents a users's savings towards some goal. For example, a car."""
    goal = models.DecimalField(max_digits=20, decimal_places=2, blank=False)
    balance = models.DecimalField(max_digits=20, decimal_places=2, default=0.0, blank=False)
    delete_on_completion = models.BooleanField(default=True, blank=False)
    name = models.CharField(max_length=100, blank=False)
    created_time = models.DateTimeField(editable=False, blank=True, default=timezone.now)
    due_date = models.DateField(blank=True)
    notify_on_completion = models.BooleanField(default=False, blank=False)
    completed = models.BooleanField(default=False, blank=True)
    hidden = models.BooleanField(default=False, blank=True)
    user = models.ForeignKey(auth.get_user_model(), on_delete=models.CASCADE)

    def __str__(self):
        """Returns the name of the savings object"""
        return self.name

@python_2_unicode_compatible
class Notification(models.Model):
    """A site-level notification"""
    type = models.CharField(max_length=40, blank=False)
    title = models.CharField(max_length=100, blank=False)
    body = models.TextField(blank=False)
    created_time = models.DateTimeField(editable=False, blank=True, default=timezone.now)
    alert = models.CharField(max_length=10, blank=True)
    dismissed = models.BooleanField(default=False)
    dismissed_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(auth.get_user_model(), on_delete=models.CASCADE)

    def __str__(self):
        """Returns the title of the notification"""
        return self.title
