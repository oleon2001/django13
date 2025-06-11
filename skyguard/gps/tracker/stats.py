#!/usr/bin/python
# -*- coding: utf-8 -*-
# stats process

import sys
import os
import io
import datetime,traceback
from geopy.point import Point as gPoint
from geopy.distance import distance as geoLen
from pytz import utc, timezone

os.environ['DJANGO_SETTINGS_MODULE'] = 'sites.www.settings'
path = '/home/django13/skyguard'
if path not in sys.path:
    sys.path.append(path)

from django.db import transaction, DatabaseError, IntegrityError, connection
from django.contrib.gis.geos import Point
from django.conf import settings
import gps.tracker.models as tracker
import gps.udp.models as udp
import math

import django.utils.tzinfo


settings.DEBUG = False
SESSION_EXPIRE = datetime.timedelta(hours = 10)
TDELTA = datetime.timedelta(minutes = 5)
NOW = datetime.datetime.utcnow().replace(tzinfo = utc)
LocalTz = django.utils.tzinfo.LocalTimezone(datetime.datetime.now())

def getPeopleCount(sensor,start,end):
	ev0 = tracker.PsiWeightLog.objects.filter(sensor = sensor, date__lte = start).order_by("-date")
	ev1 = tracker.PsiWeightLog.objects.filter(sensor = sensor, date__lte = end).order_by("-date")
	try:
		cnts = ( int(ev1[0].psi1-ev0[0].psi1),int(ev1[0].psi2-ev0[0].psi2))
	except:
		cnts = (0,0)
	if cnts[0] == 0 and cnts[1] == 0:
		cnts = None
	return cnts

if __name__ == "__main__":
	print "started @", datetime.datetime.utcnow().replace(tzinfo = utc)
	avls = tracker.SGAvl.objects.filter(ruta__isnull = False).order_by("name")
	records = 0
	for i in avls:
		last = tracker.Stats.objects.filter(name = i.name).order_by("-date_end")
		if last:
			date_start = last[0].date_end.replace(tzinfo = LocalTz)
			date_start = utc.normalize(date_start)
		else:
			date_start = NOW-TDELTA
		try:
			tracks = tracker.Event.objects.filter(imei = i,date__gte = date_start,type = "TRACK").order_by("date")
			sensor_front = tracker.PsiCal.objects.get(imei = i,offpsi1 = 1)
			sensor_back = tracker.PsiCal.objects.get(imei = i,offpsi1 = 2)
			people_front = getPeopleCount(sensor_front.sensor,date_start,NOW)
			people_back = getPeopleCount (sensor_back.sensor, date_start,NOW)
			odom = 0
			stats = tracker.Stats(name = i.name, ruta = i.ruta, economico = i.economico, date_start = date_start,
				date_end = NOW, speed_avg = 0, sub_del =0, sub_tra =0, baj_del =0, baj_tra=0)
			stats.distancia = 0
			stats.latitud = i.position.y  *1000000
			stats.longitud = i.position.x *1000000
			if tracks: 
				p0 = gPoint(tracks[0].position.y, tracks[0].position.x)
				j = tracks[0]
				for j in tracks[1:]:
					p1 = gPoint(j.position.y, j.position.x)
					odom += geoLen(p0,p1).m
					p0 = p1
				#Round odom to nearest km
				odom +=501
				odom /=1000
				period = NOW-date_start
				if period.seconds:
					stats.speed_avg = odom*3600/period.seconds
				stats.distancia = odom
				stats.latitud = j.position.y  *1000000
				stats.longitud = j.position.x *1000000
			if people_front:
				stats.sub_del = people_front[0]
				stats.baj_del = people_front[1]
			if people_back:
				stats.sub_tra = people_back[0]
				stats.baj_tra = people_back[1]
				stats.baj_tra = people_back[1]
			if tracks or people_front or people_back:
				stats.save()
				records += 1
		except Exception as e:
			print "Exception on Bus: "+i.name
			print e
			traceback.print_exc()
			#raise
	print "Updated ",records," registers @",datetime.datetime.utcnow().replace(tzinfo = utc)

