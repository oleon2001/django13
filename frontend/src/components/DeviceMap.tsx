import React from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import { Device } from '../types';
import 'leaflet/dist/leaflet.css';
import L, { LatLngTuple } from 'leaflet';

// Fix for default marker icons in Leaflet with Next.js
delete (L.Icon.Default.prototype as any)._getIconUrl;

// Create custom icons for different device states
const createCustomIcon = (status: string, speed: number = 0) => {
    let color = '#gray';
    if (status === 'ONLINE') {
        color = speed > 0 ? '#22c55e' : '#3b82f6'; // Green if moving, blue if stationary
    } else if (status === 'OFFLINE') {
        color = '#ef4444'; // Red
    }
    
    return L.divIcon({
        html: `
            <div style="
                background-color: ${color};
                width: 12px;
                height: 12px;
                border-radius: 50%;
                border: 2px solid white;
                box-shadow: 0 2px 4px rgba(0,0,0,0.3);
            "></div>
        `,
        className: 'custom-marker',
        iconSize: [16, 16],
        iconAnchor: [8, 8],
    });
};

L.Icon.Default.mergeOptions({
    iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
    iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

interface DeviceMapProps {
    devices: Device[];
    selectedDevice: Device | undefined;
    onDeviceSelect: (device: Device) => void;
}

const DeviceMap: React.FC<DeviceMapProps> = ({ devices, selectedDevice, onDeviceSelect }) => {
    const defaultCenter: LatLngTuple = [19.4326, -99.1332]; // Default to Mexico City (matching our simulator)
    
    // Filter devices that have valid coordinates
    const devicesWithLocation = devices.filter(device => 
        device.position?.latitude && device.position?.longitude && 
        !isNaN(device.position.latitude) && !isNaN(device.position.longitude)
    );
    
    // Determine center based on selected device or first device with location
    const center = selectedDevice && selectedDevice.position?.latitude && selectedDevice.position?.longitude
        ? [selectedDevice.position.latitude, selectedDevice.position.longitude] as LatLngTuple
        : devicesWithLocation.length > 0 
            ? [devicesWithLocation[0].position!.latitude, devicesWithLocation[0].position!.longitude] as LatLngTuple
            : defaultCenter;

    return (
        <MapContainer
            center={center}
            zoom={13}
            style={{ height: '100%', width: '100%' }}
        >
            <TileLayer
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            />
            {devicesWithLocation.map(device => (
                <Marker
                    key={device.imei}
                    position={[device.position!.latitude, device.position!.longitude] as LatLngTuple}
                    icon={createCustomIcon(device.connection_status || 'OFFLINE', device.speed || 0)}
                    eventHandlers={{
                        click: () => onDeviceSelect(device),
                    }}
                >
                    <Popup>
                        <div className="min-w-64">
                            <h3 className="font-bold text-lg mb-2">{device.name || `Device ${device.imei}`}</h3>
                            <div className="space-y-1 text-sm">
                                <p><strong>IMEI:</strong> {device.imei}</p>
                                <p>
                                    <strong>Estado:</strong> 
                                    <span className={`ml-2 px-2 py-1 rounded text-xs ${
                                        device.connection_status === 'ONLINE' 
                                            ? 'bg-green-100 text-green-800' 
                                            : 'bg-red-100 text-red-800'
                                    }`}>
                                        {device.connection_status || 'OFFLINE'}
                                    </span>
                                </p>
                                <p><strong>Velocidad:</strong> {device.speed || 0} km/h</p>
                                <p><strong>Coordenadas:</strong> {device.position?.latitude?.toFixed(6)}, {device.position?.longitude?.toFixed(6)}</p>
                                {device.course && (
                                    <p><strong>Rumbo:</strong> {device.course}°</p>
                                )}
                                {device.altitude && (
                                    <p><strong>Altitud:</strong> {device.altitude} m</p>
                                )}
                                {device.route && (
                                    <p><strong>Ruta:</strong> {device.route}</p>
                                )}
                                {device.economico && (
                                    <p><strong>Económico:</strong> {device.economico}</p>
                                )}
                                {device.lastUpdate && (
                                    <p><strong>Última actualización:</strong> {new Date(device.lastUpdate).toLocaleString()}</p>
                                )}
                            </div>
                            <div className="mt-3 pt-2 border-t">
                                <a 
                                    href={`https://maps.google.com/?q=${device.position?.latitude},${device.position?.longitude}`}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="text-blue-600 hover:text-blue-800 text-sm"
                                >
                                    📍 Ver en Google Maps
                                </a>
                            </div>
                        </div>
                    </Popup>
                </Marker>
            ))}
        </MapContainer>
    );
};

export default DeviceMap; 