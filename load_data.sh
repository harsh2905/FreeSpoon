#!/bin/bash

set -e

pushd /FreeSpoon

if [ -f ./data/authentication.json ]; then
	python manage.py loaddata ./data/authentication.json
	mv ./data/authentication.json ./data/authentication.json.used
fi
if [ -f ./data/socialaccount.json ]; then
	python manage.py loaddata ./data/socialaccount.json
	mv ./data/socialaccount.json ./data/socialaccount.json.used
fi
if [ -f ./data/business.json ]; then
	python manage.py loaddata ./data/business.json
	mv ./data/business.json ./data/business.json.used
fi

popd
