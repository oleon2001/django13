import React, { useState, useEffect, startTransition } from 'react';
import { Device } from '../types';
import { deviceService } from '../services/deviceService';
import DeviceList from '../components/DeviceList';
import DeviceMap from '../components/DeviceMap';
import VehicleList from '../components/VehicleList';
import DriverList from '../components/DriverList';
import { useTranslation } from 'react-i18next';
import EnhancedLoading from '../components/EnhancedLoading';
import FormLoading from '../components/FormLoading';

type TabType = 'devices' | 'vehicles' | 'drivers';

export const GPS: React.FC = () => {
    const { t } = useTranslation();
    const [activeTab, setActiveTab] = useState<TabType>('devices');
    const [devices, setDevices] = useState<Device[]>([]);
    const [selectedDevice, setSelectedDevice] = useState<Device | undefined>(undefined);
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [lastUpdate, setLastUpdate] = useState<Date | null>(null);

    useEffect(() => {
        const loadInitialData = async () => {
            try {
                setLoading(true);
                const initialDevices = await deviceService.getAll();
                
                startTransition(() => {
                    setDevices(initialDevices);
                    if (initialDevices.length > 0 && !selectedDevice) {
                        setSelectedDevice(initialDevices[0]);
                    }
                    setError(null);
                    setLastUpdate(new Date());
                });
            } catch (error) {
                console.error('Error loading initial data:', error);
                startTransition(() => {
                    setError('Error loading device data');
                });
            } finally {
                startTransition(() => {
                    setLoading(false);
                });
            }
        };

        // Solo cargar datos de dispositivos si estamos en la pestaña de dispositivos
        if (activeTab === 'devices') {
            loadInitialData();

            // Configurar actualización automática cada 30 segundos
            const interval = setInterval(async () => {
                try {
                    setRefreshing(true);
                    const updatedDevices = await deviceService.getAll();
                    
                    startTransition(() => {
                        setDevices(updatedDevices);
                        // Update selected device if it exists in the new data
                        if (selectedDevice) {
                            const updatedDevice = updatedDevices.find(d => d.imei === selectedDevice.imei);
                            if (updatedDevice) {
                                setSelectedDevice(updatedDevice);
                            }
                        }
                        setLastUpdate(new Date());
                        setError(null);
                    });
                } catch (error) {
                    console.error('Error refreshing data:', error);
                    startTransition(() => {
                        setError('Error refreshing device data');
                    });
                } finally {
                    startTransition(() => {
                        setRefreshing(false);
                    });
                }
            }, 30000);

            // Limpiar al desmontar
            return () => {
                clearInterval(interval);
            };
        }

        // Return empty cleanup function for other tabs
        return () => {};
    }, [activeTab, selectedDevice]);

    const handleDeviceSelect = (device: Device) => {
        startTransition(() => {
            setSelectedDevice(device);
        });
    };

    const handleTabChange = (tab: TabType) => {
        startTransition(() => {
            setActiveTab(tab);
            // Limpiar datos cuando cambiamos de pestaña
            if (tab !== 'devices') {
                setSelectedDevice(undefined);
            }
        });
    };

    const handleRefresh = async () => {
        if (activeTab !== 'devices') return;
        
        try {
            setRefreshing(true);
            const refreshedDevices = await deviceService.getAll();
            
            startTransition(() => {
                setDevices(refreshedDevices);
                setError(null);
                setLastUpdate(new Date());
            });
        } catch (error) {
            console.error('Error refreshing data:', error);
            startTransition(() => {
                setError('Error refreshing device data');
            });
        } finally {
            startTransition(() => {
                setRefreshing(false);
            });
        }
    };

    const renderTabContent = () => {
        switch (activeTab) {
            case 'devices':
                if (loading) {
                    return (
                        <EnhancedLoading 
                            module="gps" 
                            message="Cargando dispositivos GPS" 
                            subMessage="Obteniendo datos de dispositivos en tiempo real"
                            variant="detailed"
                        />
                    );
                }

                if (error) {
                    return (
                        <div className="flex items-center justify-center h-full">
                            <div className="text-center">
                                <div className="text-red-500 text-xl mb-4">{error}</div>
                                <button
                                    onClick={handleRefresh}
                                    disabled={refreshing}
                                    className="bg-blue-500 hover:bg-blue-700 disabled:bg-blue-300 text-white font-bold py-2 px-4 rounded transition-colors"
                                >
                                    {refreshing ? 'Actualizando...' : 'Reintentar'}
                                </button>
                            </div>
                        </div>
                    );
                }

                return (
                    <div className="h-full flex relative">
                        {refreshing && (
                            <div className="absolute top-4 right-4 z-10">
                                <FormLoading 
                                    open={refreshing} 
                                    variant="inline" 
                                    size="small" 
                                    message="Actualizando..." 
                                    action="sync"
                                />
                            </div>
                        )}
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
        <div className="h-screen flex flex-col bg-gray-50">
            {/* Header con pestañas mejorado */}
            <div className="bg-white border-b border-gray-200 px-6 py-4 shadow-sm">
                <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                        <h1 className="text-2xl font-bold text-gray-900">
                            📡 {t('gps.title') || 'Sistema GPS'}
                        </h1>
                        {lastUpdate && (
                            <div className="text-sm text-gray-500">
                                Última actualización: {lastUpdate.toLocaleTimeString()}
                            </div>
                        )}
                    </div>
                    <div className="flex items-center space-x-4">
                        <div className="flex space-x-2">
                            <button
                                onClick={() => handleTabChange('devices')}
                                className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 ${
                                    activeTab === 'devices'
                                        ? 'bg-blue-500 text-white shadow-md transform scale-105'
                                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200 hover:shadow-sm'
                                }`}
                            >
                                📡 Dispositivos GPS
                            </button>
                            <button
                                onClick={() => handleTabChange('vehicles')}
                                className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 ${
                                    activeTab === 'vehicles'
                                        ? 'bg-blue-500 text-white shadow-md transform scale-105'
                                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200 hover:shadow-sm'
                                }`}
                            >
                                🚗 Vehículos
                            </button>
                            <button
                                onClick={() => handleTabChange('drivers')}
                                className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 ${
                                    activeTab === 'drivers'
                                        ? 'bg-blue-500 text-white shadow-md transform scale-105'
                                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200 hover:shadow-sm'
                                }`}
                            >
                                👨‍💼 Conductores
                            </button>
                        </div>
                        {activeTab === 'devices' && (
                            <button
                                onClick={handleRefresh}
                                disabled={refreshing}
                                className="px-3 py-2 bg-green-500 hover:bg-green-600 disabled:bg-green-300 text-white rounded-lg font-medium transition-colors flex items-center space-x-2"
                            >
                                <span className={`${refreshing ? 'animate-spin' : ''}`}>🔄</span>
                                <span>{refreshing ? 'Actualizando...' : 'Actualizar'}</span>
                            </button>
                        )}
                    </div>
                </div>
                {activeTab === 'devices' && devices.length > 0 && (
                    <div className="mt-3 flex items-center space-x-6 text-sm text-gray-600">
                        <div className="flex items-center space-x-2">
                            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                            <span>Online: {devices.filter(d => d.connection_status === 'ONLINE').length}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                            <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                            <span>Offline: {devices.filter(d => d.connection_status === 'OFFLINE').length}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                            <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                            <span>Total: {devices.length}</span>
                        </div>
                    </div>
                )}
            </div>

            {/* Contenido de la pestaña activa */}
            <div className="flex-1 overflow-hidden">
                {renderTabContent()}
            </div>
        </div>
    );
};

export default GPS; 