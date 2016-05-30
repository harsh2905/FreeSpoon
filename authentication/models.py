from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import (
	BaseUserManager,
	AbstractBaseUser
)

import pdb

# Create your models here.

class MobUserManager(BaseUserManager):
	
	def create_user(self, mob):
		user = self.model(mob=mob)
		user.save(using=self._db)
		return user

	def create_superuser(self, mob, password):
		user = self.model(mob=mob)
		user.set_password(password)
		user.is_admin = True
		user.save(using=self._db)
		return user

class MobUser(AbstractBaseUser):
	mob = models.CharField(max_length=20, unique=True)
	USERNAME_FIELD = 'mob'
	name = models.CharField(max_length=100, null=True, blank=True)
	avatar = models.ImageField(upload_to='avatars', null=True, blank=True)
	create_time = models.DateTimeField(auto_now=True)

	is_active = models.BooleanField(default=True)
	is_admin = models.BooleanField(default=False)
	objects = MobUserManager()

	def __unicode__(self):
		return self.mob

	def get_full_name(self):
		return self.name

	def get_short_name(self):
		return self.name

	def has_perm(self, perm, obj=None):
		return True

	def has_module_perms(self, app_label):
		return True

	@property
	def is_staff(self):
		return self.is_admin

