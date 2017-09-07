from django.test import TestCase
from django.contrib.auth.models import User
from django.shortcuts import reverse
from django.utils import timezone

import datetime

from .models import Budget, BudgetCategory, Wallet


class SimpleTest(TestCase):
    def test_basic_addition(self):
        """Tests that 1 + 1 = 2"""
        self.assertEqual(1 + 1, 2)


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


class CategoryViewsTests(TestCase):
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

    def login(self):
        self.client.login(username='test_user', password='tester123')

    def tearDown(self):
        self.budget.delete()
        self.wallet.delete()
        self.category.delete()
        self.user.delete()

    def test_view_all_categories(self):
        """Test the GET to view all the budget categories"""
        self.login()
        response = self.client.get(reverse('categories'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['categories']), 1)

        new_category = BudgetCategory.objects.create(id=2, user_id=1, user=self.user, name='entertainment', is_income=False)
        new_category.save()

        response = self.client.get(reverse('categories'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['categories']), 2)

        new_category.delete()

    def test_create_new_category(self):
        """Test the POST to create a new budget category"""
        category_name = 'travel'
        self.login()
        resp = self.client.post(reverse('categories'), {'name': category_name})
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(len(resp.context['categories']), 2)
        self.assertEqual(len(resp.context['alerts']['success']), 1)

        category = BudgetCategory.objects.get(user=self.user, name=category_name)
        self.assertEqual(category.name, category_name)
        self.assertEqual(category.is_income, False)
        category.delete()

    def test_create_income_category(self):
        self.login()
        name = 'paycheck'
        resp = self.client.post(reverse('categories'), {'name': name, 'is_income': True})
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(len(resp.context['categories']), 2)
        self.assertEqual(len(resp.context['alerts']['success']), 1)

        category = BudgetCategory.objects.get(user=self.user, name=name)
        self.assertEqual(category.name, name)
        self.assertEqual(category.is_income, True)
        category.delete()

    def test_create_already_exists_category(self):
        self.login()
        name = 'groceries'
        resp = self.client.post(reverse('categories'), {'name': 'groceries'})
        self.assertEqual(resp.status_code, 409)
        self.assertEqual(len(resp.context['alerts']['errors']), 1)

        categories = BudgetCategory.objects.filter(user=self.user, name=name)
        self.assertEqual(len(categories), 1)
