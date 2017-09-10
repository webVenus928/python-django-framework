from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone

import datetime

from .models import Budget, BudgetCategory, Wallet, Transaction


class ModelStrTests(TestCase):
    def setUp(self):
        # Create a user and give them some data to test with
        self.user = User.objects.create_user(id=1, username='test_user', email='test_user@gmail.com', password='tester123')
        self.user.save()

        self.category = BudgetCategory.objects.create(id=1, user_id=1, user=self.user, name='groceries', is_income=False)
        self.category.save()

        self.wallet = Wallet.objects.create(id=1, user_id=1, name='checking', balance=100, created_time=timezone.now())
        self.wallet.save()

        self.transaction = Transaction.objects.create(id=1, amount=10.50, category=self.category, category_id=1,
                                                      description='foo', created_time=timezone.now(),
                                                      wallet=self.wallet, wallet_id=1, user=self.user, user_id=1)
        self.transaction.save()

        self.budget = Budget.objects.create(budget_id=1, user_id=1, category_id=1, goal=100, month=datetime.date(2017, 1, 1), wallet_id=1, balance=0, user=self.user)
        self.budget.save()
        self.login()

    def login(self):
        self.client.login(username='test_user', password='tester123')

    def tearDown(self):
        self.budget.delete()
        self.wallet.delete()
        self.category.delete()
        self.user.delete()

    def test_category_str(self):
        self.assertEqual(str(self.category), 'groceries')

    def test_wallet_str(self):
        self.assertEqual(str(self.wallet), 'checking')

    def test_transaction_str(self):
        self.assertEqual(str(self.transaction), 'groceries')

    def test_budget_str(self):
        self.assertEqual(str(self.budget), 'groceries')
