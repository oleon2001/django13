import React, { useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';
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

    // Fix Leaflet default icon issue
    const DefaultIcon = L.icon({
        iconUrl: icon,
        shadowUrl: iconShadow,
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41]
    });

    L.Marker.prototype.options.icon = DefaultIcon;

    // Efecto para inicializar el mapa solo una vez
    useEffect(() => {
        if (mapRef.current) return;

        const mapInstance = L.map('map').setView([0, 0], 2);
        mapRef.current = mapInstance;

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution:
                '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        }).addTo(mapInstance);

        mapInstance.whenReady(() => {
            mapInstance.invalidateSize();
        });

        return () => {
            if (mapRef.current) {
                mapRef.current.remove();
                mapRef.current = null;
            }
        };
    }, []);

    // Efecto para actualizar marcadores cuando cambian los dispositivos
    useEffect(() => {
        if (!mapRef.current) return;

        // Limpiar marcadores existentes
        markersRef.current.forEach(marker => marker.remove());
        markersRef.current = [];

        const mapInstance = mapRef.current;

        // Validar y crear marcadores solo para dispositivos con coordenadas válidas
        devices.forEach((device) => {
            if (device && 
                typeof device.latitude === 'number' && 
                typeof device.longitude === 'number' && 
                !isNaN(device.latitude) && 
                !isNaN(device.longitude)) {
                
                try {
                    // Crear el popup primero
                    const popupContent = `
                        <strong>${device.name || 'Unknown Device'}</strong><br>
                        Status: ${device.status || 'Unknown'}<br>
                        Last seen: ${device.lastSeen ? new Date(device.lastSeen).toLocaleString() : 'Unknown'}
                    `;
                    
                    // Crear el marcador con el popup
                    const marker = L.marker([device.latitude, device.longitude], {
                        title: device.name || 'Unknown Device',
                        icon: DefaultIcon
                    });

                    // Añadir el popup al marcador
                    marker.bindPopup(popupContent, {
                        closeButton: true,
                        autoClose: true,
                        closeOnEscapeKey: true
                    });

                    // Añadir el evento de clic
                    marker.on('click', () => {
                        onDeviceSelect(device);
                    });

                    // Añadir el marcador al mapa
                    marker.addTo(mapInstance);
                    markersRef.current.push(marker);
                } catch (error) {
                    console.error('Error creating marker for device:', device, error);
                }
            }
        });

        // Centrar el mapa en el dispositivo seleccionado o en el primer dispositivo válido
        if (selectedDevice && 
            typeof selectedDevice.latitude === 'number' && 
            typeof selectedDevice.longitude === 'number' && 
            !isNaN(selectedDevice.latitude) && 
            !isNaN(selectedDevice.longitude)) {
            mapInstance.setView(
                [selectedDevice.latitude, selectedDevice.longitude],
                13
            );
        } else if (devices.length > 0) {
            // Buscar el primer dispositivo con coordenadas válidas
            const validDevice = devices.find(device => 
                typeof device.latitude === 'number' && 
                typeof device.longitude === 'number' && 
                !isNaN(device.latitude) && 
                !isNaN(device.longitude)
            );
            
            if (validDevice) {
                mapInstance.setView(
                    [validDevice.latitude, validDevice.longitude],
                    13
                );
            }
        }
    }, [devices, selectedDevice, onDeviceSelect]);

    return <div id="map" className="device-map" />;
};

export default DeviceMap; 