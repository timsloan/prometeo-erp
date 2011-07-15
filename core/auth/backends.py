#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This file is part of the prometeo project.

This program is free software: you can redistribute it and/or modify it 
under the terms of the GNU Lesser General Public License as published by the
Free Software Foundation, either version 3 of the License, or (at your
option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
more details.

You should have received a copy of the GNU Lesser General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>
"""

__author__ = 'Emanuele Bertoldi <emanuele.bertoldi@gmail.com>'
__copyright__ = 'Copyright (c) 2011 Emanuele Bertoldi'
__version__ = '0.0.2'

# Inspired by http://djangoadvent.com/1.2/object-permissions/

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from models import ObjectPermission

class ObjectPermBackend(object):
    supports_object_permissions = True
    supports_anonymous_user = True

    def authenticate(self, username, password):
        return None

    def has_perm(self, user_obj, perm, obj=None):
        if not user_obj.is_authenticated():
            user_obj = User.objects.get(pk=settings.ANONYMOUS_USER_ID)

        if obj is None:
            return False

        ct = ContentType.objects.get_for_model(obj)

        try:
            perm = perm.split('.')[-1].split('_')[0]
        except IndexError:
            return False

        p = ObjectPermission.objects.filter(content_type=ct, object_id=obj.id, user=user_obj)

        return p.filter(**{'can_%s' % perm: True}).exists()

