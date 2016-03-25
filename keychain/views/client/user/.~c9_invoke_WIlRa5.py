from django.shortcuts import render
from django.views import generic 
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt  
from django import forms

from keychain import cryptool
from keychain.models import Account
from keychain.models import App
from keychain.models import User
from keychain.views.client.userview import validate_request,status_response,encrypt_response
from django import forms

import json



@csrf_exempt
def get_account(request):
	if request.method == 'POST':
		isvalid,status_code,userdb,user,certjson,datajson = validate_request(request)
		if isvalid == False:
			return status_response(status_code)
		if userdb is None:
			return status_response(-3)
		data = {}
		accountjson = json.loads(datajson['account'])
		account = Account.objects.get(account_user=userdb,account_id=accountjson['account_id'])
		userjson = json.loads(datajson['user'])
		data['account'] = Account.to_JSON(account.decrypt(userjson['user_password']))
		return encrypt_response(data,certjson)
	return status_response(-6)



@csrf_exempt
def get_accounts(request):
	if request.method == 'POST':
		isvalid,status_code,userdb,user,certjson,datajson = validate_request(request)
		if isvalid == False:
			return status_response(status_code)
		if userdb is None:
			return status_response(-3)
		data = {}
		userjson = json.loads(datajson['user'])
		accounts = Account.objects.filter(account_user=userdb)
		if accounts is not None and accounts.count() > 0:
			l = []
			for account in accounts:
				l.append(Account.to_JSON(account.decrypt(userjson['user_password'])))
			accountsJson = json.dumps(l)
			data['accounts'] = accountsJson
		else:
			data['accounts'] = None
		return encrypt_response(data,certjson)
	return status_response(-6)

@csrf_exempt
def add_account(request):
	if request.method == 'POST':
		isvalid,status_code,userdb,user,certjson,datajson = validate_request(request)
		if isvalid == False:
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
			account = Account(account_username=account_username, account_password=account_password, account_user=account_user)
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
			account.acc
			data = {}
			data['account'] = account.to_JSON()
			return encrypt_response(data,certjson)
		return status_response(-3)
	return status_response(-6)


@csrf_exempt
def delete_account(request):
	if request.method == 'POST':
		isvalid,status_code,userdb,user,certjson, datajson = validate_request(request)
		if isvalid == False:
			return status_response(status_code)
		if userdb is not None:
			accountjson = json.loads(datajson['account'])
			account_id = accountjson['account_id']
			try:
				a = Account.objects.get(account_user=userdb,account_id=account_id)
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
		isvalid,status_code,userdb,user,certjson,datajson = validate_request(request)
		if isvalid == False:
			return status_response(status_code)
		accountjson = json.loads(datajson['account'])
		account_id = accountjson['account_id']
		if userdb is not None:
			try:
				account = Account.objects.get(account_user=userdb,account_id=account_id)
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
				return status_response(1)
			return status_response(-1)
		return status_response(-3)
	return status_response(-6)


