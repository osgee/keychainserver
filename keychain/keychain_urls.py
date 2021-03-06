from django.conf.urls import url, include

from keychain import keychain_client_urls
from keychain import keychain_web_urls
from keychain.views import appview

app_name = 'keychain'
urlpatterns = [
    url(r'^web/', include(keychain_web_urls)),
    url(r'^client/', include(keychain_client_urls)),
    url(r'^app/$', appview.ListView.as_view(), name='app_list'),
    url(r'^app/signup/$', appview.signup, name='app_signup'),
    url(r'^app/service/(?P<app_id>\w{32})/$', appview.service, name='app_service'),
    url(r'^app/service/(?P<app_id>\w{32})/(?P<service_id>\w{32})/$', appview.query, name='service_query'),
]
