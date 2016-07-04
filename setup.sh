#!/bin/bash

pushd /FreeSpoon/vendor/django-allauth
python setup.py develop
popd
pushd /FreeSpoon/vendor/django-rest-framework
python setup.py develop
popd
pushd /FreeSpoon/vendor/django-rest-framework-jwt
python setup.py develop
popd
pushd /FreeSpoon/vendor/django-rest-auth
python setup.py develop
popd
echo 'Setup success'
