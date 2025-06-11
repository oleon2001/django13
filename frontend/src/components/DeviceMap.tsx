import React, { useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { Device } from '../types';
import './DeviceMap.css';



interface DeviceMapProps {
    devices: Device[];
    selectedDevice: Device | null;
    onDeviceSelect: (device: Device) => void;
}

const DeviceMap: React.FC<DeviceMapProps> = ({ devices, selectedDevice, onDeviceSelect }) => {
    const mapRef = useRef<L.Map | null>(null);
    const markersRef = useRef<L.Marker[]>([]);

    useEffect(() => {
        if (!mapRef.current) {
            mapRef.current = L.map('map').setView([0, 0], 2);
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution:
                    '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
            }).addTo(mapRef.current);
        }

        markersRef.current.forEach((marker) => marker.remove());
        markersRef.current = [];

        devices.forEach((device) => {
            const marker = L.marker([device.latitude, device.longitude])
                .bindPopup(`
                    <strong>${device.name}</strong><br>
                    Status: ${device.status}<br>
                    Last seen: ${new Date(device.lastSeen).toLocaleString()}
                `)
                .on('click', () => onDeviceSelect(device));

            marker.addTo(mapRef.current!);
            markersRef.current.push(marker);
        });

        // Center map on selected device
        if (selectedDevice) {
            mapRef.current.setView(
                [selectedDevice.latitude, selectedDevice.longitude],
                13
            );
        }
    }, [devices, selectedDevice, onDeviceSelect]);

    return <div id="map" className="device-map" />;
};

export default DeviceMap; 