"""
Subsidies views for the GPS system.
Migrated from legacy django14 system to modern architecture.
"""
import json
from datetime import datetime, date, timedelta
from typing import Dict, Any
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.db.models import Q, Sum, Count
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.core.paginator import Paginator
from django.template.loader import render_to_string

from .models import (
    Driver, DailyLog, CashReceipt, TimeSheetCapture, 
    SubsidyRoute, SubsidyReport, EconomicMapping
)
from .services import SubsidyService, TimeSheetGenerator, SubsidyReportGenerator, DriverService


@login_required
def subsidies_dashboard(request):
    """Main subsidies dashboard."""
    service = SubsidyService(request.user)
    
    # Get statistics
    total_drivers = Driver.objects.filter(active=True).count()
    total_routes = len(service.get_available_routes())
    today_logs = DailyLog.objects.filter(start__date=timezone.now().date()).count()
    this_month_reports = SubsidyReport.objects.filter(
        created_at__month=timezone.now().month,
        created_at__year=timezone.now().year
    ).count()
    
    # Get recent activities
    recent_logs = DailyLog.objects.select_related('driver').order_by('-created_at')[:5]
    recent_reports = SubsidyReport.objects.select_related('route').order_by('-created_at')[:5]
    
    context = {
        'total_drivers': total_drivers,
        'total_routes': total_routes,
        'today_logs': today_logs,
        'this_month_reports': this_month_reports,
        'recent_logs': recent_logs,
        'recent_reports': recent_reports,
    }
    
    return render(request, 'subsidies/dashboard.html', context)


@login_required
def drivers_list(request):
    """List all drivers."""
    drivers = Driver.objects.filter(active=True).order_by('last', 'middle', 'name')
    
    # Search functionality
    search = request.GET.get('search', '')
    if search:
        drivers = drivers.filter(
            Q(name__icontains=search) |
            Q(last__icontains=search) |
            Q(middle__icontains=search) |
            Q(payroll__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(drivers, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'drivers': page_obj,
        'search': search,
    }
    
    return render(request, 'subsidies/drivers_list.html', context)


@login_required
def driver_detail(request, driver_id):
    """Show driver details."""
    driver = get_object_or_404(Driver, id=driver_id)
    
    # Get driver's logs
    logs = DailyLog.objects.filter(driver=driver).order_by('-start')[:10]
    
    # Get driver's cash receipts
    receipts = CashReceipt.objects.filter(driver=driver).order_by('-created_at')[:10]
    
    context = {
        'driver': driver,
        'logs': logs,
        'receipts': receipts,
    }
    
    return render(request, 'subsidies/driver_detail.html', context)


@login_required
def driver_create(request):
    """Create a new driver."""
    if request.method == 'POST':
        service = DriverService(request.user)
        
        try:
            driver = service.create_driver({
                'name': request.POST.get('name'),
                'middle': request.POST.get('middle'),
                'last': request.POST.get('last'),
                'birth': request.POST.get('birth'),
                'cstatus': request.POST.get('cstatus'),
                'payroll': request.POST.get('payroll'),
                'socials': request.POST.get('socials'),
                'taxid': request.POST.get('taxid'),
                'license': request.POST.get('license'),
                'lic_exp': request.POST.get('lic_exp'),
                'address': request.POST.get('address'),
                'phone': request.POST.get('phone'),
                'phone1': request.POST.get('phone1'),
                'phone2': request.POST.get('phone2'),
            })
            
            messages.success(request, f'Conductor {driver.full_name} creado exitosamente.')
            return redirect('subsidies:driver_detail', driver_id=driver.id)
            
        except Exception as e:
            messages.error(request, f'Error al crear conductor: {str(e)}')
    
    return render(request, 'subsidies/driver_form.html')


@login_required
def driver_edit(request, driver_id):
    """Edit an existing driver."""
    driver = get_object_or_404(Driver, id=driver_id)
    
    if request.method == 'POST':
        service = DriverService(request.user)
        
        try:
            updated_driver = service.update_driver(driver_id, {
                'name': request.POST.get('name'),
                'middle': request.POST.get('middle'),
                'last': request.POST.get('last'),
                'birth': request.POST.get('birth'),
                'cstatus': request.POST.get('cstatus'),
                'payroll': request.POST.get('payroll'),
                'socials': request.POST.get('socials'),
                'taxid': request.POST.get('taxid'),
                'license': request.POST.get('license'),
                'lic_exp': request.POST.get('lic_exp'),
                'address': request.POST.get('address'),
                'phone': request.POST.get('phone'),
                'phone1': request.POST.get('phone1'),
                'phone2': request.POST.get('phone2'),
            })
            
            messages.success(request, f'Conductor {updated_driver.full_name} actualizado exitosamente.')
            return redirect('subsidies:driver_detail', driver_id=driver.id)
            
        except Exception as e:
            messages.error(request, f'Error al actualizar conductor: {str(e)}')
    
    context = {
        'driver': driver,
    }
    
    return render(request, 'subsidies/driver_form.html', context)


@login_required
def daily_logs_list(request):
    """List daily logs."""
    logs = DailyLog.objects.select_related('driver').order_by('-start')
    
    # Filter by date range
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    driver_id = request.GET.get('driver')
    
    if start_date:
        logs = logs.filter(start__date__gte=start_date)
    if end_date:
        logs = logs.filter(start__date__lte=end_date)
    if driver_id:
        logs = logs.filter(driver_id=driver_id)
    
    # Pagination
    paginator = Paginator(logs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get drivers for filter
    drivers = Driver.objects.filter(active=True).order_by('last', 'middle', 'name')
    
    context = {
        'logs': page_obj,
        'drivers': drivers,
        'start_date': start_date,
        'end_date': end_date,
        'driver_id': driver_id,
    }
    
    return render(request, 'subsidies/daily_logs_list.html', context)


@login_required
def daily_log_create(request):
    """Create a new daily log."""
    if request.method == 'POST':
        try:
            driver = get_object_or_404(Driver, id=request.POST.get('driver'))
            
            log = DailyLog.objects.create(
                driver=driver,
                route=request.POST.get('route'),
                start=request.POST.get('start'),
                stop=request.POST.get('stop'),
                regular=request.POST.get('regular', 0),
                preferent=request.POST.get('preferent', 0),
                total=request.POST.get('total', 0),
                due=request.POST.get('due', 0),
                payed=request.POST.get('payed', 0),
            )
            
            messages.success(request, f'Registro diario creado exitosamente para {driver.full_name}.')
            return redirect('subsidies:daily_logs_list')
            
        except Exception as e:
            messages.error(request, f'Error al crear registro: {str(e)}')
    
    drivers = Driver.objects.filter(active=True).order_by('last', 'middle', 'name')
    
    context = {
        'drivers': drivers,
    }
    
    return render(request, 'subsidies/daily_log_form.html', context)


@login_required
def timesheet_capture(request):
    """Time sheet capture interface."""
    service = SubsidyService(request.user)
    
    if request.method == 'POST':
        try:
            date_str = request.POST.get('date')
            unit_name = request.POST.get('unit_name')
            times_data = json.loads(request.POST.get('times', '[]'))
            driver = request.POST.get('driver', '')
            route = request.POST.get('route', '')
            
            if date_str and unit_name:
                capture_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                timesheet = service.create_timesheet_capture(
                    date=capture_date,
                    unit_name=unit_name,
                    times=times_data,
                    driver=driver,
                    route=route
                )
                
                messages.success(request, f'Hoja de tiempo capturada para {unit_name}.')
                return redirect('subsidies:timesheet_capture')
            
        except Exception as e:
            messages.error(request, f'Error al capturar hoja de tiempo: {str(e)}')
    
    # Get available routes and units
    routes = service.get_available_routes()
    today = timezone.now().date()
    available_units = service.get_available_units(today)
    
    context = {
        'routes': routes,
        'available_units': available_units,
        'today': today,
    }
    
    return render(request, 'subsidies/timesheet_capture.html', context)


@login_required
def timesheet_report(request):
    """Generate time sheet report."""
    service = SubsidyService(request.user)
    generator = TimeSheetGenerator(request.user)
    
    if request.method == 'POST':
        try:
            route_code = request.POST.get('route_code')
            start_date = datetime.strptime(request.POST.get('start_date'), '%Y-%m-%d').date()
            end_date = datetime.strptime(request.POST.get('end_date'), '%Y-%m-%d').date()
            format = request.POST.get('format', 'xlsx')
            
            return generator.generate_timesheet_report(
                route_code=route_code,
                start_date=start_date,
                end_date=end_date,
                format=format
            )
            
        except Exception as e:
            messages.error(request, f'Error al generar reporte: {str(e)}')
    
    routes = service.get_available_routes()
    
    context = {
        'routes': routes,
    }
    
    return render(request, 'subsidies/timesheet_report.html', context)


@login_required
def daily_report(request):
    """Generate daily subsidy report."""
    service = SubsidyService(request.user)
    generator = SubsidyReportGenerator(request.user)
    
    if request.method == 'POST':
        try:
            route_code = request.POST.get('route_code')
            report_date = datetime.strptime(request.POST.get('report_date'), '%Y-%m-%d').date()
            format = request.POST.get('format', 'xlsx')
            
            return generator.generate_daily_report(
                route_code=route_code,
                report_date=report_date,
                format=format
            )
            
        except Exception as e:
            messages.error(request, f'Error al generar reporte diario: {str(e)}')
    
    routes = service.get_available_routes()
    
    context = {
        'routes': routes,
    }
    
    return render(request, 'subsidies/daily_report.html', context)


@login_required
def cash_receipts_list(request):
    """List cash receipts."""
    receipts = CashReceipt.objects.select_related('driver').order_by('-created_at')
    
    # Filter by date range
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    driver_id = request.GET.get('driver')
    
    if start_date:
        receipts = receipts.filter(created_at__date__gte=start_date)
    if end_date:
        receipts = receipts.filter(created_at__date__lte=end_date)
    if driver_id:
        receipts = receipts.filter(driver_id=driver_id)
    
    # Pagination
    paginator = Paginator(receipts, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get drivers for filter
    drivers = Driver.objects.filter(active=True).order_by('last', 'middle', 'name')
    
    context = {
        'receipts': page_obj,
        'drivers': drivers,
        'start_date': start_date,
        'end_date': end_date,
        'driver_id': driver_id,
    }
    
    return render(request, 'subsidies/cash_receipts_list.html', context)


@login_required
def cash_receipt_create(request):
    """Create a new cash receipt."""
    if request.method == 'POST':
        try:
            driver = get_object_or_404(Driver, id=request.POST.get('driver'))
            
            receipt = CashReceipt.objects.create(
                driver=driver,
                ticket1=request.POST.get('ticket1'),
                ticket2=request.POST.get('ticket2'),
                payed1=request.POST.get('payed1', 0),
                payed2=request.POST.get('payed2', 0),
                payed3=request.POST.get('payed3', 0),
                payed4=request.POST.get('payed4', 0),
                payed5=request.POST.get('payed5', 0),
            )
            
            messages.success(request, f'Recibo de efectivo creado exitosamente para {driver.full_name}.')
            return redirect('subsidies:cash_receipts_list')
            
        except Exception as e:
            messages.error(request, f'Error al crear recibo: {str(e)}')
    
    drivers = Driver.objects.filter(active=True).order_by('last', 'middle', 'name')
    
    context = {
        'drivers': drivers,
    }
    
    return render(request, 'subsidies/cash_receipt_form.html', context)


@login_required
def routes_list(request):
    """List subsidy routes."""
    service = SubsidyService(request.user)
    routes = service.get_available_routes()
    
    context = {
        'routes': routes,
    }
    
    return render(request, 'subsidies/routes_list.html', context)


@login_required
def route_detail(request, route_code):
    """Show route details."""
    service = SubsidyService(request.user)
    
    # Find route configuration
    route_config = None
    for ruta in service.get_available_routes():
        if ruta['file'] == route_code:
            route_config = ruta
            break
    
    if not route_config:
        messages.error(request, f'Ruta {route_code} no encontrada.')
        return redirect('subsidies:routes_list')
    
    # Get route statistics
    today = timezone.now().date()
    today_logs = DailyLog.objects.filter(
        start__date=today,
        route__in=[int(route_code.replace('R', '').replace('A', '')) if route_code.startswith('R') else 0]
    ).count()
    
    # Get recent time sheets for this route
    recent_timesheets = TimeSheetCapture.objects.filter(
        route__icontains=route_code,
        date__gte=today - timedelta(days=7)
    ).order_by('-date')[:10]
    
    context = {
        'route': route_config,
        'today_logs': today_logs,
        'recent_timesheets': recent_timesheets,
    }
    
    return render(request, 'subsidies/route_detail.html', context)


@login_required
def economic_mappings_list(request):
    """List economic mappings."""
    mappings = EconomicMapping.objects.filter(is_active=True).order_by('unit_name')
    
    # Search functionality
    search = request.GET.get('search', '')
    if search:
        mappings = mappings.filter(
            Q(unit_name__icontains=search) |
            Q(economic_number__icontains=search) |
            Q(route__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(mappings, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'mappings': page_obj,
        'search': search,
    }
    
    return render(request, 'subsidies/economic_mappings_list.html', context)


@login_required
def economic_mapping_create(request):
    """Create a new economic mapping."""
    if request.method == 'POST':
        try:
            mapping = EconomicMapping.objects.create(
                unit_name=request.POST.get('unit_name'),
                economic_number=request.POST.get('economic_number'),
                route=request.POST.get('route', ''),
            )
            
            messages.success(request, f'Mapeo económico creado exitosamente: {mapping.unit_name} -> {mapping.economic_number}')
            return redirect('subsidies:economic_mappings_list')
            
        except Exception as e:
            messages.error(request, f'Error al crear mapeo económico: {str(e)}')
    
    return render(request, 'subsidies/economic_mapping_form.html')


@login_required
def api_get_route_units(request, route_code):
    """API endpoint to get units for a route."""
    service = SubsidyService(request.user)
    units = service.get_route_units(route_code)
    
    return JsonResponse({
        'units': units,
        'route_code': route_code
    })


@login_required
def api_get_timesheet_data(request, date_str, unit_name):
    """API endpoint to get time sheet data."""
    try:
        capture_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        service = SubsidyService(request.user)
        timesheet = service.get_timesheet_data(capture_date, unit_name)
        
        if timesheet:
            return JsonResponse({
                'success': True,
                'data': {
                    'times': timesheet.times,
                    'driver': timesheet.driver,
                    'route': timesheet.route,
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'No data found'
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })


@login_required
def api_get_economic_number(request, unit_name):
    """API endpoint to get economic number for a unit."""
    service = SubsidyService(request.user)
    economic_number = service.get_economic_mapping(unit_name)
    
    return JsonResponse({
        'unit_name': unit_name,
        'economic_number': economic_number
    }) 