Free Spoon - An amazing project.
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
	    - MYSQL_ROOT_PASSWORD=1a2z3b4y5c6x  
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

## Production Enviroments Install  

### Download project sources  

	git clone --recursive https://github.com/codemeow5/FreeSpoon.git  /usr/local/FreeSpoon  

### Copy config files  

	cp docker-compose.yml.production docker-compose.yml  
	cp Dockerfile.production Dockerfile  

### Configuration  

> docker-compose.yml  

	db:  
	  environment:  
	    - MYSQL_ROOT_PASSWORD=123456  
	freespoon:  
	  environment:  
	    ...  

### Pull data  

pull data files to /freespoon_data  
pull media files to /freespoon_media  

### Run  

	docker-compose up  

### Create Database (Optional)  

	create database FreeSpoon character set utf8;

### Migrate Database

	python manage.py makemigrations  
	python manage.py migrate

### Import & Export Data  

	python manage.py dumpdata authentication > /your/path/authentication.json  
	python manage.py dumpdata -e business.purchasedproducthistory business > /your/path/business.json  
	python manage.py dumpdata socialaccount > /your/path/socialaccount.json  
	python manage.py loaddata /your/path/authentication.json  
	python manage.py loaddata /your/path/business.json  
	python manage.py loaddata /your/path/socialaccount.json  

### Configuration Social App Key

> Media Platform: Mozilla  
> App: iOS  

