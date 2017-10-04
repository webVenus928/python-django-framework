#!/usr/bin/env python3
"""
File: savings_views.py
Author: Zachary King

Implements views/handlers for Savings-related requests
"""

from django.shortcuts import render, reverse, redirect
from datetime import date, datetime
from django.utils import timezone
from django.contrib.auth.decorators import login_required
import decimal

from ..models import Wallet, Budget, Transaction, Savings
from ..utils import notifications


@login_required(login_url='/pynny/login')
def savings(request):
    """Displays savings for a user"""
    # GET = display user's savings
    data = dict()
    if request.method == 'GET':
        # Get the savings for this user
        data['savings'] = Savings.objects.filter(user=request.user)

        return render(request, 'pynny/savings/savings.html', context=data)
    # POST = update a Saving
    elif request.method == 'POST':
        # Get the form data from the request
        name = request.POST['name']
        goal = float(request.POST['goal'])
        due_date = request.POST.get('due_date', '')
        if due_date:
            due_date = datetime.strptime(due_date, '%Y-%m-%d').date()
        notify = True if 'notify' in request.POST else False
        delete = True if 'delete' in request.POST else False

        # Check if the Saving name exists already
        if Savings.objects.filter(user=request.user, name=name):
            data['alerts'] = {'errors': ['A Saving already exists with that name']}
            data['savings'] = Savings.objects.filter(user=request.user)
            return render(request, 'pynny/savings/savings.html', context=data)

        # Create the new Saving
        Savings(name=name, goal=goal, balance=decimal.Decimal('0'),
                due_date=due_date if due_date else None,
                delete_on_completion=delete,
                notify_on_completion=notify, completed=False, hidden=False, user=request.user).save()

        data['alerts'] = {'success': ['<strong>Done!</strong> New Saving created successfully!']}
        if notify:
            data['alerts']['info'] = [
                '<strong>Nice!</strong> Since you asked to be notified, you\'ll receive an email when this Saving is fulfilled']
        data['savings'] = Savings.objects.filter(user=request.user)
        return render(request, 'pynny/savings/savings.html', context=data, status=201)


@login_required(login_url='/pynny/login')
def one_saving(request, savings_id):
    """Used for requests to a single saving (i.e. /savings/3)"""
    data = dict()
    # Authorize access to the saving
    try:
        saving = Savings.objects.get(id=savings_id)
    except Savings.DoesNotExist:
        data['alerts'] = {'errors': ['<strong>Oh Snap!</strong> That Saving does not exist']}
        data['savings'] = Savings.objects.filter(user=request.user)
        return render(request, 'pynny/savings/savings.html', context=data, status=404)

    if saving.user != request.user:
        data['savings'] = Savings.objects.filter(user=request.user)
        data['alerts'] = {'errors': ['<strong>Oh Snap!</strong> That Saving does not exist']}
        return render(request, 'pynny/savings/savings.html', context=data, status=403)

    if request.method == 'GET':
        pass
    elif request.method == 'POST':
        action = request.POST['action'].lower()

        if action == 'edit_complete':
            name = request.POST['name']
            goal = float(request.POST['goal'])
            due_date = request.POST.get('due_date', None)
            if due_date:
                due_date = datetime.strptime(due_date, '%Y-%m-%d').date()
            notify = True if 'notify' in request.POST else False
            delete = True if 'delete' in request.POST else False

            # Make sure the new name doesn't already exist
            if name != saving.name and Savings.objects.filter(user=request.user, name=name):
                data['alerts'] = {'errors': ['<strong>Oh Snap!</strong> A Saving already exists with that name']}
                data['savings'] = Savings.objects.filter(user=request.user)
                return render(request, 'pynny/savings/savings.html', context=data, status=200)

            # Data is fine, update the Saving
            saving.name = name
            saving.goal = goal
            saving.due_date = due_date
            saving.notify_on_completion = notify
            saving.delete_on_completion = delete
            if saving.goal <= saving.balance:
                complete_saving(saving)
                data['alerts'] = {'success': ['<strong>Congratulations!</strong> You met your Savings goal for "{}"'.format(saving.name)]}
                data['alerts']['success'].append('<strong>Done!</strong> Saving updated successfully')
            else:
                saving.save()

            data['savings'] = Savings.objects.filter(user=request.user)
            return render(request, 'pynny/savings/savings.html', context=data, status=200)

        elif action == 'delete':
            saving.delete()
            data['alerts'] = {'success': ['<strong>Done!</strong> Saving deleted successfully']}
            return render(request, 'pynny/savings/savings.html', context=data)


def complete_saving(saving):
    saving.completed = True
    saving.save()

    if saving.notify_on_completion:
        notifications.notify_saving_complete(saving)
    if saving.delete_on_completion:
        saving.delete()
