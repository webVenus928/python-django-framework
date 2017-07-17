#!/usr/bin/python3
'''
File: main_views.py
Author: Zachary King

Implements the main site views (endpoint handlers) for the Pynny web app.
'''

from django.shortcuts import render, reverse, redirect
from django.contrib.auth import logout

from datetime import date
import random

from ..models import Budget, Transaction, BudgetCategory, Wallet


def index(request):
    '''The Home page for Pynny'''
    # If user not logged in, show the landing page
    if not request.user.is_authenticated():
        return render(request, 'pynny/landing_page.html')

    # User is logged in, so retrieve their data and
    # show them their home page, displaying a dashboard
    data = {}
    budgets = Budget.objects.filter(user=request.user, month=date.today())
    colors = ['#ff4444', '#ffbb33', '#00C851', '#33b5e5', '#aa66cc', '#a1887f']
    random.shuffle(colors)
    color_index = 0
    data['budget_categories'] = []
    data['budget_colors'] = []
    data['budget_goal_data'] = []
    data['budget_balance_data'] = []
    data['transactions_per_category_data'] = []
    data['transactions_per_category_colors'] = []
    data['transactions_per_category_labels'] = []
    data['current_month'] = date.today().strftime('%B, %Y')

    for budget in budgets:
        data['budget_categories'].append(budget.category.name)
        data['budget_goal_data'].append(budget.goal)
        data['budget_balance_data'].append(budget.balance)
        data['budget_colors'].append(colors[color_index])
        color_index = (color_index + 1) % len(colors)

    random.shuffle(colors)
    for category in BudgetCategory.objects.filter(user=request.user):
        data['transactions_per_category_labels'].append(category.name)
        data['transactions_per_category_data'].append(len(Transaction.objects.filter(category=category)))
        data['transactions_per_category_colors'].append(colors[color_index])
        color_index = (color_index + 1) % len(colors)

    return render(request, 'pynny/dashboard.html', context=data)


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
