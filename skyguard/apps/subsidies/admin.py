"""
Subsidies admin for the GPS system.
Migrated from legacy django14 system to modern architecture.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import (
    Driver, DailyLog, CashReceipt, TimeSheetCapture, 
    SubsidyRoute, SubsidyReport, EconomicMapping
)


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    """Admin for Driver model."""
    list_display = ('full_name', 'payroll', 'socials', 'taxid', 'license', 'active', 'created_at')
    list_filter = ('active', 'cstatus', 'created_at')
    search_fields = ('name', 'middle', 'last', 'payroll', 'socials', 'taxid')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('last', 'middle', 'name')
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('name', 'middle', 'last', 'birth', 'cstatus')
        }),
        ('Información Laboral', {
            'fields': ('payroll', 'socials', 'taxid', 'license', 'lic_exp')
        }),
        ('Contacto', {
            'fields': ('address', 'phone', 'phone1', 'phone2')
        }),
        ('Estado', {
            'fields': ('active',)
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def full_name(self, obj):
        """Display full name."""
        return obj.full_name
    full_name.short_description = 'Nombre Completo'


@admin.register(DailyLog)
class DailyLogAdmin(admin.ModelAdmin):
    """Admin for DailyLog model."""
    list_display = ('driver', 'route', 'start', 'stop', 'total', 'due', 'payed', 'difference', 'created_at')
    list_filter = ('route', 'start', 'created_at')
    search_fields = ('driver__name', 'driver__middle', 'driver__last')
    readonly_fields = ('difference', 'created_at', 'updated_at')
    ordering = ('-start',)
    
    fieldsets = (
        ('Información del Conductor', {
            'fields': ('driver',)
        }),
        ('Información del Servicio', {
            'fields': ('route', 'start', 'stop')
        }),
        ('Pasajeros', {
            'fields': ('regular', 'preferent', 'total')
        }),
        ('Pagos', {
            'fields': ('due', 'payed', 'difference')
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def difference(self, obj):
        """Display difference with color coding."""
        if obj.difference > 0:
            return format_html('<span style="color: red;">{}</span>', obj.difference)
        elif obj.difference < 0:
            return format_html('<span style="color: green;">{}</span>', obj.difference)
        else:
            return format_html('<span style="color: black;">{}</span>', obj.difference)
    difference.short_description = 'Diferencia'


@admin.register(CashReceipt)
class CashReceiptAdmin(admin.ModelAdmin):
    """Admin for CashReceipt model."""
    list_display = ('driver', 'ticket1', 'ticket2', 'total_payed', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('driver__name', 'driver__middle', 'driver__last', 'ticket1', 'ticket2')
    readonly_fields = ('total_payed', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Información del Conductor', {
            'fields': ('driver',)
        }),
        ('Folios', {
            'fields': ('ticket1', 'ticket2')
        }),
        ('Pagos por Vuelta', {
            'fields': ('payed1', 'payed2', 'payed3', 'payed4', 'payed5')
        }),
        ('Total', {
            'fields': ('total_payed',)
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def total_payed(self, obj):
        """Display total payed amount."""
        return obj.total_payed
    total_payed.short_description = 'Total Pagado'


@admin.register(TimeSheetCapture)
class TimeSheetCaptureAdmin(admin.ModelAdmin):
    """Admin for TimeSheetCapture model."""
    list_display = ('name', 'date', 'driver', 'route', 'rounds_count', 'total_duration', 'created_at')
    list_filter = ('date', 'route', 'created_at')
    search_fields = ('name', 'driver', 'route')
    readonly_fields = ('rounds_count', 'total_duration', 'created_at', 'updated_at')
    ordering = ('-date', 'name')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('date', 'name', 'driver', 'route')
        }),
        ('Horarios', {
            'fields': ('times',)
        }),
        ('Estadísticas', {
            'fields': ('rounds_count', 'total_duration')
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def rounds_count(self, obj):
        """Display number of rounds."""
        return obj.rounds_count
    rounds_count.short_description = 'Vueltas'
    
    def total_duration(self, obj):
        """Display total duration in hours and minutes."""
        minutes = obj.total_duration
        hours = int(minutes // 60)
        remaining_minutes = int(minutes % 60)
        return f"{hours}h {remaining_minutes}m"
    total_duration.short_description = 'Tiempo Total'


@admin.register(SubsidyRoute)
class SubsidyRouteAdmin(admin.ModelAdmin):
    """Admin for SubsidyRoute model."""
    list_display = ('name', 'route_code', 'company', 'branch', 'units_count', 'km', 'frequency', 'is_active')
    list_filter = ('route_code', 'is_active', 'created_at')
    search_fields = ('name', 'company', 'branch')
    readonly_fields = ('units_count', 'created_at', 'updated_at')
    ordering = ('name',)
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'route_code', 'company', 'branch')
        }),
        ('Configuración', {
            'fields': ('flag', 'units', 'km', 'frequency', 'time_minutes')
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def units_count(self, obj):
        """Display number of units."""
        return obj.units_count
    units_count.short_description = 'Unidades'


@admin.register(SubsidyReport)
class SubsidyReportAdmin(admin.ModelAdmin):
    """Admin for SubsidyReport model."""
    list_display = ('route', 'report_type', 'start_date', 'end_date', 'generated_by', 'created_at')
    list_filter = ('report_type', 'start_date', 'end_date', 'created_at')
    search_fields = ('route__name', 'generated_by__username')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Información del Reporte', {
            'fields': ('route', 'report_type', 'start_date', 'end_date', 'generated_by')
        }),
        ('Archivo', {
            'fields': ('file_path',)
        }),
        ('Datos del Reporte', {
            'fields': ('report_data',),
            'classes': ('collapse',)
        }),
        ('Fechas', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(EconomicMapping)
class EconomicMappingAdmin(admin.ModelAdmin):
    """Admin for EconomicMapping model."""
    list_display = ('unit_name', 'economic_number', 'route', 'is_active', 'created_at')
    list_filter = ('is_active', 'route', 'created_at')
    search_fields = ('unit_name', 'economic_number', 'route')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('unit_name',)
    
    fieldsets = (
        ('Información del Mapeo', {
            'fields': ('unit_name', 'economic_number', 'route')
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    ) 