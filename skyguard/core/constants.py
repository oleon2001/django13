# Geofence Constants
GEOFENCE_CONSTANTS = {
    'MAX_POLYGON_POINTS': 1000,
    'MIN_POLYGON_POINTS': 3,
    'MAX_GEOFENCES_PER_DEVICE': 50,
    'MAX_GEOFENCES_PER_USER': 100,
    'DEFAULT_NOTIFICATION_COOLDOWN': 300,  # 5 minutes
    'MIN_NOTIFICATION_COOLDOWN': 30,       # 30 seconds
    'MAX_NOTIFICATION_COOLDOWN': 3600,     # 1 hour
    'DEFAULT_BATCH_SIZE': 100,
    'CACHE_TIMEOUT': 300,                  # 5 minutes
    'EVENT_SPAM_INTERVAL': 30,             # 30 seconds minimum between events
    'ANOMALY_DETECTION_THRESHOLD': 2.0,    # Z-score threshold
    'PERFORMANCE_SCORE_THRESHOLD': 70,     # Performance score threshold
    'ML_CONFIDENCE_THRESHOLD': 0.8,        # ML confidence threshold
} 