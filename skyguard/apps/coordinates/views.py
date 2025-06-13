from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from .models import Coordinate
from .serializers import CoordinateSerializer
import random
from datetime import datetime, timedelta

class CoordinateViewSet(viewsets.ModelViewSet):
    queryset = Coordinate.objects.all()
    serializer_class = CoordinateSerializer
    permission_classes = [AllowAny]  # Allow unauthenticated access
    
    @action(detail=False, methods=['get'])
    def generate_test_data(self, request):
        """Generate test coordinate data for a device"""
        device_id = request.query_params.get('device_id', 'test_device')
        num_points = int(request.query_params.get('points', 10))
        
        # Base coordinates (example: Mexico City)
        base_lat = 19.4326
        base_lon = -99.1332
        
        coordinates = []
        for _ in range(num_points):
            # Generate random offset within ~1km
            lat_offset = random.uniform(-0.01, 0.01)
            lon_offset = random.uniform(-0.01, 0.01)
            
            coordinate = Coordinate.objects.create(
                latitude=base_lat + lat_offset,
                longitude=base_lon + lon_offset,
                device_id=device_id
            )
            coordinates.append(coordinate)
        
        serializer = self.get_serializer(coordinates, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def get_latest(self, request):
        """Get the latest coordinates for all devices"""
        device_id = request.query_params.get('device_id')
        if device_id:
            latest = Coordinate.objects.filter(device_id=device_id).order_by('-timestamp').first()
        else:
            latest = Coordinate.objects.order_by('-timestamp').first()
            
        if latest:
            serializer = self.get_serializer(latest)
            return Response(serializer.data)
        return Response({'error': 'No coordinates found'}, status=404) 