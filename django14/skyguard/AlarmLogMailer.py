#!/usr/bin/python
# -*- coding: utf-8 -*-
# AlarmLog Mailer

import io,os,sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'sites.www.settings'
path = '/home/django13/skyguard'
if path not in sys.path:
    sys.path.append(path)

from django.conf import settings
from gps.tracker.models import *

import datetime
from pytz import utc, timezone
import smtplib
from email.mime.text import MIMEText
 
localtz = timezone(settings.TIME_ZONE)
settings.DEBUG = False
today = datetime.date.today()
now = datetime.datetime.now()
ALARM_DT = datetime.timedelta(seconds = 10*60)

FROM = '"Reporte de Alarmas" <admin@ensambles.net>'
TO = 'Edgar H. Martinez <edmtz@gpomag.com>'
TOLIST = ['Edgar H. Martinez <edmtz@gpomag.com>',"<cantuchuy.cc@gmail.com>"]
SUBJECT = "Reporte de Alarmas "
SERVER = 'smtp.zoho.com'
USER = 'admin@ensambles.net'
PASS = 'l6moSa5mgCpg'

def CheckAlarm(sensor):
	try:
		al = AlarmLog.objects.filter(sensor = sensor, date__gte = today).order_by('date')
		last = al.filter(cksum = al.latest().cksum)
		if not last.filter(comment = "STOP"):
			if now - last[0].date > ALARM_DT and not PsiWeightLog.objects.filter(sensor = sensor, date__gte = last[len(last)-1].date):
				return last[0]
	except AlarmLog.DoesNotExist:
		pass
	return None
	
if __name__ == "__main__":
	out = io.BytesIO()
	for i in sys.argv[1:]:
		avls = SGAvl.objects.filter(name__startswith = i).order_by("economico")
		for a in avls:
			print a.name
			sensors = PsiCal.objects.filter(imei = a).order_by('offpsi1')
			for s in sensors:
				alm = CheckAlarm(s.sensor)
				if alm:
					dt = now - alm.date
					if dt.seconds >3600:
						delta = "{0:5.2f} Horas".format(dt.seconds/3600.0)
						#if 'e' in delta:
						#	print alm.date, alm
					else:
						delta = "{0:5.2f} Minutos".format(dt.seconds/60.0)
					print >> out, "{0:14}-{1:9} @ {2:%H:%M:%S} - {3}".format(a.name,s.name,alm.date, delta)
	if out.getvalue():
		msg = MIMEText("Fecha :{0:%d/%m/%Y}\n{1}".format(today,out.getvalue()))
		msg['From'] = FROM
		msg['To'] = TO
		msg['Subject'] = SUBJECT
		s = smtplib.SMTP_SSL(SERVER)
		print s.login(USER,PASS)
		print s.sendmail(FROM,TOLIST,msg.as_string())
		print s.quit()
		print out.getvalue()
		
		
		
		
