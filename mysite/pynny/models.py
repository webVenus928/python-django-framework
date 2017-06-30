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

class Wallet(models.Model):
    '''A source/destination for income and spending.
    For example, your checking account, credit card, or cash'''
    pass
