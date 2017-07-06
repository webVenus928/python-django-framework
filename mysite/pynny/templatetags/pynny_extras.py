#!/usr/bin/env python3
'''
File: template_filters.py
Author: Zachary King

Implements custom Django template filters to be used
in Django templates.
'''

from django.template.defaultfilters import register

from decimal import Decimal

@register.filter
def get_item(dictionary, key):
    '''Custom filter for getting a value from a dictionary
    inside a Django template. To use in a template:
    `{{ my_dict|get_item:item.NAME }}'''
    return dictionary.get(key)


@register.simple_tag
def budget_class(budget_balance, budget_goal):
    if budget_balance > budget_goal:
        return 'danger'
    elif budget_balance > (budget_goal * Decimal(0.8)):
        return 'warning'
    else:
        return 'success'

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
