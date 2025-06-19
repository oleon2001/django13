import React, { useState, useEffect } from 'react';
import { Device } from '../types';
import { deviceService } from '../services/deviceService';
import DeviceList from '../components/DeviceList';
import DeviceMap from '../components/DeviceMap';
import VehicleList from '../components/VehicleList';
import DriverList from '../components/DriverList';
import { useTranslation } from 'react-i18next';

type TabType = 'devices' | 'vehicles' | 'drivers';

export const GPS: React.FC = () => {
    const { t } = useTranslation();
    const [activeTab, setActiveTab] = useState<TabType>('devices');
    const [devices, setDevices] = useState<Device[]>([]);
    const [selectedDevice, setSelectedDevice] = useState<Device | undefined>(undefined);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const loadInitialData = async () => {
            try {
                setLoading(true);
                const initialDevices = await deviceService.getAll();
                setDevices(initialDevices);
                if (initialDevices.length > 0 && !selectedDevice) {
                    setSelectedDevice(initialDevices[0]);
                }
            } catch (error) {
                console.error('Error loading initial data:', error);
                setError('Error loading device data');
            } finally {
                setLoading(false);
            }
        };

        // Solo cargar datos de dispositivos si estamos en la pestaña de dispositivos
        if (activeTab === 'devices') {
            loadInitialData();

            // Configurar actualización automática cada 30 segundos
            const interval = setInterval(loadInitialData, 30000);

            // Limpiar al desmontar
            return () => {
                clearInterval(interval);
            };
        }

        // Return empty cleanup function for other tabs
        return () => {};
    }, [activeTab]);

    const handleDeviceSelect = (device: Device) => {
        setSelectedDevice(device);
    };

    const handleTabChange = (tab: TabType) => {
        setActiveTab(tab);
        // Limpiar datos cuando cambiamos de pestaña
        if (tab !== 'devices') {
            setSelectedDevice(undefined);
        }
    };

    const renderTabContent = () => {
        switch (activeTab) {
            case 'devices':
                if (loading) {
                    return (
                        <div className="text-center py-12">
                            <div className="text-lg">{t('gps.loadingDeviceData')}</div>
                            <div className="mt-4">
                                <div className="spinner-border animate-spin inline-block w-8 h-8 border-4 rounded-full" role="status">
                                    <span className="visually-hidden">{t('common.loading')}</span>
                                </div>
                            </div>
                        </div>
                    );
                }

                if (error) {
                    return (
                        <div className="text-center py-12">
                            <div className="text-red-500 text-xl mb-4">{t('gps.loadingError')}</div>
                            <button
                                onClick={() => window.location.reload()}
                                className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
                            >
                                {t('common.refresh')}
                            </button>
                        </div>
                    );
                }

                return (
                    <div className="h-full flex">
                        <div className="w-1/4 border-r border-gray-200">
                            <DeviceList
                                devices={devices}
                                selectedDevice={selectedDevice}
                                onDeviceSelect={handleDeviceSelect}
                            />
                        </div>
                        <div className="flex-1">
                            <DeviceMap
                                devices={devices}
                                selectedDevice={selectedDevice}
                                onDeviceSelect={handleDeviceSelect}
                            />
                        </div>
                    </div>
                );

            case 'vehicles':
                return (
                    <div className="h-full">
                        <VehicleList />
                    </div>
                );

            case 'drivers':
                return (
                    <div className="h-full">
                        <DriverList />
                    </div>
                );

            default:
                return null;
        }
    };

    return (
        <div className="h-screen flex flex-col">
            {/* Header con pestañas */}
            <div className="bg-white border-b border-gray-200 px-6 py-4">
                <div className="flex items-center justify-between">
                    <h1 className="text-2xl font-bold text-gray-900">{t('gps.title')}</h1>
                    <div className="flex space-x-4">
                        <button
                            onClick={() => handleTabChange('devices')}
                            className={`px-4 py-2 rounded-md font-medium transition-colors ${
                                activeTab === 'devices'
                                    ? 'bg-blue-500 text-white'
                                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                            }`}
                        >
                            📡 Dispositivos GPS
                        </button>
                        <button
                            onClick={() => handleTabChange('vehicles')}
                            className={`px-4 py-2 rounded-md font-medium transition-colors ${
                                activeTab === 'vehicles'
                                    ? 'bg-blue-500 text-white'
                                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                            }`}
                        >
                            🚗 Vehículos
                        </button>
                        <button
                            onClick={() => handleTabChange('drivers')}
                            className={`px-4 py-2 rounded-md font-medium transition-colors ${
                                activeTab === 'drivers'
                                    ? 'bg-blue-500 text-white'
                                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                            }`}
                        >
                            👨‍💼 Conductores
                        </button>
                    </div>
                </div>
            </div>

            {/* Contenido de la pestaña activa */}
            <div className="flex-1 overflow-hidden">
                {renderTabContent()}
            </div>
        </div>
    );
};

export default GPS; 