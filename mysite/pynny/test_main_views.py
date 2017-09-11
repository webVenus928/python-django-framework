from django.test import TestCase
from django.contrib.auth.models import User
from django.shortcuts import reverse
from django.utils import timezone

import datetime

from .models import Budget, BudgetCategory, Wallet


class MainViewsTests(TestCase):
    def setUp(self):
        # Create a user and give them some data to test with
        self.user = User.objects.create_user(id=1, username='test_user', email='test_user@gmail.com', password='tester123')
        self.user.save()

        self.category = BudgetCategory.objects.create(id=1, user_id=1, user=self.user, name='groceries', is_income=False)
        self.category.save()

        self.wallet = Wallet.objects.create(id=1, user_id=1, name='checking', balance='100', created_time=timezone.now())
        self.wallet.save()

        self.budget = Budget.objects.create(budget_id=1, user_id=1, category_id=1, goal=100, month=datetime.date.today(), wallet_id=1, balance=0, user=self.user)
        self.budget.save()

    def tearDown(self):
        self.budget.delete()
        self.wallet.delete()
        self.category.delete()
        self.user.delete()

    def test_logout_view(self):
        self.client.login(username='test_user', password='tester123')
        # print('Before:', self.client.get(reverse('index')).context['user'])
        response = self.client.get(reverse('logout'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(response.context.get('user', '')), 'AnonymousUser')
        # print('After:', response.context['user'])

    def test_login(self):
        self.client.login(username='test_user', password='tester123')
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(response.context.get('user', '')), 'test_user')

    def test_unauthenticated_index_access(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 302)
