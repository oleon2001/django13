from django.contrib.gis.db import models
#from django.db import models

# from tracker.models import SGAvl
# Create your models here.

class Session(models.Model):
	start = models.DateTimeField(auto_now_add = True, db_index = True)
	end = models.DateTimeField(auto_now_add = True)
	ip = models.IPAddressField()
	port = models.IntegerField()
	dev = models.ForeignKey('tracker.SGAvl')
	bytes = models.PositiveIntegerField(default = 0)
	packets = models.PositiveIntegerField(default = 0)
	records = models.PositiveIntegerField(default = 0)
	events = models.PositiveIntegerField(default = 0)

	def __unicode__(self):
		return u"From: %s:%d %d packets, %d records, %d bytes, %d events"%(self.ip,self.port,self.packets,self.records,self.bytes,self.events)

class Packet(models.Model):
	session = models.ForeignKey(Session)
	request = models.TextField()
	response = models.TextField()

	def __unicode__(self):
		return u"Packet(%d):%s"%(len(self.request)/2,self.request)

class Record(models.Model):
	packet = models.ForeignKey(Packet)
	idbyte = models.SmallIntegerField()
	data = models.TextField()

	def __unicode__(self):
		return u"Record %02x (%d): %s"%(self.idbyte,len(self.data),self.data)
