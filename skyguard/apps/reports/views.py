"""
Report views.
Migrated from legacy django14 system to modern architecture.
"""
import json
from datetime import datetime, timedelta, date
from typing import Dict, Any
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views.generic.edit import FormView
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.db.models import Q, Count, Sum
from django.core.paginator import Paginator
from django.forms import Form
from django import forms
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from skyguard.apps.gps.models import GPSDevice, GPSEvent, GPSLocation, PressureWeightLog
from .models import (
    ReportTemplate, ReportExecution, TicketReport, 
    StatisticsReport, PeopleCountReport, AlarmReport
)
from .services import (
    ReportService, TicketReportGenerator, StatisticsReportGenerator,
    PeopleCountReportGenerator, AlarmReportGenerator, RouteReportGenerator,
    RUTA_CHOICES, RUTA_CHOICES2, find_choice, day_range_x, get_people_count
)


class ReportForm(forms.Form):
    """Base form for report generation."""
    device = forms.ModelChoiceField(
        queryset=GPSDevice.objects.all(),
        label="Dispositivo",
        required=True
    )
    start_date = forms.DateField(
        label="Fecha de Inicio",
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True
    )
    end_date = forms.DateField(
        label="Fecha de Fin",
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True
    )
    format = forms.ChoiceField(
        choices=[('pdf', 'PDF'), ('csv', 'CSV')],
        label="Formato",
        initial='pdf',
        required=True
    )


class RouteReportForm(forms.Form):
    """Form for route-specific reports."""
    route = forms.ChoiceField(
        choices=RUTA_CHOICES2,
        label="Ruta",
        required=True
    )
    date = forms.DateField(
        label="Fecha",
        widget=forms.DateInput(attrs={'type': 'date'}),
        initial=date.today,
        required=True
    )
    format = forms.ChoiceField(
        choices=[('pdf', 'PDF'), ('csv', 'CSV')],
        label="Formato",
        initial='pdf',
        required=True
    )


class TicketReportForm(ReportForm):
    """Form for ticket reports."""
    driver_name = forms.CharField(
        label="Nombre del Conductor",
        max_length=100,
        required=False
    )


class StatisticsReportForm(ReportForm):
    """Form for statistics reports."""
    include_distance = forms.BooleanField(
        label="Incluir Distancia",
        initial=True,
        required=False
    )
    include_speed = forms.BooleanField(
        label="Incluir Velocidad",
        initial=True,
        required=False
    )


class PeopleCountReportForm(ReportForm):
    """Form for people count reports."""
    sensor = forms.CharField(
        label="Sensor",
        max_length=50,
        required=False
    )


class AlarmReportForm(ReportForm):
    """Form for alarm reports."""
    alarm_type = forms.ChoiceField(
        choices=[
            ('all', 'Todas'),
            ('critical', 'Críticas'),
            ('warning', 'Advertencias')
        ],
        label="Tipo de Alarma",
        initial='all',
        required=True
    )


@login_required
def report_dashboard(request):
    """Dashboard for reports."""
    context = {
        'total_devices': GPSDevice.objects.count(),
        'total_reports': ReportExecution.objects.count(),
        'recent_reports': ReportExecution.objects.filter(
            executed_by=request.user
        ).order_by('-created_at')[:5],
        'available_reports': [
            {
                'name': 'Reporte de Tickets',
                'description': 'Reporte de venta de boletos y cobros',
                'url': reverse('reports:ticket_report'),
                'icon': 'receipt'
            },
            {
                'name': 'Reporte de Estadísticas',
                'description': 'Estadísticas de operación de dispositivos',
                'url': reverse('reports:statistics_report'),
                'icon': 'analytics'
            },
            {
                'name': 'Reporte de Conteo de Personas',
                'description': 'Conteo de personas por ruta',
                'url': reverse('reports:people_count_report'),
                'icon': 'people'
            },
            {
                'name': 'Reporte de Alarmas',
                'description': 'Reporte de alarmas del sistema',
                'url': reverse('reports:alarm_report'),
                'icon': 'warning'
            },
            {
                'name': 'Reporte por Ruta',
                'description': 'Reportes específicos por ruta',
                'url': reverse('reports:route_report'),
                'icon': 'route'
            }
        ]
    }
    return render(request, 'reports/dashboard.html', context)


@login_required
def ticket_report_view(request):
    """View for ticket report generation."""
    if request.method == 'POST':
        form = TicketReportForm(request.POST)
        if form.is_valid():
            try:
                device = form.cleaned_data['device']
                start_date = form.cleaned_data['start_date']
                end_date = form.cleaned_data['end_date']
                format = form.cleaned_data['format']
                
                # Convert dates to datetime
                start_dt = datetime.combine(start_date, datetime.min.time())
                end_dt = datetime.combine(end_date, datetime.max.time())
                
                # Generate report
                service = ReportService(request.user)
                response = service.generate_report(
                    'ticket', device.id, start_dt, end_dt, format
                )
                
                # Log execution
                ReportExecution.objects.create(
                    template=ReportTemplate.objects.get_or_create(
                        name='Ticket Report',
                        report_type='ticket'
                    )[0],
                    executed_by=request.user,
                    parameters={
                        'device_id': device.id,
                        'start_date': start_date.isoformat(),
                        'end_date': end_date.isoformat(),
                        'format': format
                    },
                    status='completed',
                    started_at=timezone.now(),
                    completed_at=timezone.now()
                )
                
                return response
                
            except Exception as e:
                messages.error(request, f"Error generando reporte: {str(e)}")
    else:
        form = TicketReportForm()
    
    return render(request, 'reports/ticket_report.html', {'form': form})


@login_required
def statistics_report_view(request):
    """View for statistics report generation."""
    if request.method == 'POST':
        form = StatisticsReportForm(request.POST)
        if form.is_valid():
            try:
                device = form.cleaned_data['device']
                start_date = form.cleaned_data['start_date']
                end_date = form.cleaned_data['end_date']
                format = form.cleaned_data['format']
                
                # Convert dates to datetime
                start_dt = datetime.combine(start_date, datetime.min.time())
                end_dt = datetime.combine(end_date, datetime.max.time())
                
                # Generate report
                service = ReportService(request.user)
                response = service.generate_report(
                    'statistics', device.id, start_dt, end_dt, format
                )
                
                # Log execution
                ReportExecution.objects.create(
                    template=ReportTemplate.objects.get_or_create(
                        name='Statistics Report',
                        report_type='stats'
                    )[0],
                    executed_by=request.user,
                    parameters={
                        'device_id': device.id,
                        'start_date': start_date.isoformat(),
                        'end_date': end_date.isoformat(),
                        'format': format
                    },
                    status='completed',
                    started_at=timezone.now(),
                    completed_at=timezone.now()
                )
                
                return response
                
            except Exception as e:
                messages.error(request, f"Error generando reporte: {str(e)}")
    else:
        form = StatisticsReportForm()
    
    return render(request, 'reports/statistics_report.html', {'form': form})


@login_required
def people_count_report_view(request):
    """View for people count report generation."""
    if request.method == 'POST':
        form = PeopleCountReportForm(request.POST)
        if form.is_valid():
            try:
                device = form.cleaned_data['device']
                start_date = form.cleaned_data['start_date']
                end_date = form.cleaned_data['end_date']
                format = form.cleaned_data['format']
                
                # Convert dates to datetime
                start_dt = datetime.combine(start_date, datetime.min.time())
                end_dt = datetime.combine(end_date, datetime.max.time())
                
                # Generate report
                service = ReportService(request.user)
                response = service.generate_report(
                    'people', device.id, start_dt, end_dt, format
                )
                
                # Log execution
                ReportExecution.objects.create(
                    template=ReportTemplate.objects.get_or_create(
                        name='People Count Report',
                        report_type='people'
                    )[0],
                    executed_by=request.user,
                    parameters={
                        'device_id': device.id,
                        'start_date': start_date.isoformat(),
                        'end_date': end_date.isoformat(),
                        'format': format
                    },
                    status='completed',
                    started_at=timezone.now(),
                    completed_at=timezone.now()
                )
                
                return response
                
            except Exception as e:
                messages.error(request, f"Error generando reporte: {str(e)}")
    else:
        form = PeopleCountReportForm()
    
    return render(request, 'reports/people_count_report.html', {'form': form})


@login_required
def alarm_report_view(request):
    """View for alarm report generation."""
    if request.method == 'POST':
        form = AlarmReportForm(request.POST)
        if form.is_valid():
            try:
                device = form.cleaned_data['device']
                start_date = form.cleaned_data['start_date']
                end_date = form.cleaned_data['end_date']
                format = form.cleaned_data['format']
                alarm_type = form.cleaned_data['alarm_type']
                
                # Convert dates to datetime
                start_dt = datetime.combine(start_date, datetime.min.time())
                end_dt = datetime.combine(end_date, datetime.max.time())
                
                # Generate report
                service = ReportService(request.user)
                response = service.generate_report(
                    'alarm', device.id, start_dt, end_dt, format
                )
                
                # Log execution
                ReportExecution.objects.create(
                    template=ReportTemplate.objects.get_or_create(
                        name='Alarm Report',
                        report_type='alarm'
                    )[0],
                    executed_by=request.user,
                    parameters={
                        'device_id': device.id,
                        'start_date': start_date.isoformat(),
                        'end_date': end_date.isoformat(),
                        'format': format,
                        'alarm_type': alarm_type
                    },
                    status='completed',
                    started_at=timezone.now(),
                    completed_at=timezone.now()
                )
                
                return response
                
            except Exception as e:
                messages.error(request, f"Error generando reporte: {str(e)}")
    else:
        form = AlarmReportForm()
    
    return render(request, 'reports/alarm_report.html', {'form': form})


@login_required
def route_report_view(request):
    """View for route-specific report generation."""
    if request.method == 'POST':
        form = RouteReportForm(request.POST)
        if form.is_valid():
            try:
                route_number = int(form.cleaned_data['route'])
                report_date = form.cleaned_data['date']
                format = form.cleaned_data['format']
                
                # Generate report
                service = ReportService(request.user)
                response = service.generate_route_report(
                    route_number, report_date, 'people', format
                )
                
                # Log execution
                ReportExecution.objects.create(
                    template=ReportTemplate.objects.get_or_create(
                        name='Route Report',
                        report_type='custom'
                    )[0],
                    executed_by=request.user,
                    parameters={
                        'route_number': route_number,
                        'report_date': report_date.isoformat(),
                        'format': format
                    },
                    status='completed',
                    started_at=timezone.now(),
                    completed_at=timezone.now()
                )
                
                return response
                
            except Exception as e:
                messages.error(request, f"Error generando reporte: {str(e)}")
    else:
        form = RouteReportForm()
    
    return render(request, 'reports/route_report.html', {'form': form})


@login_required
def report_executions_list(request):
    """List of report executions."""
    executions = ReportExecution.objects.filter(
        executed_by=request.user
    ).order_by('-created_at')
    
    paginator = Paginator(executions, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'reports/executions_list.html', {
        'page_obj': page_obj
    })


@login_required
def report_execution_detail(request, pk):
    """Detail view for report execution."""
    execution = get_object_or_404(ReportExecution, pk=pk, executed_by=request.user)
    
    return render(request, 'reports/execution_detail.html', {
        'execution': execution
    })


@login_required
def api_generate_report(request):
    """API endpoint for report generation."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            report_type = data.get('report_type')
            device_id = data.get('device_id')
            start_date = datetime.fromisoformat(data.get('start_date'))
            end_date = datetime.fromisoformat(data.get('end_date'))
            format = data.get('format', 'pdf')
            
            service = ReportService(request.user)
            response = service.generate_report(
                report_type, device_id, start_date, end_date, format
            )
            
            return response
            
        except Exception as e:
            return JsonResponse({
                'error': str(e)
            }, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required
def api_available_reports(request):
    """API endpoint for available reports."""
    service = ReportService(request.user)
    reports = service.get_available_reports()
    
    return JsonResponse({
        'reports': reports
    })


@login_required
def api_route_choices(request):
    """API endpoint for route choices."""
    service = ReportService(request.user)
    choices = service.get_route_choices()
    
    return JsonResponse({
        'choices': choices
    })


# Legacy compatibility views (migrated from django14)

@login_required
def legacy_ticket_report(request):
    """Legacy ticket report view for compatibility."""
    if request.method == 'GET':
        try:
            imei = int(request.GET.get('imei'))
            report_date = datetime.strptime(request.GET.get('date'), "%Y-%m-%d")
            start_time = datetime.strptime(request.GET.get('start'), "%H:%M")
            stop_time = datetime.strptime(request.GET.get('stop'), "%H:%M")
            
            # Convert to timedelta
            start_delta = timedelta(hours=start_time.hour, minutes=start_time.minute)
            stop_delta = timedelta(hours=stop_time.hour, minutes=stop_time.minute)
            
            # Get day range
            day_range = day_range_x(report_date, start_delta, stop_delta)
            
            # Get device
            device = get_object_or_404(GPSDevice, imei=imei)
            
            # Check permissions
            if not (device.owner == request.user or request.user.is_staff):
                raise Http404("No permission to access this device")
            
            # Generate report
            service = ReportService(request.user)
            response = service.generate_report(
                'ticket', device.id, day_range[0], day_range[1], 'pdf'
            )
            
            return response
            
        except Exception as e:
            messages.error(request, f"Error generando reporte: {str(e)}")
            return redirect('reports:dashboard')
    
    return redirect('reports:dashboard')


@login_required
def legacy_people_count_report(request):
    """Legacy people count report view for compatibility."""
    if request.method == 'GET':
        try:
            route = int(request.GET.get('ruta', 96))  # Default to Ruta 400
            report_date = datetime.strptime(request.GET.get('date'), "%Y-%m-%d")
            
            # Generate report
            service = ReportService(request.user)
            response = service.generate_route_report(
                route, report_date.date(), 'people', 'pdf'
            )
            
            return response
            
        except Exception as e:
            messages.error(request, f"Error generando reporte: {str(e)}")
            return redirect('reports:dashboard')
    
    return redirect('reports:dashboard')


@login_required
def legacy_alarm_report(request):
    """Legacy alarm report view for compatibility."""
    if request.method == 'GET':
        try:
            route = int(request.GET.get('ruta', 96))  # Default to Ruta 400
            report_date = datetime.strptime(request.GET.get('date'), "%Y-%m-%d")
            
            # Get devices for the route
            devices = GPSDevice.objects.filter(route=route)
            
            if not devices.exists():
                messages.error(request, "No se encontraron dispositivos para esta ruta")
                return redirect('reports:dashboard')
            
            # Generate report for first device (legacy behavior)
            device = devices.first()
            start_dt = datetime.combine(report_date, datetime.min.time())
            end_dt = datetime.combine(report_date, datetime.max.time())
            
            service = ReportService(request.user)
            response = service.generate_report(
                'alarm', device.id, start_dt, end_dt, 'pdf'
            )
            
            return response
            
        except Exception as e:
            messages.error(request, f"Error generando reporte: {str(e)}")
            return redirect('reports:dashboard')
    
    return redirect('reports:dashboard') 