from allauth.socialaccount.providers.weixin_mp.views import WeixinOAuth2Adapter
from allauth.socialaccount.providers.weixin_mp.client import WeixinOAuth2Client
from rest_auth.registration.views import SocialLoginView

from allauth.socialaccount.providers.oauth2.views import (OAuth2Adapter,
                                                          OAuth2LoginView,
                                                          OAuth2CallbackView)
from rest_auth.views import LoginView as BaseLoginView

from django.shortcuts import render

# Create your views here.

class WeixinLogin(SocialLoginView):
    adapter_class = WeixinOAuth2Adapter
    callback_url = 'http://yijiayinong.com/profile'
    client_class = WeixinOAuth2Client

class WeixinOAuth2ClientMixin(object):

    def get_client(self, request, app):
        pdb.set_trace()
        callback_url = reverse(self.adapter.provider_id + "_callback")
        protocol = (
            self.adapter.redirect_uri_protocol or
            app_settings.DEFAULT_HTTP_PROTOCOL)
        callback_url = build_absolute_uri(
            request, callback_url,
            protocol=protocol)
        provider = self.adapter.get_provider()
        scope = provider.get_scope(request)
        client = WeixinOAuth2Client(
            self.request, app.client_id, app.secret,
            self.adapter.access_token_method,
            self.adapter.access_token_url,
            callback_url,
            scope)
        return client

class WeixinOAuth2LoginView(WeixinOAuth2ClientMixin, OAuth2LoginView):
    pass


class WeixinOAuth2CallbackView(WeixinOAuth2ClientMixin, OAuth2CallbackView):
    pass

oauth2_login = WeixinOAuth2LoginView.adapter_view(WeixinOAuth2Adapter)
oauth2_callback = WeixinOAuth2CallbackView.adapter_view(WeixinOAuth2Adapter)

# Auth API

class LoginView(BaseLoginView):
	pass
