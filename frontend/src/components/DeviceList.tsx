import React from 'react';
import { Device } from '../types';
import './DeviceList.css';

interface DeviceListProps {
    devices: Device[];
    selectedDevice?: Device;
    onDeviceSelect: (device: Device) => void;
}

const DeviceList: React.FC<DeviceListProps> = ({
    devices,
    selectedDevice,
    onDeviceSelect,
}) => {
    const getStatusClass = (status: string) => {
        return status === 'online' ? 'status-online' : 'status-offline';
    };

    const getBatteryClass = (level?: number) => {
        if (!level) return 'battery-low';
        if (level > 70) return 'battery-high';
        if (level > 30) return 'battery-medium';
        return 'battery-low';
    };

    const getSignalClass = (level?: number) => {
        if (!level) return 'signal-weak';
        if (level > 70) return 'signal-strong';
        if (level > 30) return 'signal-medium';
        return 'signal-weak';
    };

    return (
        <div className="device-list">
            <h2>Dispositivos</h2>
            <div className="device-list-content">
                {devices.map((device) => (
                    <div
                        key={device.imei}
                        className={`device-item ${selectedDevice?.imei === device.imei ? 'selected' : ''}`}
                        onClick={() => onDeviceSelect(device)}
                    >
                        <div className="device-header">
                            <h3>{device.name || 'Dispositivo'}</h3>
                            <span className={`status-indicator ${getStatusClass(device.status)}`}>
                                {device.status === 'online' ? 'En línea' : 'Desconectado'}
                            </span>
                        </div>
                        <div className="device-details">
                            <p><strong>IMEI:</strong> {device.imei}</p>
                            <p><strong>Protocolo:</strong> {device.protocol}</p>
                            <p><strong>Velocidad:</strong> {device.speed || 0} km/h</p>
                            <p><strong>Dirección:</strong> {device.heading || 0}°</p>
                            <p><strong>Altitud:</strong> {device.altitude || 0} m</p>
                            <p><strong>Satélites:</strong> {device.satellites || 0}</p>
                            <p>
                                <strong>Batería:</strong>
                                <span className={getBatteryClass(device.battery_level)}>
                                    {device.battery_level || 0}%
                                </span>
                            </p>
                            <p>
                                <strong>Señal:</strong>
                                <span className={getSignalClass(device.signal_strength)}>
                                    {device.signal_strength || 0}%
                                </span>
                            </p>
                            <p><strong>Última actualización:</strong> {new Date(device.lastUpdate).toLocaleString()}</p>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default DeviceList; 