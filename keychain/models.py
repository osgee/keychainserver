import datetime
import json
import math
import time
import uuid

from django.db import models
from django.utils import timezone

from keychain import cryptool


# Create your models here.


class User(models.Model):
    USER_TYPES = (
        (1, 'USERNAME'),
        (2, 'EMAIL'),
        (3, 'CELLPHONE'),
        (4, 'USERNAME')
    )
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_type = models.CharField(max_length=1, choices=USER_TYPES)
    user_name = models.CharField(max_length=50, unique=True, null=True, default=None)
    user_password = models.CharField(max_length=100)
    user_email = models.EmailField(null=True, unique=True, default=None)
    user_cellphone = models.CharField(null=True, max_length=20, unique=True, default=None)
    user_device = models.CharField(null=True, max_length=20)
    user_secret = models.CharField(null=True, max_length=15, editable=True)
    user_cookie = models.UUIDField(null=True, editable=True)
    user_cookie_time = models.DateTimeField('cookie expire time', null=True)
    user_salt = models.CharField(max_length=50)

    def get_name(self):
        if self.user_type in [1, '1']:
            return self.user_name
        if self.user_type in [2, '2']:
            return self.user_email
        if self.user_type in [3, '3']:
            return self.user_cellphone

    def has_signed_up(self):
        if self.user_type in [1, '1']:
            try:
                User.objects.get(user_name=self.user_name)
                return True
            except User.DoesNotExist:
                pass
        if self.user_type in [2, '2']:
            try:
                User.objects.get(user_email=self.user_email)

                return True
            except User.DoesNotExist:
                pass
        if self.user_type in [3, '3']:
            try:
                User.objects.get(user_cellphone=self.user_cellphone)
                return True
            except User.DoesNotExist:
                pass
        return False

    def encrypt_save(self):
        salt = cryptool.random_salt()
        user_password_plain = self.user_password
        self.user_salt = salt
        self.user_password = cryptool.digest_sha256(self.user_password, salt)

        self.user_secret = cryptool.random_salt(12)
        self.save()
        # self.user_password_plain = user_password_plain
        return self

    def get_by_password(self):
        user_password_plain = self.user_password
        salt = self.get_salt()
        self.user_password = cryptool.digest_sha256(self.user_password, salt)

        if self.user_type in [4, '4']:
            return self.get_by_cookie()

        if self.user_type in [1, '1']:
            try:
                user = User.objects.get(user_name=self.user_name, user_password=self.user_password)
                user.user_password_plain = user_password_plain
                return user
            except User.DoesNotExist:
                pass
        if self.user_type in [2, '2']:
            try:
                user = User.objects.get(user_email=self.user_email, user_password=self.user_password)
                user.user_password_plain = user_password_plain
                return user
            except User.DoesNotExist:
                pass
        if self.user_type in [3, '3']:
            try:
                user = User.objects.get(user_cellphone=self.user_cellphone, user_password=self.user_password)
                user.user_password_plain = user_password_plain
                return user
            except User.DoesNotExist:
                pass

    def get_salt(self):
        if self.user_type in [1, '1']:
            try:
                return User.objects.get(user_name=self.user_name).user_salt
            except User.DoesNotExist:
                pass
        if self.user_type in [2, '2']:
            try:
                return User.objects.get(user_email=self.user_email).user_salt
            except User.DoesNotExist:
                pass
        if self.user_type in [3, '3']:
            try:
                return User.objects.get(user_cellphone=self.user_cellphone).user_salt
            except User.DoesNotExist:
                pass
        return ''

    def get_by_cookie(self):
        expired = True
        if hasattr(self, 'user_id') and hasattr(self,
                                                'user_cookie') and self.user_id is not None and self.user_cookie is not None:
            try:
                user = User.objects.get(user_name=self.user_name, user_cookie=self.user_cookie)
                if timezone.now() < user.user_cookie_time:
                    return user
                else:
                    expired = True
            except User.DoesNotExist:
                pass

    def delete_cookie(self):
        if hasattr(self, 'user_id') and hasattr(self, 'user_cookie'):
            try:
                user = User.objects.get(user_id=self.user_id, user_cookie=self.user_cookie)
                user.user_cookie = None
                user.user_cookie_time = None
                user.save()
            except User.DoesNotExist:
                pass

    def is_need_refresh_cookie(self):
        if hasattr(self, 'user_id') and hasattr(self, 'user_cookie'):
            try:
                user = User.objects.get(user_name=self.user_name, user_cookie=self.user_cookie)
                if timezone.now() + datetime.timedelta(days=3) < user.user_cookie_time:
                    return True
                else:
                    return False
            except User.DoesNotExist:
                pass
        return False

    def load_from_JSON(self, s):
        d = json.loads(s)
        self.user_id = uuid.UUID(d['user_id'])
        self.user_type = d['user_type']
        self.user_name = d['user_name']
        self.user_password = d['user_password']
        self.user_email = d['user_email']
        self.user_cellphone = d['user_cellphone']
        self.user_device = d['user_device']
        self.user_secret = d['user_secret']
        self.user_cookie = uuid.UUID(d['user_cookie'])
        return self

    def to_JSON(self, cert=True):
        d = {}
        if self.user_id is not None:
            d['user_id'] = self.user_id.hex
        else:
            d['user_id'] = None
        if cert:
            d['user_type'] = self.user_type
            d['user_name'] = self.user_name
            d['user_password'] = self.user_password
            d['user_email'] = self.user_email
            d['user_cellphone'] = self.user_cellphone
            d['user_device'] = self.user_device
            d['user_secret'] = self.user_secret
            if self.user_cookie is not None:
                d['user_cookie'] = self.user_cookie.hex
            else:
                d['user_cookie'] = None
            if self.user_cookie_time is not None:
                d['user_cookie_time'] = math.floor(time.mktime(self.user_cookie_time.timetuple()))
            else:
                d['user_cookie_time'] = None
        return json.dumps(d)


class App(models.Model):
    app_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    app_name = models.CharField(max_length=25, unique=True)
    app_sign_in_action_uri = models.CharField(max_length=200)
    app_logo_uri = models.CharField(max_length=200)
    app_public_key_uri = models.CharField(max_length=200)

    def app_publickey_path(self, name):
        return './upload/apps/{0}/publickey/{1}'.format(self.app_name, 'id_rsa.pub')

    def app_logo_path(self, name):
        return './upload/apps/{0}/logo/{1}'.format(self.app_name, 'logo_' + name)

    def has_signed_up(self):
        try:
            App.objects.get(app_name=self.app_name)
            return True
        except App.DoesNotExist:
            return False

    app_publickey = models.FileField(upload_to=app_publickey_path)
    app_logo = models.ImageField(upload_to=app_logo_path)

    def load_from_JSON(self, s):
        jsonApp = json.loads(s)
        self.app_id = uuid.UUID(jsonApp['app_id'])
        self.app_name = jsonApp['app_name']
        self.app_sign_in_action_uri = jsonApp['app_sign_in_action_uri']
        self.app_logo_uri = jsonApp['app_logo_uri']
        self.app_public_key_uri = jsonApp['app_public_key_uri']
        return self

    def to_JSON(self):
        d = {}
        if self.app_id is not None:
            d['app_id'] = self.app_id.hex
        else:
            d['app_id'] = None
        d['app_name'] = self.app_name
        d['app_sign_in_action_uri'] = self.app_sign_in_action_uri
        d['app_logo_uri'] = self.app_logo_uri
        d['app_public_key_uri'] = self.app_public_key_uri

        return json.dumps(d)


class Account(models.Model):
    ACCOUNT_TYPES = (
        ('U', 'USERNAME'),
        ('E', 'EMAIL'),
        ('C', 'CELLPHONE'),
    )
    account_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    account_type = models.CharField(max_length=1, choices=ACCOUNT_TYPES)
    account_username = models.CharField(max_length=50)
    account_password = models.CharField(max_length=50)
    account_email = models.CharField(max_length=50, null=True)
    account_cellphone = models.CharField(max_length=20, null=True)
    account_user = models.ForeignKey(User, on_delete=models.CASCADE)
    account_app = models.ForeignKey(App, on_delete=models.CASCADE, null=True)

    def encrypt_save(self, password):
        salt = self.account_user.user_salt
        if password is None:
            password = self.account_user.user_password_plain
        self.account_password_plain = self.account_password
        self.account_password = cryptool.encrypt_aes(self.account_password, password, salt)
        self.save()
        return self

    def decrypt(self, password):
        salt = self.account_user.user_salt
        if password is None:
            password = self.account_user.user_password_plain
        self.account_password = cryptool.decrypt_aes(self.account_password, password, salt)
        return self

    def load_from_JSON(self, s):
        jsonAccount = json.loads(s)
        self.account_id = uuid.UUID(jsonAccount['account_id'])
        self.account_type = jsonAccount['account_type']
        self.account_username = jsonAccount['account_username']
        self.account_password = jsonAccount['account_password']
        self.account_email = jsonAccount['account_email']
        self.account_cellphone = jsonAccount['account_cellphone']
        if jsonAccount['account_user'] is not None:
            try:
                self.account_user = User.objects.get(user_id=json.loads(jsonAccount['account_user'])['user_id'])
            except User.DoesNotExist:
                self.account_user = None
        else:
            self.account_user = None
        if jsonAccount['account_app'] is not None:
            try:
                self.account_app = App.objects.get(app_id=json.loads(jsonAccount['account_app'])['app_id'])
            except App.DoesNotExist:
                self.account_app = None
        else:
            self.account_app = None

        return self

    def to_JSON(self):
        d = {}
        if self.account_id is not None:
            d['account_id'] = self.account_id.hex
        else:
            d['account_id'] = None
        d['account_type'] = self.account_type
        d['account_username'] = self.account_username
        d['account_password'] = self.account_password
        d['account_email'] = self.account_email
        d['account_cellphone'] = self.account_cellphone
        if self.account_user is not None and self.account_user.user_id is not None:
            d['account_user'] = self.account_user.to_JSON(False)
        else:
            d['account_user'] = None
        if self.account_app is not None and self.account_app.app_id is not None:
            d['account_app'] = self.account_app.to_JSON()
        else:
            d['account_app'] = None
        return json.dumps(d)


class Service(models.Model):
    ACTION_TYPES = (
        ('I', 'SING IN'),
        ('U', 'SING UP'),
    )
    STATUS_TYPES = (
        ('I', 'INIT'),
        ('S', 'SERVICE'),
        ('C', 'CONFIRM'),
        ('E', 'EXPIRE'),
        ('F', 'FINISH'),
    )
    service_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    service_action = models.CharField(null=True, max_length=1, choices=ACTION_TYPES)
    service_secret = models.UUIDField(default=uuid.uuid4, editable=False)
    service_time = models.DateTimeField('time applied')
    service_status = models.CharField(max_length=1, choices=STATUS_TYPES)
    service_app = models.ForeignKey(App, on_delete=models.CASCADE)
    service_account = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
    service_qrcode = models.CharField(max_length=200)

    def has_expired(self):
        now = timezone.now()
        return now >= self.service_time + datetime.timedelta(minutes=1)
