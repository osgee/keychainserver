import datetime
import json
import math
import re
import time
import uuid

from django import forms
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils import timezone

from keychain import captcha as captcha_generator
from keychain import cryptool
from keychain.models import Account, User, Service

# Create your views here.

account_type_default = 1
account_type_user_name = 1
account_type_user_email = 2
account_type_user_cellphone = 3
account_type_cellphone_scan = 4


class UserForm(forms.Form):
    user_name = forms.CharField(max_length=50)
    password = forms.CharField(max_length=50, widget=forms.PasswordInput)
    captcha = forms.CharField(max_length=4)


class UserSignUpForm(forms.Form):
    user_name = forms.CharField(max_length=50)
    password = forms.CharField(max_length=50, widget=forms.PasswordInput)
    password_repeat = forms.CharField(max_length=50, widget=forms.PasswordInput)
    captcha = forms.CharField(max_length=4)


def next_captcha():
    app_dir = 'keychain/static/'
    captcha_dir = 'keychain/cache/captcha/'
    captcha = captcha_generator.getcaptcha()
    captcha_id = uuid.uuid4().hex
    captcha_path = captcha_dir + captcha_id + '.png'
    captcha[0].save(app_dir + captcha_path)
    return captcha_path, captcha[1]


def set_cookie(response, user):
    if user.user_type == account_type_cellphone_scan:
        pass
    dt = timezone.now() + datetime.timedelta(minutes=30)
    time_now = math.floor(time.mktime(dt.timetuple()))
    response.set_cookie('account_type', user.user_type, expires=dt, domain='localhost')
    response.set_cookie('time', time_now, expires=dt, domain='localhost')
    d = {}
    d['time'] = time_now
    d['password'] = user.user_password_plain
    if user.user_type == account_type_user_name:
        d['user_name'] = user.user_name
    if user.user_type == account_type_user_email:
        d['user_name'] = user.user_email
    if user.user_type == account_type_user_cellphone:
        d['user_name'] = user.user_cellphone
    if user.user_type == account_type_default:
        d['user_name'] = user.user_name
    user_password_json = json.dumps(d)
    user_password_crypt = cryptool.encrypt_rsa_base64(user_password_json, 'public_key_py.pem')
    response.set_cookie('user_password_crypt', user_password_crypt, expires=dt, domain='localhost')
    sign = cryptool.digest_sha256(str(user.user_type) + str(time_now) + user_password_crypt)
    response.set_cookie('signature', sign, expires=dt, domain='localhost')
    return response


def index(request):
    user = None
    if 'account_type' in request.COOKIES and 'user_password_crypt' in request.COOKIES:
        account_type = int(request.COOKIES['account_type'])
        user_password_crypt = request.COOKIES['user_password_crypt']
        signature = request.COOKIES['signature']
        time_request = request.COOKIES['time']
        sign = cryptool.digest_sha256(str(account_type) + str(time_request) + user_password_crypt)
        if sign == signature:
            user_password_json = cryptool.decrypt_rsa_base64(user_password_crypt, 'private_key_py.pem')
            user_password_dict = json.loads(user_password_json)
            time_in = user_password_dict['time']
            password = user_password_dict['password']
            user_name = user_password_dict['user_name']
            dt = timezone.now()
            time_now = math.floor(time.mktime(dt.timetuple()))
            if time_now < time_in:
                user_password = password
                user = User(user_password=user_password)
                if account_type == account_type_user_name:
                    user.user_name = user_name
                elif account_type == account_type_user_email:
                    user.user_email = user_name
                elif account_type == account_type_user_cellphone:
                    user.user_cellphone = user_name
                else:
                    user.user_name = user_name
                user.user_type = account_type
                # print('in time')
                # print(password)
                user = user.get_by_password()
                if user is not None:
                    request.session['user_password_plain'] = password
    if user is not None:
        account_list = Account.objects.filter(account_user=user)
        return render(request, 'keychain/web/user/index.html', {
            'user_name': user.get_name(),
            'account_list': account_list,
        })
    return render(request, 'keychain/web/user/index.html', {})


def signout(request):
    try:
        del request.session['user_id']
        del request.session['user_password_plain']
    except KeyError as e:
        pass
    response = render(request, 'keychain/web/user/index.html', {})
    if 'user_name' in request.COOKIES:
        user_name = request.COOKIES['user_name']
        response.delete_cookie('user_name')
        # response.delete_cookie('user_cookie')
        response.delete_cookie('user_password_crypt')

    return response


def get_account_type(s):
    if isEmail(s):
        return account_type_user_email
    elif isCellphone(s):
        return account_type_user_cellphone
    elif isUsername(s):
        return account_type_user_email
    else:
        return account_type_default


def isEmail(s):
    m = re.match(r'^(\w)+(\.\w+)*@(\w)+((\.\w+)+)$', s)
    if m:
        return True
    else:
        return False


def isCellphone(s):
    m = re.match(r'^((13[0-9])|(15[^4,\D])|(18[0,5-9]))\d{8}$', s)
    if m:
        return True
    else:
        return False


def isUsername(s):
    m = re.match(r'(\w|\d){6,20}', s)
    if m:
        return True
    else:
        return False


def signin(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        if user_form.is_valid():
            user_name = user_form.cleaned_data['user_name']
            user_password = user_form.cleaned_data['password']
            captcha = user_form.cleaned_data['captcha'].lower()
            if 'captcha' in request.session and request.session['captcha'] == captcha:
                del request.session['captcha']
                user_password_plain = user_password
                user = User(user_password=user_password)
                account_type = get_account_type(user_name)
                if account_type == account_type_user_name:
                    user.user_name = user_name
                elif account_type == account_type_user_email:
                    user.user_email = user_name
                elif account_type == account_type_user_cellphone:
                    user.user_cellphone = user_name
                else:
                    user.user_name = user_name
                user.user_type = account_type
                user = user.get_by_password()
                if user is not None:
                    request.session['user_id'] = user.user_id.hex
                    request.session['user_password_plain'] = user_password_plain
                    response = HttpResponseRedirect('../')
                    user.user_type = account_type
                    set_cookie(response, user)
                    return response
                else:
                    err_message = 'Account Does Not Exist, Please Sign Up!'
            else:
                err_message = 'Captcha Is False!'
            user_form = UserForm(initial={'user_name': user_name})
        else:
            err_message = ''
    else:
        user_form = UserForm()
        err_message = ''
    captcha = next_captcha()
    request.session['captcha'] = captcha[1].lower()

    return render(request, 'keychain/web/user/signin.html', {
        'user_form': user_form,
        'captcha_url': captcha[0],
        'err_message': err_message,
    })


def signinquick(request, service_id, service_secret):
    if request.method == 'GET':
        s = Service.objects.get(service_id)
        if not s.has_expired():
            if s.service_status=='C' and s.service_secret.hex==service_secret:
                user = s.service_account.account_user
                if user is not None:
                    request.session['user_id'] = user.user_id.hex
                    response = HttpResponseRedirect('../')
                    user.user_type = account_type_cellphone_scan
                    set_cookie(response, user)
                    return response


def signup(request):
    if request.method == 'POST':
        user_form = UserSignUpForm(request.POST)
        if user_form.is_valid():
            user_name = user_form.cleaned_data['user_name']
            password = user_form.cleaned_data['password']
            password_repeat = user_form.cleaned_data['password_repeat']
            captcha = user_form.cleaned_data['captcha'].lower()
            if 'captcha' in request.session and request.session['captcha'] == captcha:
                del request.session['captcha']
                if password == password_repeat:
                    user = User(user_password=password)
                    account_type = get_account_type(user_name)
                    if account_type == account_type_user_name:
                        user.user_name = user_name
                    elif account_type == account_type_user_email:
                        user.user_email = user_name
                    elif account_type == account_type_user_cellphone:
                        user.user_cellphone = user_name
                    else:
                        user.user_name = user_name
                    user.user_type = account_type
                    if not user.has_signed_up():
                        user.encrypt_save();
                        user.user_password_plain = password
                        response = HttpResponseRedirect('../index', {
                            'signup': True,
                        })
                        request.session['user_id'] = user.user_id.hex
                        set_cookie(response, user)
                        return response
                    else:
                        err_message = 'Username ' + user_name + ' Has Already Signed Up!'
                else:
                    err_message = 'Password Is Inconsistent!'
            else:
                err_message = 'Captcha Is False!'
            user_form = UserSignUpForm(initial={'user_name': user_name})
        else:
            err_message = ''
    else:
        user_form = UserSignUpForm()
        err_message = ''

    captcha = next_captcha()
    request.session['captcha'] = captcha[1].lower()

    return render(request, 'keychain/web/user/signup.html', {
        'user_form': user_form,
        'captcha_url': captcha[0],
        'err_message': err_message,
    })
