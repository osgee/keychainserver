from io import BytesIO

import qrcode
from django import forms
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.utils import timezone
from django.views import generic
from django.views.decorators.csrf import csrf_exempt

from keychain.models import App, Service


baseurl = 'https://keychain-miui.c9users.io/keychain/app/service/'

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
            app = App(app_name=app_name)
            if not app.has_signed_up():
                app.app_publickey = app_publickey
                app.app_logo = app_logo
                app.save()
                return HttpResponseRedirect('/keychain/app/')
            else:
                app_form = AppForm()
                return render(request, 'keychain/app/signup.html', {
                    'err_message': 'App ' + app_name + ' has already signed up!',
                    'app_form': app_form,
                })
        else:
            app_form = AppForm()
            return render(request, 'keychain/app/signup.html', {
                'err_message': 'Invalid Request!',
                'app_form': app_form,
            })
    else:
        app_form = AppForm()
        return render(request, 'keychain/app/signup.html', {'app_form': app_form})

@csrf_exempt
def query(request, app_id, service_id):
    try:
        app = App.objects.get(app_id=app_id)
        s = Service.objects.get(service_id=service_id)
        s.has_expired()
        if request.method == 'GET':
            return render(request, 'keychain/user/client/qrcode.html', {
                    'service_qrcode': s.service_qrcode,
                    'app_service': '/keychain/app/service/'+app_id+'/',
                    'service_url': '/keychain/app/service/'+app_id+'/'+service_id+'/',
                    'service_status': s.service_status,
               })
        elif request.method == 'POST':
            return HttpResponse(s.service_status)
        else:
            return HttpResponse(-1)
        # return HttpResponse(mstream.getvalue(), "image/png")

    except App.DoesNotExist:
        return HttpResponse(-1)
    except Service.DoesNotExist:
        return HttpResponse(-1)
        
@csrf_exempt      
def redirect(request, app_id, service_id ):
    try:
        app = App.objects.get(app_id=app_id)
        s = Service.objects.get(service_id=service_id)
        s.has_expired()
        if request.method == 'GET':
            return render(request, 'keychain/user/client/qrcode.html', {
                    'service_qrcode': s.service_qrcode,
                    'app_service': '/keychain/app/service/'+app_id+'/',
                    'service_url': '/keychain/app/service/'+app_id+'/'+service_id+'/',
                    'service_status': s.service_status,
               })
        elif request.method == 'POST':
            return HttpResponse(s.service_status)
        else:
            return HttpResponse(-1)
        # return HttpResponse(mstream.getvalue(), "image/png")
    except App.DoesNotExist:
        return HttpResponse(-1)
    except Service.DoesNotExist:
        return HttpResponse(-1)

def service(request, app_id):
    try:
        app = App.objects.get(app_id=app_id)

        # urlbase = 'http://192.168.253.108/keychain/user/client/'
        s = Service(service_status='I', service_app=app)
        # url = urlbase + s.service_id.hex + '/'
        img = qrcode.make(s.service_id.hex)
        img_dir = 'keychain/static/'
        img_path = 'keychain/cache/qrcode/{0}'.format(s.service_id.hex + '.png')
        img.save(img_dir + img_path)
        mstream = BytesIO()
        img.save(mstream, "PNG")
        s.service_qrcode = img_path
        s.service_time = timezone.now()
        s.service_app = app
        s.save()
        # return render(request, 'keychain/user/client/qrcode.html', {
        #        'qrcode_path': img_path,
        #        'qrcode_link': url,

        #    })
        return HttpResponseRedirect('/keychain/app/service/'+app_id+'/'+s.service_id.hex+'/')

    except App.DoesNotExist:
        app_form = AppForm()
        return render(request, 'keychain/app/signup.html', {
            'app_form': app_form,
            'err_message': 'Please Sign Up First!'
        })
