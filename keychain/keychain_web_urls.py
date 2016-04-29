from django.conf.urls import url

from keychain.views.web import userview as userwebview
from keychain.views.web.user import accountview as accountwebview

app_name = 'web'
urlpatterns = [
    url(r'^user/$', userwebview.index, name='user_index'),
    url(r'^user/index/$', userwebview.index, name='user_index'),
    url(r'^user/signin/$', userwebview.signin, name='user_signin'),
    url(r'^user/signin/(?P<service_id>\w{32})/(?P<service_secret>\w{32})/$', userwebview.signinquick, name='user_signin_quick'),
    url(r'^user/signup/$', userwebview.signup, name='user_signup'),
    url(r'^user/signout/$', userwebview.signout, name='user_signout'),
    url(r'^user/account/$', accountwebview.ListView.as_view(), name='user_account'),
    url(r'^user/account/add/$', accountwebview.add_account, name='user_add_account'),
    url(r'^user/account/delete/(?P<account_id>\w{32})/$', accountwebview.delete_account, name='user_delete_account'),
    url(r'^user/account/update/(?P<account_id>\w{32})/$', accountwebview.update_account, name='user_update_account'),
]
