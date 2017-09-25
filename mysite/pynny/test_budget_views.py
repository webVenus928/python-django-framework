from django.test import TestCase
from django.contrib.auth.models import User
from django.shortcuts import reverse
from django.utils import timezone

import datetime
import decimal

from .models import Budget, BudgetCategory, Wallet, Transaction


class BudgetViewsTests(TestCase):
    def setUp(self):
        # Create a user and give them some data to test with
        self.user = User.objects.create_user(id=1, username='test_user', email='test_user@gmail.com', password='tester123')
        self.user.save()
        self.other_user = User.objects.create_user(id=2, username='test_user2', email='test_user2@gmail.com',
                                             password='123tester')
        self.other_user.save()

        self.category = BudgetCategory.objects.create(id=1, user_id=1, user=self.user, name='groceries', is_income=False)
        self.category.save()
        self.other_category = BudgetCategory.objects.create(id=2, user_id=1, user=self.user, name='entertainment', is_income=False)
        self.other_category.save()

        self.wallet = Wallet.objects.create(id=1, user_id=1, name='checking', balance=100, created_time=timezone.now())
        self.wallet.save()
        self.other_wallet = Wallet.objects.create(id=2, user_id=2, name='debit card', balance=0, created_time=timezone.now())
        self.other_wallet.save()

        self.transaction = Transaction.objects.create(id=1, amount=10.50, category=self.category, category_id=1,
                                                      description='foo', created_time=timezone.now(),
                                                      wallet=self.wallet, wallet_id=1, user=self.user, user_id=1)
        self.transaction.save()
        self.other_transcation = Transaction.objects.create(id=2, amount=25.00, category=self.other_category, category_id=2,
                                                      description='blah', created_time=timezone.now(),
                                                      wallet=self.wallet, wallet_id=1, user=self.user, user_id=1)
        self.other_transcation.save()

        self.budget = Budget.objects.create(budget_id=1, user_id=1, category_id=1, goal=100, month=datetime.date(2017, 1, 1), wallet_id=1, balance=0, user=self.user)
        self.budget.save()
        self.login()

    def login(self):
        self.client.login(username='test_user', password='tester123')

    def tearDown(self):
        self.budget.delete()
        self.wallet.delete()
        self.other_wallet.delete()
        self.category.delete()
        self.other_category.delete()
        self.user.delete()
        self.other_user.delete()

    def test_renew_budgets(self):
        last_month = datetime.date(datetime.date.today().year, datetime.date.today().month - 1 if datetime.date.today().month > 1 else 12, 1)
        self.budget.month = last_month
        self.budget.save()
        resp = self.client.get(reverse('renew_budgets'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(Budget.objects.filter(budget_id=1)), 2)

    def test_get_budgets(self):
        resp = self.client.get(reverse('budgets'))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('budgets' in resp.context)

    def test_post_to_create_new_budget(self):
        resp = self.client.post(reverse('budgets'),
                                {
                                    'category': '2',
                                    'goal': '50',
                                    'wallet': '1'
                                })
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(len(Budget.objects.filter(user=self.user)), 2)
        self.assertEqual(Budget.objects.get(user=self.user, wallet=self.wallet, category=self.other_category).goal, decimal.Decimal('50'))

    def test_post_to_create_already_existing_budget(self):
        budget = self.budget
        budget.month = datetime.date.today()
        budget.save()
        resp = self.client.post(
            reverse('budgets'),
            {
                'category': '1',
                'goal': '230',
                'wallet': '1'
            }
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(Budget.objects.filter(user=self.user)), 1)
        self.assertEqual(Budget.objects.get(budget_id=1).goal, decimal.Decimal('100'))
        self.assertEqual(len(resp.context['alerts']['errors']), 1)

    def test_new_budget_page(self):
        resp = self.client.get(reverse('new_budget'))
        self.assertEqual(resp.status_code, 200)

    def test_new_budget_without_categories(self):
        self.category.delete()
        self.other_category.delete()
        resp = self.client.get(reverse('new_budget'))
        self.assertEqual(resp.status_code, 200)
        self.category = BudgetCategory.objects.create(id=1, user_id=1, user=self.user, name='groceries',
                                                      is_income=False)
        self.category.save()
        self.other_category = BudgetCategory.objects.create(id=2, user_id=1, user=self.user, name='entertainment',
                                                            is_income=False)
        self.other_category.save()

    def test_new_budget_without_wallets(self):
        self.wallet.delete()
        self.other_wallet.delete()
        resp = self.client.get(reverse('new_budget'))
        self.assertEqual(resp.status_code, 200)
        self.wallet = Wallet.objects.create(id=1, user_id=1, name='checking', balance=100, created_time=timezone.now())
        self.wallet.save()
        self.other_wallet = Wallet.objects.create(id=2, user_id=2, name='debit card', balance=0,
                                                  created_time=timezone.now())
        self.other_wallet.save()

    def test_get_one_budget(self):
        resp = self.client.get('/pynny/budgets/1')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['budget'], self.budget)
        self.assertEqual(len(resp.context['transactions']), 1)

    def test_get_nonexistent_budget(self):
        resp = self.client.get('/pynny/budgets/1000')
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(len(resp.context['alerts']['errors']), 1)

    def test_get_someone_elses_budget(self):
        self.budget.user = self.other_user
        self.budget.save()
        resp = self.client.get('/pynny/budgets/1')
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(len(resp.context['alerts']['errors']), 1)

    def test_post_to_delete_a_budget(self):
        resp = self.client.post(
            '/pynny/budgets/1',
            {
                'action': 'delete'
            }
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.context['alerts']['success']), 1)
        with self.assertRaises(Budget.DoesNotExist):
            Budget.objects.get(id=1)

    def test_post_to_edit_a_budget(self):
        resp = self.client.post(
            '/pynny/budgets/1',
            {
                'action': 'edit'
            }
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['budget'], self.budget)
        self.assertEqual(len(resp.context['wallets']), 1)
        self.assertEqual(len(resp.context['categories']), 2)

    def test_to_finish_editing_a_budget(self):
        resp = self.client.post(
            '/pynny/budgets/1',
            {
                'action': 'edit_complete',
                'category': '2',
                'wallet': '2',
                'goal': '999'
            }
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.context['alerts']['success']), 1)
        budget = Budget.objects.get(id=1)
        self.assertEqual(budget.category, self.other_category)
        self.assertEqual(budget.wallet, self.other_wallet)
        self.assertEqual(budget.goal, decimal.Decimal('999'))
