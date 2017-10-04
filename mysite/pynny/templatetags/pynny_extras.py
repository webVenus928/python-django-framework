#!/usr/bin/env python3
'''
File: template_filters.py
Author: Zachary King

Implements custom Django template filters to be used
in Django templates.
'''

from django.template.defaultfilters import register
from datetime import date, datetime

from decimal import Decimal


@register.simple_tag
def saving_class(saving):
    ratio = (saving.balance / saving.goal) * Decimal('100')
    if ratio < Decimal('25'):
        return 'danger'
    elif ratio < Decimal('50'):
        return 'warning'
    elif ratio < Decimal('75'):
        return 'info'
    return 'success'


@register.simple_tag
def saving_prg_bar_width(saving):
    return Decimal('100') * (saving.balance / saving.goal)


@register.filter
def get_item(dictionary, key):
    '''Custom filter for getting a value from a dictionary
    inside a Django template. To use in a template:
    `{{ my_dict|get_item:item.NAME }}'''
    return dictionary.get(key)

@register.simple_tag
def wallet_class(balance):
    if balance > 0:
        return 'success'
    elif balance < 0:
        return 'danger'
    return 'default'

@register.simple_tag
def category_class(is_income):
    if is_income:
        return 'success'
    return 'danger'

@register.simple_tag
def budget_class(budget):
    goal = budget.goal
    bal = budget.balance
    if budget.category.is_income:
        if bal >= goal:
            return 'success'
        elif bal >= (goal * Decimal(0.8)):
            return 'warning'
        return 'danger'

    if bal >= goal:
        return 'danger'
    elif bal >= (goal * Decimal(0.8)):
        return 'warning'
    return 'success'

@register.simple_tag
def get_month(d):
    return date.strftime(d, '%B, %Y')

@register.simple_tag
def fmt_time(t):
    return datetime.strftime(t, '%Y-%m-%d')

@register.simple_tag
def transaction_class(transaction):
    '''Returns a Bootstrap class string for a Transaction'''
    if transaction.amount == 0:
        return 'default'

    is_income = transaction.category.is_income
    if is_income:
        if transaction.amount >= 0:
            return 'success'
        return 'danger'
    else:
        if transaction.amount >= 0:
            return 'danger'
        return 'success'


@register.simple_tag
def shorten_string(string, limit):
    '''Returns the string, shortened to limit chars and with '...' appended'''
    if len(string) <= limit:
        return string
    return string[:limit-3] + '...'
