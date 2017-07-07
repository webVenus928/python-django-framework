#!/usr/bin/python3
'''
File: main_views.py
Author: Zachary King

Implements the main site views (endpoint handlers) for the Pynny web app.
'''

from django.shortcuts import render, reverse, redirect
from django.contrib.auth import logout


def index(request):
    '''The Home page for Pynny'''
    # If user not logged in, show the landing page
    if not request.user.is_authenticated():
        return render(request, 'pynny/landing_page.html')

    # User is logged in, so retrieve their data and
    # show them their home page, displaying a dashboard
    data = {}
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
