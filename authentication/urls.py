from django.conf.urls import url, include

from rest_auth.views import (
	LoginView,
	UserDetailsView,
)

from rest_framework_jwt.views import refresh_jwt_token

from .views import *

urlpatterns = [
	url(r'^refresh$', refresh_jwt_token, name='refresh'),
]
