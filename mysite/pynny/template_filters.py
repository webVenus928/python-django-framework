#!/usr/bin/env python3
'''
File: template_filters.py
Author: Zachary King

Implements custom Django template filters to be used
in Django templates.
'''

from django.template.defaultfilters import register

@register.filter
def get_item(dictionary, key):
    '''Custom filter for getting a value from a dictionary
    inside a Django template. To use in a template:
    `{{ my_dict|get_item:item.NAME }}'''
    return dictionary.get(key)
