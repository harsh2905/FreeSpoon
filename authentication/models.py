from __future__ import unicode_literals

from django.db import models
from django.db.models import Q
from django.contrib.auth.models import (
	BaseUserManager,
	AbstractBaseUser
)
from allauth.socialaccount.models import SocialAccount

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
	mob = models.CharField(max_length=20, unique=False, null=True, blank=True)
	USERNAME_FIELD = 'mob'
	parent = models.ForeignKey('MobUser', on_delete=models.CASCADE, null=True)
	create_time = models.DateTimeField(auto_now=True)

	is_active = models.BooleanField(default=True)
	is_admin = models.BooleanField(default=False)
	objects = MobUserManager()

	def __unicode__(self):
		return '%s(%s)' % (self.mob, self.id)

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
	def associated(self):
		mob_users = None
		if self.parent is None:
			mob_users = MobUser.objects.filter(Q(id=self.id) 
				| Q(parent=self)) 
		else:
			mob_users = MobUser.objects.filter(Q(id=self.id) 
				| Q(parent=self) 
				| Q(parent=self.parent))
		return mob_users

	@property
	def real_mob(self):
		if self.parent:
			return self.parent.mob
		return self.mob

	@property
        def real_wx_extra_data(self):
		social_account = SocialAccount.objects.filter(user__in=self.associated).first()
		if hasattr(social_account, 'extra_data'):
			return social_account.extra_data
		return None

	@property
        def real_wx_nickname(self):
                extra_data = self.real_wx_extra_data
                if extra_data:
                        return extra_data.get('nickname', None)
                return None

	@property
        def real_wx_headimgurl(self):
                extra_data = self.real_wx_extra_data
                if extra_data:
                        return extra_data.get('headimgurl', None)
                return None

	@property
        def real_wx_openid(self):
                extra_data = self.real_wx_extra_data
                if extra_data:
                        return extra_data.get('openid', None)
                return None




