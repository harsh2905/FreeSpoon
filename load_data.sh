#!/bin/bash

set -e

pushd /FreeSpoon

if [ -f ./data/basic.json ]; then
	python manage.py loaddata ./data/basic.json
fi
if [ -f ./data/auth.json ]; then
	python manage.py loaddata ./data/auth.json
fi

popd
