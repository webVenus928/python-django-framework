#!/usr/bin/env python3
'''
File: wallet_views.py
Author: Zachary King

Implements views/handlers for Wallet-related requests
'''

from django.shortcuts import render, reverse, redirect
from datetime import date
from django.contrib.auth.decorators import login_required

from ..models import Wallet, Budget, Transaction


@login_required(login_url='/pynny/login')
def wallets(request):
    '''Display Wallets for a user'''
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
        return render(request, 'pynny/wallets.html', context=data, status=201)


@login_required(login_url='/pynny/login')
def new_wallet(request):
    '''Display form for creating a new wallet'''
    return render(request, 'pynny/new_wallet.html')


@login_required(login_url='/pynny/login')
def one_wallet(request, wallet_id):
    '''Handles requests to a specific wallet'''
    data = {}

    # Check if the wallet is owned by the logged in user
    try:
        wallet = Wallet.objects.get(id=wallet_id)
    except:
        # DNE
        data['wallets'] = Wallet.objects.filter(user=request.user)
        data['alerts'] = {'errors': ['<strong>Oh snap!</strong> That wallet does not exist.']}
        return render(request, 'pynny/wallets.html', context=data, status=404)

    if wallet.user != request.user:
        data['wallets'] = Wallet.objects.filter(user=request.user)
        data['alerts'] = {'errors': ['<strong>Oh snap!</strong> That wallet does not exist.']}
        return render(request, 'pynny/wallets.html', context=data, status=403)

    if request.method == 'POST':
        # What action?
        action = request.POST['action'].lower()

        if action == 'delete':
            # Delete the wallet
            wallet.delete()

            # And return them to the wallets page
            data['wallets'] = Wallet.objects.filter(user=request.user)
            data['alerts'] = {'info': ['<strong>Done!</strong> Your <em>' + wallet.name + '</em> wallet was successfully deleted']}
            return render(request, 'pynny/wallets.html', context=data)
        elif action == 'edit':
            # Render the edit_wallet view
            data['wallet'] = wallet
            return render(request, 'pynny/edit_wallet.html', context=data)
        elif action == 'edit_complete':
            # Get the form data from the request
            _name = request.POST['name']

            # Edit the Wallet
            wallet.name = _name
            wallet.save()

            data = {'alerts': {'success': ['<strong>Done!</strong> Wallet updated successfully!']}}
            data['wallets'] = Wallet.objects.filter(user=request.user)
            return render(request, 'pynny/wallets.html', context=data)
    elif request.method == 'GET':
        # Show the specific Wallet data
        data['wallet'] = wallet
        data['budgets'] = Budget.objects.filter(wallet=wallet, month__contains=date.strftime(date.today(), '%Y-%m'))
        data['transactions'] = Transaction.objects.filter(wallet=wallet).order_by('-created_time')
        return render(request, 'pynny/one_wallet.html', context=data)
