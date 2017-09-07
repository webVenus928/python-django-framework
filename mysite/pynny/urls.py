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

from .views import wallet_views, budget_views, category_views, transaction_views, main_views

urlpatterns = [
    url(r'^$', main_views.index, name='index'), # /
    url(r'^login/$', auth_views.login, name='login'), # /login/
    url(r'^logout/$', main_views.logout_view, name='logout'), # /logout/
    url(r'^wallets/$', wallet_views.wallets, name='wallets'), # /wallets/
    url(r'^wallets/create/$', wallet_views.new_wallet, name='new_wallet'), # /wallets/create
    url(r'^wallets/(?P<wallet_id>[0-9]+)$', wallet_views.one_wallet, name='one_wallet',), # /wallets/3
    url(r'^budgets/$', budget_views.budgets, name='budgets'), # /budgets/
    url(r'^budgets/create/$', budget_views.new_budget, name='new_budget'), # /budgets/create
    url(r'^budgets/(?P<budget_id>[0-9]+)$', budget_views.one_budget, name='one_budget'), # /budgets/9
    url(r'^categories/$', category_views.budget_categories, name='categories'), # /categories/
    url(r'^categories/create/$', category_views.new_category, name='new_category'), # /categories/create
    url(r'^categories/(?P<category_id>[0-9]+)$', category_views.one_category, name='one_category'), # /categories/5
    url(r'^transactions/$', transaction_views.transactions, name='transactions'), # /transactions/
    url(r'^transactions/(?P<transaction_id>[0-9]+)$', transaction_views.one_transaction, name='one_transaction'), # /transactions/9
    url(r'^transactions/create/$', transaction_views.new_transaction, name='new_transaction'), # /transactions/create
    url(r'^budgets/renew/$', budget_views.renew_budgets, name='renew_budgets'),  # /budgets/renew
]
