
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone

import datetime
import decimal

from .models import Budget, BudgetCategory, Wallet, Transaction

from .templatetags import pynny_extras


class TemplateTagTests(TestCase):
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

    def test_get_item_tag(self):
        foo = {'bar': 'buzz'}
        self.assertEqual(pynny_extras.get_item(foo, 'bar'), 'buzz')

    def test_wallet_class_tag(self):
        self.wallet.balance = decimal.Decimal('5')
        self.assertEqual(pynny_extras.wallet_class(self.wallet.balance), 'success')
        self.wallet.balance = decimal.Decimal('-5')
        self.assertEqual(pynny_extras.wallet_class(self.wallet.balance), 'danger')
        self.wallet.balance = decimal.Decimal('0')
        self.assertEqual(pynny_extras.wallet_class(self.wallet.balance), 'default')

    def test_budget_class_tag(self):
        self.assertEqual(pynny_extras.budget_class(self.budget), 'success')
        self.budget.balance = decimal.Decimal('90')
        self.assertEqual(pynny_extras.budget_class(self.budget), 'warning')
        self.budget.balance = decimal.Decimal('1000')
        self.assertEqual(pynny_extras.budget_class(self.budget), 'danger')

        self.category.is_income = True
        self.category.save()
        self.budget.category = self.category

        self.budget.balance = decimal.Decimal('0')
        self.assertEqual(pynny_extras.budget_class(self.budget), 'danger')
        self.budget.balance = decimal.Decimal('90')
        self.assertEqual(pynny_extras.budget_class(self.budget), 'warning')
        self.budget.balance = decimal.Decimal('1000')
        self.assertEqual(pynny_extras.budget_class(self.budget), 'success')

    def test_transaction_class_tag(self):
        self.transaction.amount = decimal.Decimal('0')
        self.assertEqual(pynny_extras.transaction_class(self.transaction), 'default')
        self.transaction.amount = decimal.Decimal('10')
        self.assertEqual(pynny_extras.transaction_class(self.transaction), 'danger')
        self.transaction.amount = decimal.Decimal('-10')
        self.assertEqual(pynny_extras.transaction_class(self.transaction), 'success')

        self.category.is_income = True
        self.transaction.category = self.category
        self.assertEqual(pynny_extras.transaction_class(self.transaction), 'danger')
        self.transaction.amount = decimal.Decimal('10')
        self.assertEqual(pynny_extras.transaction_class(self.transaction), 'success')

    def test_shorten_string_tag(self):
        self.assertEqual(pynny_extras.shorten_string('1234567890', 6), '123...')
