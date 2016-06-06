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
	parent = models.ForeignKey('MobUser', on_delete=models.CASCADE, null=True)
	#name = models.CharField(max_length=100, null=True, blank=True)
	#avatar = models.ImageField(upload_to='avatars', null=True, blank=True)
	create_time = models.DateTimeField(auto_now=True)

	is_active = models.BooleanField(default=True)
	is_admin = models.BooleanField(default=False)
	objects = MobUserManager()

	def __unicode__(self):
		return self.mob

	def get_full_name(self):
		return self.mob

	def get_short_name(self):
		return self.mob

	def has_perm(self, perm, obj=None):
		return True

	def has_module_perms(self, app_label):
		return True

	@property
	def is_staff(self):
		return self.is_admin

	@property
	def real_mob(self):
		if self.parent:
			return self.parent.mob
		return self.mob

        def real_wx_extra_data(self):
		#if not hasattr(self, 'mob_user'):
		#	return None
		#self = self.mob_user
		if not self:
			return None
                extra_data = None
                socialaccounts = self.socialaccount_set.all()
                for socialaccount in socialaccounts:
                        provider = socialaccount.provider
                        if provider == 'weixin': # Could be configuration
                                extra_data = socialaccount.extra_data
                                if extra_data:
                                        break
                if extra_data:
                        return extra_data
                else:
                        children = self.mobuser_set.all()
                        for child in children:
                                extra_data = child.get_real_wx_extra_data()
                                if extra_data:
                                        break
                return extra_data

	@property
        def real_wx_nickname(self):
                extra_data = self.real_wx_extra_data()
                if extra_data:
                        return extra_data.get('nickname', None)
                return None

	@property
        def real_wx_headimgurl(self):
                extra_data = self.real_wx_extra_data()
                if extra_data:
                        return extra_data.get('headimgurl', None)
                return None




