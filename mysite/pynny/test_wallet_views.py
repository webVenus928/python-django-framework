from django.test import TestCase
from django.contrib.auth.models import User
from django.shortcuts import reverse
from django.utils import timezone

import datetime
import decimal

from .models import Budget, BudgetCategory, Wallet, Transaction


class WalletViewsTests(TestCase):
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
        self.other_wallet = Wallet.objects.create(id=2, user_id=2, name='debit card', balance=0, created_time=timezone.now())
        self.other_wallet.save()

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
        self.other_wallet.delete()
        self.category.delete()
        self.user.delete()
        self.other_user.delete()

    def test_get_all_wallets(self):
        resp = self.client.get(reverse('wallets'))
        self.assertEqual(resp.status_code, 200)
        wallets = resp.context['wallets']
        self.assertEqual(len(wallets), 1)
        self.assertEqual(wallets[0], self.wallet)

    def test_post_to_create_a_new_wallet(self):
        resp = self.client.post(reverse('wallets'),
                                {
                                    'name': 'credit card',
                                    'balance': '10.00'
                                })
        self.assertEqual(resp.status_code, 201)
        self.assertTrue(len(resp.context['alerts']['success']) == 1)
        wallets = resp.context['wallets']
        self.assertEqual(len(wallets), 2)
        wallet = Wallet.objects.get(user=self.user, name='credit card')
        self.assertEqual(wallet.balance, decimal.Decimal('10.00'))
        wallet.delete()

    def test_post_to_create_existing_wallet(self):
        resp = self.client.post(reverse('wallets'),
                                {
                                    'name': 'checking',
                                    'balance': '10.00'
                                })
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(len(resp.context['alerts']['errors']) == 1)
        self.assertEqual(len(Wallet.objects.filter(user=self.user)), 1)
        wallet = Wallet.objects.get(id=1)
        self.assertEqual(wallet.balance, decimal.Decimal('100'))

    def test_new_wallet_view(self):
        resp = self.client.get(reverse('new_wallet'))
        self.assertEqual(resp.status_code, 200)

    def test_get_specific_wallet(self):
        resp = self.client.get('/pynny/wallets/1')
        self.assertEqual(resp.status_code, 200)
        wallet = resp.context['wallet']
        self.assertEqual(wallet, self.wallet)

    def test_get_nonexistent_wallet(self):
        resp = self.client.get('/pynny/wallets/95')
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(len(resp.context['alerts']['errors']), 1)

    def test_get_someone_elses_wallet(self):
        resp = self.client.get('/pynny/wallets/2')
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(len(resp.context['alerts']['errors']), 1)

    def test_post_to_delete_a_wallet(self):
        resp = self.client.post(
            '/pynny/wallets/1',
            {
                'action': 'delete'
            }
        )
        self.assertEqual(resp.status_code, 200)
        with self.assertRaises(Wallet.DoesNotExist):
            Wallet.objects.get(id=1)

    def test_edit_a_wallet_view(self):
        resp = self.client.post(
            '/pynny/wallets/1',
            {
                'action': 'edit'
            }
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['wallet'], self.wallet)

    def test_edit_completion(self):
        resp = self.client.post(
            '/pynny/wallets/1',
            {
                'action': 'edit_complete',
                'name': 'savings'
            }
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Wallet.objects.get(id=1).name, 'savings')
        self.assertEqual(len(resp.context['alerts']['success']), 1)
