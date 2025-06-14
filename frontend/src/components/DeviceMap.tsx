import React, { useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { Device } from '../types';
import './DeviceMap.css';

interface DeviceMapProps {
    devices: Device[];
    selectedDevice?: Device;
    onDeviceSelect: (device: Device) => void;
}

const DeviceMap: React.FC<DeviceMapProps> = ({ devices, selectedDevice, onDeviceSelect }) => {
    const mapRef = useRef<L.Map | null>(null);
    const markersRef = useRef<L.Marker[]>([]);

    useEffect(() => {
        if (!mapRef.current) {
            mapRef.current = L.map('map').setView([-12.0464, -77.0428], 13);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© OpenStreetMap contributors'
            }).addTo(mapRef.current);
        }

        // Limpiar marcadores existentes
        markersRef.current.forEach(marker => marker.remove());
        markersRef.current = [];

        // Crear nuevos marcadores
        devices.forEach(device => {
            if (device.latitude && device.longitude) {
                const marker = L.marker([device.latitude, device.longitude])
                    .bindPopup(`
                        <div class="device-popup">
                            <h3>${device.name || 'Dispositivo'}</h3>
                            <p><strong>IMEI:</strong> ${device.imei}</p>
                            <p><strong>Protocolo:</strong> ${device.protocol}</p>
                            <p><strong>Estado:</strong> 
                                <span class="status-${device.status === 'online' ? 'online' : 'offline'}">
                                    ${device.status === 'online' ? 'En línea' : 'Desconectado'}
                                </span>
                            </p>
                            <p><strong>Velocidad:</strong> ${device.speed || 0} km/h</p>
                            <p><strong>Dirección:</strong> ${device.heading || 0}°</p>
                            <p><strong>Altitud:</strong> ${device.altitude || 0} m</p>
                            <p><strong>Satélites:</strong> ${device.satellites || 0}</p>
                            <p><strong>Batería:</strong> 
                                <span class="battery-${getBatteryLevelClass(device.battery_level)}">
                                    ${device.battery_level || 0}%
                                </span>
                            </p>
                            <p><strong>Señal:</strong> 
                                <span class="signal-${getSignalLevelClass(device.signal_strength)}">
                                    ${device.signal_strength || 0}%
                                </span>
                            </p>
                            <p><strong>Última actualización:</strong> ${new Date(device.lastUpdate).toLocaleString()}</p>
                        </div>
                    `);
                marker.on('click', () => onDeviceSelect(device));
                marker.addTo(mapRef.current!);
                    markersRef.current.push(marker);
            }
        });

        // Centrar el mapa en el dispositivo seleccionado o en el primer dispositivo válido
        if (selectedDevice && selectedDevice.latitude && selectedDevice.longitude) {
            mapRef.current.setView([selectedDevice.latitude, selectedDevice.longitude], 15);
        } else if (devices.length > 0 && devices[0].latitude && devices[0].longitude) {
            mapRef.current.setView([devices[0].latitude, devices[0].longitude], 13);
        }

        return () => {
            if (mapRef.current) {
                mapRef.current.remove();
                mapRef.current = null;
            }
        };
    }, [devices, selectedDevice, onDeviceSelect]);

    const getBatteryLevelClass = (level?: number): string => {
        if (!level) return 'low';
        if (level > 70) return 'high';
        if (level > 30) return 'medium';
        return 'low';
    };

    const getSignalLevelClass = (level?: number): string => {
        if (!level) return 'weak';
        if (level > 70) return 'strong';
        if (level > 30) return 'medium';
        return 'weak';
    };

    return <div id="map" className="device-map" />;
};

export default DeviceMap; 