import json

from django.views.decorators.csrf import csrf_exempt

from keychain.models import Account
from keychain.models import App
from keychain.models import User
from keychain.models import Service
from keychain.views.client.userview import validate_request, status_response, encrypt_response

import re


@csrf_exempt
def query(request):
    if request.method == 'POST':
        valid, status_code, userdb, user, certjson, datajson = validate_request(request)
        if not valid:
            return status_response(status_code)
        if userdb is None:
            return status_response(-3)
        if not 'service_id' in certjson.keys():
            return status_response(-11)
        service_id = certjson['service_id']
        p = re.compile(r'\w*')
        if len(service_id)!=32 or not p.match(service_id):
            return status_response(-11)
        try:
            s = Service.objects.get(service_id=service_id)
            if not s.has_expired():
                s.service_status = 'S'
                s.save()
                data = {}
                accounts = Account.objects.filter(account_app=s.service_app,account_user=userdb)
                if accounts is not None and accounts.count() > 0:
                    l = []
                    for account in accounts:
                        l.append(account.to_json(False, False))
                    accountsjson = json.dumps(l)
                    data['service_accounts'] = accountsjson
                else:
                    data['service_accounts'] = None
                data['service'] = s.to_json()
                return encrypt_response(data, certjson)
            else:
                return status_response(-9)
        except Service.DoesNotExist:
            return status_response(-8)
        return encrypt_response(data, certjson)
    return status_response(-6)
    
    
@csrf_exempt
def confirm(request):
    if request.method == 'POST':
        valid, status_code, userdb, user, certjson, datajson = validate_request(request)
        if not valid:
            return status_response(status_code)
        if userdb is None:
            return status_response(-3)
        service_id = certjson['service_id']
        account_id = certjson['account_id']
        try:
            s = Service.objects.get(service_id=service_id)
            a = Account.objects.get(account_id=account_id)
            if not s.has_expired():
                s.service_status = 'C'
                s.service_account = a
                s.save()
                return status_response(1)
            else:
                return status_response(-9)
        except Service.DoesNotExist:
            return status_response(-8)
        return encrypt_response(data, certjson)
    return status_response(-6)


@csrf_exempt
def get_accounts(request):
    if request.method == 'POST':
        valid, status_code, userdb, user, certjson, datajson = validate_request(request)
        if not valid:
            return status_response(status_code)
        if userdb is None:
            return status_response(-3)
        data = {}
        userjson = json.loads(datajson['user'])
        accounts = Account.objects.filter(account_user=userdb)
        if accounts is not None and accounts.count() > 0:
            l = []
            for account in accounts:
                l.append(Account.to_json(account.decrypt(userjson['user_password'])))
            accountsJson = json.dumps(l)
            data['accounts'] = accountsJson
        else:
            data['accounts'] = None
        return encrypt_response(data, certjson)
    return status_response(-6)


@csrf_exempt
def add_account(request):
    if request.method == 'POST':
        valid, status_code, userdb, user, certjson, datajson = validate_request(request)
        if not valid:
            return status_response(status_code)
        if userdb is not None:
            userjsonstr = datajson['user']
            userjson = json.loads(userjsonstr)
            user_password = userjson['user_password']
            accountjson = json.loads(datajson['account'])
            account_username = accountjson['account_username']
            account_password = accountjson['account_password']

            user_id = accountjson['account_user']['user_id']
            account_user = User.objects.get(user_id=user_id)
            account = Account(account_username=account_username, account_password=account_password,
                              account_user=account_user)
            account_type = accountjson['account_type']
            account.account_type = account_type
            if 'account_app' in accountjson:
                app_id = accountjson['account_app']['app_id']
                account_app = App.objects.get(app_id=app_id)
                account.account_app = account_app
            if 'account_email' in accountjson:
                account.account_email = accountjson['account_email']
            if 'account_cellphone' in accountjson:
                account.account_cellphone = accountjson['account_cellphone']
            account.encrypt_save(user_password)
            account.decrypt(user_password)
            data = {}
            data['account'] = account.to_json()
            return encrypt_response(data, certjson)
        return status_response(-3)
    return status_response(-6)


@csrf_exempt
def delete_account(request):
    if request.method == 'POST':
        valid, status_code, userdb, user, certjson, datajson = validate_request(request)
        if not valid:
            return status_response(status_code)
        if userdb is not None:
            accountjson = json.loads(datajson['account'])
            account_id = accountjson['account_id']
            try:
                a = Account.objects.get(account_user=userdb, account_id=account_id)
                a.delete()
                return status_response(1)
            except Account.DoesNotExist:
                pass
            return status_response(-1)
        return status_response(-3)
    return status_response(-6)


@csrf_exempt
def update_account(request):
    if request.method == 'POST':
        valid, status_code, userdb, user, certjson, datajson = validate_request(request)
        if valid == False:
            return status_response(status_code)
        accountjson = json.loads(datajson['account'])
        account_id = accountjson['account_id']
        if userdb is not None:
            try:
                account = Account.objects.get(account_user=userdb, account_id=account_id)
            except Account.DoesNotExist:
                pass
            if account is not None:
                userjsonstr = datajson['user']
                userjson = json.loads(userjsonstr)
                user_password = userjson['user_password']
                accountjson = json.loads(datajson['account'])
                account_username = accountjson['account_username']
                account_password = accountjson['account_password']
                user_id = accountjson['account_user']['user_id']
                account_type = accountjson['account_type']
                account_user = User.objects.get(user_id=user_id)

                account.account_username = account_username
                account.account_password = account_password
                account.account_type = account_type

                if 'account_app' in accountjson:
                    app_id = accountjson['account_app']['app_id']
                    account_app = App.objects.get(app_id=app_id)
                    account.account_app = account_app
                if 'account_email' in accountjson:
                    account.account_email = accountjson['account_email']
                else:
                    account.account_email = None
                if 'account_cellphone' in accountjson:
                    account.account_cellphone = accountjson['account_cellphone']
                else:
                    account.account_cellphone = None
                account.encrypt_save(user_password)
                account.decrypt(user_password)
                data = {}
                data['account'] = account.to_json()
                return encrypt_response(data, certjson)
            return status_response(-1)
        return status_response(-3)
    return status_response(-6)
