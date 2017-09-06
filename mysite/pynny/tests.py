from django.test import TestCase
from django.contrib.auth.models import User
from django.shortcuts import reverse


class SimpleTest(TestCase):
    def test_basic_addition(self):
        """Tests that 1 + 1 = 2"""
        self.assertEqual(1 + 1, 2)


class MainViewsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test_user', email='test_user@gmail.com', password='tester123').save()

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
