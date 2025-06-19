"""
Driver API views for GPS system.
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.db import transaction

from .models import Driver, GPSDevice, Vehicle


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def driver_list(request):
    """
    List all drivers or create a new driver.
    
    GET:
    - Query parameters:
      - available: true/false - filter available drivers
      - with_vehicle: true/false - filter drivers with vehicle
      - is_active: true/false - filter active drivers
    
    POST:
    - Create new driver with JSON data
    """
    if request.method == 'GET':
        drivers = Driver.objects.select_related().prefetch_related('vehicles').all()
        
        # Apply filters
        available = request.GET.get('available')
        if available == 'true':
            drivers = drivers.filter(is_active=True)
        
        with_vehicle = request.GET.get('with_vehicle')
        if with_vehicle == 'true':
            drivers = drivers.filter(vehicles__isnull=False)
        elif with_vehicle == 'false':
            drivers = drivers.filter(vehicles__isnull=True)
        
        is_active = request.GET.get('is_active')
        if is_active == 'true':
            drivers = drivers.filter(is_active=True)
        elif is_active == 'false':
            drivers = drivers.filter(is_active=False)
        
        # Build response data
        driver_data = []
        for driver in drivers:
            # Get assigned vehicle (if any)
            assigned_vehicle = driver.vehicles.first()
            
            data = {
                'id': driver.id,
                'name': driver.name,
                'middle_name': driver.middle_name,
                'last_name': driver.last_name,
                'full_name': f"{driver.name} {driver.middle_name} {driver.last_name}",
                'birth_date': driver.birth_date.isoformat() if driver.birth_date else None,
                'civil_status': driver.civil_status,
                'payroll': driver.payroll,
                'social_security': driver.social_security,
                'tax_id': driver.tax_id,
                'license': driver.license,
                'license_expiry': driver.license_expiry.isoformat() if driver.license_expiry else None,
                'address': driver.address,
                'phone': driver.phone,
                'phone1': driver.phone1,
                'phone2': driver.phone2,
                'is_active': driver.is_active,
                'created_at': driver.created_at.isoformat(),
                'updated_at': driver.updated_at.isoformat(),
                
                # Vehicle info (if assigned)
                'vehicle_id': assigned_vehicle.id if assigned_vehicle else None,
                'vehicle': {
                    'id': assigned_vehicle.id,
                    'plate': assigned_vehicle.plate,
                    'make': assigned_vehicle.make,
                    'model': assigned_vehicle.model,
                    'year': assigned_vehicle.year,
                    'color': assigned_vehicle.color,
                    'status': assigned_vehicle.status,
                } if assigned_vehicle else None,
                
                # GPS Device info (through vehicle)
                'device_id': assigned_vehicle.device.imei if assigned_vehicle and assigned_vehicle.device else None,
                'device': {
                    'id': assigned_vehicle.device.id,
                    'imei': assigned_vehicle.device.imei,
                    'name': assigned_vehicle.device.name,
                    'connection_status': assigned_vehicle.device.connection_status,
                    'position': {
                        'latitude': assigned_vehicle.device.position.y,
                        'longitude': assigned_vehicle.device.position.x
                    } if assigned_vehicle.device.position else None,
                    'speed': assigned_vehicle.device.speed,
                    'last_heartbeat': assigned_vehicle.device.last_heartbeat.isoformat() if assigned_vehicle.device.last_heartbeat else None,
                } if assigned_vehicle and assigned_vehicle.device else None,
            }
            driver_data.append(data)
        
        return Response(driver_data)
    
    elif request.method == 'POST':
        try:
            with transaction.atomic():
                # Extract driver data
                driver_data = {
                    'name': request.data.get('name'),
                    'middle_name': request.data.get('middle_name', ''),
                    'last_name': request.data.get('last_name', ''),
                    'birth_date': request.data.get('birth_date'),
                    'civil_status': request.data.get('civil_status', 'SOL'),
                    'payroll': request.data.get('payroll'),
                    'social_security': request.data.get('social_security'),
                    'tax_id': request.data.get('tax_id'),
                    'license': request.data.get('license'),
                    'license_expiry': request.data.get('license_expiry'),
                    'address': request.data.get('address', ''),
                    'phone': request.data.get('phone', ''),
                    'phone1': request.data.get('phone1'),
                    'phone2': request.data.get('phone2'),
                    'is_active': request.data.get('is_active', True),
                }
                
                # Remove None values
                driver_data = {k: v for k, v in driver_data.items() if v is not None}
                
                # Create driver
                driver = Driver.objects.create(**driver_data)
                
                # Assign vehicle if provided
                vehicle_id = request.data.get('vehicle_id')
                if vehicle_id:
                    try:
                        vehicle = Vehicle.objects.get(id=vehicle_id)
                        vehicle.assign_driver(driver)
                    except Vehicle.DoesNotExist:
                        return Response({'error': f'Vehicle with ID {vehicle_id} not found'}, status=400)
                
                # Return created driver data
                return Response({
                    'id': driver.id,
                    'name': driver.name,
                    'middle_name': driver.middle_name,
                    'last_name': driver.last_name,
                    'full_name': f"{driver.name} {driver.middle_name} {driver.last_name}",
                    'payroll': driver.payroll,
                    'license': driver.license,
                    'phone': driver.phone,
                    'is_active': driver.is_active,
                    'created_at': driver.created_at.isoformat(),
                    'vehicle_id': vehicle_id if vehicle_id else None,
                }, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def driver_detail(request, driver_id):
    """
    Retrieve, update or delete a driver.
    """
    driver = get_object_or_404(Driver, id=driver_id)
    
    if request.method == 'GET':
        # Get assigned vehicle (if any)
        assigned_vehicle = driver.vehicles.first()
        
        data = {
            'id': driver.id,
            'name': driver.name,
            'middle_name': driver.middle_name,
            'last_name': driver.last_name,
            'full_name': f"{driver.name} {driver.middle_name} {driver.last_name}",
            'birth_date': driver.birth_date.isoformat() if driver.birth_date else None,
            'civil_status': driver.civil_status,
            'payroll': driver.payroll,
            'social_security': driver.social_security,
            'tax_id': driver.tax_id,
            'license': driver.license,
            'license_expiry': driver.license_expiry.isoformat() if driver.license_expiry else None,
            'address': driver.address,
            'phone': driver.phone,
            'phone1': driver.phone1,
            'phone2': driver.phone2,
            'is_active': driver.is_active,
            'created_at': driver.created_at.isoformat(),
            'updated_at': driver.updated_at.isoformat(),
            
            # Vehicle info (if assigned)
            'vehicle_id': assigned_vehicle.id if assigned_vehicle else None,
            'vehicle': {
                'id': assigned_vehicle.id,
                'plate': assigned_vehicle.plate,
                'make': assigned_vehicle.make,
                'model': assigned_vehicle.model,
                'year': assigned_vehicle.year,
                'color': assigned_vehicle.color,
                'status': assigned_vehicle.status,
            } if assigned_vehicle else None,
            
            # GPS Device info (through vehicle)
            'device_id': assigned_vehicle.device.imei if assigned_vehicle and assigned_vehicle.device else None,
            'device': {
                'id': assigned_vehicle.device.id,
                'imei': assigned_vehicle.device.imei,
                'name': assigned_vehicle.device.name,
                'connection_status': assigned_vehicle.device.connection_status,
                'position': {
                    'latitude': assigned_vehicle.device.position.y,
                    'longitude': assigned_vehicle.device.position.x
                } if assigned_vehicle.device.position else None,
                'speed': assigned_vehicle.device.speed,
                'last_heartbeat': assigned_vehicle.device.last_heartbeat.isoformat() if assigned_vehicle.device.last_heartbeat else None,
            } if assigned_vehicle and assigned_vehicle.device else None,
        }
        return Response(data)
    
    elif request.method in ['PUT', 'PATCH']:
        try:
            with transaction.atomic():
                # Update driver fields
                updateable_fields = [
                    'name', 'middle_name', 'last_name', 'birth_date', 'civil_status',
                    'payroll', 'social_security', 'tax_id', 'license', 'license_expiry',
                    'address', 'phone', 'phone1', 'phone2', 'is_active'
                ]
                
                for field in updateable_fields:
                    if field in request.data:
                        setattr(driver, field, request.data[field])
                
                driver.save()
                
                # Handle vehicle assignment
                if 'vehicle_id' in request.data:
                    vehicle_id = request.data['vehicle_id']
                    if vehicle_id:
                        try:
                            vehicle = Vehicle.objects.get(id=vehicle_id)
                            # Remove driver from previous vehicle if exists
                            previous_vehicle = driver.vehicles.first()
                            if previous_vehicle:
                                previous_vehicle.driver = None
                                previous_vehicle.save()
                            # Assign to new vehicle
                            vehicle.assign_driver(driver)
                        except Vehicle.DoesNotExist:
                            return Response({'error': f'Vehicle with ID {vehicle_id} not found'}, status=400)
                    else:
                        # Remove vehicle assignment
                        assigned_vehicle = driver.vehicles.first()
                        if assigned_vehicle:
                            assigned_vehicle.driver = None
                            assigned_vehicle.save()
                
                return Response({
                    'id': driver.id,
                    'name': driver.name,
                    'middle_name': driver.middle_name,
                    'last_name': driver.last_name,
                    'full_name': f"{driver.name} {driver.middle_name} {driver.last_name}",
                    'payroll': driver.payroll,
                    'license': driver.license,
                    'phone': driver.phone,
                    'is_active': driver.is_active,
                    'updated_at': driver.updated_at.isoformat(),
                    'vehicle_id': driver.vehicles.first().id if driver.vehicles.first() else None,
                })
                
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        driver_info = f"{driver.name} {driver.middle_name} {driver.last_name}"
        # Remove driver from any assigned vehicle first
        assigned_vehicle = driver.vehicles.first()
        if assigned_vehicle:
            assigned_vehicle.driver = None
            assigned_vehicle.save()
        
        driver.delete()
        return Response({
            'message': f'Driver {driver_info} deleted successfully'
        })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def available_vehicles(request):
    """Get all available vehicles (not assigned to any driver)."""
    vehicles = Vehicle.objects.filter(driver__isnull=True, status='ACTIVE').values(
        'id', 'plate', 'make', 'model', 'year', 'color', 'vehicle_type'
    )
    
    # Format vehicle display
    formatted_vehicles = []
    for vehicle in vehicles:
        formatted_vehicles.append({
            'id': vehicle['id'],
            'plate': vehicle['plate'],
            'display_name': f"{vehicle['plate']} - {vehicle['make']} {vehicle['model']} ({vehicle['year']})",
            'make': vehicle['make'],
            'model': vehicle['model'],
            'year': vehicle['year'],
            'color': vehicle['color'],
            'vehicle_type': vehicle['vehicle_type']
        })
    
    return Response(formatted_vehicles)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def assign_vehicle_to_driver(request, driver_id):
    """Assign vehicle to driver."""
    driver = get_object_or_404(Driver, id=driver_id)
    vehicle_id = request.data.get('vehicle_id')
    
    if not vehicle_id:
        return Response({'error': 'vehicle_id is required'}, status=400)
    
    try:
        vehicle = Vehicle.objects.get(id=vehicle_id)
        # Remove driver from previous vehicle if exists
        previous_vehicle = driver.vehicles.first()
        if previous_vehicle:
            previous_vehicle.driver = None
            previous_vehicle.save()
        
        # Assign to new vehicle
        vehicle.assign_driver(driver)
        
        return Response({
            'message': f'Vehicle {vehicle.plate} assigned to driver {driver.name}',
            'driver_id': driver.id,
            'vehicle_id': vehicle.id
        })
    except Vehicle.DoesNotExist:
        return Response({'error': f'Vehicle with ID {vehicle_id} not found'}, status=404) 