#!/usr/bin/env python3
'''
File: transaction_views.py
Author: Zachary King

Implements the views/handlers for Transaction-related requetss
'''

from datetime import date, datetime
from django.shortcuts import render, redirect, reverse
from django.contrib.auth.decorators import login_required
import decimal

from ..models import Transaction, BudgetCategory, Wallet, Budget


@login_required(login_url='/pynny/login')
def transactions(request):
    '''View transactions for a user'''
    data = {}
    if request.method == 'GET':
        data['transactions'] = Transaction.objects.filter(user=request.user).order_by('-created_time')
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

        # Update the balance of appropriate budgets
        budgets = Budget.objects.filter(category=category)
        amount = abs(_amount)

        for budget in budgets:
            budget.balance += decimal.Decimal(amount)
            budget.save()

        # Update the wallet balance
        if category.is_income:
            wallet.balance += decimal.Decimal(_amount)
        else:
            wallet.balance -= decimal.Decimal(_amount)
        wallet.save()

        # Render the transactions
        data = {'alerts': {'success': ['<strong>Done!</strong> New Transaction recorded successfully!']}}
        data['transactions'] = Transaction.objects.filter(user=request.user).order_by('-created_time')
        return render(request, 'pynny/transactions.html', context=data, status=201)


@login_required(login_url='/pynny/login')
def new_transaction(request):
    '''View for creating a new transaction'''
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


@login_required(login_url='/pynny/login')
def one_transaction(request, transaction_id):
    '''View for a single Transaction'''
    data = {}

    # Check if transaction is owned by user
    try:
        transaction = Transaction.objects.get(id=transaction_id)
    except Transaction.DoesNotExist:
        # DNE
        data['transactions'] = Transaction.objects.filter(user=request.user).order_by('-created_time')
        data['alerts'] = {'errors': ['<strong>Oh snap!</strong> That Transaction does not exist.']}
        return render(request, 'pynny/transactions.html', context=data)

    if transaction.user != request.user:
        data['transactions'] = Transaction.objects.filter(user=request.user).order_by('-created_time')
        data['alerts'] = {'errors': ['<strong>Oh snap!</strong> That Transaction does not exist.']}
        return render(request, 'pynny/transactions.html', context=data)

    if request.method == "POST":
        # What kind of POST was this?
        action = request.POST['action'].lower()
        if action == 'delete':
            # Update the balance of appropriate budgets
            budgets = Budget.objects.filter(category=transaction.category)
            amount = abs(transaction.amount)

            for budget in budgets:
                budget.balance -= decimal.Decimal(amount)
                budget.save()

            # Update Wallet
            if transaction.category.is_income:
                transaction.wallet.balance -= decimal.Decimal(transaction.amount)
            else:
                transaction.wallet.balance += decimal.Decimal(transaction.amount)
            transaction.wallet.save()

            # Delete the Transaction
            transaction.delete()

            # And return them to the Transactions page
            data['transactions'] = Transaction.objects.filter(user=request.user).order_by('-created_time')
            data['alerts'] = {'info': ['<strong>Done!</strong> Transaction was deleted successfully']}
            return render(request, 'pynny/transactions.html', context=data)
        elif action == 'edit':
            # Render the edit_transaction view
            data['transaction'] = transaction
            data['categories'] = BudgetCategory.objects.filter(user=request.user)
            data['wallets'] = Wallet.objects.filter(user=request.user)
            return render(request, 'pynny/edit_transaction.html', context=data)
        elif action == 'edit_complete':
            # Get the form data from the request
            _category = int(request.POST['category'])
            _wallet = int(request.POST['wallet'])
            _amount = float(request.POST['amount'])
            _description = request.POST['description']
            _created_time = request.POST['created_time'] # %Y-%m-%d date
            _created_time = datetime.strptime(_created_time, '%Y-%m-%d').date()

            new_category = BudgetCategory.objects.get(id=_category)

            # Undo the last version of the transaction
            print('balance before undo: ' + str(transaction.wallet.balance))
            undo_transaction(transaction)
            print('balance after undo: ' + str(transaction.wallet.balance))

            # Now carry out the effects of the revised transaction
            # Update the balance of appropriate budgets
            budgets = Budget.objects.filter(category=new_category)
            amount = abs(_amount)
            for budget in budgets:
                budget.balance += decimal.Decimal(amount)
                budget.save()

            # Update the wallet balance
            new_wallet = Wallet.objects.get(id=_wallet)
            print('balance before update: ' + str(new_wallet.balance))
            if new_category.is_income:
                new_wallet.balance += decimal.Decimal(_amount)
            else:
                new_wallet.balance -= decimal.Decimal(_amount)
            new_wallet.save()
            print('balance after update: ' + str(new_wallet.balance))

            # And update the transaction itself
            transaction.category = new_category
            transaction.wallet = new_wallet
            transaction.amount = _amount
            transaction.description = _description
            transaction.created_time = _created_time
            transaction.save()

            data = {'alerts': {'success': ['<strong>Done!</strong> Transaction updated successfully!']}}
            data['transactions'] = Transaction.objects.filter(user=request.user).order_by('-created_time')
            return render(request, 'pynny/transactions.html', context=data)
    elif request.method == 'GET':
        # Show the specific Transaction data
        data['transaction'] = transaction
        return render(request, 'pynny/one_transaction.html', context=data)


def undo_transaction(trans):
    '''Reverts the effects of a Transaction on budgets and its wallet'''
    amount = trans.amount
    
    # Replace the money in the category
    for budget in Budget.objects.filter(category=trans.category):
        budget.balance -= amount
        budget.save()
    
    # Replace the money in the wallet
    if trans.category.is_income:
        trans.wallet.balance -= trans.amount
    else:
        trans.wallet.balance += trans.amount
    trans.wallet.save()
