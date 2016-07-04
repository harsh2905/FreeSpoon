# Free Spoon  

[![Build Status](https://travis-ci.org/codemeow5/FreeSpoon.svg?branch=dev)](https://travis-ci.org/codemeow5/FreeSpoon)

A group purchase website based on WeChat.

## Development Enviroment Install

### Prerequisites  

	sudo wget -qO- https://get.docker.com/ | sh  
	sudo pip install docker-compose  

### Copy config files  

	cp docker-compose.yml.development docker-compose.yml  
	cp smbkeys.template smbkeys  
	cp smbusers.template smbusers  
	cp sshkeys.template sshkeys  
	cp sshkeys web/sshkeys

### Download git repository  

	git clone https://github.com/cuilyGitHub/FreeSpoonUI /your/path/FreeSpoonUI  

### Modify config  

> docker-compose.yml  

	web:  
	  volumes:  
	    - /your/path:/FreeSpoonUI  
	nginx:  
	  environment:  
	    - DOMAINNAME=yourdomain  
	db:  
	  environment:  
	    - MYSQL_ROOT_PASSWORD=123456  
	freespoon:  
	  volumes:  
	    - /your/path:/FreeSpoon  
	  environment:  
	    ...  

### Migrate data  

Copy data json files to /freespoon_data  
Copy media files to /freespoon_media  

### Run  

> freespoon  

	python manage.py migrate  
	export ENV...   
	mysql -hdb -uroot -p123456 -DFreeSpoon < ./views.sql  
	python manage.py createsuperuser  
	python manage.py runserver 0.0.0.0:80  

> web  

	npm install  
	gulp run  

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

