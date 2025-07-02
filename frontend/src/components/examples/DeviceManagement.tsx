import React, { useState } from 'react';
import {
  useDevices,
  useCreateDevice,
  useUpdateDevice,
  useDeleteDevice,
  useDeviceStatus,
  useDeviceHistory,
  useDeviceEvents,
  useSendDeviceCommand,
  queryKeys
} from '../../hooks/unifiedHooks';
import { GPSDevice, DeviceCommand } from '../../types/unified';

const DeviceManagement: React.FC = () => {
  const [selectedDevice, setSelectedDevice] = useState<GPSDevice | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [showEditForm, setShowEditForm] = useState(false);

  // Hooks para dispositivos
  const { data: devices, isLoading: devicesLoading, error: devicesError } = useDevices();
  const createDeviceMutation = useCreateDevice();
  const updateDeviceMutation = useUpdateDevice();
  const deleteDeviceMutation = useDeleteDevice();
  const sendCommandMutation = useSendDeviceCommand();

  // Hooks para dispositivo específico
  const { data: deviceStatus } = useDeviceStatus(selectedDevice?.imei || 0, {
    queryKey: queryKeys.devices.status(selectedDevice?.imei || 0),
    enabled: !!selectedDevice?.imei
  });

  const { data: deviceHistory } = useDeviceHistory(
    selectedDevice?.imei || 0,
    undefined,
    undefined,
    { 
      queryKey: queryKeys.devices.history(selectedDevice?.imei || 0),
      enabled: !!selectedDevice?.imei 
    }
  );

  const { data: deviceEvents } = useDeviceEvents(
    selectedDevice?.imei || 0,
    undefined,
    undefined,
    undefined,
    { 
      queryKey: queryKeys.devices.events(selectedDevice?.imei || 0),
      enabled: !!selectedDevice?.imei 
    }
  );

  // Estados del formulario
  const [formData, setFormData] = useState({
    imei: '',
    name: '',
    protocol: 'concox',
    route: 1,
    economico: 1
  });

  const handleCreateDevice = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await createDeviceMutation.mutateAsync({
        imei: parseInt(formData.imei),
        name: formData.name,
        protocol: formData.protocol,
        route: formData.route,
        economico: formData.economico,
        is_active: true
      });
      setShowCreateForm(false);
      setFormData({ imei: '', name: '', protocol: 'concox', route: 1, economico: 1 });
    } catch (error) {
      console.error('Error creating device:', error);
    }
  };

  const handleUpdateDevice = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedDevice) return;
    
    try {
      await updateDeviceMutation.mutateAsync({
        imei: selectedDevice.imei,
        data: {
          name: formData.name,
          protocol: formData.protocol,
          route: formData.route,
          economico: formData.economico
        }
      });
      setShowEditForm(false);
    } catch (error) {
      console.error('Error updating device:', error);
    }
  };

  const handleDeleteDevice = async (imei: number) => {
    if (window.confirm('¿Estás seguro de que quieres eliminar este dispositivo?')) {
      try {
        await deleteDeviceMutation.mutateAsync(imei);
      } catch (error) {
        console.error('Error deleting device:', error);
      }
    }
  };

  const handleSendCommand = async (commandType: string) => {
    if (!selectedDevice) return;
    
    try {
      const command: DeviceCommand = {
        device: selectedDevice,
        command_type: commandType,
        parameters: {},
        status: 'PENDING',
        sent_at: null,
        acknowledged_at: null,
        response: null
      };
      
      await sendCommandMutation.mutateAsync({
        imei: selectedDevice.imei,
        command
      });
    } catch (error) {
      console.error('Error sending command:', error);
    }
  };

  if (devicesLoading) {
    return <div className="p-4">Cargando dispositivos...</div>;
  }

  if (devicesError) {
    return <div className="p-4 text-red-500">Error al cargar dispositivos: {devicesError.message}</div>;
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Gestión de Dispositivos GPS</h1>
        <button
          onClick={() => setShowCreateForm(true)}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
        >
          Nuevo Dispositivo
        </button>
      </div>

      {/* Lista de dispositivos */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">Dispositivos</h2>
          <div className="space-y-2">
            {devices?.map((device: GPSDevice) => (
              <div
                key={device.imei}
                className={`p-3 border rounded-lg cursor-pointer transition-colors ${
                  selectedDevice?.imei === device.imei
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
                onClick={() => setSelectedDevice(device)}
              >
                <div className="flex justify-between items-center">
                  <div>
                    <h3 className="font-medium">{device.name}</h3>
                    <p className="text-sm text-gray-600">IMEI: {device.imei}</p>
                    <p className="text-sm text-gray-600">
                      Estado: 
                      <span className={`ml-1 px-2 py-1 rounded-full text-xs ${
                        device.connection_status === 'ONLINE' 
                          ? 'bg-green-100 text-green-800'
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {device.connection_status}
                      </span>
                    </p>
                  </div>
                  <div className="flex space-x-2">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setSelectedDevice(device);
                        setFormData({
                          imei: device.imei.toString(),
                          name: device.name,
                          protocol: device.protocol,
                          route: device.route,
                          economico: device.economico
                        });
                        setShowEditForm(true);
                      }}
                      className="text-blue-600 hover:text-blue-800 text-sm"
                    >
                      Editar
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDeleteDevice(device.imei);
                      }}
                      className="text-red-600 hover:text-red-800 text-sm"
                    >
                      Eliminar
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Detalles del dispositivo seleccionado */}
        {selectedDevice && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4">Detalles del Dispositivo</h2>
            <div className="space-y-4">
              <div>
                <h3 className="font-medium">{selectedDevice.name}</h3>
                <p className="text-sm text-gray-600">IMEI: {selectedDevice.imei}</p>
                <p className="text-sm text-gray-600">Protocolo: {selectedDevice.protocol}</p>
                <p className="text-sm text-gray-600">Ruta: {selectedDevice.route}</p>
                <p className="text-sm text-gray-600">Económico: {selectedDevice.economico}</p>
              </div>

              {/* Estado del dispositivo */}
              {deviceStatus && (
                <div className="border-t pt-4">
                  <h4 className="font-medium mb-2">Estado</h4>
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div>
                      <span className="text-gray-600">En línea:</span>
                      <span className={`ml-2 px-2 py-1 rounded-full text-xs ${
                        deviceStatus.is_online 
                          ? 'bg-green-100 text-green-800'
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {deviceStatus.is_online ? 'Sí' : 'No'}
                      </span>
                    </div>
                    <div>
                      <span className="text-gray-600">Batería:</span>
                      <span className="ml-2">{deviceStatus.battery_level || 'N/A'}%</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Señal:</span>
                      <span className="ml-2">{deviceStatus.signal_strength || 'N/A'}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Último latido:</span>
                      <span className="ml-2">
                        {deviceStatus.last_heartbeat 
                          ? new Date(deviceStatus.last_heartbeat).toLocaleString()
                          : 'N/A'
                        }
                      </span>
                    </div>
                  </div>
                </div>
              )}

              {/* Comandos */}
              <div className="border-t pt-4">
                <h4 className="font-medium mb-2">Comandos</h4>
                <div className="flex space-x-2">
                  <button
                    onClick={() => handleSendCommand('REBOOT')}
                    className="bg-yellow-600 text-white px-3 py-1 rounded text-sm hover:bg-yellow-700"
                  >
                    Reiniciar
                  </button>
                  <button
                    onClick={() => handleSendCommand('GET_STATUS')}
                    className="bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700"
                  >
                    Estado
                  </button>
                  <button
                    onClick={() => handleSendCommand('GET_CONFIG')}
                    className="bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700"
                  >
                    Configuración
                  </button>
                </div>
              </div>

              {/* Historial reciente */}
              {deviceHistory && deviceHistory.length > 0 && (
                <div className="border-t pt-4">
                  <h4 className="font-medium mb-2">Últimas ubicaciones</h4>
                  <div className="space-y-1 max-h-32 overflow-y-auto">
                    {deviceHistory.slice(0, 5).map((location: any, index: number) => (
                      <div key={index} className="text-sm text-gray-600">
                        {new Date(location.timestamp).toLocaleString()} - 
                        Lat: {location.position.y.toFixed(6)}, 
                        Lon: {location.position.x.toFixed(6)}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Eventos recientes */}
              {deviceEvents && deviceEvents.length > 0 && (
                <div className="border-t pt-4">
                  <h4 className="font-medium mb-2">Últimos eventos</h4>
                  <div className="space-y-1 max-h-32 overflow-y-auto">
                    {deviceEvents.slice(0, 5).map((event: any, index: number) => (
                      <div key={index} className="text-sm text-gray-600">
                        {new Date(event.timestamp).toLocaleString()} - {event.type}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Modal para crear dispositivo */}
      {showCreateForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h2 className="text-xl font-semibold mb-4">Nuevo Dispositivo</h2>
            <form onSubmit={handleCreateDevice} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">IMEI</label>
                <input
                  type="text"
                  value={formData.imei}
                  onChange={(e) => setFormData({ ...formData, imei: e.target.value })}
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Nombre</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Protocolo</label>
                <select
                  value={formData.protocol}
                  onChange={(e) => setFormData({ ...formData, protocol: e.target.value })}
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                >
                  <option value="concox">Concox</option>
                  <option value="gt06">GT06</option>
                  <option value="meiligao">Meiligao</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Ruta</label>
                <input
                  type="number"
                  value={formData.route}
                  onChange={(e) => setFormData({ ...formData, route: parseInt(e.target.value) })}
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Económico</label>
                <input
                  type="number"
                  value={formData.economico}
                  onChange={(e) => setFormData({ ...formData, economico: parseInt(e.target.value) })}
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                  required
                />
              </div>
              <div className="flex space-x-3">
                <button
                  type="submit"
                  className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700"
                  disabled={createDeviceMutation.isPending}
                >
                  {createDeviceMutation.isPending ? 'Creando...' : 'Crear'}
                </button>
                <button
                  type="button"
                  onClick={() => setShowCreateForm(false)}
                  className="flex-1 bg-gray-300 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-400"
                >
                  Cancelar
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal para editar dispositivo */}
      {showEditForm && selectedDevice && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h2 className="text-xl font-semibold mb-4">Editar Dispositivo</h2>
            <form onSubmit={handleUpdateDevice} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Nombre</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Protocolo</label>
                <select
                  value={formData.protocol}
                  onChange={(e) => setFormData({ ...formData, protocol: e.target.value })}
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                >
                  <option value="concox">Concox</option>
                  <option value="gt06">GT06</option>
                  <option value="meiligao">Meiligao</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Ruta</label>
                <input
                  type="number"
                  value={formData.route}
                  onChange={(e) => setFormData({ ...formData, route: parseInt(e.target.value) })}
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Económico</label>
                <input
                  type="number"
                  value={formData.economico}
                  onChange={(e) => setFormData({ ...formData, economico: parseInt(e.target.value) })}
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                  required
                />
              </div>
              <div className="flex space-x-3">
                <button
                  type="submit"
                  className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700"
                  disabled={updateDeviceMutation.isPending}
                >
                  {updateDeviceMutation.isPending ? 'Actualizando...' : 'Actualizar'}
                </button>
                <button
                  type="button"
                  onClick={() => setShowEditForm(false)}
                  className="flex-1 bg-gray-300 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-400"
                >
                  Cancelar
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default DeviceManagement; 