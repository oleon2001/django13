"""
Utility functions for the GPS tracking system core.
"""

import logging
import hashlib
import hmac
import base64
import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from django.conf import settings
from django.core.cache import cache
from django.contrib.gis.geos import Point


logger = logging.getLogger(__name__)


def generate_device_token(imei: int, secret: str = None) -> str:
    """Generate a secure token for device authentication."""
    if secret is None:
        secret = getattr(settings, 'DEVICE_SECRET_KEY', 'default-secret-key')
    
    timestamp = str(int(datetime.now().timestamp()))
    message = f"{imei}:{timestamp}"
    
    # Create HMAC signature
    signature = hmac.new(
        secret.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    # Combine message and signature
    token_data = f"{message}:{signature}"
    return base64.b64encode(token_data.encode('utf-8')).decode('utf-8')


def verify_device_token(token: str, imei: int, secret: str = None) -> bool:
    """Verify a device authentication token."""
    try:
        if secret is None:
            secret = getattr(settings, 'DEVICE_SECRET_KEY', 'default-secret-key')
        
        # Decode token
        token_data = base64.b64decode(token.encode('utf-8')).decode('utf-8')
        message, signature = token_data.rsplit(':', 1)
        
        # Verify signature
        expected_signature = hmac.new(
            secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(signature, expected_signature):
            return False
        
        # Parse message
        device_imei, timestamp = message.split(':', 1)
        
        # Verify IMEI
        if int(device_imei) != imei:
            return False
        
        # Check timestamp (token valid for 1 hour)
        token_time = datetime.fromtimestamp(int(timestamp))
        if datetime.now() - token_time > timedelta(hours=1):
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Error verifying device token: {e}")
        return False


def calculate_distance(point1: Point, point2: Point) -> float:
    """Calculate distance between two points in kilometers."""
    try:
        from geopy.distance import geodesic
        
        lat1, lon1 = point1.y, point1.x
        lat2, lon2 = point2.y, point2.x
        
        return geodesic((lat1, lon1), (lat2, lon2)).kilometers
        
    except ImportError:
        # Fallback calculation using Haversine formula
        import math
        
        lat1, lon1 = math.radians(point1.y), math.radians(point1.x)
        lat2, lon2 = math.radians(point2.y), math.radians(point2.x)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Earth radius in kilometers
        r = 6371
        
        return c * r


def validate_coordinates(latitude: float, longitude: float) -> bool:
    """Validate GPS coordinates."""
    return -90 <= latitude <= 90 and -180 <= longitude <= 180


def format_coordinates(latitude: float, longitude: float, precision: int = 6) -> str:
    """Format coordinates for display."""
    lat_dir = 'N' if latitude >= 0 else 'S'
    lon_dir = 'E' if longitude >= 0 else 'W'
    
    lat_abs = abs(latitude)
    lon_abs = abs(longitude)
    
    return f"{lat_abs:.{precision}f}°{lat_dir}, {lon_abs:.{precision}f}°{lon_dir}"


def parse_coordinates(coord_string: str) -> Optional[tuple]:
    """Parse coordinate string into (latitude, longitude) tuple."""
    try:
        # Remove common formatting
        coord_string = coord_string.replace('°', '').replace(' ', '')
        
        # Split by comma
        parts = coord_string.split(',')
        if len(parts) != 2:
            return None
        
        lat_str, lon_str = parts
        
        # Parse latitude
        if 'N' in lat_str:
            lat = float(lat_str.replace('N', ''))
        elif 'S' in lat_str:
            lat = -float(lat_str.replace('S', ''))
        else:
            lat = float(lat_str)
        
        # Parse longitude
        if 'E' in lon_str:
            lon = float(lon_str.replace('E', ''))
        elif 'W' in lon_str:
            lon = -float(lon_str.replace('W', ''))
        else:
            lon = float(lon_str)
        
        if validate_coordinates(lat, lon):
            return (lat, lon)
        
        return None
        
    except (ValueError, AttributeError):
        return None


def cache_device_data(imei: int, data: Dict[str, Any], timeout: int = 300) -> None:
    """Cache device data."""
    cache_key = f"device_data:{imei}"
    cache.set(cache_key, data, timeout)


def get_cached_device_data(imei: int) -> Optional[Dict[str, Any]]:
    """Get cached device data."""
    cache_key = f"device_data:{imei}"
    return cache.get(cache_key)


def clear_device_cache(imei: int) -> None:
    """Clear cached device data."""
    cache_key = f"device_data:{imei}"
    cache.delete(cache_key)


def format_speed(speed_kmh: float) -> str:
    """Format speed for display."""
    if speed_kmh < 1:
        return f"{speed_kmh * 1000:.0f} m/h"
    elif speed_kmh < 60:
        return f"{speed_kmh:.1f} km/h"
    else:
        return f"{speed_kmh:.0f} km/h"


def format_duration(seconds: int) -> str:
    """Format duration for display."""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes}m {seconds % 60}s"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"


def calculate_bearing(point1: Point, point2: Point) -> float:
    """Calculate bearing between two points in degrees."""
    try:
        import math
        
        lat1, lon1 = math.radians(point1.y), math.radians(point1.x)
        lat2, lon2 = math.radians(point2.y), math.radians(point2.x)
        
        dlon = lon2 - lon1
        
        y = math.sin(dlon) * math.cos(lat2)
        x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
        
        bearing = math.degrees(math.atan2(y, x))
        
        # Normalize to 0-360
        bearing = (bearing + 360) % 360
        
        return bearing
        
    except Exception as e:
        logger.error(f"Error calculating bearing: {e}")
        return 0.0


def is_point_in_polygon(point: Point, polygon: List[Point]) -> bool:
    """Check if point is inside polygon using ray casting algorithm."""
    try:
        x, y = point.x, point.y
        n = len(polygon)
        inside = False
        
        p1x, p1y = polygon[0].x, polygon[0].y
        for i in range(n + 1):
            p2x, p2y = polygon[i % n].x, polygon[i % n].y
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        
        return inside
        
    except Exception as e:
        logger.error(f"Error checking point in polygon: {e}")
        return False


def generate_device_report(device_data: Dict[str, Any], 
                         locations: List[Dict[str, Any]],
                         events: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate a comprehensive device report."""
    try:
        report = {
            'device_info': device_data,
            'summary': {
                'total_locations': len(locations),
                'total_events': len(events),
                'date_range': None,
                'total_distance': 0.0,
                'average_speed': 0.0,
                'max_speed': 0.0
            },
            'locations': locations,
            'events': events
        }
        
        if locations:
            # Calculate date range
            timestamps = [loc['timestamp'] for loc in locations]
            report['summary']['date_range'] = {
                'start': min(timestamps),
                'end': max(timestamps)
            }
            
            # Calculate total distance
            total_distance = 0.0
            speeds = []
            
            for i in range(1, len(locations)):
                prev_loc = locations[i-1]
                curr_loc = locations[i]
                
                prev_point = Point(prev_loc['longitude'], prev_loc['latitude'])
                curr_point = Point(curr_loc['longitude'], curr_loc['latitude'])
                
                distance = calculate_distance(prev_point, curr_point)
                total_distance += distance
                
                if curr_loc['speed'] > 0:
                    speeds.append(curr_loc['speed'])
            
            report['summary']['total_distance'] = total_distance
            report['summary']['average_speed'] = sum(speeds) / len(speeds) if speeds else 0.0
            report['summary']['max_speed'] = max(speeds) if speeds else 0.0
        
        return report
        
    except Exception as e:
        logger.error(f"Error generating device report: {e}")
        return {
            'device_info': device_data,
            'summary': {'error': str(e)},
            'locations': [],
            'events': []
        }


def sanitize_device_name(name: str) -> str:
    """Sanitize device name for safe display."""
    import re
    
    # Remove special characters except spaces and hyphens
    sanitized = re.sub(r'[^\w\s\-]', '', name)
    
    # Limit length
    if len(sanitized) > 50:
        sanitized = sanitized[:50]
    
    return sanitized.strip()


def validate_imei(imei: str) -> bool:
    """Validate IMEI format."""
    try:
        # Check if it's a number and has correct length
        if not imei.isdigit():
            return False
        
        if len(imei) not in [14, 15]:
            return False
        
        # Luhn algorithm check
        digits = [int(d) for d in imei]
        checksum = 0
        
        for i in range(len(digits) - 1):
            if i % 2 == 0:
                doubled = digits[i] * 2
                checksum += doubled if doubled < 10 else doubled - 9
            else:
                checksum += digits[i]
        
        return (checksum + digits[-1]) % 10 == 0
        
    except Exception:
        return False


def format_imei(imei: int) -> str:
    """Format IMEI for display."""
    imei_str = str(imei)
    if len(imei_str) == 15:
        return f"{imei_str[:6]}-{imei_str[6:12]}-{imei_str[12:]}"
    else:
        return imei_str 