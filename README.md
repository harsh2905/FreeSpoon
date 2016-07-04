# Free Spoon  

[![Build Status](https://travis-ci.org/codemeow5/FreeSpoon.svg?branch=dev)](https://travis-ci.org/codemeow5/FreeSpoon)

A group purchase website based on WeChat.

### Install

	sudo wget -qO- https://get.docker.com/ | sh  
	sudo pip install docker-compose  

### Create Database

	create database FreeSpoon character set utf8;

### Migrate Database

	python manage.py makemigrations  
	python manage.py migrate

### Import & Export Data  

	python manage.py dumpdata -e business.purchasedproducthistory business > /data/business.json  
	python manage.py loaddata /your/path/business.json  

### Configuration Social App Key

> Media Platform: Mozilla  
> App: iOS  

