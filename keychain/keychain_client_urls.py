from django.conf.urls import url

from keychain.views.client import httptest
from keychain.views.client import userview
from keychain.views.client.user import accountview

app_name = 'client'

urlpatterns = [
    url(r'^httptest/decodersa/$', httptest.decodersa),
    url(r'^httptest/decodeaes/$', httptest.decodeaes),
    url(r'^httptest/userstatus/$', httptest.userstatus),

    # url(r'^user/$',userview.index, name='user_client_index'),
    # url(r'^user/index/$',userview.index, name='user_client_index'),
    url(r'^user/signin/$', userview.signin),
    url(r'^user/cookie/check/$', userview.chkcookie),
    url(r'^user/signup/$', userview.signup),
    url(r'^user/signout/$', userview.signout),
    url(r'^user/accounts/get/$', accountview.get_accounts),
    url(r'^user/account/get/$', accountview.get_account),
    url(r'^user/account/add/$', accountview.add_account),
    url(r'^user/account/delete/$', accountview.delete_account),
    url(r'^user/account/update/$', accountview.update_account),
    url(r'^user/apps/getall/$', userview.get_all_apps),
    url(r'^user/get/$', userview.get_user),
    # url(r'^user/set/$', userview.get_all_apps),
]
