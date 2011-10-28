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
from django.db.models import permalink
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from prometeo.core.models import Commentable

class Contact(models.Model):
    """Contact model.
    """
    firstname = models.CharField(max_length=255, verbose_name=_('firstname'))
    lastname = models.CharField(max_length=255, verbose_name=_('lastname'))
    nickname = models.SlugField(null=True, blank=True, verbose_name=_('nickname'))
    ssn = models.CharField(max_length=255, null=True, blank=True, verbose_name=_('SSN'))
    language = models.CharField(max_length=5, null=True, blank=True, choices=settings.LANGUAGES, default=settings.LANGUAGE_CODE, verbose_name=_("language"))
    timezone = models.CharField(max_length=20, null=True, blank=True, choices=settings.TIME_ZONES, default=settings.TIME_ZONE, verbose_name=_("timezone"))
    email = models.EmailField(max_length=255, null=True, blank=True, verbose_name=_('email'))
    url = models.URLField(max_length=255, null=True, blank=True, verbose_name=_('url'))
    addresses = models.ManyToManyField('addressing.Address', null=True, blank=True, verbose_name=_('addresses'))
    phone_numbers = models.ManyToManyField('addressing.PhoneNumber', null=True, blank=True, verbose_name=_('phone numbers'))
    main_address = models.ForeignKey('addressing.Address', null=True, blank=True, related_name=_('main_of_contact'), verbose_name=_('main address'))
    main_phone_number = models.ForeignKey('addressing.PhoneNumber', null=True, blank=True, related_name=_('main_of_contact'), verbose_name=_('main phone number'))
    user = models.ForeignKey('auth.User', blank=True, null=True, verbose_name=_('user account'))
    created = models.DateTimeField(auto_now_add=True, verbose_name=_('created on'))
    categories = models.ManyToManyField('taxonomy.Category', null=True, blank=True, verbose_name=_('categories'))
    tags = models.ManyToManyField('taxonomy.Tag', null=True, blank=True, verbose_name=_('tags'))

    class Meta:
        verbose_name = _('contact')
        verbose_name_plural = _('contacts')
        
    def __unicode__(self):
        return self.get_full_name()   

    @models.permalink
    def get_absolute_url(self):
        return ('contact_detail', (), {"id": self.pk})
    
    @models.permalink
    def get_edit_url(self):
        return ('contact_edit', (), {"id": self.pk})
    
    @models.permalink
    def get_delete_url(self):
        return ('contact_delete', (), {"id": self.pk})

    def get_full_name(self):
        return ' '.join([self.firstname, self.lastname])

    full_name = property(get_full_name)

class Partner(Commentable):
    """Partner model.
    """
    name = models.CharField(max_length=255, unique=True, verbose_name=_('name'))
    is_managed = models.BooleanField(default=False, verbose_name=_('managed?'))
    is_customer = models.BooleanField(default=False, verbose_name=_('customer?'))
    is_supplier = models.BooleanField(default=False, verbose_name=_('supplier?'))
    lead_status = models.CharField(max_length=10, null=True, blank=True, choices=settings.LEAD_STATUS_CHOICES, default=settings.LEAD_DEFAULT_STATUS, verbose_name=_('lead status'))
    vat_number = models.CharField(max_length=64, null=True, blank=True, unique=True, verbose_name=_('VAT number'))
    currency = models.CharField(max_length=3, choices=settings.CURRENCIES, default=settings.DEFAULT_CURRENCY, null=True, blank=True, verbose_name=_('currency'))
    language = models.CharField(max_length=5, null=True, blank=True, choices=settings.LANGUAGES, default=settings.LANGUAGE_CODE, verbose_name=_('language'))
    timezone = models.CharField(max_length=20, null=True, blank=True, choices=settings.TIME_ZONES, default=settings.TIME_ZONE, verbose_name=_('timezone'))    
    url = models.URLField(null=True, blank=True, verbose_name=_('url'))
    email = models.EmailField(null=True, blank=True, verbose_name=_('email'))
    addresses = models.ManyToManyField('addressing.Address', null=True, blank=True, verbose_name=_('addresses'))
    phone_numbers = models.ManyToManyField('addressing.PhoneNumber', null=True, blank=True, verbose_name=_('phone numbers'))
    main_address = models.ForeignKey('addressing.Address', null=True, blank=True, related_name=_('main_of_partner'), verbose_name=_('main address'))
    main_phone_number = models.ForeignKey('addressing.PhoneNumber', null=True, blank=True, related_name=_('main_of_partner'), verbose_name=_('main phone number'))
    contacts = models.ManyToManyField(Contact, through='partners.Job', null=True, blank=True, verbose_name=_('contacts'))
    description = models.TextField(null=True, blank=True, verbose_name=_('description'))
    assignee = models.ForeignKey('auth.User', related_name="assigned_partners", null=True, blank=True, verbose_name=_('assignee'))
    created = models.DateTimeField(auto_now_add=True, verbose_name=_('created on'))
    categories = models.ManyToManyField('taxonomy.Category', null=True, blank=True, verbose_name=_('categories'))
    tags = models.ManyToManyField('taxonomy.Tag', null=True, blank=True, verbose_name=_('tags'))
    dashboard = models.OneToOneField('widgets.Region', null=True, verbose_name=_("dashboard"))
    stream = models.OneToOneField('streams.Stream', null=True, verbose_name=_('stream'))

    class Meta:
        verbose_name = _('partner')
        verbose_name_plural = _('partners')
        
    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('partner_detail', (), {"id": self.pk})
    
    @models.permalink
    def get_edit_url(self):
        return ('partner_edit', (), {"id": self.pk})
    
    @models.permalink
    def get_delete_url(self):
        return ('partner_delete', (), {"id": self.pk})
        
class Job(models.Model):
    """Job model.
    """
    contact = models.ForeignKey(Contact, verbose_name=_('contact'))
    partner = models.ForeignKey(Partner, verbose_name=_('partner'))
    role = models.CharField(max_length=30, choices=settings.ROLES, default=settings.DEFAULT_ROLE, verbose_name=_('role'))
    notes = models.TextField(null=True, blank=True, verbose_name=_('notes'))
    created = models.DateTimeField(auto_now_add=True, verbose_name=_('created on'))
        
    def __unicode__(self):
        return _("%(contact)s as %(role)s") % {'contact': self.contact, 'role': self.get_role_display()}

    def get_absolute_url(self):
        if self.contact:
            return self.contact.get_absolute_url()
        elif self.partner:
            return self.partner.get_absolute_url()
        return ""
    
    @models.permalink
    def get_edit_url(self):
        return ('contact_edit_job', (), {"contact_id": self.contact.pk, "id": self.pk})
    
    @models.permalink
    def get_delete_url(self):
        return ('contact_delete_job', (), {"contact_id": self.contact.pk, "id": self.pk})
