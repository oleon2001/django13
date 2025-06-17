from skyguard.gps.tracker.models import User, SGAvl, SimCard, GeoFence, ServerSMS
from django import forms
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe
from skyguard.gps.tracker.forms import *

class SGAvlAdmin(admin.ModelAdmin):
	fieldsets = [
		(None, {'fields': ['name','serial','model',
						   'owner','swversion','harness','comments','icon']}),
		('Updates', {'fields': ['fwFile','lastFwUpdate'], }),
		('SIM', {'fields': ['sim', ]}),
		('Feria', {'fields': ['ruta', 'economico']}),
		]
	list_display = ['imei', 'name', 'ruta', 'economico', 'owner','swversion','fwFile', 'comments','sim','harness']
	readonly_fields = ('serial','model','swversion','lastFwUpdate')

class GeoFenceAdmin(admin.ModelAdmin):
    list_display = ['name','owner','base']
    fieldsets = [
        (None,{'fields':['name','owner','base']}),
    ]

admin.site.register(SGAvl,SGAvlAdmin)
admin.site.register(GeoFence,GeoFenceAdmin)
admin.site.register(SimCard,admin.ModelAdmin)
admin.site.register(ServerSMS,admin.ModelAdmin)
