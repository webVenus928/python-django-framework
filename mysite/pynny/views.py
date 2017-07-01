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
    # If user not logged in, show the landing page
    if not request.user.is_authenticated():
        return render(request, 'pynny/landing_page.html')

    # User is logged in, so retrieve their data and
    # show them their home page, displaying a dashboard
    data = {}
    return render(request, 'pynny/dashboard.html', context=data)


def wallets(request):
    '''Display Wallets for a user'''
    # Is user logged in?
    if request.user.is_authenticated():
        data = {}

        # Get the wallets for this user
        data['wallets'] = Wallet.objects.filter(user=request.user)

        return render(request, 'pynny/wallets.html', context=data)

    # Not authenticated; send to login
    return redirect(reverse('login'))


def budgets(request):
    '''Display Budgets for a user'''
    # Is user logged in?
    if request.user.is_authenticated():
        data = {}
        return render(request, 'pynny/budgets.html', context=data)

    # Not authenticated; send to login
    return redirect(reverse('login'))


def transactions(request):
    '''View transactions for a user'''
    # Is user logged in?
    if request.user.is_authenticated():
        data = {}
        return render(request, 'pynny/transactions.html', context=data)

    # Not authenticated; send to login
    return redirect(reverse('login'))


def budget_categories(request):
    '''View BudgetCategories for a user'''
    # Is user logged in?
    if request.user.is_authenticated():
        data = {}
        return render(request, 'pynny/categories.html', context=data)

    # Not authenticated; send to login
    return redirect(reverse('login'))


def profile(request):
    '''Display a user profile'''
    # Is user logged in?
    if request.user.is_authenticated():
        data = {}
        return render(request, 'pynny/profile.html', context=data)

    # Not authenticated; send to login
    return redirect(reverse('login'))
