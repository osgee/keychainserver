import datetime
import json
import math
import time

from django.http import HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from keychain import cryptool
from keychain.models import User


def setcookie(response, user):
    dt = timezone.now() + datetime.timedelta(days=5)
    # user_cookie = uuid.uuid4().hex
    # user.user_cookie = user_cookie
    # user.user_cookie_time = dt
    # user.save()
    # response.set_cookie('user_cookie', user_cookie, expires=dt, domain='localhost')
    response.set_cookie('user_name', user.user_name, expires=dt, domain='localhost')
    d = {}
    d['time'] = math.floor(time.mktime(dt.timetuple()))
    d['password'] = user.user_password_plain
    user_password_json = json.dumps(d)
    user_password_crypt = cryptool.encrypt_rsa_base64(user_password_json, 'public_key_py.pem')
    response.set_cookie('user_password_crypt', user_password_crypt, expires=dt, domain='localhost')
    return response


@csrf_exempt
def decodersa(request):
    if request.method == 'POST':
        body = request.body.decode('utf-8')
        req = json.loads(body)
        key = req['key']
        password = req['password']
        password = cryptool.decrypt_rsa_base64(password, 'private_key_py.pem')
        response = HttpResponse("succeed! is " + password)
        user = User.objects.get(user_name='taofeng')
        user.user_password_plain = 'ft1234'
        setcookie(response, user)
        return response
    return HttpResponse("failed!")


@csrf_exempt
def decodeaes(request):
    if request.method == 'POST':
        body = request.body.decode('utf-8')
        req = json.loads(body)
        key = req['key']
        password = req['password']
        password = cryptool.decrypt_aes(password, key)
        return HttpResponse("succeed! is " + password)
    return HttpResponse("failed!")


@csrf_exempt
def userstatus(request):
    if request.method == 'POST':
        body = request.body.decode('utf-8')
        userin = User()
        userin.load_from_json(body)
        user = User.objects.get(user_name='taofeng')
        userjson = user.to_json()
        return HttpResponse(userjson)
    return HttpResponse("failed!")
