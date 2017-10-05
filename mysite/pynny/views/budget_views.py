#!/usr/bin/env python3
'''
File: budget_views.py
Author: Zachary King

Implements the views/handlers for Budget-related requests
'''

from django.shortcuts import render, redirect, reverse
from django.contrib.auth.decorators import login_required
import decimal
from datetime import date

from ..models import Budget, BudgetCategory, Wallet, Transaction


@login_required(login_url='/pynny/login')
def renew_budgets(request):
    if request.user.is_authenticated():
        all_budgets = Budget.objects.filter(user=request.user)
        renewed = set()
        today = date.today()
        last_month = date(today.year, today.month - 1 if today.month > 1 else 12, today.day)
        last_month_budgets = Budget.objects.filter(user=request.user,
                                                           month__contains=date.strftime(last_month, '%Y-%m'))
        for budget in last_month_budgets:
            if budget.budget_id not in renewed:
                renewed_budget = Budget.objects.get(pk=budget.pk)
                renewed_budget.pk = None
                renewed_budget.month = date.today()
                renewed_budget.balance = decimal.Decimal('0')
                renewed_budget.save()
                renewed.add(budget.budget_id)
    return budgets(request)


@login_required(login_url='/pynny/login')
def budgets(request):
    '''Display Budgets for a user'''
    # GET = display user's budgets
    if request.method == 'GET':
        data = {}

        # Get the wallets for this user
        data['budgets'] = Budget.objects.filter(user=request.user, month__contains=date.strftime(date.today(), '%Y-%m'))
        today = date.today()
        last_month = date(today.year, today.month - 1 if today.month > 1 else 12, today.day)
        data['last_month_budgets'] = Budget.objects.filter(user=request.user, month__contains=date.strftime(last_month, '%Y-%m'))
        data['categories'] = BudgetCategory.objects.filter(user=request.user)
        data['wallets'] = Wallet.objects.filter(user=request.user)

        return render(request, 'pynny/budgets/budgets.html', context=data)
    # POST = create a new Budget
    elif request.method == 'POST':
        # Get the form data from the request
        _category = int(request.POST['category'])
        _goal = float(request.POST['goal'])
        _start_balance = decimal.Decimal(0.0)
        _wallet = int(request.POST['wallet'])

        category = BudgetCategory.objects.get(id=_category)
        wallet = Wallet.objects.get(id=_wallet)

        # Calculate the starting balance
        for transaction in Transaction.objects.filter(category=category):
            _start_balance += transaction.amount

        # Check if the budget already exists
        if Budget.objects.filter(user=request.user, category=category, wallet=wallet, month__contains=date.strftime(date.today(), '%Y-%m')):
            data = {'alerts': {'errors': ['<strong>Oops!</strong> A Budget already exists for that Wallet and Category, for this month']}}
            today = date.today()
            last_month = date(today.year, today.month - 1 if today.month > 1 else 12, today.day)
            data['last_month_budgets'] = Budget.objects.filter(user=request.user,
                                                               month__contains=date.strftime(last_month, '%Y-%m'))
            data['budgets'] = Budget.objects.filter(user=request.user,
                                                    month__contains=date.strftime(date.today(), '%Y-%m'))
            return render(request, 'pynny/budgets/new_budget.html', context=data)

        # Create the new Budget
        try:
            latest_budget = Budget.objects.latest('budget_id')
        except Budget.DoesNotExist:
            latest_budget = None

        new_id = latest_budget.budget_id + 1 if latest_budget is not None else 0
        Budget(category=category, wallet=wallet, goal=_goal, balance=_start_balance, user=request.user, budget_id=new_id).save()
        data = {'alerts': {'success': ['<strong>Done!</strong> New Budget created successfully!']}}
        data['budgets'] = Budget.objects.filter(user=request.user, month__contains=date.strftime(date.today(), '%Y-%m'))
        today = date.today()
        last_month = date(today.year, today.month - 1 if today.month > 1 else 12, today.day)
        data['last_month_budgets'] = Budget.objects.filter(user=request.user,
                                                           month__contains=date.strftime(last_month, '%Y-%m'))
        data['categories'] = BudgetCategory.objects.filter(user=request.user)
        data['wallets'] = Wallet.objects.filter(user=request.user)
        return render(request, 'pynny/budgets/budgets.html', context=data, status=201)


@login_required(login_url='/pynny/login')
def new_budget(request):
    '''Create a new Budget form'''
    # Get the categories
    data = {}
    data['categories'] = BudgetCategory.objects.filter(user=request.user)
    data['wallets'] = Wallet.objects.filter(user=request.user)
    today = date.today()
    last_month = date(today.year, today.month - 1 if today.month > 1 else 12, today.day)
    data['last_month_budgets'] = Budget.objects.filter(user=request.user,
                                                       month__contains=date.strftime(last_month, '%Y-%m'))

    # Check if they have any categories or wallets first
    if not data['categories']:
        data = {
            'alerts': {
                'errors': [
                    '<strong>Oy!</strong> You don\'t have any Categories yet! You need to create a Category before you can create a Budget!'
                ]
            },
        }
        return render(request, 'pynny/categories/new_category.html', context=data)

    if not data['wallets']:
        data = {
            'alerts': {
                'errors': [
                    '<strong>Oy!</strong> You don\'t have any Wallets yet! You need to create a Wallet before you can create a Budget!'
                ]
            },
        }
        return render(request, 'pynny/wallets/new_wallet.html', context=data)

    # They have a wallet and category so continue
    return render(request, 'pynny/budgets/new_budget.html', context=data)


@login_required(login_url='/pynny/login')
def one_budget(request, budget_id):
    '''View a specific Budget'''
    data = {}

    # Check if the budget is owned by the logged in user
    try:
        budget = Budget.objects.get(id=budget_id)
    except Budget.DoesNotExist:
        # DNE
        data['budgets'] = Budget.objects.filter(user=request.user, month__contains=date.strftime(date.today(), '%Y-%m'))
        data['categories'] = BudgetCategory.objects.filter(user=request.user)
        today = date.today()
        last_month = date(today.year, today.month - 1 if today.month > 1 else 12, today.day)
        data['last_month_budgets'] = Budget.objects.filter(user=request.user,
                                                           month__contains=date.strftime(last_month, '%Y-%m'))
        data['wallets'] = Wallet.objects.filter(user=request.user)
        data['alerts'] = {'errors': ['<strong>Oh snap!</strong> That Budget does not exist.']}
        return render(request, 'pynny/budgets/budgets.html', context=data, status=404)

    if budget.user != request.user:
        data['budgets'] = Budget.objects.filter(user=request.user, month__contains=date.strftime(date.today(), '%Y-%m'))
        today = date.today()
        last_month = date(today.year, today.month - 1 if today.month > 1 else 12, today.day)
        data['last_month_budgets'] = Budget.objects.filter(user=request.user,
                                                           month__contains=date.strftime(last_month, '%Y-%m'))
        data['categories'] = BudgetCategory.objects.filter(user=request.user)
        data['wallets'] = Wallet.objects.filter(user=request.user)
        data['alerts'] = {'errors': ['<strong>Oh snap!</strong> That Budget isn\'t yours! You don\'t have permission to view it']}
        return render(request, 'pynny/budgets/budgets.html', context=data, status=403)

    if request.method == "POST":
        # What kind of action?
        action = request.POST['action'].lower()

        if action == 'delete':
            # Delete the Budget
            budget.delete()

            # And return them to the budgets page
            data['budgets'] = Budget.objects.filter(user=request.user, month__contains=date.strftime(date.today(), '%Y-%m'))
            data['categories'] = BudgetCategory.objects.filter(user=request.user)
            today = date.today()
            last_month = date(today.year, today.month - 1 if today.month > 1 else 12, today.day)
            data['last_month_budgets'] = Budget.objects.filter(user=request.user,
                                                               month__contains=date.strftime(last_month, '%Y-%m'))
            data['wallets'] = Wallet.objects.filter(user=request.user)
            data['alerts'] = {'success': ['<strong>Done!</strong> Budget was deleted successfully']}
            return render(request, 'pynny/budgets/budgets.html', context=data)
        elif action == 'edit':
            # Render the edit_budget view
            data['budget'] = budget
            today = date.today()
            last_month = date(today.year, today.month - 1 if today.month > 1 else 12, today.day)
            data['last_month_budgets'] = Budget.objects.filter(user=request.user,
                                                               month__contains=date.strftime(last_month, '%Y-%m'))
            data['categories'] = BudgetCategory.objects.filter(user=request.user)
            data['wallets'] = Wallet.objects.filter(user=request.user)
            return render(request, 'pynny/budgets/edit_budget.html', context=data)
        elif action == 'edit_complete':
            # Get the form data from the request
            _category = int(request.POST['category'])
            _wallet = int(request.POST['wallet'])
            _goal = float(request.POST['goal'])

            category = BudgetCategory.objects.get(id=_category)
            wallet = Wallet.objects.get(id=_wallet)

            # Edit the Budget
            budget.category = category
            budget.wallet = wallet
            budget.goal = _goal
            budget.save()

            data = {'alerts': {'success': ['<strong>Done!</strong> Budget updated successfully!']}}
            today = date.today()
            last_month = date(today.year, today.month - 1 if today.month > 1 else 12, today.day)
            data['last_month_budgets'] = Budget.objects.filter(user=request.user,
                                                               month__contains=date.strftime(last_month, '%Y-%m'))
            data['categories'] = BudgetCategory.objects.filter(user=request.user)
            data['wallets'] = Wallet.objects.filter(user=request.user)
            data['budgets'] = Budget.objects.filter(user=request.user, month__contains=date.strftime(date.today(), '%Y-%m'))
            return render(request, 'pynny/budgets/budgets.html', context=data)
    elif request.method == 'GET':
        # Show the specific Budget data
        data['budget'] = budget
        today = date.today()
        last_month = date(today.year, today.month - 1 if today.month > 1 else 12, today.day)
        data['last_month_budgets'] = Budget.objects.filter(user=request.user,
                                                           month__contains=date.strftime(last_month, '%Y-%m'))
        data['categories'] = BudgetCategory.objects.filter(user=request.user)
        data['wallets'] = Wallet.objects.filter(user=request.user)
        data['transactions'] = Transaction.objects.filter(category=budget.category).order_by('-created_time')
        return render(request, 'pynny/budgets/one_budget.html', context=data)
