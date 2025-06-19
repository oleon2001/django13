"""
Vehicle API views for GPS system.
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.db import transaction

from .models import Vehicle, GPSDevice, Driver


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def vehicle_list(request):
    """
    List all vehicles or create a new vehicle.
    
    GET:
    - Query parameters:
      - available: true/false - filter available vehicles
      - with_gps: true/false - filter vehicles with GPS
      - with_driver: true/false - filter vehicles with driver
      - status: filter by status
    
    POST:
    - Create new vehicle with JSON data
    """
    if request.method == 'GET':
        vehicles = Vehicle.objects.select_related('device', 'driver').all()
        
        # Apply filters
        available = request.GET.get('available')
        if available == 'true':
            vehicles = vehicles.filter(status='ACTIVE')
        
        with_gps = request.GET.get('with_gps')
        if with_gps == 'true':
            vehicles = vehicles.filter(device__isnull=False)
        elif with_gps == 'false':
            vehicles = vehicles.filter(device__isnull=True)
        
        with_driver = request.GET.get('with_driver')
        if with_driver == 'true':
            vehicles = vehicles.filter(driver__isnull=False)
        elif with_driver == 'false':
            vehicles = vehicles.filter(driver__isnull=True)
        
        status_filter = request.GET.get('status')
        if status_filter:
            vehicles = vehicles.filter(status=status_filter)
        
        # Build response data
        vehicle_data = []
        for vehicle in vehicles:
            data = {
                'id': vehicle.id,
                'plate': vehicle.plate,
                'make': vehicle.make,
                'model': vehicle.model,
                'year': vehicle.year,
                'color': vehicle.color,
                'vehicle_type': vehicle.vehicle_type,
                'status': vehicle.status,
                'vin': vehicle.vin,
                'economico': vehicle.economico,
                'fuel_type': vehicle.fuel_type,
                'engine_size': vehicle.engine_size,
                'passenger_capacity': vehicle.passenger_capacity,
                'cargo_capacity': vehicle.cargo_capacity,
                'insurance_policy': vehicle.insurance_policy,
                'insurance_expiry': vehicle.insurance_expiry.isoformat() if vehicle.insurance_expiry else None,
                'registration_expiry': vehicle.registration_expiry.isoformat() if vehicle.registration_expiry else None,
                'mileage': vehicle.mileage,
                'last_service_date': vehicle.last_service_date.isoformat() if vehicle.last_service_date else None,
                'next_service_date': vehicle.next_service_date.isoformat() if vehicle.next_service_date else None,
                'created_at': vehicle.created_at.isoformat(),
                'updated_at': vehicle.updated_at.isoformat(),
                
                # GPS Device info
                'device_id': vehicle.device.imei if vehicle.device else None,
                'device': {
                    'id': vehicle.device.id,
                    'imei': vehicle.device.imei,
                    'name': vehicle.device.name,
                    'connection_status': vehicle.device.connection_status,
                    'position': {
                        'latitude': vehicle.device.position.y,
                        'longitude': vehicle.device.position.x
                    } if vehicle.device.position else None,
                    'speed': vehicle.device.speed,
                    'last_heartbeat': vehicle.device.last_heartbeat.isoformat() if vehicle.device.last_heartbeat else None,
                } if vehicle.device else None,
                
                # Driver info
                'driver_id': vehicle.driver.id if vehicle.driver else None,
                'driver': {
                    'id': vehicle.driver.id,
                    'name': f"{vehicle.driver.name} {vehicle.driver.middle_name} {vehicle.driver.last_name}",
                    'payroll': vehicle.driver.payroll,
                    'license': vehicle.driver.license,
                    'phone': vehicle.driver.phone,
                    'is_active': vehicle.driver.is_active,
                } if vehicle.driver else None,
            }
            vehicle_data.append(data)
        
        return Response(vehicle_data)
    
    elif request.method == 'POST':
        try:
            with transaction.atomic():
                # Extract vehicle data
                vehicle_data = {
                    'plate': request.data.get('plate'),
                    'make': request.data.get('make'),
                    'model': request.data.get('model'),
                    'year': request.data.get('year'),
                    'color': request.data.get('color'),
                    'vehicle_type': request.data.get('vehicle_type', 'CAR'),
                    'status': request.data.get('status', 'ACTIVE'),
                    'vin': request.data.get('vin'),
                    'economico': request.data.get('economico'),
                    'fuel_type': request.data.get('fuel_type', 'GASOLINE'),
                    'engine_size': request.data.get('engine_size'),
                    'passenger_capacity': request.data.get('passenger_capacity'),
                    'cargo_capacity': request.data.get('cargo_capacity'),
                    'insurance_policy': request.data.get('insurance_policy'),
                    'insurance_expiry': request.data.get('insurance_expiry'),
                    'registration_expiry': request.data.get('registration_expiry'),
                    'mileage': request.data.get('mileage', 0),
                    'last_service_date': request.data.get('last_service_date'),
                    'next_service_date': request.data.get('next_service_date'),
                }
                
                # Remove None values
                vehicle_data = {k: v for k, v in vehicle_data.items() if v is not None}
                
                # Create vehicle
                vehicle = Vehicle.objects.create(**vehicle_data)
                
                # Assign GPS device if provided
                device_id = request.data.get('device_id')
                if device_id:
                    try:
                        device = GPSDevice.objects.get(imei=device_id)
                        vehicle.assign_gps_device(device)
                    except GPSDevice.DoesNotExist:
                        return Response({'error': f'GPS device with IMEI {device_id} not found'}, status=400)
                
                # Assign driver if provided
                driver_id = request.data.get('driver_id')
                if driver_id:
                    try:
                        driver = Driver.objects.get(id=driver_id)
                        vehicle.assign_driver(driver)
                    except Driver.DoesNotExist:
                        return Response({'error': f'Driver with ID {driver_id} not found'}, status=400)
                
                # Return created vehicle data
                return Response({
                    'id': vehicle.id,
                    'plate': vehicle.plate,
                    'make': vehicle.make,
                    'model': vehicle.model,
                    'year': vehicle.year,
                    'color': vehicle.color,
                    'vehicle_type': vehicle.vehicle_type,
                    'status': vehicle.status,
                    'created_at': vehicle.created_at.isoformat(),
                    'device_id': vehicle.device.imei if vehicle.device else None,
                    'driver_id': vehicle.driver.id if vehicle.driver else None,
                }, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def vehicle_detail(request, vehicle_id):
    """
    Retrieve, update or delete a vehicle.
    """
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    
    if request.method == 'GET':
        data = {
            'id': vehicle.id,
            'plate': vehicle.plate,
            'make': vehicle.make,
            'model': vehicle.model,
            'year': vehicle.year,
            'color': vehicle.color,
            'vehicle_type': vehicle.vehicle_type,
            'status': vehicle.status,
            'vin': vehicle.vin,
            'economico': vehicle.economico,
            'fuel_type': vehicle.fuel_type,
            'engine_size': vehicle.engine_size,
            'passenger_capacity': vehicle.passenger_capacity,
            'cargo_capacity': vehicle.cargo_capacity,
            'insurance_policy': vehicle.insurance_policy,
            'insurance_expiry': vehicle.insurance_expiry.isoformat() if vehicle.insurance_expiry else None,
            'registration_expiry': vehicle.registration_expiry.isoformat() if vehicle.registration_expiry else None,
            'mileage': vehicle.mileage,
            'last_service_date': vehicle.last_service_date.isoformat() if vehicle.last_service_date else None,
            'next_service_date': vehicle.next_service_date.isoformat() if vehicle.next_service_date else None,
            'created_at': vehicle.created_at.isoformat(),
            'updated_at': vehicle.updated_at.isoformat(),
            
            # GPS Device info
            'device_id': vehicle.device.imei if vehicle.device else None,
            'device': {
                'id': vehicle.device.id,
                'imei': vehicle.device.imei,
                'name': vehicle.device.name,
                'connection_status': vehicle.device.connection_status,
                'position': {
                    'latitude': vehicle.device.position.y,
                    'longitude': vehicle.device.position.x
                } if vehicle.device.position else None,
                'speed': vehicle.device.speed,
                'last_heartbeat': vehicle.device.last_heartbeat.isoformat() if vehicle.device.last_heartbeat else None,
            } if vehicle.device else None,
            
            # Driver info
            'driver_id': vehicle.driver.id if vehicle.driver else None,
            'driver': {
                'id': vehicle.driver.id,
                'name': f"{vehicle.driver.name} {vehicle.driver.middle_name} {vehicle.driver.last_name}",
                'payroll': vehicle.driver.payroll,
                'license': vehicle.driver.license,
                'phone': vehicle.driver.phone,
                'is_active': vehicle.driver.is_active,
            } if vehicle.driver else None,
        }
        return Response(data)
    
    elif request.method in ['PUT', 'PATCH']:
        try:
            with transaction.atomic():
                # Update vehicle fields
                updateable_fields = [
                    'plate', 'make', 'model', 'year', 'color', 'vehicle_type', 'status',
                    'vin', 'economico', 'fuel_type', 'engine_size', 'passenger_capacity',
                    'cargo_capacity', 'insurance_policy', 'insurance_expiry', 'registration_expiry',
                    'mileage', 'last_service_date', 'next_service_date'
                ]
                
                for field in updateable_fields:
                    if field in request.data:
                        setattr(vehicle, field, request.data[field])
                
                vehicle.save()
                
                # Handle GPS device assignment
                if 'device_id' in request.data:
                    device_id = request.data['device_id']
                    if device_id:
                        try:
                            device = GPSDevice.objects.get(imei=device_id)
                            vehicle.assign_gps_device(device)
                        except GPSDevice.DoesNotExist:
                            return Response({'error': f'GPS device with IMEI {device_id} not found'}, status=400)
                    else:
                        # Remove GPS device assignment
                        vehicle.device = None
                        vehicle.save()
                
                # Handle driver assignment
                if 'driver_id' in request.data:
                    driver_id = request.data['driver_id']
                    if driver_id:
                        try:
                            driver = Driver.objects.get(id=driver_id)
                            vehicle.assign_driver(driver)
                        except Driver.DoesNotExist:
                            return Response({'error': f'Driver with ID {driver_id} not found'}, status=400)
                    else:
                        # Remove driver assignment
                        vehicle.driver = None
                        vehicle.save()
                
                return Response({
                    'id': vehicle.id,
                    'plate': vehicle.plate,
                    'make': vehicle.make,
                    'model': vehicle.model,
                    'status': vehicle.status,
                    'updated_at': vehicle.updated_at.isoformat(),
                    'device_id': vehicle.device.imei if vehicle.device else None,
                    'driver_id': vehicle.driver.id if vehicle.driver else None,
                })
                
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        vehicle_info = f"{vehicle.plate} - {vehicle.make} {vehicle.model}"
        vehicle.delete()
        return Response({
            'message': f'Vehicle {vehicle_info} deleted successfully'
        })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def available_gps_devices(request):
    """Get all available GPS devices (not assigned to any vehicle)."""
    devices = GPSDevice.objects.filter(vehicle__isnull=True).values(
        'id', 'imei', 'name', 'connection_status', 'route', 'economico'
    )
    return Response(list(devices))


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def available_drivers(request):
    """Get all available drivers."""
    drivers = Driver.objects.filter(is_active=True).values(
        'id', 'name', 'middle_name', 'last_name', 'payroll', 'license', 'phone'
    )
    
    # Format driver names
    formatted_drivers = []
    for driver in drivers:
        formatted_drivers.append({
            'id': driver['id'],
            'name': f"{driver['name']} {driver['middle_name']} {driver['last_name']}",
            'payroll': driver['payroll'],
            'license': driver['license'],
            'phone': driver['phone']
        })
    
    return Response(formatted_drivers)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def assign_device_to_vehicle(request, vehicle_id):
    """Assign GPS device to vehicle."""
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    device_id = request.data.get('device_id')
    
    if not device_id:
        return Response({'error': 'device_id is required'}, status=400)
    
    try:
        device = GPSDevice.objects.get(imei=device_id)
        vehicle.assign_gps_device(device)
        
        return Response({
            'message': f'GPS device {device.name} assigned to vehicle {vehicle.plate}',
            'vehicle_id': vehicle.id,
            'device_id': device.imei
        })
    except GPSDevice.DoesNotExist:
        return Response({'error': f'GPS device with IMEI {device_id} not found'}, status=404)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def assign_driver_to_vehicle(request, vehicle_id):
    """Assign driver to vehicle."""
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    driver_id = request.data.get('driver_id')
    
    if not driver_id:
        return Response({'error': 'driver_id is required'}, status=400)
    
    try:
        driver = Driver.objects.get(id=driver_id)
        vehicle.assign_driver(driver)
        
        return Response({
            'message': f'Driver {driver.name} assigned to vehicle {vehicle.plate}',
            'vehicle_id': vehicle.id,
            'driver_id': driver.id
        })
    except Driver.DoesNotExist:
        return Response({'error': f'Driver with ID {driver_id} not found'}, status=404) 