from django.test import TestCase
from django.contrib.auth.models import User
from django.shortcuts import reverse
from django.utils import timezone

import datetime
import decimal

from .models import Savings


class SavingsViewsTests(TestCase):
    def setUp(self):
        # Create a user and give them some data to test with
        self.user = User.objects.create_user(id=1, username='test_user', email='test_user@gmail.com', password='tester123')
        self.user.save()
        self.other_user = User.objects.create_user(id=2, username='test_user2', email='test_user2@gmail.com',
                                             password='123tester')
        self.other_user.save()

        self.saving = Savings.objects.create(id=1, user_id=1, user=self.user, name='TestSaving', goal=10.0, balance=1.0,
                                              due_date=datetime.datetime.today(), notify_on_completion=False,
                                              delete_on_completion=True, hidden=False, completed=False)
        self.saving.save()
        self.login()

    def login(self):
        self.client.login(username='test_user', password='tester123')

    def tearDown(self):
        self.saving.delete()
        self.user.delete()
        self.other_user.delete()

    def test_get_all_savings(self):
        resp = self.client.get(reverse('savings'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.context['savings']), 1)
        self.assertTrue(self.saving in resp.context['savings'])

    def test_create_new_saving(self):
        resp = self.client.post(
            reverse('savings'),
            data={
                'name': 'TestSaving2',
                'goal': '20.50',
                'due_date': '2017-12-31',
                'notify': True,
                'delete': False
            }
        )
        self.assertEqual(resp.status_code, 201)
        savings = Savings.objects.filter(user=self.user, name='TestSaving2')
        self.assertEqual(len(savings), 1)



