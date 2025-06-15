import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { Icon } from 'leaflet';
import { gpsService, GPSDevice, GPSEvent } from '../services/gpsService';

// Fix for default marker icon
const defaultIcon = new Icon({
    iconUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png',
    iconRetinaUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon-2x.png',
    shadowUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41]
});

interface GPSMapProps {
    selectedDevice?: string;
    showHistory?: boolean;
}

export const GPSMap: React.FC<GPSMapProps> = ({ selectedDevice, showHistory = false }) => {
    const [devices, setDevices] = useState<GPSDevice[]>([]);
    const [events, setEvents] = useState<GPSEvent[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                setLoading(true);
                const devicesData = await gpsService.getDevices();
                setDevices(devicesData);

                if (selectedDevice && showHistory) {
                    const eventsData = await gpsService.getDeviceEvents(selectedDevice);
                    setEvents(eventsData);
                }

                setError(null);
            } catch (err) {
                setError('Error loading GPS data');
                console.error(err);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
        const interval = setInterval(fetchData, 30000); // Update every 30 seconds

        return () => clearInterval(interval);
    }, [selectedDevice, showHistory]);

    if (loading) {
        return <div className="loading">Loading map data...</div>;
    }

    if (error) {
        return <div className="error">{error}</div>;
    }

    return (
        <MapContainer
            center={[19.4326, -99.1332]} // Default to Mexico City
            zoom={13}
            style={{ height: '100vh', width: '100%' }}
        >
            <TileLayer
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            />
            
            {devices.map(device => (
                <Marker
                    key={device.imei}
                    position={[device.position.latitude, device.position.longitude]}
                    icon={defaultIcon}
                >
                    <Popup>
                        <div>
                            <h3>{device.name}</h3>
                            <p>IMEI: {device.imei}</p>
                            <p>Speed: {device.speed} km/h</p>
                            <p>Course: {device.course}°</p>
                            <p>Altitude: {device.altitude} m</p>
                            <p>Battery: {device.battery}%</p>
                            <p>Signal: {device.signal}/5</p>
                            <p>Satellites: {device.satellites}</p>
                            <p>Last seen: {new Date(device.last_seen).toLocaleString()}</p>
                            <p>Status: {device.connection_status}</p>
                        </div>
                    </Popup>
                </Marker>
            ))}

            {showHistory && selectedDevice && events.length > 0 && (
                <Polyline
                    positions={events.map(event => [event.position.latitude, event.position.longitude])}
                    color="blue"
                    weight={3}
                    opacity={0.7}
                />
            )}
        </MapContainer>
    );
}; 