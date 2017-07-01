#!/usr/bin/python3
'''
File: urls.py
Author: Zachary King
Created: 2017-06-29

Defines the URLs (endpoint routing) for 
the Pynny web app.
'''

from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'), # /
    url(r'^login/$', auth_views.login, name='login'), # /login/
    url(r'^logout/$', auth_views.logout, name='logout'), # /logout/
    url(r'^profile/$', views.profile, name='profile'), # /profile/
    url(r'^wallets/$', views.wallets, name='wallets'), # /zcking/wallets/
    url(r'^budgets/$', views.budgets, name='budgets'), # /zcking/budgets/
    url(r'^categories/$', views.budget_categories, name='categories'), # /zcking/categories/
    url(r'^transactions/$', views.transactions, name='transactions'), # /zcking/transactions/
]
