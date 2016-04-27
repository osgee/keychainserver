from django import forms
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import generic

from keychain.models import Account
from keychain.models import App
from keychain.models import User


class AccountForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(AccountForm, self).__init__(*args, **kwargs)
        self.fields['account_app'].choices = [(a.app_id, a.app_name) for a in App.objects.all()]

    account_username = forms.CharField(max_length=50)
    account_password = forms.CharField(max_length=50)
    # account_password = forms.CharField(max_length = 50, widget=forms.PasswordInput)
    account_app = forms.ChoiceField(widget=forms.Select(attrs={'class': 'required'}), choices=())


class ListView(generic.ListView):
    template_name = 'keychain/web/user/account/list.html'
    context_objext_name = 'account_list'

    def set_queryset(self):
        # not implemented yet!
        return Account.objects.all()[:5]


def add_account(request):
    if 'user_id' in request.session:
        user_id = request.session['user_id']
        user_password_plain = request.session['user_password_plain']
        user = User.objects.get(user_id=user_id)
    else:
        return HttpResponseRedirect('../')
    if request.method == 'POST':
        account_form = AccountForm(request.POST)
        if account_form.is_valid():
            account_username = account_form.cleaned_data['account_username']
            account_password = account_form.cleaned_data['account_password']
            app_id = account_form.cleaned_data['account_app']
            account_app = App.objects.get(app_id=app_id)
            account = Account(account_username=account_username, account_password=account_password,
                              account_app=account_app, account_user=user)
            account.encrypt_save(user_password_plain)
            return HttpResponseRedirect('/keychain/web/user/')
    account_form = AccountForm()
    return render(request, 'keychain/web/user/account/add.html', {
        'account_form': account_form,
    })


def delete_account(request, account_id):
    if 'user_id' in request.session:
        user_id = request.session['user_id']
        user = User.objects.get(user_id=user_id)
    else:
        return HttpResponseRedirect('/keychain/web/user/')
    try:
        a = Account.objects.get(account_user=user, account_id=account_id)
        a.delete()
    except Account.DoesNotExist:
        pass
    return HttpResponseRedirect('/keychain/web/user/')


def update_account(request, account_id):
    if 'user_id' in request.session:
        user_id = request.session['user_id']
        user_password_plain = request.session['user_password_plain']
        user = User.objects.get(user_id=user_id)
    else:
        return HttpResponseRedirect('/keychain/web/user/')
    if request.method == "POST":
        account_form = AccountForm(request.POST)
        if account_form.is_valid():
            account_username = account_form.cleaned_data['account_username']
            account_password = account_form.cleaned_data['account_password']
            app_id = account_form.cleaned_data['account_app']
            account_app = App.objects.get(app_id=app_id)
            account = Account(account_user=user, account_id=account_id)
            account.account_username = account_username
            account.account_password = account_password
            account.account_app = account_app
            account.encrypt_save(user_password_plain)
            return HttpResponseRedirect('/keychain/web/user/')
    account = Account.objects.get(account_user=user, account_id=account_id)
    account = account.decrypt(user_password_plain)
    account_form = AccountForm(
        initial={'account_username': account.account_username, 'account_password': account.account_password,
                 'account_app': account.account_app.app_id})
    return render(request, 'keychain/web/user/account/update.html', {
        'account_form': account_form,
        'account_id': account_id,
    })
