from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django import forms
from keychain.models import App, Service, Account, User
from django.db import models
from django.views import generic
import qrcode
import os
import datetime
import uuid
from keychain import captcha as captcha_generator

from io import BytesIO

from django.utils import timezone


# Create your views here.
class AppForm(forms.Form):
	app_name = forms.CharField(max_length=50)
	app_publickey = forms.FileField()
	app_logo = forms.ImageField()


class ListView(generic.ListView):
	template_name = 'keychain/app/list.html'
	context_object_name = 'app_list'

	def get_queryset(self):
		return App.objects.all()[:10]

def signup(request):
	if request.method == "POST":
		app_form = AppForm(request.POST, request.FILES)
		if app_form.is_valid():
			app_name = app_form.cleaned_data['app_name']
			app_publickey = app_form.cleaned_data['app_publickey']
			app_logo = app_form.cleaned_data['app_logo']
			app=App(app_name=app_name)
			if not app.has_signed_up():
				app.app_publickey =app_publickey
				app.app_logo = app_logo
				app.save()
				return HttpResponseRedirect('/keychain/app/')
			else:
				app_form = AppForm()
				return render(request,'keychain/app/signup.html', {
						'err_message': 'App '+app_name+' has already signed up!',
						'app_form': app_form,
					})
		else:
			app_form = AppForm()
			return render(request,'keychain/app/signup.html', {
						'err_message': 'Invalid Request!',
						'app_form': app_form,
					})
	else:
		app_form = AppForm()
		return render(request,'keychain/app/signup.html', {'app_form': app_form})

def service(request, app_id):
	try:
		app = App.objects.get(app_id=app_id)

		urlbase='http://192.168.253.108/keychain/user/client/'
		s =Service(service_status='I', service_app=app)
		url = urlbase+s.service_id.hex+'/'
		img = qrcode.make(url)
		img_dir = 'keychain/static/'
		img_path = 'keychain/cache/qrcode/{0}'.format(s.service_id.hex+'.png')
		img.save(img_dir+img_path)
		mstream = BytesIO()
		img.save(mstream, "PNG")
		s.service_qrcode=img_path
		s.service_time = timezone.now()
		s.save()
		# return render(request, 'keychain/user/client/qrcode.html', {
		#		'qrcode_path': img_path,
		#		'qrcode_link': url,

		#	})
		return HttpResponse(mstream.getvalue(), "image/png")

	except App.DoesNotExist:
		app_form = AppForm()
		return render(request,'keychain/app/signup.html', {
					'app_form': app_form,
					'err_message': 'Please Sign Up First!'
				})


		
		