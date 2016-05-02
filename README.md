# Free Spoon  

A group purchase website based on WeChat.

### Install

	sudo apt-get install mysql-server mysql-client -y  
	sudo apt-get install python-pip python-dev -y  
	sudo pip install django  
	sudo apt-get install libmysqlclient-dev -y  
	sudo pip install MySQL-python  
	sudo pip install qrcode  
	sudo pip install Pillow  
	sudo pip install openpyxl  

### About install Pillow

	$ sudo apt-get install libtiff5-dev libjpeg8-dev zlib1g-dev \  
		libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python-tk  

Visiting https://pillow.readthedocs.org/en/3.0.0/installation.html#linux-installation  

### Create Database

	create database FreeSpoon character set utf8;

### Migrate Database

	python manage.py makemigrations  
	python manage.py migrate
