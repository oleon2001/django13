import React, { useState } from 'react';
import { Device } from '../types/index';
import DeviceList from '../components/DeviceList';
import DeviceMap from '../components/DeviceMap';

const GPSPage: React.FC = () => {
    const [selectedDevice, setSelectedDevice] = useState<Device | undefined>(undefined);

    return (
        <div className="h-screen flex">
            <div className="w-1/4 border-r border-gray-200">
                <div className="h-[calc(100vh-8rem)] overflow-y-auto">
                    <DeviceList
                        devices={[]} // TODO: Add devices from API
                        selectedDevice={selectedDevice}
                        onDeviceSelect={setSelectedDevice}
                    />
                </div>
            </div>
            <div className="flex-1">
                <DeviceMap
                    devices={[]} // TODO: Add devices from API
                    selectedDevice={selectedDevice}
                    onDeviceSelect={setSelectedDevice}
                />
            </div>
        </div>
    );
};

export default GPSPage; 