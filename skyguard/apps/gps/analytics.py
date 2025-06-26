"""
Real-Time GPS Analytics System with Machine Learning
Provides advanced analytics, anomaly detection, and predictive insights.
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Avg, Count, Max, Min, Q
from django.core.cache import cache
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import logging
import json
from dataclasses import dataclass
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

from .models import GPSDevice, GPSLocation, GPSEvent
from .serializers import GPSDeviceSerializer

logger = logging.getLogger(__name__)
channel_layer = get_channel_layer()


@dataclass
class AnalyticsMetrics:
    """Data class for analytics metrics."""
    total_devices: int
    online_devices: int
    offline_devices: int
    avg_speed: float
    max_speed: float
    total_distance: float
    alerts_count: int
    battery_avg: float
    signal_avg: float
    anomalies_detected: int
    efficiency_score: float


@dataclass
class DeviceAnalytics:
    """Analytics data for a specific device."""
    device_imei: str
    total_locations: int
    avg_speed: float
    max_speed: float
    distance_traveled: float
    uptime_percentage: float
    battery_health: str
    signal_quality: str
    anomaly_score: float
    efficiency_rating: str
    predicted_maintenance: Optional[datetime]


class GPSAnalyticsEngine:
    """Advanced GPS analytics and machine learning engine."""
    
    def __init__(self):
        """Initialize analytics engine."""
        self.anomaly_detector = None
        self.scaler = StandardScaler()
        self.cache_timeout = 300  # 5 minutes
        
    def generate_real_time_metrics(self, time_window_hours: int = 24) -> AnalyticsMetrics:
        """Generate real-time analytics metrics."""
        try:
            cache_key = f"analytics_metrics_{time_window_hours}h"
            cached_metrics = cache.get(cache_key)
            
            if cached_metrics:
                return AnalyticsMetrics(**cached_metrics)
            
            # Time window for analysis
            end_time = timezone.now()
            start_time = end_time - timedelta(hours=time_window_hours)
            
            # Basic device statistics
            all_devices = GPSDevice.objects.all()
            online_devices = all_devices.filter(connection_status='ONLINE')
            offline_devices = all_devices.filter(connection_status='OFFLINE')
            
            # Speed statistics
            recent_locations = GPSLocation.objects.filter(
                timestamp__gte=start_time,
                timestamp__lte=end_time
            )
            
            speed_stats = recent_locations.aggregate(
                avg_speed=Avg('speed'),
                max_speed=Max('speed')
            )
            
            # Distance calculation (simplified)
            total_distance = self._calculate_total_distance(recent_locations)
            
            # Alert statistics
            alerts_count = GPSEvent.objects.filter(
                timestamp__gte=start_time,
                type__in=['ALARM', 'PANIC', 'SOS']
            ).count()
            
            # Battery and signal statistics
            device_stats = all_devices.aggregate(
                battery_avg=Avg('battery_level'),
                signal_avg=Avg('signal_strength')
            )
            
            # Anomaly detection
            anomalies_detected = self._detect_anomalies(recent_locations)
            
            # Efficiency score calculation
            efficiency_score = self._calculate_fleet_efficiency(all_devices, recent_locations)
            
            metrics = AnalyticsMetrics(
                total_devices=all_devices.count(),
                online_devices=online_devices.count(),
                offline_devices=offline_devices.count(),
                avg_speed=speed_stats['avg_speed'] or 0.0,
                max_speed=speed_stats['max_speed'] or 0.0,
                total_distance=total_distance,
                alerts_count=alerts_count,
                battery_avg=device_stats['battery_avg'] or 0.0,
                signal_avg=device_stats['signal_avg'] or 0.0,
                anomalies_detected=anomalies_detected,
                efficiency_score=efficiency_score
            )
            
            # Cache metrics
            cache.set(cache_key, metrics.__dict__, self.cache_timeout)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error generating analytics metrics: {e}")
            return self._get_default_metrics()
    
    def analyze_device_performance(self, device_imei: str, 
                                 days_back: int = 7) -> DeviceAnalytics:
        """Analyze performance for a specific device."""
        try:
            device = GPSDevice.objects.get(imei=device_imei)
            end_time = timezone.now()
            start_time = end_time - timedelta(days=days_back)
            
            # Get device locations
            locations = GPSLocation.objects.filter(
                device=device,
                timestamp__gte=start_time
            ).order_by('timestamp')
            
            if not locations.exists():
                return self._get_default_device_analytics(device_imei)
            
            # Calculate metrics
            speed_stats = locations.aggregate(
                avg_speed=Avg('speed'),
                max_speed=Max('speed')
            )
            
            # Distance calculation
            distance_traveled = self._calculate_device_distance(locations)
            
            # Uptime calculation
            uptime_percentage = self._calculate_uptime(device, start_time, end_time)
            
            # Battery health assessment
            battery_health = self._assess_battery_health(device)
            
            # Signal quality assessment
            signal_quality = self._assess_signal_quality(device)
            
            # Anomaly score
            anomaly_score = self._calculate_device_anomaly_score(locations)
            
            # Efficiency rating
            efficiency_rating = self._calculate_device_efficiency(device, locations)
            
            # Predictive maintenance
            predicted_maintenance = self._predict_maintenance_date(device, locations)
            
            return DeviceAnalytics(
                device_imei=device_imei,
                total_locations=locations.count(),
                avg_speed=speed_stats['avg_speed'] or 0.0,
                max_speed=speed_stats['max_speed'] or 0.0,
                distance_traveled=distance_traveled,
                uptime_percentage=uptime_percentage,
                battery_health=battery_health,
                signal_quality=signal_quality,
                anomaly_score=anomaly_score,
                efficiency_rating=efficiency_rating,
                predicted_maintenance=predicted_maintenance
            )
            
        except GPSDevice.DoesNotExist:
            logger.warning(f"Device {device_imei} not found for analytics")
            return self._get_default_device_analytics(device_imei)
        except Exception as e:
            logger.error(f"Error analyzing device {device_imei}: {e}")
            return self._get_default_device_analytics(device_imei)
    
    def detect_driving_patterns(self, device_imei: str, 
                              days_back: int = 30) -> Dict[str, Any]:
        """Detect and analyze driving patterns using ML."""
        try:
            device = GPSDevice.objects.get(imei=device_imei)
            end_time = timezone.now()
            start_time = end_time - timedelta(days=days_back)
            
            locations = GPSLocation.objects.filter(
                device=device,
                timestamp__gte=start_time
            ).order_by('timestamp')
            
            if locations.count() < 10:  # Need minimum data
                return {'error': 'Insufficient data for pattern analysis'}
            
            # Convert to DataFrame for analysis
            df = pd.DataFrame.from_records(
                locations.values('timestamp', 'speed', 'course', 'accuracy')
            )
            
            # Extract patterns
            patterns = {
                'peak_hours': self._analyze_peak_hours(df),
                'speed_patterns': self._analyze_speed_patterns(df),
                'route_consistency': self._analyze_route_consistency(df),
                'driving_behavior': self._analyze_driving_behavior(df),
                'efficiency_trends': self._analyze_efficiency_trends(df)
            }
            
            return patterns
            
        except Exception as e:
            logger.error(f"Error detecting patterns for device {device_imei}: {e}")
            return {'error': str(e)}
    
    def broadcast_analytics_update(self, metrics: AnalyticsMetrics) -> None:
        """Broadcast analytics update via WebSocket."""
        try:
            analytics_data = {
                'timestamp': timezone.now().isoformat(),
                'metrics': metrics.__dict__,
                'update_type': 'real_time_metrics'
            }
            
            # Broadcast to analytics WebSocket channel
            async_to_sync(channel_layer.group_send)(
                "gps_analytics",
                {
                    'type': 'analytics_update',
                    'data': analytics_data
                }
            )
            
        except Exception as e:
            logger.error(f"Error broadcasting analytics update: {e}")
    
    # Private helper methods
    def _calculate_total_distance(self, locations) -> float:
        """Calculate total distance traveled (simplified Haversine)."""
        try:
            if locations.count() < 2:
                return 0.0
            
            total_distance = 0.0
            prev_location = None
            
            for location in locations.order_by('timestamp'):
                if prev_location and location.position and prev_location.position:
                    # Simplified distance calculation (Haversine formula)
                    lat1, lon1 = prev_location.position.y, prev_location.position.x
                    lat2, lon2 = location.position.y, location.position.x
                    
                    distance = self._haversine_distance(lat1, lon1, lat2, lon2)
                    total_distance += distance
                
                prev_location = location
            
            return round(total_distance, 2)
            
        except Exception:
            return 0.0
    
    def _haversine_distance(self, lat1: float, lon1: float, 
                          lat2: float, lon2: float) -> float:
        """Calculate distance between two points using Haversine formula."""
        R = 6371  # Earth's radius in kilometers
        
        lat1_rad = np.radians(lat1)
        lat2_rad = np.radians(lat2)
        delta_lat = np.radians(lat2 - lat1)
        delta_lon = np.radians(lon2 - lon1)
        
        a = (np.sin(delta_lat / 2) ** 2 +
             np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(delta_lon / 2) ** 2)
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
        
        return R * c
    
    def _detect_anomalies(self, locations) -> int:
        """Detect anomalies in GPS data using Isolation Forest."""
        try:
            if locations.count() < 10:
                return 0
            
            # Prepare data for anomaly detection
            data = []
            for location in locations:
                if location.position:
                    data.append([
                        location.speed or 0,
                        location.course or 0,
                        location.accuracy or 0,
                        location.satellites or 0
                    ])
            
            if len(data) < 10:
                return 0
            
            # Initialize and fit anomaly detector
            if self.anomaly_detector is None:
                self.anomaly_detector = IsolationForest(
                    contamination=0.1,
                    random_state=42
                )
            
            X = np.array(data)
            X_scaled = self.scaler.fit_transform(X)
            
            # Detect anomalies
            anomalies = self.anomaly_detector.fit_predict(X_scaled)
            anomaly_count = np.sum(anomalies == -1)
            
            return int(anomaly_count)
            
        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")
            return 0
    
    def _calculate_fleet_efficiency(self, devices, locations) -> float:
        """Calculate overall fleet efficiency score."""
        try:
            if not devices.exists():
                return 0.0
            
            # Factors for efficiency calculation
            online_ratio = devices.filter(connection_status='ONLINE').count() / devices.count()
            
            # Average battery level
            avg_battery = devices.aggregate(avg=Avg('battery_level'))['avg'] or 0
            battery_score = min(avg_battery / 100.0, 1.0)
            
            # Signal quality
            avg_signal = devices.aggregate(avg=Avg('signal_strength'))['avg'] or 0
            signal_score = min(avg_signal / 100.0, 1.0)
            
            # Data transmission efficiency
            transmission_score = min(locations.count() / (devices.count() * 24), 1.0)
            
            # Weighted efficiency score
            efficiency = (
                online_ratio * 0.4 +
                battery_score * 0.2 +
                signal_score * 0.2 +
                transmission_score * 0.2
            ) * 100
            
            return round(efficiency, 2)
            
        except Exception:
            return 0.0
    
    def _get_default_metrics(self) -> AnalyticsMetrics:
        """Get default metrics in case of error."""
        return AnalyticsMetrics(
            total_devices=0, online_devices=0, offline_devices=0,
            avg_speed=0.0, max_speed=0.0, total_distance=0.0,
            alerts_count=0, battery_avg=0.0, signal_avg=0.0,
            anomalies_detected=0, efficiency_score=0.0
        )
    
    def _get_default_device_analytics(self, device_imei: str) -> DeviceAnalytics:
        """Get default device analytics in case of error."""
        return DeviceAnalytics(
            device_imei=device_imei, total_locations=0, avg_speed=0.0,
            max_speed=0.0, distance_traveled=0.0, uptime_percentage=0.0,
            battery_health='Unknown', signal_quality='Unknown',
            anomaly_score=0.0, efficiency_rating='Unknown',
            predicted_maintenance=None
        )
    
    # Additional helper methods for device-specific analytics
    def _calculate_device_distance(self, locations) -> float:
        """Calculate distance for a specific device."""
        return self._calculate_total_distance(locations)
    
    def _calculate_uptime(self, device: GPSDevice, start_time: datetime, 
                         end_time: datetime) -> float:
        """Calculate device uptime percentage."""
        try:
            total_hours = (end_time - start_time).total_seconds() / 3600
            
            # Count online events
            online_events = GPSEvent.objects.filter(
                device=device,
                timestamp__gte=start_time,
                timestamp__lte=end_time,
                type='LOCATION'
            ).count()
            
            # Estimate uptime (simplified)
            estimated_uptime_hours = min(online_events * 0.1, total_hours)
            uptime_percentage = (estimated_uptime_hours / total_hours) * 100
            
            return round(min(uptime_percentage, 100.0), 2)
            
        except Exception:
            return 0.0
    
    def _assess_battery_health(self, device: GPSDevice) -> str:
        """Assess battery health based on recent data."""
        battery_level = device.battery_level or 0
        
        if battery_level >= 80:
            return 'Excellent'
        elif battery_level >= 60:
            return 'Good'
        elif battery_level >= 40:
            return 'Fair'
        elif battery_level >= 20:
            return 'Poor'
        else:
            return 'Critical'
    
    def _assess_signal_quality(self, device: GPSDevice) -> str:
        """Assess signal quality based on recent data."""
        signal_strength = device.signal_strength or 0
        
        if signal_strength >= 80:
            return 'Excellent'
        elif signal_strength >= 60:
            return 'Good'
        elif signal_strength >= 40:
            return 'Fair'
        else:
            return 'Poor'
    
    def _calculate_device_anomaly_score(self, locations) -> float:
        """Calculate anomaly score for a specific device."""
        anomalies = self._detect_anomalies(locations)
        total_locations = locations.count()
        
        if total_locations == 0:
            return 0.0
        
        anomaly_rate = anomalies / total_locations
        return round(anomaly_rate * 100, 2)
    
    def _calculate_device_efficiency(self, device: GPSDevice, locations) -> str:
        """Calculate efficiency rating for a device."""
        try:
            # Factors: data frequency, battery usage, signal consistency
            data_frequency = locations.count() / 24  # per hour
            battery_efficiency = (device.battery_level or 0) / 100
            signal_consistency = (device.signal_strength or 0) / 100
            
            efficiency_score = (
                min(data_frequency / 4, 1.0) * 0.4 +  # Expect ~4 points per hour
                battery_efficiency * 0.3 +
                signal_consistency * 0.3
            )
            
            if efficiency_score >= 0.8:
                return 'Excellent'
            elif efficiency_score >= 0.6:
                return 'Good'
            elif efficiency_score >= 0.4:
                return 'Fair'
            else:
                return 'Poor'
                
        except Exception:
            return 'Unknown'
    
    def _predict_maintenance_date(self, device: GPSDevice, locations) -> Optional[datetime]:
        """Predict next maintenance date based on usage patterns."""
        try:
            # Simplified predictive model
            battery_level = device.battery_level or 100
            error_count = device.error_count or 0
            usage_intensity = locations.count() / 30  # per day
            
            # Calculate maintenance urgency score
            urgency_score = (
                (100 - battery_level) * 0.4 +
                error_count * 0.3 +
                max(usage_intensity - 10, 0) * 0.3
            )
            
            if urgency_score > 50:
                days_until_maintenance = max(7, 60 - urgency_score)
            else:
                days_until_maintenance = 90  # Regular maintenance
            
            return timezone.now() + timedelta(days=days_until_maintenance)
            
        except Exception:
            return None
    
    # Pattern analysis methods
    def _analyze_peak_hours(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze peak usage hours."""
        try:
            df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
            hourly_activity = df.groupby('hour').size()
            peak_hour = hourly_activity.idxmax()
            
            return {
                'peak_hour': int(peak_hour),
                'peak_activity': int(hourly_activity.max()),
                'hourly_distribution': hourly_activity.to_dict()
            }
        except Exception:
            return {'error': 'Unable to analyze peak hours'}
    
    def _analyze_speed_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze speed patterns."""
        try:
            speed_stats = df['speed'].describe()
            
            return {
                'avg_speed': round(speed_stats['mean'], 2),
                'max_speed': round(speed_stats['max'], 2),
                'speed_variance': round(speed_stats['std'], 2),
                'speed_percentiles': {
                    '25th': round(speed_stats['25%'], 2),
                    '50th': round(speed_stats['50%'], 2),
                    '75th': round(speed_stats['75%'], 2),
                    '90th': round(df['speed'].quantile(0.9), 2)
                }
            }
        except Exception:
            return {'error': 'Unable to analyze speed patterns'}
    
    def _analyze_route_consistency(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze route consistency."""
        try:
            course_variance = df['course'].std()
            
            consistency_score = max(0, 100 - course_variance / 3.6)
            
            return {
                'consistency_score': round(consistency_score, 2),
                'course_variance': round(course_variance, 2),
                'route_type': 'Consistent' if consistency_score > 70 else 'Variable'
            }
        except Exception:
            return {'error': 'Unable to analyze route consistency'}
    
    def _analyze_driving_behavior(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze driving behavior patterns."""
        try:
            # Detect aggressive driving patterns
            high_speed_count = (df['speed'] > 80).sum()
            rapid_acceleration = 0  # Would need speed derivatives
            
            behavior_score = max(0, 100 - (high_speed_count * 2))
            
            return {
                'behavior_score': round(behavior_score, 2),
                'high_speed_events': int(high_speed_count),
                'behavior_rating': 'Safe' if behavior_score > 80 else 'Moderate' if behavior_score > 60 else 'Aggressive'
            }
        except Exception:
            return {'error': 'Unable to analyze driving behavior'}
    
    def _analyze_efficiency_trends(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze efficiency trends over time."""
        try:
            df['date'] = pd.to_datetime(df['timestamp']).dt.date
            daily_efficiency = df.groupby('date').agg({
                'speed': 'mean',
                'accuracy': 'mean'
            })
            
            efficiency_trend = 'stable'
            if len(daily_efficiency) > 1:
                speed_trend = daily_efficiency['speed'].pct_change().mean()
                if speed_trend > 0.1:
                    efficiency_trend = 'improving'
                elif speed_trend < -0.1:
                    efficiency_trend = 'declining'
            
            return {
                'trend': efficiency_trend,
                'avg_daily_speed': round(daily_efficiency['speed'].mean(), 2),
                'efficiency_variance': round(daily_efficiency['speed'].std(), 2)
            }
        except Exception:
            return {'error': 'Unable to analyze efficiency trends'}


# Global analytics engine instance
analytics_engine = GPSAnalyticsEngine() 