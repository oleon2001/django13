import React from 'react';
import { Device } from '../types';

interface DeviceListProps {
    devices: Device[];
    selectedDevice: Device | undefined;
    onDeviceSelect: (device: Device) => void;
}

const DeviceList: React.FC<DeviceListProps> = ({ devices, selectedDevice, onDeviceSelect }) => {
    const getStatusColor = (status: string) => {
        switch (status.toLowerCase()) {
            case 'online':
                return 'text-green-500';
            case 'offline':
                return 'text-red-500';
            default:
                return 'text-yellow-500';
        }
    };

    const formatDate = (date: string | undefined) => {
        if (!date) return 'Never';
        return new Date(date).toLocaleString();
    };

    return (
        <div className="bg-white shadow rounded-lg">
            <div className="px-4 py-5 border-b border-gray-200">
                <h3 className="text-lg font-medium text-gray-900">GPS Devices</h3>
            </div>
            <div className="divide-y divide-gray-200">
                {devices.map(device => (
                    <div
                        key={device.imei}
                        className={`p-4 hover:bg-gray-50 cursor-pointer ${
                            selectedDevice?.imei === device.imei ? 'bg-blue-50' : ''
                        }`}
                        onClick={() => onDeviceSelect(device)}
                    >
                        <div className="flex items-center justify-between">
                            <div>
                                <h4 className="text-sm font-medium text-gray-900">{device.name || `Device ${device.imei}`}</h4>
                                <p className="text-sm text-gray-500">IMEI: {device.imei}</p>
                                {device.lastUpdate && (
                                    <div className="text-sm text-gray-500">
                                        Last seen: {formatDate(device.lastUpdate)}
                                    </div>
                                )}
                            </div>
                            <div className="flex items-center">
                                <span className={`text-sm ${getStatusColor(device.connection_status || 'OFFLINE')}`}>
                                    {device.connection_status || 'OFFLINE'}
                                </span>
                            </div>
                        </div>
                        <div className="mt-2 grid grid-cols-2 gap-2 text-sm">
                            <div>
                                <p className="text-gray-500">Speed</p>
                                <p className="font-medium">{device.speed || 0} km/h</p>
                            </div>
                            <div>
                                <p className="text-gray-500">Battery</p>
                                <p className="font-medium">{device.battery_level || 0}%</p>
                            </div>
                            <div>
                                <p className="text-gray-500">Signal</p>
                                <p className="font-medium">{device.signal_strength || 0}/5</p>
                            </div>
                            <div>
                                <p className="text-gray-500">Last Seen</p>
                                <p className="font-medium">
                                    {formatDate(device.lastUpdate)}
                                </p>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default DeviceList; 