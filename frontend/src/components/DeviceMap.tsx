import React from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import { Device } from '../types';
import 'leaflet/dist/leaflet.css';
import L, { LatLngTuple } from 'leaflet';

// Fix for default marker icons in Leaflet with Next.js
delete (L.Icon.Default.prototype as any)._getIconUrl;
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
    const defaultCenter: LatLngTuple = [-12.0464, -77.0428]; // Default to Lima, Peru
    
    // Filter devices that have valid coordinates
    const devicesWithLocation = devices.filter(device => 
        device.latitude && device.longitude && 
        !isNaN(device.latitude) && !isNaN(device.longitude)
    );
    
    // Determine center based on selected device or first device with location
    const center = selectedDevice && selectedDevice.latitude && selectedDevice.longitude
        ? [selectedDevice.latitude, selectedDevice.longitude] as LatLngTuple
        : devicesWithLocation.length > 0 
            ? [devicesWithLocation[0].latitude!, devicesWithLocation[0].longitude!] as LatLngTuple
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
                    position={[device.latitude!, device.longitude!] as LatLngTuple}
                    eventHandlers={{
                        click: () => onDeviceSelect(device),
                    }}
                >
                    <Popup>
                        <div>
                            <h3>{device.name || `Device ${device.imei}`}</h3>
                            <p><strong>IMEI:</strong> {device.imei}</p>
                            <p><strong>Estado:</strong> {device.connection_status || 'OFFLINE'}</p>
                            <p><strong>Velocidad:</strong> {device.speed || 0} km/h</p>
                            <p><strong>Batería:</strong> {device.battery_level || 0}%</p>
                            <p><strong>Señal:</strong> {device.signal_strength || 0}%</p>
                            {device.lastUpdate && (
                                <p><strong>Última actualización:</strong> {new Date(device.lastUpdate).toLocaleString()}</p>
                            )}
                        </div>
                    </Popup>
                </Marker>
            ))}
        </MapContainer>
    );
};

export default DeviceMap; 