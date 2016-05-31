from allauth.socialaccount.providers.weixin_mp.views import WeixinOAuth2Adapter
from allauth.socialaccount.providers.weixin_mp.client import WeixinOAuth2Client
from rest_auth.registration.views import SocialLoginView

from django.shortcuts import render

# Create your views here.

class WeixinLogin(SocialLoginView):
    adapter_class = WeixinOAuth2Adapter
    client_class = WeixinOAuth2Client
    callback_url = 'localhost:8000' # :(

