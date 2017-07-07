#!/usr/bin/env python3
'''
File: budget_views.py
Author: Zachary King

Implements the views/handlers for Budget-related requests
'''

from django.shortcuts import render, redirect, reverse

from ..models import Budget, BudgetCategory, Wallet

def budgets(request):
    '''Display Budgets for a user'''
    # Is user logged in?
    if not request.user.is_authenticated():
        # Not authenticated; send to login
        return redirect(reverse('login'))

    # GET = display user's budgets
    if request.method == 'GET':
        data = {}

        # Get the wallets for this user
        data['budgets'] = Budget.objects.filter(user=request.user)

        return render(request, 'pynny/budgets.html', context=data)
    # POST = create a new Budget
    elif request.method == 'POST':
        # Get the form data from the request
        _category = int(request.POST['category'])
        _goal = float(request.POST['goal'])
        _start_balance = float(request.POST['start_balance'])
        _wallet = int(request.POST['wallet'])

        category = BudgetCategory.objects.get(id=_category)
        wallet = Wallet.objects.get(id=_wallet)

        # Check if the budget already exists
        if Budget.objects.filter(user=request.user, category=category, wallet=wallet):
            data = {'alerts': {'errors': ['<strong>Oops!</strong> A Budget already exists for that Wallet and Category']}}
            return render(request, 'pynny/new_budget.html', context=data)

        # Create the new Budget
        Budget(category=category, wallet=wallet, goal=_goal, balance=_start_balance, user=request.user).save()
        data = {'alerts': {'success': ['<strong>Done!</strong> New Budget created successfully!']}}
        data['budgets'] = Budget.objects.filter(user=request.user)
        return render(request, 'pynny/budgets.html', context=data)

def new_budget(request):
    '''Create a new Budget form'''
    # Is user logged in?
    if not request.user.is_authenticated():
        return redirect(reverse('login'))

    # Get the categories
    data = {}
    data['categories'] = BudgetCategory.objects.filter(user=request.user)
    data['wallets'] = Wallet.objects.filter(user=request.user)

    return render(request, 'pynny/new_budget.html', context=data)


def one_budget(request, budget_id):
    '''View a specific Budget'''
    if not request.user.is_authenticated:
        return redirect(reverse('login'))

    data = {}

    # Check if the budget is owned by the logged in user
    try:
        budget = Budget.objects.get(id=budget_id)
    except Budget.DoesNotExist:
        # DNE
        data['budgets'] = Budget.objects.filter(user=request.user)
        data['alerts'] = {'errors': ['<strong>Oh snap!</strong> That Budget does not exist.']}
        return render(request, 'pynny/budgets.html', context=data)

    if budget.user != request.user:
        data['budgets'] = Budget.objects.filter(user=request.user)
        data['alerts'] = {'errors': ['<strong>Oh snap!</strong> That Budget does not exist.']}
        return render(request, 'pynny/budgets.html', context=data)

    if request.method == "POST":
        # Delete the Budget
        budget.delete()

        # And return them to the categories page
        data['budgets'] = Budget.objects.filter(user=request.user)
        data['alerts'] = {'info': ['<strong>Done!</strong> Budget was deleted successfully']}
        return render(request, 'pynny/budgets.html', context=data)
    elif request.method == 'GET':
        # Show the specific Budget data
        data['budget'] = budget
        return render(request, 'pynny/one_budget.html', context=data)
