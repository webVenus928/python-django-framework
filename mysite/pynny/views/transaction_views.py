#!/usr/bin/env python3
'''
File: transaction_views.py
Author: Zachary King

Implements the views/handlers for Transaction-related requetss
'''

from datetime import date, datetime
from django.shortcuts import render, redirect, reverse

from ..models import Transaction, BudgetCategory, Wallet

def transactions(request):
    '''View transactions for a user'''
    # Is user logged in?
    if not request.user.is_authenticated():
        # Not authenticated; send to login
        return redirect(reverse('login'))

    data = {}
    if request.method == 'GET':
        data['transactions'] = Transaction.objects.filter(user=request.user)
        return render(request, 'pynny/transactions.html', context=data)
    # POST = create a new Transaction
    elif request.method == 'POST':
        # Get the form data from the request
        _category = int(request.POST['category'])
        _wallet = int(request.POST['wallet'])
        _amount = float(request.POST['amount'])
        _description = request.POST['description']
        _created_time = request.POST['created_time'] # %Y-%m-%d date
        _created_time = datetime.strptime(_created_time, '%Y-%m-%d').date()

        category = BudgetCategory.objects.get(id=_category)
        wallet = Wallet.objects.get(id=_wallet)

        # Create the new Transaction
        Transaction(category=category, wallet=wallet, amount=_amount, description=_description, created_time=_created_time, user=request.user).save()
        data = {'alerts': {'success': ['<strong>Done!</strong> New Transaction recorded successfully!']}}
        data['transactions'] = Transaction.objects.filter(user=request.user)
        return render(request, 'pynny/transactions.html', context=data)

    

def new_transaction(request):
    '''View for creating a new transaction'''
    if not request.user.is_authenticated():
        return redirect(reverse('login'))

    data = {}
    data['categories'] = BudgetCategory.objects.filter(user=request.user)
    data['wallets'] = Wallet.objects.filter(user=request.user)

    # Check if they have any categories or wallets first
    if not data['categories']:
        data = {
            'alerts': {
                'errors': [
                    '<strong>Oy!</strong> You don\'t have any Categories yet! You need to create a Category before you can record a Transaction!'
                ]
            },
        }
        return render(request, 'pynny/new_category.html', context=data)

    if not data['wallets']:
        data = {
            'alerts': {
                'errors': [
                    '<strong>Oy!</strong> You don\'t have any Wallets yet! You need to create a Wallet before you can record a Transaction!'
                ]
            },
        }
        return render(request, 'pynny/new_wallet.html', context=data)

    # They have a wallet and category so continue
    data['default_date'] = date.strftime(date.today(), '%Y-%m-%d')
    return render(request, 'pynny/new_transaction.html', context=data)

def one_transaction(request, transaction_id):
    '''View for a single Transaction'''
    if not request.user.is_authenticated():
        return redirect(reverse('login'))

    data = {}

    # Check if transaction is owned by user
    try:
        transaction = Transaction.objects.get(id=transaction_id)
    except Transaction.DoesNotExist:
        # DNE
        data['transactions'] = Transaction.objects.filter(user=request.user)
        data['alerts'] = {'errors': ['<strong>Oh snap!</strong> That Transaction does not exist.']}
        return render(request, 'pynny/transactions.html', context=data)

    if transaction.user != request.user:
        data['transactions'] = Transaction.objects.filter(user=request.user)
        data['alerts'] = {'errors': ['<strong>Oh snap!</strong> That Transaction does not exist.']}
        return render(request, 'pynny/transactions.html', context=data)

    if request.method == "POST":
        # Delete the Transaction
        transaction.delete()

        # And return them to the Transactions page
        data['transactions'] = Transaction.objects.filter(user=request.user)
        data['alerts'] = {'info': ['<strong>Done!</strong> Transaction was deleted successfully']}
        return render(request, 'pynny/transactions.html', context=data)
    elif request.method == 'GET':
        # Show the specific Transaction data
        data['transaction'] = transaction
        return render(request, 'pynny/one_transaction.html', context=data)
