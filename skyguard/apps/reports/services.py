"""
Report generation services.
"""
import csv
import json
from datetime import datetime, timedelta, time
from decimal import Decimal
from io import StringIO, BytesIO
from typing import Dict, List, Any, Optional
from django.db.models import Avg, Max, Min, Sum, Count, Q
from django.http import HttpResponse
from django.utils import timezone
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill

from skyguard.apps.gps.models import GPSDevice, GPSEvent, GPSLocation
from .models import (
    ReportTemplate, ReportExecution, TicketReport, 
    StatisticsReport, PeopleCountReport, AlarmReport
)


class ReportGenerator:
    """Base class for report generation."""
    
    def __init__(self, user):
        """Initialize the report generator."""
        self.user = user
        self.styles = getSampleStyleSheet()
    
    def generate_pdf(self, data: List[List], title: str, filename: str) -> HttpResponse:
        """Generate PDF report."""
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}.pdf"'
        
        doc = SimpleDocTemplate(response, pagesize=letter, 
                              leftMargin=0.25*inch, rightMargin=0.25*inch,
                              topMargin=0.25*inch, bottomMargin=0.25*inch)
        
        story = []
        
        # Add title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        story.append(Paragraph(title, title_style))
        story.append(Spacer(1, 12))
        
        # Create table
        table = Table(data)
        table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('BOX', (0, 0), (-1, -1), 1.5, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightyellow),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        
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
    
    def generate_excel(self, data: List[List], title: str, filename: str) -> HttpResponse:
        """Generate Excel report."""
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="{filename}.xlsx"'
        
        wb = Workbook()
        ws = wb.active
        ws.title = "Report"
        
        # Add title
        ws['A1'] = title
        ws['A1'].font = Font(bold=True, size=16)
        ws.merge_cells('A1:E1')
        ws['A1'].alignment = Alignment(horizontal='center')
        
        # Add data
        for row_idx, row in enumerate(data, start=3):
            for col_idx, cell_value in enumerate(row, start=1):
                ws.cell(row=row_idx, column=col_idx, value=cell_value)
        
        # Style header row
        for col in range(1, len(data[0]) + 1):
            cell = ws.cell(row=3, column=col)
            cell.font = Font(bold=True)
            cell.fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
        
        wb.save(response)
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
            type='TICKET'
        ).order_by('timestamp')
        
        # Prepare data
        data = [
            ['Fecha', 'Hora', 'Conductor', 'Total', 'Recibido', 'Diferencia', 'Detalles']
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
                event.timestamp.strftime('%H:%M:%S'),
                driver_name,
                f"${amount:.2f}",
                f"${received:.2f}",
                f"${difference:.2f}",
                ticket_data.get('details', '')
            ])
        
        # Add totals row
        data.append([
            'TOTALES', '', '', 
            f"${total_amount:.2f}", 
            f"${total_received:.2f}", 
            f"${total_amount - total_received:.2f}", 
            ''
        ])
        
        title = f"Reporte de Tickets - {device.name} ({start_date.date()} - {end_date.date()})"
        filename = f"ticket_report_{device.imei}_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}"
        
        if format == 'pdf':
            return self.generate_pdf(data, title, filename)
        elif format == 'csv':
            return self.generate_csv(data, filename)
        elif format == 'xlsx':
            return self.generate_excel(data, title, filename)
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
        
        # Get events
        events = GPSEvent.objects.filter(
            device=device,
            timestamp__range=(start_date, end_date)
        )
        
        total_events = events.count()
        alarm_events = events.filter(type='ALARM').count()
        
        # Prepare data
        data = [
            ['Métrica', 'Valor', 'Unidad']
        ]
        
        data.extend([
            ['Distancia Total', f"{total_distance:.2f}", 'km'],
            ['Velocidad Promedio', f"{average_speed:.2f}", 'km/h'],
            ['Horas Operación', f"{operating_hours:.2f}", 'horas'],
            ['Total Eventos', str(total_events), 'eventos'],
            ['Eventos de Alarma', str(alarm_events), 'alarmas'],
            ['Última Actualización', device.last_connection.strftime('%Y-%m-%d %H:%M:%S') if device.last_connection else 'N/A', ''],
        ])
        
        title = f"Reporte de Estadísticas - {device.name} ({start_date.date()} - {end_date.date()})"
        filename = f"stats_report_{device.imei}_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}"
        
        if format == 'pdf':
            return self.generate_pdf(data, title, filename)
        elif format == 'csv':
            return self.generate_csv(data, filename)
        elif format == 'xlsx':
            return self.generate_excel(data, title, filename)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _calculate_total_distance(self, locations) -> float:
        """Calculate total distance from location points."""
        if not locations:
            return 0.0
        
        total_distance = 0.0
        prev_location = None
        
        for location in locations:
            if prev_location and location.position and prev_location.position:
                # Calculate distance between points
                distance = self._haversine_distance(
                    prev_location.position.y, prev_location.position.x,
                    location.position.y, location.position.x
                )
                total_distance += distance
            prev_location = location
        
        return total_distance
    
    def _calculate_average_speed(self, locations) -> float:
        """Calculate average speed from location data."""
        if not locations:
            return 0.0
        
        speeds = [loc.speed for loc in locations if loc.speed and loc.speed > 0]
        return sum(speeds) / len(speeds) if speeds else 0.0
    
    def _calculate_operating_hours(self, locations) -> float:
        """Calculate operating hours from location data."""
        if not locations:
            return 0.0
        
        first_location = locations.first()
        last_location = locations.last()
        
        if first_location and last_location:
            duration = last_location.timestamp - first_location.timestamp
            return duration.total_seconds() / 3600  # Convert to hours
        
        return 0.0
    
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
        # Get people count events
        events = GPSEvent.objects.filter(
            device=device,
            timestamp__range=(start_date, end_date),
            type='PEOPLE_COUNT'
        ).order_by('timestamp')
        
        # Group by hour
        hourly_data = {}
        total_people = 0
        
        for event in events:
            hour = event.timestamp.hour
            count = event.raw_data.get('count', 0)
            
            if hour not in hourly_data:
                hourly_data[hour] = 0
            hourly_data[hour] += count
            total_people += count
        
        # Find peak hour
        peak_hour = max(hourly_data.items(), key=lambda x: x[1]) if hourly_data else (0, 0)
        
        # Prepare data
        data = [
            ['Hora', 'Personas', 'Porcentaje']
        ]
        
        for hour in range(24):
            count = hourly_data.get(hour, 0)
            percentage = (count / total_people * 100) if total_people > 0 else 0
            data.append([
                f"{hour:02d}:00",
                str(count),
                f"{percentage:.1f}%"
            ])
        
        # Add summary
        data.extend([
            ['', '', ''],
            ['TOTAL', str(total_people), '100%'],
            ['HORA PICO', f"{peak_hour[0]:02d}:00", f"{peak_hour[1]} personas"]
        ])
        
        title = f"Reporte de Conteo de Personas - {device.name} ({start_date.date()} - {end_date.date()})"
        filename = f"people_count_{device.imei}_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}"
        
        if format == 'pdf':
            return self.generate_pdf(data, title, filename)
        elif format == 'csv':
            return self.generate_csv(data, filename)
        elif format == 'xlsx':
            return self.generate_excel(data, title, filename)
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
            type='ALARM'
        ).order_by('timestamp')
        
        # Group alarms by type
        alarm_types = {}
        critical_alarms = 0
        warning_alarms = 0
        
        for event in events:
            alarm_type = event.raw_data.get('alarm_type', 'Unknown')
            severity = event.raw_data.get('severity', 'warning')
            
            if alarm_type not in alarm_types:
                alarm_types[alarm_type] = 0
            alarm_types[alarm_type] += 1
            
            if severity == 'critical':
                critical_alarms += 1
            else:
                warning_alarms += 1
        
        # Prepare data
        data = [
            ['Tipo de Alarma', 'Cantidad', 'Porcentaje']
        ]
        
        total_alarms = len(events)
        
        for alarm_type, count in alarm_types.items():
            percentage = (count / total_alarms * 100) if total_alarms > 0 else 0
            data.append([
                alarm_type,
                str(count),
                f"{percentage:.1f}%"
            ])
        
        # Add summary
        data.extend([
            ['', '', ''],
            ['TOTAL ALARMAS', str(total_alarms), '100%'],
            ['ALARMAS CRÍTICAS', str(critical_alarms), ''],
            ['ALARMAS DE ADVERTENCIA', str(warning_alarms), '']
        ])
        
        title = f"Reporte de Alarmas - {device.name} ({start_date.date()} - {end_date.date()})"
        filename = f"alarm_report_{device.imei}_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}"
        
        if format == 'pdf':
            return self.generate_pdf(data, title, filename)
        elif format == 'csv':
            return self.generate_csv(data, filename)
        elif format == 'xlsx':
            return self.generate_excel(data, title, filename)
        else:
            raise ValueError(f"Unsupported format: {format}")


class ReportService:
    """Main service for report operations."""
    
    def __init__(self, user):
        """Initialize the report service."""
        self.user = user
        self.ticket_generator = TicketReportGenerator(user)
        self.stats_generator = StatisticsReportGenerator(user)
        self.people_generator = PeopleCountReportGenerator(user)
        self.alarm_generator = AlarmReportGenerator(user)
    
    def generate_report(self, report_type: str, device_id: int, start_date: datetime, 
                       end_date: datetime, format: str = 'pdf') -> HttpResponse:
        """Generate a report based on type."""
        try:
            device = GPSDevice.objects.get(id=device_id)
            
            if report_type == 'ticket':
                return self.ticket_generator.generate_ticket_report(device, start_date, end_date, format)
            elif report_type == 'stats':
                return self.stats_generator.generate_statistics_report(device, start_date, end_date, format)
            elif report_type == 'people':
                return self.people_generator.generate_people_count_report(device, start_date, end_date, format)
            elif report_type == 'alarm':
                return self.alarm_generator.generate_alarm_report(device, start_date, end_date, format)
            else:
                raise ValueError(f"Unsupported report type: {report_type}")
        
        except GPSDevice.DoesNotExist:
            raise ValueError(f"Device with ID {device_id} not found")
    
    def get_available_reports(self) -> List[Dict[str, Any]]:
        """Get list of available report types."""
        return [
            {
                'type': 'ticket',
                'name': 'Reporte de Tickets',
                'description': 'Reporte de tickets y pagos por conductor',
                'formats': ['pdf', 'csv', 'xlsx']
            },
            {
                'type': 'stats',
                'name': 'Reporte de Estadísticas',
                'description': 'Estadísticas de operación del dispositivo',
                'formats': ['pdf', 'csv', 'xlsx']
            },
            {
                'type': 'people',
                'name': 'Reporte de Conteo de Personas',
                'description': 'Conteo de personas por hora',
                'formats': ['pdf', 'csv', 'xlsx']
            },
            {
                'type': 'alarm',
                'name': 'Reporte de Alarmas',
                'description': 'Reporte de alarmas del dispositivo',
                'formats': ['pdf', 'csv', 'xlsx']
            }
        ] 