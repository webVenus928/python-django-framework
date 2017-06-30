#!/usr/bin/python3
'''
File: views.py
Author: Zachary King
Created: 2017-06-29

Implements the views (endpoint handlers) for the Pynny web app.
'''

from django.http import HttpResponse

def index(request):
    '''The Home page for Pynny'''
    if request.method == 'GET':
        return HttpResponse('Hi. Welcome to Pynny.')
    return HttpResponse('Eck!')
