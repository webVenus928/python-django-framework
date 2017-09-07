#!/usr/bin/env python3
'''
File: category_views.py
Author: Zachary King

Implements the views/handlers for BudgetCategory-related requests
'''

from django.shortcuts import redirect, render, reverse
from django.contrib.auth.decorators import login_required
from datetime import date

from ..models import BudgetCategory, Budget, Transaction


@login_required(login_url='/pynny/login')
def budget_categories(request):
    """View BudgetCategories for a user"""

    # GET = display user's categories
    if request.method == 'GET':
        data = {}

        # Get the wallets for this user
        data['categories'] = BudgetCategory.objects.filter(user=request.user)

        return render(request, 'pynny/categories.html', context=data)
    # POST = create a new BudgetCategory
    elif request.method == 'POST':
        # Get the form data from the request
        name = request.POST['name']
        is_income = False
        if 'is_income' in request.POST:
            is_income = True

        # Check if the category name exists already
        if BudgetCategory.objects.filter(user=request.user, name=name):
            data = {'alerts': {'errors': ['<strong>Oops!</strong> A category already exists with that name']}}
            return render(request, 'pynny/new_category.html', context=data, status=409)

        # Create the new BudgetCategory
        BudgetCategory(name=name, is_income=is_income, user=request.user).save()
        data = {'alerts': {'success': ['<strong>Done!</strong> New Category created successfully!']}}
        data['categories'] = BudgetCategory.objects.filter(user=request.user)
        return render(request, 'pynny/categories.html', context=data, status=201)


@login_required(login_url='/pynny/login')
def new_category(request):
    '''Create a new BudgetCategory form'''

    return render(request, 'pynny/new_category.html')


@login_required(login_url='/pynny/login')
def one_category(request, category_id):
    '''View a specific BudgetCategory'''
    data = {}

    # Check if the category is owned by the logged in user
    try:
        category = BudgetCategory.objects.get(id=category_id)
    except BudgetCategory.DoesNotExist:
        # DNE
        data['categories'] = BudgetCategory.objects.filter(user=request.user)
        data['alerts'] = {'errors': ['<strong>Oh snap!</strong> That Category does not exist.']}
        return render(request, 'pynny/categories.html', context=data)

    if category.user != request.user:
        data['categories'] = BudgetCategory.objects.filter(user=request.user)
        data['alerts'] = {'errors': ['<strong>Oh snap!</strong> That Category does not exist.']}
        return render(request, 'pynny/categories.html', context=data)

    if request.method == "POST":
        # What kind of action?
        action = request.POST['action'].lower()

        if action == 'delete':
            # Delete the Category
            category.delete()

            # And return them to the categories page
            data['categories'] = BudgetCategory.objects.filter(user=request.user)
            data['alerts'] = {'info': ['<strong>Done!</strong> Your <em>' + category.name + '</em> Category was deleted successfully']}
            return render(request, 'pynny/categories.html', context=data)
        elif action == 'edit':
            # Render the edit_category view
            data['category'] = category
            return render(request, 'pynny/edit_category.html', context=data)
        elif action == 'edit_complete':
            # Get the form data from the request
            _name = request.POST['name']
            _is_income = False
            if 'is_income' in request.POST:
                _is_income = True

            # Edit the Category
            category.name = _name
            category.is_income = _is_income
            category.save()

            data = {'alerts': {'success': ['<strong>Done!</strong> Category updated successfully!']}}
            data['categories'] = BudgetCategory.objects.filter(user=request.user)
            return render(request, 'pynny/categories.html', context=data)
    elif request.method == 'GET':
        # Show the specific Category data
        data['category'] = category
        data['budgets'] = Budget.objects.filter(category=category, month__contains=date.strftime(date.today(), '%Y-%m'))
        data['transactions'] = Transaction.objects.filter(category=category).order_by('-created_time')
        return render(request, 'pynny/one_category.html', context=data)
