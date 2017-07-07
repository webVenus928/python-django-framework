#!/usr/bin/env python3
'''
File: transaction_views.py
Author: Zachary King

Implements the views/handlers for Transaction-related requetss
'''

from django.shortcuts import render, redirect, reverse

def transactions(request):
    '''View transactions for a user'''
    # Is user logged in?
    if request.user.is_authenticated():
        data = {}
        return render(request, 'pynny/transactions.html', context=data)

    # Not authenticated; send to login
    return redirect(reverse('login'))
