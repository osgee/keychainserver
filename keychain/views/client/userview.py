import datetime
import json
import math
import threading
import time
import uuid

from django.http import HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from keychain import captcha as captcha_generator
from keychain import cryptool
from keychain import emailutil
from keychain.models import App, Account, User

account_type_user_name = 1
account_type_user_email = 2
account_type_user_cellphone = 3
account_type_cookie = 4


def next_captcha():
    app_dir = 'keychain/static/'
    captcha_dir = 'keychain/cache/captcha/'
    captcha = captcha_generator.getcaptcha()
    captcha_id = uuid.uuid4().hex
    captcha_path = captcha_dir + captcha_id + '.png'
    captcha[0].save(app_dir + captcha_path)
    return captcha_path, captcha[1]


@csrf_exempt
def signout(request):
    if request.method == 'POST':
        valid, status_code, userdb, user, certjson, datajson = validate_request(request)
        if not valid:
            return status_response(status_code)
        if userdb is not None:
            userdb.delete_cookie()
            return status_response(1)
        return status_response(-1)
    return status_response(-6)


def status_response(error_code):
    d = {}
    d['status_code'] = error_code
    print(error_code)
    return HttpResponse(json.dumps(d))


@csrf_exempt
def signin(request):
    if request.method == 'POST':
        valid, status_code, userdb, user, certjson, datajson = validate_request(request, False)
        if not valid:
            return status_response(status_code)
        if user is None:
            return status_response(-4)
        # TO DO chk device_id

        if userdb is not None:
            dt = timezone.now() + datetime.timedelta(days=5)
            userdb.user_cookie = uuid.uuid4()
            userdb.user_cookie_time = dt
            userdb.save()
            data = {}
            userdb.user_password = certjson['user_password']
            userjson = userdb.to_JSON()
            user.user_password = certjson['user_password']
            data['user'] = userjson

            accounts = Account.objects.filter(account_user=userdb)
            # print(dir(accounts))
            if accounts is not None and accounts.count() > 0:
                l = []
                for account in accounts:
                    l.append(Account.to_JSON(account.decrypt(certjson['user_password'])))
                accountsJson = json.dumps(l)
                data['accounts'] = accountsJson
            else:
                data['accounts'] = None

            apps = App.objects.all()
            if apps is not None and apps.count() > 0:
                l = []
                for app in apps:
                    l.append(App.to_JSON(app))
                appsJson = json.dumps(l)
                data['apps'] = appsJson
            else:
                data['apps'] = None
            return encrypt_response(data, certjson)
        else:
            return status_response(-1)
    return status_response(-6)


def validate_request(request, allowcookie=True):
    body = request.body.decode('utf-8')
    signreqjson = json.loads(body)
    sign_client = signreqjson['sign']
    reqjson = json.loads(signreqjson['data'])
    dt = timezone.now() + datetime.timedelta(days=1)
    time_server = math.floor(time.mktime(dt.timetuple()))
    time_client = reqjson['time']
    if time_server < time_client:
        return False, -5
    account_type = reqjson['account_type']
    cert_crypt_rsa = reqjson['cert_crypt_rsa']
    cert = cryptool.decrypt_rsa_base64(cert_crypt_rsa, 'private_key_py.pem')
    certjson = json.loads(cert)
    time_in_cert = certjson['time']
    if time_client != time_in_cert:
        return False, -3
    aes_key = certjson['aes_key']
    sign_server = cryptool.sign(signreqjson['data'], aes_key)
    if not sign_client == sign_server:
        return False, -8
    datajson = None
    if 'data_crypt_aes' in reqjson:
        data_crypt_aes = reqjson['data_crypt_aes']
        datajsonstring = cryptool.decrypt_aes(data_crypt_aes, aes_key)
        datajson = json.loads(datajsonstring)
    user = None
    userdb = None
    if allowcookie and account_type == account_type_cookie:
        user = User()
        user.user_id = uuid.UUID(certjson['user_id'])
        user.user_cookie = uuid.UUID(certjson['user_cookie'])
        user.user_type = account_type
    elif account_type == account_type_user_email:
        user = User()
        user.user_email = certjson['user_name']
        user.user_password = certjson['user_password']
        user.user_type = account_type
    elif account_type == account_type_user_cellphone:
        user = User()
        user.user_cellphone = certjson['user_name']
        user.user_password = certjson['user_password']
        user.user_type = account_type
    elif account_type == account_type_user_name:
        user = User()
        user.user_name = certjson['user_name']
        user.user_password = certjson['user_password']
        user.user_type = account_type
    if user is not None:
        userdb = user.get_by_password()
    return True, 1, userdb, user, certjson, datajson


def encrypt_response(data, certjson):
    datajson = json.dumps(data)

    data_crypt_aes = cryptool.encrypt_aes(datajson, certjson['aes_key'])
    response = {}
    response['status_code'] = 1
    response['data_crypt_aes'] = data_crypt_aes
    return HttpResponse(json.dumps(response))


@csrf_exempt
def chkcookie(request):
    if request.method == 'POST':
        valid, status_code, userdb, user, certjson, datajson = validate_request(request)
        if not valid:
            return status_response(status_code)
        if userdb is None:
            return status_response(-8)
        return status_response(1)
    return status_response(-6)


@csrf_exempt
def get_all_apps(request):
    if request.method == 'POST':
        valid, status_code, userdb, userdb, certjson, datajson = validate_request(request)
        if not valid:
            return status_response(status_code)
        aes_key = certjson['aes_key']
        if userdb is not None:
            response = {}
            response['status_code'] = 1
            data = {}
            apps = App.objects.all()
            if apps is not None and apps.count() > 0:
                l = []
                for app in apps:
                    l.append(App.to_JSON(app))
                appsJson = json.dumps(l)
                data['apps'] = appsJson
            else:
                data['apps'] = None
            return encrypt_response(data, certjson)
    return status_response(-6)


@csrf_exempt
def signup(request):
    if request.method == 'POST':
        valid, status_code, userdb, user, certjson, datajson = validate_request(request, False)
        if not valid:
            return status_response(status_code)
        if user is None:
            return status_response(-4)
        # TO DO chk device_id
        if 'device_id' in certjson:
            device_id = certjson['device_id']

        if user.has_signed_up() is False:
            dt = timezone.now() + datetime.timedelta(days=5)
            user.user_cookie = uuid.uuid4()
            user.user_cookie_time = dt
            user.user_password = certjson['user_password']
            if device_id is not None:
                user.user_device = device_id
            user = user.encrypt_save()
            if user.user_type == account_type_user_email:
                t = threading.Thread(target=emailutil.send, args=(user.user_email, user.user_email))
                t.setDaemon(True)
                t.start()
            # user.save()
            data = {}
            userjson = user.to_JSON()
            user.user_password = certjson['user_password']
            data['user'] = userjson

            accounts = Account.objects.filter(account_user=user)
            if accounts is not None and accounts.count() > 0:
                l = []
                for account in accounts:
                    l.append(Account.to_JSON(account.decrypt(certjson['user_password'])))
                accountsJson = json.dumps(l)
                data['accounts'] = accountsJson
            else:
                data['accounts'] = None

            apps = App.objects.all()
            if apps is not None and apps.count() > 0:
                l = []
                for app in apps:
                    l.append(App.to_JSON(app))
                appsJson = json.dumps(l)
                data['apps'] = appsJson
            else:
                data['apps'] = None
            return encrypt_response(data, certjson)
        else:
            return status_response(-2)
    return status_response(-6)


@csrf_exempt
def get_user(request):
    if request.method == 'POST':
        valid, status_code, userdb, user, certjson, datajson = validate_request(request, False)
        if not valid:
            return status_response(status_code)
        if user is None:
            return status_response(-4)

        if userdb is not None:
            if userdb.is_need_refresh_cookie():
                dt = timezone.now() + datetime.timedelta(days=5)
                userdb.user_cookie = uuid.uuid4()
                userdb.user_cookie_time = dt
                userdb.save()
            data = {}
            userdb.user_password = certjson['user_password']
            userjson = userdb.to_JSON()
            user.user_password = certjson['user_password']
            data['user'] = userjson

            accounts = Account.objects.filter(account_user=userdb)
            # print(dir(accounts))
            if accounts is not None and accounts.count() > 0:
                l = []
                for account in accounts:
                    l.append(Account.to_JSON(account.decrypt(certjson['user_password'])))
                accountsJson = json.dumps(l)
                data['accounts'] = accountsJson
            else:
                data['accounts'] = None

            apps = App.objects.all()
            if apps is not None and apps.count() > 0:
                l = []
                for app in apps:
                    l.append(App.to_JSON(app))
                appsJson = json.dumps(l)
                data['apps'] = appsJson
            else:
                data['apps'] = None
            return encrypt_response(data, certjson)
        else:
            return status_response(-1)
    return status_response(-6)
