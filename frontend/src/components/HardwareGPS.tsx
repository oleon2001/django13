import React, { useState, useEffect } from 'react';
import { Device } from '../types';
import { gpsConnectionService, GPSConfig } from '../services/hardware/gpsConnection';

const HardwareGPS: React.FC = () => {
    const [isConnected, setIsConnected] = useState(false);
    const [device, setDevice] = useState<Device | null>(null);
    const [config, setConfig] = useState<GPSConfig>({
        host: 'localhost',
        port: 8080,
        protocol: 'TCP',
        deviceId: '1'
    });
    const [command, setCommand] = useState('');
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);

    const formatDate = (date: string | undefined) => {
        if (!date) return 'Never';
        return new Date(date).toLocaleString();
    };

    useEffect(() => {
        // Suscribirse a actualizaciones del dispositivo
        const unsubscribe = gpsConnectionService.subscribe((updatedDevice) => {
            setDevice(updatedDevice);
        });

        // Limpiar al desmontar
        return () => {
            unsubscribe();
            if (isConnected) {
                gpsConnectionService.disconnect();
            }
        };
    }, [isConnected]);

    const handleConnect = async () => {
        setLoading(true);
        setError(null);
        
        try {
            const success = await gpsConnectionService.connect(config);
            if (success) {
                setIsConnected(true);
            } else {
                setError('No se pudo establecer la conexión');
            }
        } catch (err) {
            setError('Error al conectar: ' + (err as Error).message);
        } finally {
            setLoading(false);
        }
    };

    const handleDisconnect = () => {
        gpsConnectionService.disconnect();
        setIsConnected(false);
        setDevice(null);
    };

    const handleSendCommand = () => {
        if (command.trim()) {
            const success = gpsConnectionService.sendCommand(command);
            if (success) {
                setCommand('');
            } else {
                setError('No se pudo enviar el comando');
            }
        }
    };

    return (
        <div className="h-screen flex flex-col p-4">
            <div className="mb-4">
                <h1 className="text-2xl font-bold mb-4">Conexión Directa GPS</h1>
                
                {/* Configuración de conexión */}
                <div className="grid grid-cols-2 gap-4 mb-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700">Host</label>
                        <input
                            type="text"
                            value={config.host}
                            onChange={(e) => setConfig({ ...config, host: e.target.value })}
                            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                            disabled={isConnected}
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700">Puerto</label>
                        <input
                            type="number"
                            value={config.port}
                            onChange={(e) => setConfig({ ...config, port: parseInt(e.target.value) })}
                            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                            disabled={isConnected}
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700">Protocolo</label>
                        <select
                            value={config.protocol}
                            onChange={(e) => setConfig({ ...config, protocol: e.target.value as 'TCP' | 'UDP' })}
                            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                            disabled={isConnected}
                        >
                            <option value="TCP">TCP</option>
                            <option value="UDP">UDP</option>
                        </select>
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700">ID del Dispositivo</label>
                        <input
                            type="text"
                            value={config.deviceId}
                            onChange={(e) => setConfig({ ...config, deviceId: e.target.value })}
                            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                            disabled={isConnected}
                        />
                    </div>
                </div>

                {/* Botones de control */}
                <div className="flex gap-4 mb-4">
                    {!isConnected ? (
                        <button
                            onClick={handleConnect}
                            disabled={loading}
                            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
                        >
                            {loading ? 'Conectando...' : 'Conectar'}
                        </button>
                    ) : (
                        <button
                            onClick={handleDisconnect}
                            className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
                        >
                            Desconectar
                        </button>
                    )}
                </div>

                {/* Comandos rápidos */}
                {isConnected && (
                    <div className="mb-4">
                        <h2 className="text-lg font-semibold mb-2">Comandos Rápidos</h2>
                        <div className="flex gap-2">
                            <button
                                onClick={() => {
                                    setCommand('STATUS');
                                    gpsConnectionService.sendCommand('STATUS');
                                }}
                                className="bg-gray-500 text-white px-3 py-1 rounded hover:bg-gray-600"
                            >
                                Estado
                            </button>
                            <button
                                onClick={() => {
                                    setCommand('POSITION');
                                    gpsConnectionService.sendCommand('POSITION');
                                }}
                                className="bg-gray-500 text-white px-3 py-1 rounded hover:bg-gray-600"
                            >
                                Posición
                            </button>
                            <button
                                onClick={() => {
                                    setCommand('BATTERY');
                                    gpsConnectionService.sendCommand('BATTERY');
                                }}
                                className="bg-gray-500 text-white px-3 py-1 rounded hover:bg-gray-600"
                            >
                                Batería
                            </button>
                        </div>
                        
                        {/* Campo para comandos personalizados */}
                        <div className="mt-4">
                            <label className="block text-sm font-medium text-gray-700 mb-1">Comando Personalizado</label>
                            <div className="flex gap-2">
                                <input
                                    type="text"
                                    value={command}
                                    onChange={(e) => setCommand(e.target.value)}
                                    onKeyPress={(e) => e.key === 'Enter' && handleSendCommand()}
                                    placeholder="Ingrese comando GPS"
                                    className="flex-1 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                                />
                                <button
                                    onClick={handleSendCommand}
                                    className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600"
                                >
                                    Enviar
                                </button>
                            </div>
                        </div>
                    </div>
                )}

                {/* Mensaje de error */}
                {error && (
                    <div className="text-red-500 mb-4">
                        {error}
                    </div>
                )}

                {/* Estado de la conexión */}
                <div className="mb-4">
                    <span className={`inline-block px-2 py-1 rounded ${
                        isConnected ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    }`}>
                        {isConnected ? 'Conectado' : 'Desconectado'}
                    </span>
                </div>
            </div>

            {/* Mapa y datos del dispositivo */}
            <div className="flex-1 flex">
                <div className="w-1/3 pr-4">
                    {device && (
                        <div className="bg-white shadow rounded-lg p-4">
                            <h2 className="text-lg font-semibold mb-4">Datos del Dispositivo</h2>
                            <div className="space-y-2">
                                <p><span className="font-medium">Nombre:</span> {device.name}</p>
                                <p><span className="font-medium">IMEI:</span> {device.imei}</p>
                                <p><span className="font-medium">Estado:</span> {device.status}</p>
                                <p><span className="font-medium">Velocidad:</span> {device.speed || 0} km/h</p>
                                <p><span className="font-medium">Batería:</span> {device.battery_level || 0}%</p>
                                <p><span className="font-medium">Última actualización:</span> {formatDate(device.lastUpdate)}</p>
                            </div>
                        </div>
                    )}
                </div>
                <div className="flex-1">
                    {device && (
                        <div className="bg-white shadow rounded-lg p-4 h-full">
                            <h2 className="text-lg font-semibold mb-4">Ubicación del Dispositivo</h2>
                            <div className="bg-gray-100 rounded p-4">
                                <p><span className="font-medium">Latitud:</span> {device.position?.latitude || 'N/A'}</p>
                                <p><span className="font-medium">Longitud:</span> {device.position?.longitude || 'N/A'}</p>
                                <p><span className="font-medium">Altitud:</span> {device.altitude || 'N/A'} m</p>
                                <p><span className="font-medium">Satélites:</span> {device.satellites || 'N/A'}</p>
                                <p><span className="font-medium">HDOP:</span> {device.hdop || 'N/A'}</p>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default HardwareGPS; 