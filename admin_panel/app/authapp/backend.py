import json

import requests

import http

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
from django.conf import settings

User = get_user_model()


class AdminPanelAuthBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        url = settings.AUTH_API_LOGIN_URL
        payload = {'username': username, 'password': password}
        response = requests.post(url, data=payload)
        if response.status_code != http.HTTPStatus.OK:
            print('Invalid username or password')
            return None

        data = response.json()

        try:
            print(data)
            user, created = User.objects.get_or_create(id=data['id'])
            user.email = data.get('email')
            user.first_name = data.get('first_name')
            user.last_name = data.get('last_name')
            user.is_admin = 'admin' in data.get('roles')
            user.is_staff = 'admin' in data.get('roles')
            user.save()
        except Exception:
            print('Problems to save user')
            return None

        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            print('User not found')
            return None
