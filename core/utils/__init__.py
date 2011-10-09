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

from django.db import models
from django.db.models import Q, query
from django.db.models import fields as django_fields
from django.utils.datastructures import SortedDict

def filter_objects(request, model_or_queryset=None, fields=[], exclude=[]):
    matches = []
    model = None
    object_list = None
    queryset = None

    if isinstance(model_or_queryset, query.QuerySet):
        model = model_or_queryset.model
        object_list = model_or_queryset

    elif issubclass(model_or_queryset, models.Model):
        model = model_or_queryset
        object_list = model.objects.all()

    if not object_list.query.can_filter():
        pks = [instance.pk for instance in object_list]
        object_list = model.objects.filter(pk__in=pks)
    
    filter_fields = get_filter_fields(request, model, fields, exclude)
    
    if request.method == 'POST':
        queryset = []
        for f, value in filter_fields:
            if value is not None:
                if isinstance(f, django_fields.related.RelatedField):
                    pass # Fail silently.
                else:
                    queryset.append(Q(**{"%s__startswith" % f.name: value}) | Q(**{"%s__endswith" % f.name: value}))

    if (queryset is not None):
        matches = object_list.filter(*queryset)
    else:
        matches = object_list

    try:
        order_by = request.GET['order_by']
        matches = matches.order_by(order_by)
    except:
        pass
        
    return [f.name for f, value in filter_fields], SortedDict(filter_fields), matches
    
def get_filter_fields(request, model, fields, exclude):
    filter_fields = [(f, filter_field_value(request, f)) for f in model._meta.fields if is_visible(f.name, fields, exclude)]
    return filter_fields

def is_visible(field, fields=[], exclude=[]):
    return (len(fields) == 0 or field in fields) and field not in exclude

def filter_field_value(request, field):
    name = field.name
    if request.POST.has_key("sub_%s" % name):
        return None
    elif request.POST.has_key(name):
        return request.POST[name]
    elif request.POST.has_key(u'filter_field') and request.POST[u'filter_field'] == name:
        return request.POST[u'filter_query']
    return None

def clean_referer(request):
    try:
        referer = request.META['HTTP_REFERER']
    except:
        referer = '/'
    return referer.replace("http://", "").replace(request.META['HTTP_HOST'], "")
