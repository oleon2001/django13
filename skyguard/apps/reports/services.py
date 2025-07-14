"""
Report generation services.
Migrated from legacy django14 system to modern architecture.
"""
import csv
import json
import os
from datetime import datetime, timedelta, time, date
from decimal import Decimal
from io import StringIO, BytesIO
from typing import Dict, List, Any, Optional, Tuple
from django.db.models import Avg, Max, Min, Sum, Count, Q
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, BaseDocTemplate, PageTemplate, Frame, PageBreak
from reportlab.lib.styles import ParagraphStyle
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill
import reportlab.rl_config
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from skyguard.apps.gps.models import GPSDevice, GPSEvent, GPSLocation, PressureWeightLog, IOEvent, GSMEvent
from .models import (
    ReportTemplate, ReportExecution, TicketReport, 
    StatisticsReport, PeopleCountReport, AlarmReport
)

# Configure ReportLab
reportlab.rl_config.warnOnMissingFontGlyphs = 0

# Register fonts (adjust paths as needed)
try:
    pdfmetrics.registerFont(TTFont('Arial', '/usr/share/fonts/truetype/arial.ttf'))
    pdfmetrics.registerFont(TTFont('ArialNarrow', '/usr/share/fonts/truetype/arialn.ttf'))
except:
    # Fallback to default fonts
    pass


# Route choices from legacy system
RUTA_CHOICES = (
    (92, "Ruta 4"),
    (112, "Ruta 6"),
    (114, "Ruta 12"),
    (115, "Ruta 31"),
    (90, "Ruta 82"),
    (88, "Ruta 118"),
    (215, "Ruta 140"),
    (89, "Ruta 202"),
    (116, "Ruta 207"),
    (96, "Ruta 400"),
    (97, "Ruta 408"),
)

RUTA_CHOICES2 = (
    (90, "Ruta 82"),
    (92, "Ruta 4"),
    (96, "Ruta 400"),
    (97, "Ruta 408"),
    (112, "Ruta 6"),
    (115, "Ruta 31"),
    (116, "Ruta 207"),
)


def find_choice(choice):
    """Find route name by choice value."""
    for i in RUTA_CHOICES:
        if i[0] == int(choice):
            return i[1]
    return "Ruta Desconocida"


def day_range_x(date_obj, start_time, stop_time):
    """Create day range with time offsets."""
    start_dt = datetime.combine(date_obj, time(3, 0))  # 3 AM
    end_dt = start_dt + timedelta(days=1)
    return (start_dt, end_dt)


def get_people_count(sensor, start_time, end_time):
    """Get people count for a sensor in time range."""
    logs = PressureWeightLog.objects.filter(
        sensor=sensor,
        timestamp__range=(start_time, end_time)
    ).order_by('timestamp')
    
    if not logs:
        return 0, 0
    
    # Calculate people count from pressure logs
    total_in = sum(log.psi1 for log in logs if log.psi1)
    total_out = sum(log.psi2 for log in logs if log.psi2)
    
    return total_in, total_out


class ReportGenerator:
    """Base class for report generation."""
    
    def __init__(self, user):
        """Initialize the report generator."""
        self.user = user
        self.styles = getSampleStyleSheet()
        self.boxgrid = TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('BOX', (0, 0), (-1, -1), 1.5, colors.black),
            ('BOX', (0, 0), (-1, 0), 1.5, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightyellow),
            ('SPAN', (0, 0), (-1, 0)),
            ('LINEBELOW', (0, 'splitlast'), (-1, 'splitlast'), 1.5, colors.black),
            ('ALIGN', (0, 0), (-1, 1), 'CENTER'),
            ('VALIGN', (0, 2), (-1, -1), "TOP"),
        ])
    
    def generate_pdf(self, data: List[List], title: str, filename: str) -> HttpResponse:
        """Generate PDF report."""
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'filename="{filename}.pdf"'
        
        doc = BaseDocTemplate(response, pagesize=letter, 
                            leftMargin=0.25*inch, rightMargin=0.25*inch,
                            topMargin=0.25*inch, bottomMargin=0.25*inch)
        
        frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='normal')
        template = PageTemplate(id='page', frames=frame)
        doc.addPageTemplates([template])
        
        story = []
        
        # Add title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=1
        )
        story.append(Paragraph(title, title_style))
        story.append(Spacer(1, 12))
        
        # Create table
        table = Table(data, repeatRows=2)
        table.setStyle(self.boxgrid)
        
        story.append(table)
        doc.build(story)
        return response
    
    def generate_csv(self, data: List[List], filename: str) -> HttpResponse:
        """Generate CSV report."""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{filename}.csv"'
        
        writer = csv.writer(response)
        for row in data:
            writer.writerow(row)
        
        return response


class TicketReportGenerator(ReportGenerator):
    """Generate ticket reports."""
    
    def generate_ticket_report(self, device: GPSDevice, start_date: datetime, 
                             end_date: datetime, format: str = 'pdf') -> HttpResponse:
        """Generate ticket report for a device."""
        # Get ticket events
        events = GPSEvent.objects.filter(
            device=device,
            timestamp__range=(start_date, end_date),
            event_type='TICKET'
        ).order_by('timestamp')
        
        # Prepare data
        data = [
            ['Reporte de Tickets'],
            ['Ticket', 'Unidad', 'Chofer', 'Hora', 'Vueltas', 'Inicio', 'Fin', 'Duración', 'Pasaje', 'Ord', 'Pref', 'Sistema', 'Liq', 'Diferencia']
        ]
        
        total_amount = Decimal('0.00')
        total_received = Decimal('0.00')
        
        for event in events:
            ticket_data = event.raw_data.get('ticket_data', {})
            driver_name = ticket_data.get('driver_name', 'N/A')
            amount = Decimal(str(ticket_data.get('amount', 0)))
            received = Decimal(str(ticket_data.get('received', 0)))
            difference = amount - received
            
            total_amount += amount
            total_received += received
            
            data.append([
                event.timestamp.strftime('%Y-%m-%d'),
                device.name,
                driver_name,
                event.timestamp.strftime('%H:%M:%S'),
                ticket_data.get('rounds', 0),
                ticket_data.get('start_time', ''),
                ticket_data.get('end_time', ''),
                ticket_data.get('duration', ''),
                f"${amount:.2f}",
                ticket_data.get('normal_tickets', 0),
                ticket_data.get('pref_tickets', 0),
                ticket_data.get('system_amount', 0),
                f"${received:.2f}",
                f"${difference:.2f}"
            ])
        
        # Add totals row
        data.append([
            'TOTALES', '', '', '', '', '', '', '', 
            f"${total_amount:.2f}", '', '', '', 
            f"${total_received:.2f}", 
            f"${total_amount - total_received:.2f}"
        ])
        
        title = f"Tickets.{device.name}.{start_date.strftime('%Y.%m.%d')}"
        filename = f"Tickets.{device.name}.{start_date.strftime('%Y.%m.%d')}"
        
        if format == 'pdf':
            return self.generate_pdf(data, title, filename)
        elif format == 'csv':
            return self.generate_csv(data, filename)
        else:
            raise ValueError(f"Unsupported format: {format}")


class StatisticsReportGenerator(ReportGenerator):
    """Generate statistics reports."""
    
    def generate_statistics_report(self, device: GPSDevice, start_date: datetime, 
                                 end_date: datetime, format: str = 'pdf') -> HttpResponse:
        """Generate statistics report for a device."""
        # Get location data
        locations = GPSLocation.objects.filter(
            device=device,
            timestamp__range=(start_date, end_date)
        ).order_by('timestamp')
        
        # Calculate statistics
        total_distance = self._calculate_total_distance(locations)
        average_speed = self._calculate_average_speed(locations)
        operating_hours = self._calculate_operating_hours(locations)
        
        # Get people count data
        people_count = self._get_people_count(device, start_date, end_date)
        
        # Prepare data
        data = [
            [f'Stats.{device.name}.{start_date.strftime("%Y.%m.%d")}'],
            ['Unidad', 'Kms', 'Sub. Del.', 'Sub. Tra.', 'Baj. Del.', 'Baj. Tra.']
        ]
        
        data.append([
            device.name,
            f"{total_distance:.2f}",
            people_count.get('sub_del', 0),
            people_count.get('sub_tra', 0),
            people_count.get('baj_del', 0),
            people_count.get('baj_tra', 0)
        ])
        
        title = f"Stats.{device.name}.{start_date.strftime('%Y.%m.%d')}"
        filename = f"Stats.{device.name}.{start_date.strftime('%Y.%m.%d')}"
        
        if format == 'pdf':
            return self.generate_pdf(data, title, filename)
        elif format == 'csv':
            return self.generate_csv(data, filename)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _calculate_total_distance(self, locations) -> float:
        """Calculate total distance from location data."""
        if len(locations) < 2:
            return 0.0
        
        total_distance = 0.0
        for i in range(1, len(locations)):
            prev_loc = locations[i-1]
            curr_loc = locations[i]
            distance = self._haversine_distance(
                prev_loc.position.y, prev_loc.position.x,
                curr_loc.position.y, curr_loc.position.x
            )
            total_distance += distance
        
        return total_distance
    
    def _calculate_average_speed(self, locations) -> float:
        """Calculate average speed from location data."""
        if not locations:
            return 0.0
        
        speeds = [loc.speed for loc in locations if loc.speed]
        return sum(speeds) / len(speeds) if speeds else 0.0
    
    def _calculate_operating_hours(self, locations) -> float:
        """Calculate operating hours from location data."""
        if not locations:
            return 0.0
        
        start_time = locations.first().timestamp
        end_time = locations.last().timestamp
        duration = end_time - start_time
        return duration.total_seconds() / 3600.0
    
    def _get_people_count(self, device, start_date, end_date) -> Dict[str, int]:
        """Get people count statistics."""
        logs = PressureWeightLog.objects.filter(
            device=device,
            timestamp__range=(start_date, end_date)
        )
        
        sub_del = sum(log.psi1 for log in logs if log.psi1)
        sub_tra = sum(log.psi1 for log in logs if log.psi1 and log.psi1 > 0)
        baj_del = sum(log.psi2 for log in logs if log.psi2)
        baj_tra = sum(log.psi2 for log in logs if log.psi2 and log.psi2 > 0)
        
        return {
            'sub_del': sub_del,
            'sub_tra': sub_tra,
            'baj_del': baj_del,
            'baj_tra': baj_tra
        }
    
    def _haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points using Haversine formula."""
        from math import radians, cos, sin, asin, sqrt
        
        # Convert to radians
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        r = 6371  # Radius of earth in kilometers
        return c * r


class PeopleCountReportGenerator(ReportGenerator):
    """Generate people count reports."""
    
    def generate_people_count_report(self, device: GPSDevice, start_date: datetime, 
                                   end_date: datetime, format: str = 'pdf') -> HttpResponse:
        """Generate people count report for a device."""
        # Get pressure weight logs
        logs = PressureWeightLog.objects.filter(
            device=device,
            timestamp__range=(start_date, end_date)
        ).order_by('timestamp')
        
        # Prepare data
        data = [
            [f'Conteo de Personas - {device.name}'],
            ['Fecha', 'Hora', 'Sensor', 'Subidas', 'Bajadas', 'Total']
        ]
        
        total_in = 0
        total_out = 0
        
        for log in logs:
            in_count = log.psi1 if log.psi1 else 0
            out_count = log.psi2 if log.psi2 else 0
            total_in += in_count
            total_out += out_count
            
            data.append([
                log.timestamp.strftime('%Y-%m-%d'),
                log.timestamp.strftime('%H:%M:%S'),
                log.sensor,
                in_count,
                out_count,
                in_count + out_count
            ])
        
        # Add totals
        data.append([
            'TOTALES', '', '', total_in, total_out, total_in + total_out
        ])
        
        title = f"Conteo de Personas - {device.name} ({start_date.date()} - {end_date.date()})"
        filename = f"people_count_{device.imei}_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}"
        
        if format == 'pdf':
            return self.generate_pdf(data, title, filename)
        elif format == 'csv':
            return self.generate_csv(data, filename)
        else:
            raise ValueError(f"Unsupported format: {format}")


class AlarmReportGenerator(ReportGenerator):
    """Generate alarm reports."""
    
    def generate_alarm_report(self, device: GPSDevice, start_date: datetime, 
                            end_date: datetime, format: str = 'pdf') -> HttpResponse:
        """Generate alarm report for a device."""
        # Get alarm events
        events = GPSEvent.objects.filter(
            device=device,
            timestamp__range=(start_date, end_date),
            event_type__in=['ALARM', 'WARNING', 'CRITICAL']
        ).order_by('timestamp')
        
        # Prepare data
        data = [
            [f'Alarmas del dia: {start_date.strftime("%A %d. %B %Y")}'],
            ['Unidad', 'Sensor', 'ID', 'Duración', 'Hora', 'Tipo']
        ]
        
        total_alarms = 0
        critical_alarms = 0
        warning_alarms = 0
        
        for event in events:
            alarm_data = event.raw_data.get('alarm_data', {})
            sensor = alarm_data.get('sensor', 'N/A')
            alarm_id = alarm_data.get('alarm_id', 'N/A')
            duration = alarm_data.get('duration', 'N/A')
            alarm_type = event.event_type
            
            total_alarms += 1
            if alarm_type == 'CRITICAL':
                critical_alarms += 1
            elif alarm_type == 'WARNING':
                warning_alarms += 1
            
            data.append([
                device.name,
                sensor,
                alarm_id,
                duration,
                event.timestamp.strftime('%H:%M:%S'),
                alarm_type
            ])
        
        # Add summary
        data.append([
            'RESUMEN', '', '', '', '', ''
        ])
        data.append([
            'Total Alarmas', total_alarms, '', '', '', ''
        ])
        data.append([
            'Alarmas Críticas', critical_alarms, '', '', '', ''
        ])
        data.append([
            'Alarmas de Advertencia', warning_alarms, '', '', '', ''
        ])
        
        title = f"Alarmas - {device.name} ({start_date.date()})"
        filename = f"alarm_report_{device.imei}_{start_date.strftime('%Y%m%d')}"
        
        if format == 'pdf':
            return self.generate_pdf(data, title, filename)
        elif format == 'csv':
            return self.generate_csv(data, filename)
        else:
            raise ValueError(f"Unsupported format: {format}")


class RouteReportGenerator(ReportGenerator):
    """Generate route-specific reports."""
    
    def generate_route_people_report(self, route_number: int, report_date: date, 
                                   format: str = 'pdf') -> HttpResponse:
        """Generate people count report for a specific route."""
        # Get devices for the route
        devices = GPSDevice.objects.filter(route=route_number)
        
        # Prepare data
        data = [
            [f'Conteo de Personas - {find_choice(route_number)} - {report_date.strftime("%A %d. %B %Y")}'],
            ['Unidad', 'Sensor', 'Subidas', 'Bajadas', 'Total', 'Diferencia']
        ]
        
        total_up = 0
        total_down = 0
        
        for device in devices:
            # Get people count for the device
            start_time = datetime.combine(report_date, time(3, 0))
            end_time = start_time + timedelta(days=1)
            
            logs = PressureWeightLog.objects.filter(
                device=device,
                timestamp__range=(start_time, end_time)
            )
            
            device_up = sum(log.psi1 for log in logs if log.psi1)
            device_down = sum(log.psi2 for log in logs if log.psi2)
            
            total_up += device_up
            total_down += device_down
            
            data.append([
                device.name,
                'Sensor Principal',
                device_up,
                device_down,
                device_up + device_down,
                abs(device_up - device_down)
            ])
        
        # Add totals
        data.append([
            'TOTALES', '', total_up, total_down, total_up + total_down, abs(total_up - total_down)
        ])
        
        title = f"Conteo de Personas - {find_choice(route_number)} - {report_date.strftime('%Y.%m.%d')}"
        filename = f"people_count_route_{route_number}_{report_date.strftime('%Y%m%d')}"
        
        if format == 'pdf':
            return self.generate_pdf(data, title, filename)
        elif format == 'csv':
            return self.generate_csv(data, filename)
        else:
            raise ValueError(f"Unsupported format: {format}")


class ReportService:
    """Main service for report generation."""
    
    def __init__(self, user):
        """Initialize the report service."""
        self.user = user
        self.ticket_generator = TicketReportGenerator(user)
        self.stats_generator = StatisticsReportGenerator(user)
        self.people_generator = PeopleCountReportGenerator(user)
        self.alarm_generator = AlarmReportGenerator(user)
        self.route_generator = RouteReportGenerator(user)
    
    def generate_report(self, report_type: str, device_id: int, start_date: datetime, 
                       end_date: datetime, format: str = 'pdf') -> HttpResponse:
        """Generate a specific type of report."""
        device = get_object_or_404(GPSDevice, id=device_id)
        
        # Check permissions
        if not (device.owner == self.user or self.user.is_staff):
            raise Http404("No permission to access this device")
        
        if report_type == 'ticket':
            return self.ticket_generator.generate_ticket_report(device, start_date, end_date, format)
        elif report_type == 'statistics':
            return self.stats_generator.generate_statistics_report(device, start_date, end_date, format)
        elif report_type == 'people':
            return self.people_generator.generate_people_count_report(device, start_date, end_date, format)
        elif report_type == 'alarm':
            return self.alarm_generator.generate_alarm_report(device, start_date, end_date, format)
        else:
            raise ValueError(f"Unknown report type: {report_type}")
    
    def generate_route_report(self, route_number: int, report_date: date, 
                            report_type: str = 'people', format: str = 'pdf') -> HttpResponse:
        """Generate a route-specific report."""
        if report_type == 'people':
            return self.route_generator.generate_route_people_report(route_number, report_date, format)
        else:
            raise ValueError(f"Unknown route report type: {report_type}")
    
    def get_available_reports(self) -> List[Dict[str, Any]]:
        """Get list of available report types."""
        return [
            {
                'type': 'ticket',
                'name': 'Ticket Report',
                'description': 'Report of ticket sales and collections'
            },
            {
                'type': 'statistics',
                'name': 'Statistics Report',
                'description': 'Statistical report of device operations'
            },
            {
                'type': 'people',
                'name': 'People Count Report',
                'description': 'Report of people boarding and alighting'
            },
            {
                'type': 'alarm',
                'name': 'Alarm Report',
                'description': 'Report of system alarms and warnings'
            }
        ]
    
    def get_route_choices(self) -> List[Tuple[int, str]]:
        """Get available route choices."""
        return list(RUTA_CHOICES2) 