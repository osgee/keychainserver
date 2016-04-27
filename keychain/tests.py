from django.test import TestCase
from django.core.urlresolvers import reverse
from .models import User, App
import uuid

# Create your tests here.

class UserMethodTest(TestCase):
    def test_user_has_signed_up(self):
        u = User(user_name='taofeng', user_password='ft')
        u.save()
        b = u.has_signed_up()
        self.assertEqual(b, True)

    def test_user_sign_in(self):
        response = self.client.post(reverse('keychain:web:user_signin'), {
                'user_name':'taofeng',
                'user_password': 'ft',
            })
        self.assertContains(response, 'Sign In', status_code=200)

    def test_user_sign_up(self):
        response = self.client.post(reverse('keychain:web:user_signup'),{
                'user_name': 'taofeng',
                'user_password': 'ft'
            })
        self.assertContains(response, 'Sign Up', status_code=200)
    # def test_signin(self):
    #     response = self.client(reverse)

class AppMethodTest(TestCase):
    def test_app_sign_up(self):
        publickey = open('id_rsa.pub', 'rb')
        logo = open('qq.jpeg', 'rb')
        response = self.client.post(reverse('keychain:app_signup'), {
                'app_name': 'QQ',
                'app_publickey': publickey,
                'app_logo': logo, 
            })
        self.assertContains(response, '', status_code = 302)

    def test_app_has_signed_up(self):
        a = App(app_name='QQ')
        a.save()
        b = a.has_signed_up()
        self.assertEqual(b, True)

    def test_app_list(self):
        response = self.client.get(reverse('keychain:app_list'))
        self.assertContains(response, 'App List', status_code=200)

    # def test_app_service(self):
    #     a = App(app_name='QQ')
    #     a.save()
    #     a = App.objects.all()[0]
    #     response = self.client.get(reverse('keychain:app_service', app_id=a.app_id.hex))
    #     self.assertContains(response, status_code=200)

