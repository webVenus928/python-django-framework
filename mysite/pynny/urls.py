#!/usr/bin/python3
'''
File: urls.py
Author: Zachary King
Created: 2017-06-29

Defines the URLs (endpoint routing) for 
the Pynny web app.
'''

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'), # /
]
