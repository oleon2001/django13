#!/usr/bin/python
# -*- coding: utf-8 -*-
# Udp Models

from django.db import models
from gps.tracker.models import SGAvl
import random

random.seed()

class UdpSession(models.Model):
	#session = models.IntegerField('session',primary_key = True)
	session = models.AutoField('session',primary_key = True)
	imei = models.ForeignKey('tracker.Device',null=False, unique = True)
	expires = models.DateTimeField('expires',null = False)
	host = models.CharField("host",max_length = 128, null = False)
	port = models.IntegerField("port", null = False)
	lastRec = models.IntegerField("rec", default = 0)
	
	class Meta:
		ordering = ('imei',)
	def __unicode__(self):
		return u'Session {0:015}-{1:010}'.format(self.imei.imei,self.session)

