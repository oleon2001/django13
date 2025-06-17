#!/usr/bin/python
# -*- coding: utf-8 -*-
# SGAvl server


#from django.db import models
from django.contrib.gis.db import models
from django.contrib.auth.models import User #as auth_User, UserManager
from django.contrib.sites.models import Site
from django.conf import settings
from django.db.models.signals import post_save
from django.contrib.sites.managers import CurrentSiteManager
from django.utils.translation import ugettext_lazy as _
from datetime import datetime,date,time

# Create your models here.
MODEL_CHOICES = (
	(0,'Desconocido'),
	(1,'SGB4612'),
	(2,'SGP4612'),
	)

GSM_OPERATOR = (
	(0,'Telcel'),
	(1,'Movistar'),
	(2,'IusaCell'),
	)

RUTA_CHOICES = (
	( 92,"Ruta 4"),
	(112,"Ruta 6"),
	(114,"Ruta 12"),
	(115,"Ruta 31"),
	( 90,"Ruta 82"),
	( 88,"Ruta 118"),
	(215,"Ruta 140"),
	( 89,"Ruta 202"),
	(116,"Ruta 207"),
	( 96,"Ruta 400"),
	( 97,"Ruta 408"),
	)

RUTA_CATALOG = {
	"4":92,
	"6":112,
	"12":114,
	"31":115,
	"82":90,
	"118":88,
	"140":215,
	"202":89,
	"207":116,
	"400":96,
	"408":97
}

EDOCIVIL_CHOICES = (
	("SOL", "Soltero"),
	("CAS", "Casado"),
	("VIU", "Viudo"),
	("DIV", "Divorciado")
)
#lass User(auth_User):
#	user = models.OneToOneField(auth_User, parent_link = True)
#	site = models.ForeignKey(Site, null = False, default = settings.SITE_ID)
#	objects = UserManager()

class Stats(models.Model):
	name = models.CharField(_('name'),null = False, max_length = 20)
	ruta = models.IntegerField(null = False,blank = False, choices = RUTA_CHOICES)
	economico = models.IntegerField(null = False, blank = False)
	date_start = models.DateTimeField(_('date'), null = True, editable = False)
	date_end = models.DateTimeField(_('date'), null = False, editable = False)
	latitud = models.IntegerField(null = True, blank = True)
	longitud = models.IntegerField(null = True, blank = True)
	distancia = models.IntegerField(null = True, blank = True)
	sub_del = models.IntegerField(null = True, blank = True)
	baj_del = models.IntegerField(null = True, blank = True)
	sub_tra = models.IntegerField(null = True, blank = True)
	baj_tra = models.IntegerField(null = True, blank = True)
	speed_avg = models.IntegerField(null = True, blank = True)

class Device(models.Model):
	imei = models.BigIntegerField(_('imei'), primary_key = True, editable = False)
	name = models.CharField(_('name'), max_length = 20)
	position = models.PointField(_('position'), null = True, editable = False)
	speed = models.SmallIntegerField(_('speed'), default = 0, editable = False)
	course = models.SmallIntegerField(_('course'), default = 0, editable = False)
	date = models.DateTimeField(_('date'), null = True, editable = False)
	lastLog = models.DateTimeField(_('last update'), null = True, editable = False)
	owner = models.ForeignKey(User, null = True, default = None, blank = True)
	icon = models.CharField(_('icon'), max_length = 64, default = 'camion100sff.png')
	type = models.CharField(_('type'), max_length = 64, default = 'tracker.SGAvl', editable = False)
	odom = models.IntegerField(_('odometer'), default = 0, editable = False, null = True)
	altitude = models.IntegerField(_('altitude'), editable = False, null = True, default = 0)

	objects = models.GeoManager()

	class Meta:
		unique_together = (('name','owner'),)
		verbose_name = _('device')
		verbose_name_plural = _('devices')
		ordering = ('imei',)

	def __unicode__(self):
		return u'{0:015}-{1}'.format(self.imei,self.name)

class SimCard(models.Model):
	iccid = models.BigIntegerField(primary_key = True)
	imsi = models.BigIntegerField(null = True)
	provider = models.SmallIntegerField(default = 0, choices = GSM_OPERATOR)
	phone = models.CharField(max_length = 16)
	def __unicode__(self):
		return u'{0}'.format(self.phone)

class SGAvl(Device):
	serial = models.IntegerField(_('serial'), max_length = 10, default=0)#, editable = False)
	model = models.SmallIntegerField(_('model'), default = 0, choices = MODEL_CHOICES)#, editable = False)
	swversion = models.CharField(_('version'), max_length = 4, default ='----')#, editable = False)
	inputs = models.IntegerField(_('inputs'), default = 0, editable = False)
	outputs = models.IntegerField(_('outputs'), default = 0, editable = False)
	alarmMask = models.IntegerField(_('alarm mask'), default = 0x0141, editable = False)
	alarms = models.IntegerField(_('alarms'), default = 0, editable = False)
	fwFile = models.CharField(_('firmware file'), max_length = 16, blank = True)
	newOutputs = models.IntegerField(_('new outputs'), null = True, blank = True, editable = False)
	newInflags = models.CharField(_('new inbputs'), max_length = 32, blank = True, editable = False)
	lastFwUpdate = models.DateTimeField(_('last firmware update'), null = True, blank = True)#, editable = False)
	harness = models.ForeignKey('tracker.SGHarness', null = False, blank = False)
	comments = models.TextField(_('Comments'), null = True, blank = True)
	sim = models.OneToOneField(SimCard, blank = True, null = True, on_delete=models.SET_NULL, related_name = 'avl')

	ruta = models.IntegerField(null = True,blank = True, choices = RUTA_CHOICES)
	economico = models.IntegerField(null = True, blank = True)

	objects = models.GeoManager()

	def __unicode__(self):
		return u"%s(%s): %015d - %s"%(self.model,self.swversion,self.imei,self.name)

	class Meta:
		verbose_name = _('device')
		verbose_name_plural = _('devices')

AVL_COMMANDS = (
	(1, "Send SMS"),
	(2, "Send Position"),
	(3, "Execute Command"),
)

AVL_DIRECTION = (
    (0, "From Server"),
    (1, "From Device")
)
    
AVL_STATUS = (
    (0, "Pending"),
    (1, "Sucess"),
    (2, "Failed")
)

import pytz
def nowtz():
    return datetime.now(tz = pytz.UTC)
    
class ServerSMS(models.Model):
    imei = models.ForeignKey(SGAvl,null=False)
    command = models.SmallIntegerField('Command', default = 0, choices = AVL_COMMANDS)
    direction = models.SmallIntegerField('Command', default = 0, choices = AVL_DIRECTION)
    status = models.SmallIntegerField('Command', default = 0, choices = AVL_STATUS)
    msg = models.CharField(_('mensaje'),max_length=160, default="Nuevo Mensaje")
    sent = models.DateTimeField(_("enviado"),null=True)
    issued = models.DateTimeField(_("enviado"),null=False, default = nowtz)

    def __unicode__(self):
        return u"To: %s Test: %s"%(self.imei.name,self.msg)

class SGHarness(models.Model):
	name = models.CharField(_('name'), max_length = 32, unique = True)
	in00 = models.CharField(_('input 0'), max_length = 32, default = "PANIC")
	in01 = models.CharField(_('input 1'), max_length = 32, default = "IGNITION")
	in02 = models.CharField(_('input 2'), max_length = 32)
	in03 = models.CharField(_('input 3'), max_length = 32)
	in04 = models.CharField(_('input 4'), max_length = 32)
	in05 = models.CharField(_('input 5'), max_length = 32)
	in06 = models.CharField(_('input 6'), max_length = 32, default = "BAT_DOK")
	in07 = models.CharField(_('input 7'), max_length = 32, default = "BAT_CHG")
	in08 = models.CharField(_('input 8'), max_length = 32, default = "BAT_FLT")
	in09 = models.CharField(_('input 9'), max_length = 32)
	in10 = models.CharField(_('input 10'), max_length = 32)
	in11 = models.CharField(_('input 11'), max_length = 32)
	in12 = models.CharField(_('input 12'), max_length = 32)
	in13 = models.CharField(_('input 13'), max_length = 32)
	in14 = models.CharField(_('input 14'), max_length = 32)
	in15 = models.CharField(_('input 15'), max_length = 32)
	out00 = models.CharField(_('output 0'), max_length = 32, default = "MOTOR")
	out01 = models.CharField(_('output 1'), max_length = 32)
	out02 = models.CharField(_('output 2'), max_length = 32)
	out03 = models.CharField(_('output 3'), max_length = 32)
	out04 = models.CharField(_('output 4'), max_length = 32)
	out05 = models.CharField(_('output 5'), max_length = 32)
	out06 = models.CharField(_('output 6'), max_length = 32)
	out07 = models.CharField(_('output 7'), max_length = 32)
	out08 = models.CharField(_('output 8'), max_length = 32)
	out09 = models.CharField(_('output 9'), max_length = 32)
	out10 = models.CharField(_('output 10'), max_length = 32)
	out11 = models.CharField(_('output 11'), max_length = 32)
	out12 = models.CharField(_('output 12'), max_length = 32)
	out13 = models.CharField(_('output 13'), max_length = 32)
	out14 = models.CharField(_('output 14'), max_length = 32)
	out15 = models.CharField(_('output 15'), max_length = 32)
	inputCfg = models.CharField(_('input configuration'), max_length = 32)

	def __unicode__(self):
		return u"{0}".format(self.name)

	def GetInputCableName(self,bit):
		if bit==0: return self.in00 or 'IN00'
		if bit==1: return self.in01 or 'IN01'
		if bit==2: return self.in02 or 'IN02'
		if bit==3: return self.in03 or 'IN03'
		if bit==4: return self.in04 or 'IN04'
		if bit==5: return self.in05 or 'IN05'
		if bit==6: return self.in06 or 'IN06'
		if bit==7: return self.in07 or 'IN07'
		if bit==8: return self.in08 or 'IN08'
		if bit==9: return self.in09 or 'IN09'
		if bit==10: return self.in10 or 'IN10'
		if bit==11: return self.in11 or 'IN11'
		if bit==12: return self.in12 or 'IN12'
		if bit==13: return self.in13 or 'IN13'
		if bit==14: return self.in14 or 'IN14'
		if bit==15: return self.in15 or 'IN15'
		return ''

	def GetOutputCableName(self,bit):
		if bit==0: return self.out00 or 'OUT00'
		if bit==1: return self.out01 or 'OUT01'
		if bit==2: return self.out02 or 'OUT02'
		if bit==3: return self.out03 or 'OUT03'
		if bit==4: return self.out04 or 'OUT04'
		if bit==5: return self.out05 or 'OUT05'
		if bit==6: return self.out06 or 'OUT06'
		if bit==7: return self.out07 or 'OUT07'
		if bit==8: return self.out08 or 'OUT08'
		if bit==9: return self.out09 or 'OUT09'
		if bit==10: return self.out10 or 'OUT10'
		if bit==11: return self.out11 or 'OUT11'
		if bit==12: return self.out12 or 'OUT12'
		if bit==13: return self.out13 or 'OUT13'
		if bit==14: return self.out14 or 'OUT14'
		if bit==15: return self.out15 or 'OUT15'
		return ''

	class Meta:
		verbose_name = _('harness')
		verbose_name_plural = _('devices')

class AccelLog(models.Model):
	imei = models.ForeignKey('tracker.Device', null = False)
	position = models.PointField(editable = False)
	date = models.DateTimeField(null = False, editable = False)
	duration = models.DecimalField(null = False, max_digits=6, decimal_places =4, default = 0.0)
	errDuration = models.DecimalField(null = False, max_digits=6, decimal_places =4, default = 0.0)

	entry = models.DecimalField(null = False, max_digits=6, decimal_places =4, default = 0.0)
	errEntry = models.DecimalField(null = False, max_digits=6, decimal_places =4, default = 0.0)
	peak = models.DecimalField(null = False, max_digits=6, decimal_places =4, default = 0.0)
	errExit = models.DecimalField(null = False, max_digits=6, decimal_places =4, default = 0.0)
	exit = models.DecimalField(null = False, max_digits=6, decimal_places =4, default = 0.0)
	
	objects = models.GeoManager()

	def __unicode__(self):
		return u"{0}-{1}".format(self.id, self.imei)

	class Meta:
		ordering = ('imei','date')


class Event(models.Model):
	imei = models.ForeignKey('tracker.Device', null = False)
	type = models.CharField(max_length = 16)
	position = models.PointField(null = True, editable = False)
	speed = models.SmallIntegerField(default = 0, editable = False)
	course = models.SmallIntegerField(default = 0, editable = False)
	date = models.DateTimeField(null = False, editable = False)
	odom = models.IntegerField(_('odometer'), editable = False, null = True, default = 0)
	altitude = models.IntegerField(_('altitude'), editable = False, null = True, default = 0)

	objects = models.GeoManager()

	def __unicode__(self):
		return u"{0}-{1}".format(self.id, self.imei)

class GsmEvent(Event):
	source = models.CharField(max_length=20)
	text = models.CharField(max_length=180)

class IOEvent(Event):
	inputs = models.IntegerField(max_length = 16)
	outputs= models.IntegerField(max_length = 16)
	indelta= models.IntegerField(default = 0, editable = False, null = False)
	outdelta= models.IntegerField(default = 0, editable = False, null = False)
	alarmdelta= models.IntegerField(default = 0, editable = False, null = False)
	changes= models.TextField()

class ResetEvent(Event):
	reason = models.CharField(max_length = 180)

class GeoFence(models.Model):
	name = models.CharField(_('name'), max_length = 32, unique = True)
	fence = models.PolygonField(_('polygon'), null = False)
	owner = models.ForeignKey(User, null = False, blank = False)
	base = models.IntegerField(null = True,blank = True, choices = RUTA_CHOICES)

	objects = models.GeoManager()
	def __unicode__(self):
		return u"{0}".format(self.name)

class PsiWeightLog(models.Model):
	imei = models.ForeignKey('tracker.Device', null = False)
	sensor = models.CharField(_('sensor serial'),max_length = 32,null =False)
	date = models.DateTimeField(null = False, editable = False)
	psi1 = models.DecimalField(_('Psi1'), max_digits = 20, decimal_places=6, editable = False)
	psi2 = models.DecimalField(_('Psi1'), max_digits = 20, decimal_places=6, editable = False)

class PsiCal(models.Model):
	imei = models.ForeignKey('tracker.Device', null = False)
	sensor = models.CharField(_('sensor serial'),max_length = 32,null =False)
	offpsi1 = models.DecimalField(_('Psi1'), max_digits = 10, decimal_places=6, editable = False)
	offpsi2 = models.DecimalField(_('Psi1'), max_digits = 10, decimal_places=6, editable = False)
	mulpsi1 = models.DecimalField(_('Psi1'), max_digits = 10, decimal_places=6, editable = False)
	mulpsi2 = models.DecimalField(_('Psi1'), max_digits = 10, decimal_places=6, editable = False)
	name = models.CharField('Nombre',max_length = 32)

def SensorSetup():
	for i in PsiCal.objects.all():
		if len(i.sensor)==8:
			try:
				r = PsiWeightLog.objects.filter(sensor__startswith=i.sensor)[2]#.order_by('-date')[0]
				w = PsiWeightLog.objects.filter(sensor=r.sensor).order_by('-date')[0]
				i.sensor=w.sensor
				i.save()
				print(i.sensor, w.date)
			except:
				print(i.sensor)

class Tracking(models.Model):
	tracking = models.CharField(_("tracking"), max_length = 40, unique = True)
	imei = models.ForeignKey('tracker.Device', null = False)
	stopFence = models.ForeignKey(GeoFence, related_name = 'stop_set')
	fences = models.ManyToManyField(GeoFence, related_name = 'events_set')
	start = models.DateTimeField(null = False, editable = False, db_index = True)
	stop = models.DateTimeField(null = True, editable = False, db_index = True)
	def __unicode__(self):
		return u"{0}".format(self.tracking)

class AlarmLog(models.Model):
	imei = models.ForeignKey('tracker.Device', null=False)
	sensor = models.CharField(_('sensor serial'), max_length=32, null=False)
	date = models.DateTimeField(null=False, editable=False)
	cksum = models.IntegerField()
	duration = models.IntegerField()
	comment = models.CharField(max_length=24)
	def __unicode__(self):
		return u'Sensor alarm {2}:{0} @ {1:%H:%M:%S}'.format(self.sensor[:8],self.date,self.comment)

	class Meta:
		get_latest_by = 'date'


class Tarjetas(models.Model):
	nlinea = models.TextField(db_column = "nombre_linea")
	nramal = models.TextField(db_column = "nombre_ramal")
	linea = models.IntegerField(db_column = "linea")
	economico = models.IntegerField(db_column = "economico")
	date = models.DateTimeField(db_column = "dfecha",primary_key = True)
	tipo = models.IntegerField(db_column = "itipo")
	unidad = models.CharField(db_column = "cunidad",max_length = 12)
	tarjeta =  models.IntegerField(db_column = "itarjeta")
	monto = models.IntegerField(db_column = "imonto")

	class Meta:
		db_table = 'tbltarjetas'
		managed = False
		get_latest_by = 'date'
		ordering = ('linea','economico','date')
		app_label = 'feria'

class Overlays(models.Model):
	name = models.CharField(_('name'), max_length = 32, unique = True)
	geometry = models.LineStringField(_('line'), null = False)
	owner = models.ForeignKey(User, null = False, blank = False)
	base = models.IntegerField(null = True,blank = True, choices = RUTA_CHOICES)

	objects = models.GeoManager()
	def __unicode__(self):
		return u"{0}".format(self.name)

class AddressCache(models.Model):
	position = models.PointField(null=True, editable=False, spatial_index = True)
	date = models.DateTimeField(null=False, editable=False)
	text = models.TextField(null = False, default = "N/D", editable = True )

	objects = models.GeoManager()

	def __unicode__(self):
		return u"[{0:.4f}:{1:.4f}]{2}".format(self.position.y,self.position.x, self.text)

		
class Driver(models.Model):
	name = models.CharField(_('Nombre'), max_length = 40)
	middle = models.CharField(_('A. Paterno'), max_length = 40)
	last = models.CharField(_('A. Materno'), max_length = 40)
	birth = models.DateField(_('F. de nacimiento'))
	cstatus = models.CharField(_('Estado Civil'), max_length = 40, choices = EDOCIVIL_CHOICES)
	payroll = models.CharField('Nómina', max_length = 40)
	socials = models.CharField(_('Seguro social'), max_length = 40)
	taxid = models.CharField(_('RFC'), max_length = 40)
	license = models.CharField(_('Licencia'), max_length = 40, null = True, blank = True)
	lic_exp = models.DateField("Vencimiento", null = True, blank = True) 
	address = models.TextField('Dirección')
	phone = models.CharField('Teléfono', max_length = 40)
	phone1 = models.CharField('Teléfono 1', max_length = 40, null = True, blank = True)
	phone2 = models.CharField('Teléfono 2', max_length = 40, null = True, blank = True)
	active = models.BooleanField('Activo', default = True)
	
	def __unicode__(self):
		return u"{0} {1}, {2}".format(self.middle,self.last, self.name)
	class Meta:
		verbose_name = _('Chofer')
		verbose_name_plural = _('Choferes')
		ordering = ('middle','last','name')

class TicketsLog(models.Model):
	id = models.AutoField("Folio",primary_key=True)
	data = models.TextField('Data')
	ruta = models.IntegerField(null = True,blank = True, choices = RUTA_CHOICES)
	date = models.DateTimeField(_('Inicio'),null=True)
	
class TicketDetails(models.Model):
	id = models.AutoField("Folio",primary_key=True)
	imei = models.ForeignKey('tracker.Device', null=False)
	date = models.DateTimeField(_('Inicio'),null=True)
	chofer = models.CharField(_('Nombre'), max_length = 80)
	total = models.IntegerField()
	recibido = models.IntegerField()
	ticket = models.TextField('Data')

class TimeSheetCapture(models.Model):
	id = models.AutoField("Folio",primary_key=True)
	name = models.CharField(_('name'),null = False, max_length = 20)
	date = models.DateTimeField(_('Inicio'),null=True)
	chofer = models.CharField(_('Nombre'), max_length = 80)
	vueltas = models.IntegerField()
	times = models.TextField()

def NamedAvls(s):
	return SGAvl.objects.filter(name__startswith = s).order_by("name")

def SensorHell(avls):
	hell = []
	for i in avls:
		cals = PsiCal.objects.filter(imei = i).order_by("offpsi1")
		for j in cals:
			j.avl = i
			try:
				j.latest = PsiWeightLog.objects.filter(sensor = j.sensor).latest("date")
			except:
				j.latest = None
			hell.append(j)
	for i in hell:
		if i.latest:
			status = datetime.now() - i.latest.date
		else:
			status = "NEVER"
		print(i.avl.name,"{0:9s}".format( i.name), status)
	return hell

padd = """
def alarmOrigin(cksum,plist = []):
	alarms = AlarmLog.objects.filter(cksum = cksum)
	for i in alarms:
		sensors = PsiCal.objects.filter(imei = i.imei).values_list("sensor",flat=True)
		if i.sensor in sensors:
			plist.append(i.id)
	return plist

from django.contrib.gis.geos.linestring import LineString
from gps.tracker.views import *
l = getLineStrings('APOYO A RUTA 118.kml')
u = User.objects.get(username = 'ruta400')
a = []
for i in l[0].coords:
 a.append((i[0],i[1]))

c1 = tuple(a)
a = []
for i in l[1].coords:
 a.append((i[0],i[1]))

c2 = tuple(a)
l1 = LineString(c1)
l2 = LineString(c2)
o1 = Overlays(name = "R118.1",owner = u, base = 89, geometry = l1)
o2 = Overlays(name = "R118.2",owner = u, base = 89, geometry = l2)
"""
