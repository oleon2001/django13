#from django.db import models
from django.contrib.gis.db import models
from django.db import models as old_models
from django.utils.translation import ugettext_lazy as _

from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
import json
import math
from geopy import Point as gPoint
from geopy.distance import distance
from datetime import time,datetime,date
from pytz import utc, timezone
from django.conf import settings

localtz = timezone(settings.TIME_ZONE)

# Create your models here.

class CarPark(models.Model):
	name = models.CharField(_('name'), max_length = 30)
	description = models.TextField(_('description'), max_length = 200, null = True)

class CarLane(models.Model):
	prefix = models.CharField(_('prefix'), max_length = 5)
	slots = models.SmallIntegerField(_('slots'), default = 62)
	start = models.PointField(_('start'), null = False, editable = False)
	end = models.PointField(_('end'), null = False, editable = False)
	single = models.BooleanField(_('single'), null = False, default = False)
	park = models.ForeignKey(CarPark, null = False)
	objects = models.GeoManager()

class CarSlot(models.Model):
	lane = models.ForeignKey(CarLane, null = False)
	number = models.SmallIntegerField(_('number'))
	position = models.PointField(_('position'), null = False, editable = False)
	carSerial = models.CharField(_("serial"),null = True, max_length = 80, db_index = True)
	carDate = models.DateTimeField(_('date'), null = True, editable = False)
	def __unicode__(self):
		return u'{0}{1:03}'.format(self.lane.prefix,self.number)
	class Meta:
		unique_together = (('lane','number'),)
		#index_together = [('lane','number'),]
	objects = models.GeoManager()
	def number1(self): return self.number + 1

class GridlessCar(models.Model):
	position = models.PointField(_('position'), null = False, editable = False)
	carSerial = models.CharField(_("serial"),null = True, max_length = 80, db_index = True)
	carDate = models.DateTimeField(_('date'), null = True, editable = False)
	objects = models.GeoManager()

	def carDateTz(self):
		if not self.carDate.tzinfo:
			self.carDate = utc.localize(self.carDate)
		return self.carDate.astimezone(localtz)

class DemoCar(models.Model):
	position = models.PointField(_('position'), null = False, editable = False)
	carSerial = models.CharField(_("serial"),null = True, max_length = 80, db_index = True)
	carDate = models.DateTimeField(_('date'), null = True, editable = False)
	objects = models.GeoManager()

	def carDateTz(self):
		if not self.carDate.tzinfo:
			self.carDate = utc.localize(self.carDate)
		return self.carDate.astimezone(localtz)

def getgPoint(p):
	return gPoint(p.y,p.x)

def getBearing(p1,p2):
	lat1 = math.radians(p1.y)
	lat2 = math.radians(p2.y)
	dLon = math.radians(p2.x - p1.x)
	y = math.sin(dLon) * math.cos(lat2)
	x = math.cos(lat1)*math.sin(lat2) - math.sin(lat1)*math.cos(lat2)*math.cos(dLon)
	return math.degrees(math.atan2(y, x))

def loadJsonLanes(fname,cp = None):
	if cp is None: cp = CarPark.objects.all()[0]
	f = open(fname)
	lanes = json.load(f)
	f.close()
	for l in lanes:
		prefix = l["name"].split()[1]
		if prefix == u'A':
			slots = 31
			single = True
		else:
			slots = 62
			single = False
		start = Point(l["start"]["x"],l["start"]["y"])
		end = Point(l["end"]["x"],l["end"]["y"])
		cl = CarLane(prefix = prefix, slots = slots, start = start, end = end, single = single, park = cp)
		cl.save()

def generateSlots(cp = None,offset = 3.0,turn = 90.0):
	if not cp:
		cp = CarPark.objects.all()[0]
	lanes = CarLane.objects.filter(park = cp)
	for l in lanes:
		bearing = getBearing(l.start,l.end)
		dist = distance(getgPoint(l.start),getgPoint(l.end))
		off = distance(meters = offset)
		hinc = dist / l.slots
		if l.single: hinc /= 2.0
		print l.prefix,bearing,dist.m
		p0 = hinc.destination(getgPoint(l.start),bearing)
		hinc *= 2
		if l.single: inc = 1
		else: inc = 2
		for i in range(0,l.slots,inc):
			pos = off.destination(p0,bearing+90.0)
			cs = CarSlot(number = i, lane = l,position = Point(pos.longitude,pos.latitude))
			cs.save()
			if not l.single:
				pos = off.destination(p0,bearing-90.0)
				cs = CarSlot(number = i+1, lane = l,position = Point(pos.longitude,pos.latitude))
				cs.save()
			p0 = hinc.destination(p0,bearing)

def parseCsvLine(l):
	v = l.split(",")
	serial = v[0]
	position = Point(float(v[2]),float(v[1]))
	dt = " ".join(v[3:]).split("+")[0]
	dt = datetime.strptime(dt,"%Y-%m-%d %H:%M:%S")
	dt.replace(tzinfo = utc)
	return dict(serial = serial, pos = position, date = dt)

def loadGridless(fname):
	f = open(fname)
	data = []
	for l in f:
		data.append(parseCsvLine(l))
	f.close()
	for d in data:
		if d["serial"] != "NuevaFila" and d["serial"] != "FinDeFila" and (len(d["serial"]) == 18 or len(d["serial"]) == 8):
				gl = GridlessCar(carSerial = d["serial"], carDate = d["date"],position = d["pos"])
				gl.save()
		else:
			print "Rejected",d

def loadCsv(fname):
	f = open(fname)
	data = []
	for l in f:
		data.append(parseCsvLine(l))
	f.close()
	lane = None
	number = 0
	inc = 0
	for d in data:
		if d["serial"] == "NuevaFila":
			lane = None
			number = 0
			inc = 0
			try:
				lane = CarLane.objects.get(start__distance_lte=(d["pos"],D(m=10)))
				print "Found at start of lane: ", lane.prefix, "of park", lane.park.description
				number = 0
				inc = 1
			except CarLane.DoesNotExist:
				try:
					lane = CarLane.objects.get(end__distance_lte=(d["pos"],D(m=10)))
					print "Found at end of lane: ", lane.prefix, "of park", lane.park.description
					number = lane.slots - 1
					inc = -1
				except CarLane.DoesNotExist:
					print "Car lane not found, discard data"
		elif d["serial"] == "EspacioVacio":
			if lane: number += inc
		elif d["serial"] == "FinDeFila":
			if lane:
				if number == -1 or number == lane.slots:
					print "Fila {0} del lote {1} completa".format(lane.prefix,lane.park.description)
				else:
					print "Fila {0} del lote {1} INCOMPLETA".format(lane.prefix,lane.park.description)
			lane = None
			number = 0
			inc = 0
		else:
			if lane:
				if number == -1 or number >= lane.slots:
					print "Fila {0} del lote {1} EXCEDIDA".format(lane.prefix,lane.park.description)
				else:
					slot = CarSlot.objects.get(lane = lane, number = number)
					slot.carSerial = d["serial"]
					slot.carDate = d["date"]
					slot.save()
					number += inc


def cleatLot(park = None):
	if park is None: park = CarPark.objects.all()[0]
	slots = CarSlot.objects.filter(lane__park = park)
	for s in slots:
		s.carSerial = None
		s.carDate = datetime.now(utc)
		s.save()

def glFix(fname):
	f = open(fname)
	cars = []
	for l in f:
		#print l,l.split()
		for s in l.split():
			q = GridlessCar.objects.filter(carSerial__icontains = s)
			for i in q:
				cars.append(i)
	cars.sort(lambda x,y: x.id - y.id)
	for i in cars:
		print i.id

#from gps.assets.models import *
#CarPark(name = "TRACO1", description = "Tracomex Patio #1").save()
#loadJsonLanes("/home/bcantu/SkyGuard/gps/assets/tracomex.json")
#generateSlots()
#loadCsv("/home/bcantu/SkyGuard/cfe3.csv")
#loadGridless("/home/bcantu/chrysler.csv")
#glFix("/home/bcantu/fixlist.txt")

#cierre13_23
#Rejected {'date': datetime.datetime(2013, 4, 3, 16, 28, 14), 'serial': 'I3C7WRTAL3DG5298', 'pos': <Point object at 0x2a65b50>}
#Rejected {'date': datetime.datetime(2013, 4, 3, 17, 49, 23), 'serial': 'I3C7WRMBL6DG523025U', 'pos': <Point object at 0x2b05490>}
