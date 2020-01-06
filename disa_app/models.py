# -*- coding: utf-8 -*-

import datetime, json, logging, os, pprint
from django.conf import settings as project_settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
from django.http import HttpResponseRedirect

from django.db.models.signals import post_save
from django.dispatch import receiver


log = logging.getLogger(__name__)


class UserProfile( models.Model ):
    """
    - from <https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html#onetoone>
    - reminder: if I know I'll need to access UserProfile entries...
      `users = User.objects.all().select_related('profile')`
      ...to minimize extra db queries.
    """
    user = models.OneToOneField( User, on_delete=models.CASCADE, related_name='profile' )
    old_db_id = models.IntegerField( blank=True, null=True )


## auto create and save UserProfile entries

@receiver( post_save, sender=User )
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver( post_save, sender=User )
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
