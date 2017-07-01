#!/usr/bin/python3
'''
File: views.py
Author: Zachary King
Created: 2017-06-29

Implements the views (endpoint handlers) for the Pynny web app.
'''

from django.http import HttpResponse
from django.shortcuts import render, reverse, redirect

from .models import Wallet, BudgetCategory, Transaction, Budget

def index(request):
    '''The Home page for Pynny'''
    if request.method == 'GET':
        return HttpResponse('Hi. Welcome to Pynny.')
    return HttpResponse('Eck!')


def wallets(request):
    '''Display Wallets for a user'''
    # Is user logged in?
    if request.user.is_authenticated():
        username = request.user.get_username()
        return HttpResponse('Viewing Wallets for ' + username + '...')

    # Not authenticated; send to login
    return redirect(reverse('login'))


def budgets(request):
    '''Display Budgets for a user'''
    # Is user logged in?
    if request.user.is_authenticated():
        username = request.user.get_username()
        return HttpResponse('Viewing Budgets for ' + username + '...')

    # Not authenticated; send to login
    return redirect(reverse('login'))


def transactions(request):
    '''View transactions for a user'''
    # Is user logged in?
    if request.user.is_authenticated():
        username = request.user.get_username()
        return HttpResponse('Viewing Transactions for ' + username + '...')

    # Not authenticated; send to login
    return redirect(reverse('login'))


def budget_categories(request):
    '''View BudgetCategories for a user'''
    # Is user logged in?
    if request.user.is_authenticated():
        username = request.user.get_username()
        return HttpResponse('Viewing Budget Categories for ' + username + '...')

    # Not authenticated; send to login
    return redirect(reverse('login'))


def profile(request):
    '''Display a user profile'''
    # Is user logged in?
    if request.user.is_authenticated():
        username = request.user.get_username()
        return HttpResponse('Viewing profile for ' + username)

    # Not authenticated; send to login
    return redirect(reverse('login'))
