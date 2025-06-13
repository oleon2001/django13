import React, { useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
// Importar el CSS de compatibilidad para los iconos de Leaflet
import 'leaflet-defaulticon-compatibility/dist/leaflet-defaulticon-compatibility.webpack.css';
// Importar el paquete de compatibilidad
import 'leaflet-defaulticon-compatibility';
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

    // Solución para el problema de los iconos predeterminados de Leaflet con Webpack
    delete (L.Icon.Default.prototype as any)._getIconUrl;
    L.Icon.Default.mergeOptions({
        iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
        iconUrl: require('leaflet/dist/images/marker-icon.png'),
        shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
    });

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

        return () => {
            if (mapRef.current) {
                mapRef.current.remove();
                mapRef.current = null;
            }
        };
    }, [devices, selectedDevice, onDeviceSelect]);

    return <div id="map" className="device-map" />;
};

export default DeviceMap; 