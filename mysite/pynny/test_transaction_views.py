from django.test import TestCase
from django.contrib.auth.models import User
from django.shortcuts import reverse
from django.utils import timezone

import datetime
import decimal

from .models import Budget, BudgetCategory, Wallet, Transaction


class TransactionViewsTests(TestCase):
    def setUp(self):
        # Create a user and give them some data to test with
        self.user = User.objects.create_user(id=1, username='test_user', email='test_user@gmail.com', password='tester123')
        self.user.save()
        self.other_user = User.objects.create_user(id=2, username='test_user2', email='test_user2@gmail.com',
                                             password='123tester')
        self.other_user.save()

        self.category = BudgetCategory.objects.create(id=1, user_id=1, user=self.user, name='groceries', is_income=False)
        self.category.save()

        self.wallet = Wallet.objects.create(id=1, user_id=1, name='checking', balance=100, created_time=timezone.now())
        self.wallet.save()

        self.transaction = Transaction.objects.create(id=1, amount=10.50, category=self.category, category_id=1,
                                                      description='foo', created_time=timezone.now(),
                                                      wallet=self.wallet, wallet_id=1, user=self.user, user_id=1)
        self.transaction.save()

        self.budget = Budget.objects.create(budget_id=1, user_id=1, category_id=1, goal=100, month=datetime.date.today(), wallet_id=1, balance=0, user=self.user)
        self.budget.save()
        self.login()

    def login(self):
        self.client.login(username='test_user', password='tester123')

    def tearDown(self):
        self.budget.delete()
        self.wallet.delete()
        self.category.delete()
        self.user.delete()
        self.other_user.delete()

    def test_get_all_transaction(self):
        resp = self.client.get(reverse('transactions'))
        self.assertEqual(resp.status_code, 200)
        transactions = resp.context['transactions']
        self.assertTrue(len(transactions) >= 1)
        self.assertEqual(transactions[0].user, self.user)
        self.assertEqual(transactions[0], self.transaction)

    def test_create_new_transaction(self):
        resp = self.client.post(
            reverse('transactions'),
            {
                'category': 1,
                'wallet': 1,
                'amount': 50.75,
                'description': 'bar',
                'created_time': '2017-09-07'
            }
        )
        self.assertEqual(resp.status_code, 201)
        new_balance = Wallet.objects.get(id=1).balance
        self.assertEqual(new_balance, 100 - 50.75)
        transactions = Transaction.objects.filter(user=self.user)
        self.assertTrue(len(transactions) >= 2)
        transactions = Transaction.objects.filter(user=self.user, category=self.category)
        self.assertTrue(len(transactions) >= 2)

    def test_create_transaction_of_income(self):
        category = BudgetCategory.objects.create(id=2, user_id=1, user=self.user, name='paycheck',
                                                      is_income=True)
        category.save()
        resp = self.client.post(
            reverse('transactions'),
            {
                'category': 2,
                'wallet': 1,
                'amount': 50.75,
                'description': 'bar',
                'created_time': '2017-09-07'
            }
        )
        self.assertEqual(resp.status_code, 201)
        new_balance = Wallet.objects.get(id=1).balance
        self.assertEqual(new_balance, 100 + 50.75)
        transactions = Transaction.objects.filter(user=self.user)
        self.assertTrue(len(transactions) >= 2)
        transactions = Transaction.objects.filter(user=self.user, category=category)
        self.assertTrue(len(transactions) == 1)

    def test_new_transaction_page(self):
        resp = self.client.get(reverse('new_transaction'))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('categories' in resp.context)
        self.assertTrue(len(resp.context['categories']) == 1)
        self.assertTrue('wallets' in resp.context)
        self.assertEqual(len(resp.context['wallets']), 1)

    def test_new_transaction_with_no_categories(self):
        self.client.logout()
        self.client.login(username='test_user2', password='123tester')
        resp = self.client.get(reverse('new_transaction'))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(len(resp.context['alerts']['errors']) >= 1)
        self.assertTrue('don\'t have any Categories yet' in resp.context['alerts']['errors'][0])

    def test_new_transaction_with_no_wallet(self):
        self.client.logout()
        category = BudgetCategory.objects.create(id=2, user_id=2, user=self.other_user, name='paycheck',
                                                 is_income=True)
        category.save()
        self.client.login(username='test_user2', password='123tester')
        resp = self.client.get(reverse('new_transaction'))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(len(resp.context['alerts']['errors']) >= 1)
        self.assertTrue('don\'t have any Wallets yet' in resp.context['alerts']['errors'][0])

    def test_get_one_transaction(self):
        resp = self.client.get('/pynny/transactions/1')
        self.assertEqual(resp.status_code, 200)
        trans = resp.context['transaction']
        self.assertEqual(trans, self.transaction)

    def test_get_nonexistent_transaction(self):
        resp = self.client.get('/pynny/transactions/100')
        self.assertEqual(resp.status_code, 404)
        self.assertTrue(len(resp.context['alerts']['errors']) >= 1)

    def test_get_someone_elses_transaction(self):
        new_transaction = Transaction.objects.create(id=2, amount=20.75, category=self.category, category_id=1,
                                                      description='biz', created_time=timezone.now(),
                                                      wallet=self.wallet, wallet_id=1, user=self.other_user, user_id=2)
        new_transaction.save()
        resp = self.client.get('/pynny/transactions/2')
        self.assertEqual(resp.status_code, 403)
        self.assertTrue(len(resp.context['alerts']['errors']) >= 1)
        new_transaction.delete()

    def test_post_to_delete_a_transaction(self):
        resp = self.client.post(
            '/pynny/transactions/1',
            {
                'action': 'delete'
            }
        )
        self.assertEqual(resp.status_code, 200)
        wallet = Wallet.objects.get(id=1)
        self.assertEqual(wallet.balance, 100 + 10.50)
        budget = Budget.objects.get(id=1)
        self.assertEqual(budget.balance, 0 - 10.50)
        self.assertTrue(len(resp.context['alerts']['info']) >= 1)
        with self.assertRaises(Transaction.DoesNotExist):
            Transaction.objects.get(id=1)

    def test_post_to_delete_an_income_transaction(self):
        category = BudgetCategory.objects.create(
            id=2, user=self.user, user_id=1, name='paycheck',
            is_income=True
        )
        category.save()
        new_transaction = Transaction.objects.create(
            id=2, amount=14.50, category=self.category, category_id=2,
            description='raise', created_time=timezone.now(),
            wallet=self.wallet, wallet_id=1, user=self.user, user_id=1
        )
        new_transaction.save()
        budget = Budget.objects.create(budget_id=2, user_id=1, category_id=2, goal=1000, month=datetime.date.today(), wallet_id=1,
                              balance=200, user=self.user)
        budget.save()

        resp = self.client.post(
            '/pynny/transactions/2',
            {
                'action': 'delete'
            }
        )
        self.assertEqual(resp.status_code, 200)
        wallet = Wallet.objects.get(id=1)
        self.assertEqual(wallet.balance, 100 - 14.50)
        budget = Budget.objects.get(id=2)
        self.assertEqual(budget.balance, 200 - 14.50)
        self.assertTrue(len(resp.context['alerts']['info']) >= 1)
        with self.assertRaises(Transaction.DoesNotExist):
            Transaction.objects.get(id=2)

        budget.delete()
        category.delete()

    def test_edit_a_transaction(self):
        resp = self.client.post(
            '/pynny/transactions/1',
            {
                'action': 'edit'
            }
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['transaction'], self.transaction)

    def test_submit_edit_of_a_transaction(self):
        resp = self.client.post(
            '/pynny/transactions/1',
            {
                'action': 'edit_complete',
                'category': 1,
                'wallet': 1,
                'amount': '19.99',
                'description': 'kapowz',
                'created_time': '2017-01-01'
            }
        )
        self.assertEqual(resp.status_code, 200)
        trans = Transaction.objects.get(id=1)
        self.assertEqual(trans.amount, decimal.Decimal('19.99'))
        self.assertEqual(trans.description, 'kapowz')
        self.assertEqual(trans.created_time, datetime.date(2017, 1, 1))

    def test_submit_edit_of_an_income_transaction(self):
        self.category.is_income = True
        self.category.save()
        resp = self.client.post(
            '/pynny/transactions/1',
            {
                'action': 'edit_complete',
                'category': 1,
                'wallet': 1,
                'amount': '19.98',
                'description': 'dooz',
                'created_time': '2010-06-03'
            }
        )
        self.assertEqual(resp.status_code, 200)
        trans = Transaction.objects.get(id=1)
        self.assertEqual(trans.amount, decimal.Decimal('19.98'))
        self.assertEqual(trans.description, 'dooz')
        self.assertEqual(trans.created_time, datetime.date(2010, 6, 3))
        self.assertEqual(float(Wallet.objects.get(id=1).balance), 100 - 10.50 + 19.98)
