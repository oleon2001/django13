from models import Driver, Tarjetas #, CashReceipt, DailyTicketsLog, DailyLog
from django import forms
from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from forms import *
import datetime

site2 = AdminSite("captura","capture")

class GeoFenceAdmin(admin.ModelAdmin):
    list_display = ['name','owner','base']
    fieldsets = [
        (None,{'fields':['name','owner','base']}),
    ]

class DriverAdmin(admin.ModelAdmin):
	list_display = ['middle','last','name','phone']
	
#class DailyLogAdmin(admin.ModelAdmin):
#	list_display = ['driver','route','payed']

def Total(obj):
	return (obj.tickets1 or 0)+(obj.tickets2 or 0)+(obj.tickets3 or 0)+(obj.tickets4 or 0)+(obj.tickets5 or 0)
Total.short_description = "Total"	

def CashTotal(obj):
	return (obj.payed1 or 0)+(obj.payed2 or 0)+(obj.payed3 or 0)+(obj.payed4 or 0)+(obj.payed5 or 0)
CashTotal.short_description = "Total"	

def cardCount(obj,drange):
		cards = Tarjetas.objects.filter(linea = obj.route, economico = obj.econ, date__range = drange)
		return len(cards)

def tdelta(t):
			return datetime.timedelta(hours=t.hour,minutes=t.minute)
			
def Tarj1(obj):
		if obj.start1 and obj.stop1:
			d1 = datetime.datetime(obj.date.year, obj.date.month, obj.date.day)+tdelta(obj.start1)
			d2 = datetime.datetime(obj.date.year, obj.date.month, obj.date.day)+tdelta(obj.stop1)
		else:
			return ""
		if d2<d1:
			d2 += datetime.timedelta(days=1)
		return cardCount(obj,(d1,d2))
		
def Tarj2(obj):
		if obj.start1 and obj.start2 and obj.stop2:
			d1 = datetime.datetime(obj.date.year, obj.date.month, obj.date.day)+tdelta(obj.start2)
			d2 = datetime.datetime(obj.date.year, obj.date.month, obj.date.day)+tdelta(obj.stop2)
		else:
			return ""
		if obj.stop2<obj.start1:
			d2 += datetime.timedelta(days=1)
		return cardCount(obj,(d1,d2))
		
def Tarj3(obj):
		if obj.start1 and obj.start3 and obj.stop3:
			d1 = datetime.datetime(obj.date.year, obj.date.month, obj.date.day)+tdelta(obj.start3)
			d2 = datetime.datetime(obj.date.year, obj.date.month, obj.date.day)+tdelta(obj.stop3)
		else:
			return ""
		if obj.stop3<obj.start1:
			d2 += datetime.timedelta(days=1)
		return cardCount(obj,(d1,d2))
		
def Tarj4(obj):
		if obj.start1 and obj.start4 and obj.stop4:
			d1 = datetime.datetime(obj.date.year, obj.date.month, obj.date.day)+tdelta(obj.start4)
			d2 = datetime.datetime(obj.date.year, obj.date.month, obj.date.day)+tdelta(obj.stop4)
		else:
			return ""
		if obj.stop4<obj.start1:
			d2 += datetime.timedelta(days=1)
		return cardCount(obj,(d1,d2))
		
def Tarj5(obj):
		if obj.start1 and obj.start5 and obj.stop5:
			d1 = datetime.datetime(obj.date.year, obj.date.month, obj.date.day)+tdelta(obj.start5)
			d2 = datetime.datetime(obj.date.year, obj.date.month, obj.date.day)+tdelta(obj.stop5)
		else:
			return ""
		if (obj.stop5<obj.start1):
			d2 += datetime.timedelta(days=1)
		return cardCount(obj,(d1,d2))

Tarj1.short_description = "Tarj."	
Tarj2.short_description = "Tarj."	
Tarj3.short_description = "Tarj."	
Tarj4.short_description = "Tarj."	
Tarj5.short_description = "Tarj."	
		
#class TicketsAdmin(admin.ModelAdmin):	
#	#change_form_template = "test1"
#	#add_form_template = "test2"
#	
#	change_list_template = "admin/change_list_boletos.html"
#	list_display = ['driver','route','econ','date',
#		'start1','stop1','tickets1',Tarj1, 
#		'start2','stop2','tickets2',Tarj2,
#		'start3','stop3','tickets3',Tarj3,
#		'start4','stop4','tickets4',Tarj4,
#		'start5','stop5','tickets5',Tarj5,
#		Total]
#	fieldsets = (
#		(None,{'fields':('driver','route','econ','ticket','date')}),
#		('Vuelta 1', {'fields':('start1','stop1','tickets1')}),
#		('Vuelta 2', {'fields':('start2','stop2','tickets2')}),
#		('Vuelta 3', {'fields':('start3','stop3','tickets3')}),
#		('Vuelta 4', {'fields':('start4','stop4','tickets4')}),
#		('Vuelta 5', {'fields':('start5','stop5','tickets5')}),
#		(None,{'fields':('notes',)})
#	)
	
#class CashAdmin(admin.ModelAdmin):
#	list_display = ['ticket1','ticket2','driver','payed1','payed2','payed3','payed4','payed5',CashTotal]
	
#site2.register(DailyTicketsLog,TicketsAdmin)
site2.register(Driver,DriverAdmin)
#site2.register(DailyLog,DailyLogAdmin)
#site2.register(CashReceipt,CashAdmin)
