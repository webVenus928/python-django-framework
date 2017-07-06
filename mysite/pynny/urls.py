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
    url(r'^logout/$', views.logout_view, name='logout'), # /logout/
    url(r'^profile/$', views.profile, name='profile'), # /profile/
    url(r'^wallets/$', views.wallets, name='wallets'), # /wallets/
    url(r'^wallets/create/$', views.new_wallet, name='new_wallet'), # /wallets/create
    url(r'^wallets/(?P<wallet_id>[0-9]+)$', views.one_wallet, name='one_wallet',), # /wallets/3
    url(r'^budgets/$', views.budgets, name='budgets'), # /budgets/
    url(r'^categories/$', views.budget_categories, name='categories'), # /categories/
    url(r'^categories/create/$', views.new_category, name='new_category'), # /categories/create
    url(r'^categories/(?P<category_id>[0-9]+)$', views.one_category, name='one_category'), # /categories/5
    url(r'^transactions/$', views.transactions, name='transactions'), # /transactions/
]
