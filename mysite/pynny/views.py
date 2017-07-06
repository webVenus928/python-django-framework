#!/usr/bin/python3
'''
File: views.py
Author: Zachary King
Created: 2017-06-29

Implements the views (endpoint handlers) for the Pynny web app.
'''

from django.http import HttpResponse
from django.shortcuts import render, reverse, redirect, get_object_or_404
from django.contrib.auth import logout
from datetime import date

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
    if not request.user.is_authenticated():
        # Not authenticated; send to login
        return redirect(reverse('login'))

    # GET = display user's wallets
    if request.method == 'GET':
        data = {}

        # Get the wallets for this user
        data['wallets'] = Wallet.objects.filter(user=request.user)

        return render(request, 'pynny/wallets.html', context=data)
    # POST = create a new Wallet
    elif request.method == 'POST':
        # Get the form data from the request
        name = request.POST['name']
        start_balance = 0
        start_balance = float(request.POST['balance'])

        # Check if the wallet name exists already
        if Wallet.objects.filter(user=request.user, name=name):
            data = {'alerts': {'errors': ['A wallet already exists with that name']}}
            return render(request, 'pynny/new_wallet.html', context=data)

        # Create the new Wallet
        Wallet(name=name, balance=start_balance, user=request.user).save()
        data = {'alerts': {'success': ['<strong>Done!</strong> New wallet created successfully!']}}
        data['wallets'] = Wallet.objects.filter(user=request.user)
        return render(request, 'pynny/wallets.html', context=data)



def new_wallet(request):
    '''Display form for creating a new wallet'''
    # Is user logged in?
    if not request.user.is_authenticated():
        return redirect(reverse('login'))

    return render(request, 'pynny/new_wallet.html')


def one_wallet(request, wallet_id):
    '''Handles requests to a specific wallet'''
    if not request.user.is_authenticated:
        return redirect(reverse('login'))

    data = {}

    # Check if the wallet is owned by the logged in user
    try:
        wallet = Wallet.objects.get(id=wallet_id)
    except:
        # DNE
        data['wallets'] = Wallet.objects.filter(user=request.user)
        data['alerts'] = {'errors': ['<strong>Oh snap!</strong> That wallet does not exist.']}
        return render(request, 'pynny/wallets.html', context=data)

    if wallet.user != request.user:
        data['wallets'] = Wallet.objects.filter(user=request.user)
        data['alerts'] = {'errors': ['<strong>Oh snap!</strong> That wallet does not exist.']}
        return render(request, 'pynny/wallets.html', context=data)

    if request.method == 'POST':
        # Delete the wallet
        wallet.delete()

        # And return them to the wallets page
        data['wallets'] = Wallet.objects.filter(user=request.user)
        data['alerts'] = {'info': ['<strong>Done!</strong> Your <em>' + wallet.name + '</em> wallet was successfully deleted']}
        return render(request, 'pynny/wallets.html', context=data)
    elif request.method == 'GET':
        # Show the specific Wallet data
        data['wallet'] = wallet
        data['budgets'] = Budget.objects.filter(wallet=wallet, month__contains=date.strftime(date.today(), '%Y-%m'))
        data['transactions'] = Transaction.objects.filter(wallet=wallet)
        return render(request, 'pynny/one_wallet.html', context=data)


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
    if not request.user.is_authenticated():
        # Not authenticated; send to login
        return redirect(reverse('login'))

    # GET = display user's categories
    if request.method == 'GET':
        data = {}

        # Get the wallets for this user
        data['categories'] = BudgetCategory.objects.filter(user=request.user)

        return render(request, 'pynny/categories.html', context=data)
    # POST = create a new BudgetCategory
    elif request.method == 'POST':
        # Get the form data from the request
        print(request.POST)
        name = request.POST['name']
        is_income = False
        if 'is_income' in request.POST:
            is_income = True

        # Check if the category name exists already
        if BudgetCategory.objects.filter(user=request.user, name=name):
            data = {'alerts': {'errors': ['<strong>Oops!</strong> A category already exists with that name']}}
            return render(request, 'pynny/new_category.html', context=data)

        # Create the new Wallet
        BudgetCategory(name=name, is_income=is_income, user=request.user).save()
        data = {'alerts': {'success': ['<strong>Done!</strong> New Category created successfully!']}}
        data['categories'] = BudgetCategory.objects.filter(user=request.user)
        return render(request, 'pynny/categories.html', context=data)

def new_category(request):
    '''Create a new BudgetCategory form'''
    # Is user logged in?
    if not request.user.is_authenticated():
        return redirect(reverse('login'))

    return render(request, 'pynny/new_category.html')


def one_category(request, category_id):
    '''View a specific BudgetCategory'''
    if not request.user.is_authenticated:
        return redirect(reverse('login'))

    data = {}

    # Check if the category is owned by the logged in user
    try:
        category = BudgetCategory.objects.get(id=category_id)
    except:
        # DNE
        data['categories'] = BudgetCategory.objects.filter(user=request.user)
        data['alerts'] = {'errors': ['<strong>Oh snap!</strong> That Category does not exist.']}
        return render(request, 'pynny/categories.html', context=data)

    if category.user != request.user:
        data['categories'] = BudgetCategory.objects.filter(user=request.user)
        data['alerts'] = {'errors': ['<strong>Oh snap!</strong> That Category does not exist.']}
        return render(request, 'pynny/categories.html', context=data)

    if request.method == "POST":
        print('Deleting...')
        # Delete the Category
        category.delete()

        # And return them to the categories page
        data['categories'] = BudgetCategory.objects.filter(user=request.user)
        data['alerts'] = {'info': ['<strong>Done!</strong> Your <em>' + category.name + '</em> Category was deleted successfully']}
        return render(request, 'pynny/categories.html', context=data)
    elif request.method == 'GET':
        # Show the specific Category data
        data['category'] = category
        data['budgets'] = Budget.objects.filter(category=category, month__contains=date.strftime(date.today(), '%Y-%m'))
        data['transactions'] = Transaction.objects.filter(category=category)
        return render(request, 'pynny/one_category.html', context=data)


def profile(request):
    '''Display a user profile'''
    # Is user logged in?
    if request.user.is_authenticated():
        data = {}
        return render(request, 'pynny/profile.html', context=data)

    # Not authenticated; send to login
    return redirect(reverse('login'))


def logout_view(request):
    '''Handlers user logout requests'''
    # Is user logged in?
    if not request.user.is_authenticated():
        # Not authenticated; send to login
        return redirect(reverse('login'))

    # User is logged in, so log them out
    logout(request)

    data = {
        'alerts': {
            'success': ['<strong>Done!</strong> You have been logged out successfully']
        }
    }
    return render(request, 'registration/login.html', context=data)
