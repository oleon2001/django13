import React from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import { Device } from '../types/index';
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
    const defaultCenter: LatLngTuple = [19.4326, -99.1332]; // Default to Mexico City
    const center = selectedDevice 
        ? [selectedDevice.latitude, selectedDevice.longitude] as LatLngTuple
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
            {devices.map(device => (
                <Marker
                    key={device.imei}
                    position={[device.latitude, device.longitude] as LatLngTuple}
                    eventHandlers={{
                        click: () => onDeviceSelect(device),
                    }}
                >
                    <Popup>
                        <div>
                            <h3>{device.name}</h3>
                            <p>IMEI: {device.imei}</p>
                            <p>Status: {device.status}</p>
                            <p>Speed: {device.speed} km/h</p>
                            <p>Last Update: {new Date(device.lastUpdate).toLocaleString()}</p>
                        </div>
                    </Popup>
                </Marker>
            ))}
        </MapContainer>
    );
};

export default DeviceMap; 