#!/usr/bin/python3
'''
File: main_views.py
Author: Zachary King

Implements the main site views (endpoint handlers) for the Pynny web app.
'''

from django.shortcuts import render, reverse, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import  login_required

from datetime import date, datetime
from django.utils import timezone
import random

from ..models import Budget, Transaction, BudgetCategory, Notification


@login_required(login_url='/pynny/login')
def index(request):
    """The Home page for Pynny"""

    # User is logged in, so retrieve their data and
    # show them their home page, displaying a dashboard
    data = {}
    budgets = Budget.objects.filter(user=request.user, month__contains=date.strftime(date.today(), '%Y-%m'))
    colors = ['#ff4444', '#ffbb33', '#00C851', '#33b5e5', '#aa66cc', '#a1887f']
    random.shuffle(colors)
    color_index = 0
    data['budgets'] = budgets
    data['categories'] = BudgetCategory.objects.filter(user=request.user)
    data['transactions'] = Transaction.objects.filter(user=request.user, created_time__year=timezone.now().year, created_time__month=timezone.now().month)
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

    return render(request, 'pynny/base/dashboard.html', context=data)


@login_required(login_url='/pynny/login')
def logout_view(request):
    '''Handlers user logout requests'''

    # User is logged in, so log them out
    logout(request)

    data = {
        'alerts': {
            'success': ['<strong>Done!</strong> You have been logged out successfully']
        }
    }
    return render(request, 'registration/login.html', context=data)
