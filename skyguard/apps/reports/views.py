"""
Views for the reports application.
"""
from datetime import datetime, timedelta
from typing import Dict, Any
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
import logging
from django.db.models import Count

from skyguard.apps.gps.models import GPSDevice
from .services import ReportService
from .models import ReportTemplate, ReportExecution

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def available_reports(request):
    """
    Get list of available report types.
    
    Returns:
        JSON response with available report types
    """
    try:
        service = ReportService(request.user)
        reports = service.get_available_reports()
        
        return Response({
            'status': 'success',
            'reports': reports
        })
    except Exception as e:
        logger.error(f"Error getting available reports: {e}")
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def device_reports(request, device_id):
    """
    Get reports for a specific device.
    
    Args:
        device_id: ID of the device
        
    Returns:
        JSON response with device reports
    """
    try:
        device = GPSDevice.objects.get(id=device_id)
        
        # Get recent report executions for this device
        executions = ReportExecution.objects.filter(
            template__report_type__in=['ticket', 'stats', 'people', 'alarm'],
            parameters__device_id=device_id
        ).order_by('-created_at')[:10]
        
        report_data = []
        for execution in executions:
            report_data.append({
                'id': execution.id,
                'type': execution.template.report_type,
                'name': execution.template.name,
                'status': execution.status,
                'created_at': execution.created_at.isoformat(),
                'completed_at': execution.completed_at.isoformat() if execution.completed_at else None,
                'duration': execution.duration.total_seconds() if execution.duration else None
            })
        
        return Response({
            'status': 'success',
            'device_id': device_id,
            'device_name': device.name,
            'reports': report_data
        })
    except GPSDevice.DoesNotExist:
        return Response({
            'status': 'error',
            'message': 'Device not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error getting device reports: {e}")
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_report(request):
    """
    Generate a report.
    
    Args:
        report_type: Type of report (ticket, stats, people, alarm)
        device_id: ID of the device
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        format: Output format (pdf, csv, xlsx)
        
    Returns:
        File response with the generated report
    """
    try:
        # Validate parameters
        report_type = request.data.get('report_type')
        device_id = request.data.get('device_id')
        start_date_str = request.data.get('start_date')
        end_date_str = request.data.get('end_date')
        format_type = request.data.get('format', 'pdf')
        
        if not all([report_type, device_id, start_date_str, end_date_str]):
            return Response({
                'status': 'error',
                'message': 'Missing required parameters'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Parse dates
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        except ValueError:
            return Response({
                'status': 'error',
                'message': 'Invalid date format. Use YYYY-MM-DD'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate date range
        if start_date > end_date:
            return Response({
                'status': 'error',
                'message': 'Start date must be before end date'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate report
        service = ReportService(request.user)
        response = service.generate_report(
            report_type=report_type,
            device_id=device_id,
            start_date=start_date,
            end_date=end_date,
            format=format_type
        )
        
        # Log report generation
        logger.info(f"Report generated: {report_type} for device {device_id} by user {request.user.username}")
        
        return response
        
    except ValueError as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def report_templates(request):
    """
    Get available report templates.
    
    Returns:
        JSON response with report templates
    """
    try:
        templates = ReportTemplate.objects.filter(is_active=True).order_by('name')
        
        template_data = []
        for template in templates:
            template_data.append({
                'id': template.id,
                'name': template.name,
                'description': template.description,
                'report_type': template.report_type,
                'format': template.format,
                'created_by': template.created_by.username,
                'created_at': template.created_at.isoformat()
            })
        
        return Response({
            'status': 'success',
            'templates': template_data
        })
    except Exception as e:
        logger.error(f"Error getting report templates: {e}")
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_report_template(request):
    """
    Create a new report template.
    
    Args:
        name: Template name
        description: Template description
        report_type: Type of report
        format: Output format
        template_data: Template configuration data
        
    Returns:
        JSON response with created template
    """
    try:
        # Validate required fields
        required_fields = ['name', 'report_type', 'format']
        for field in required_fields:
            if field not in request.data:
                return Response({
                    'status': 'error',
                    'message': f'Missing required field: {field}'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create template
        template = ReportTemplate.objects.create(
            name=request.data['name'],
            description=request.data.get('description', ''),
            report_type=request.data['report_type'],
            format=request.data['format'],
            template_data=request.data.get('template_data', {}),
            created_by=request.user
        )
        
        return Response({
            'status': 'success',
            'template': {
                'id': template.id,
                'name': template.name,
                'description': template.description,
                'report_type': template.report_type,
                'format': template.format,
                'created_by': template.created_by.username,
                'created_at': template.created_at.isoformat()
            }
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Error creating report template: {e}")
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def report_executions(request):
    """
    Get recent report executions.
    
    Returns:
        JSON response with report executions
    """
    try:
        executions = ReportExecution.objects.filter(
            executed_by=request.user
        ).order_by('-created_at')[:20]
        
        execution_data = []
        for execution in executions:
            execution_data.append({
                'id': execution.id,
                'template_name': execution.template.name,
                'report_type': execution.template.report_type,
                'status': execution.status,
                'created_at': execution.created_at.isoformat(),
                'completed_at': execution.completed_at.isoformat() if execution.completed_at else None,
                'duration': execution.duration.total_seconds() if execution.duration else None,
                'error_message': execution.error_message if execution.status == 'failed' else None
            })
        
        return Response({
            'status': 'success',
            'executions': execution_data
        })
    except Exception as e:
        logger.error(f"Error getting report executions: {e}")
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_report_template(request, template_id):
    """
    Delete a report template.
    
    Args:
        template_id: ID of the template to delete
        
    Returns:
        JSON response with deletion status
    """
    try:
        template = ReportTemplate.objects.get(id=template_id, created_by=request.user)
        template.delete()
        
        return Response({
            'status': 'success',
            'message': 'Template deleted successfully'
        })
    except ReportTemplate.DoesNotExist:
        return Response({
            'status': 'error',
            'message': 'Template not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error deleting report template: {e}")
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def report_statistics(request):
    """
    Get report generation statistics.
    
    Returns:
        JSON response with report statistics
    """
    try:
        # Get statistics for the last 30 days
        thirty_days_ago = timezone.now() - timedelta(days=30)
        
        total_executions = ReportExecution.objects.filter(
            executed_by=request.user,
            created_at__gte=thirty_days_ago
        ).count()
        
        completed_executions = ReportExecution.objects.filter(
            executed_by=request.user,
            status='completed',
            created_at__gte=thirty_days_ago
        ).count()
        
        failed_executions = ReportExecution.objects.filter(
            executed_by=request.user,
            status='failed',
            created_at__gte=thirty_days_ago
        ).count()
        
        # Get report type distribution
        report_types = ReportExecution.objects.filter(
            executed_by=request.user,
            created_at__gte=thirty_days_ago
        ).values('template__report_type').annotate(count=Count('id'))
        
        return Response({
            'status': 'success',
            'statistics': {
                'total_executions': total_executions,
                'completed_executions': completed_executions,
                'failed_executions': failed_executions,
                'success_rate': (completed_executions / total_executions * 100) if total_executions > 0 else 0,
                'report_types': list(report_types)
            }
        })
    except Exception as e:
        logger.error(f"Error getting report statistics: {e}")
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class ReportDownloadView(View):
    """View for downloading generated reports."""
    
    def get(self, request, execution_id):
        """
        Download a generated report.
        
        Args:
            execution_id: ID of the report execution
            
        Returns:
            File response with the report
        """
        try:
            execution = ReportExecution.objects.get(
                id=execution_id,
                executed_by=request.user,
                status='completed'
            )
            
            if not execution.result_file:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Report file not found'
                }, status=404)
            
            response = HttpResponse(
                execution.result_file.read(),
                content_type='application/octet-stream'
            )
            response['Content-Disposition'] = f'attachment; filename="{execution.result_file.name}"'
            return response
            
        except ReportExecution.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Report execution not found'
            }, status=404)
        except Exception as e:
            logger.error(f"Error downloading report: {e}")
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500) 