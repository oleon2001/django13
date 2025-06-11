import React, { useEffect, useRef } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import './Map.css';

interface Location {
  latitude: number;
  longitude: number;
  speed: number;
  heading: number;
}

interface Device {
  imei: number;
  protocol: string;
  status: string;
  lastUpdate: string;
  location?: Location;
}

interface MapProps {
  devices: Device[];
  center?: [number, number];
  zoom?: number;
}

const Map: React.FC<MapProps> = ({
  devices,
  center = [-33.4489, -70.6693], // Santiago, Chile
  zoom = 13,
}) => {
  const mapRef = useRef<L.Map>(null);

  useEffect(() => {
    if (mapRef.current && devices.length > 0) {
      const bounds = devices
        .filter((device) => device.location)
        .map((device) => [
          device.location!.latitude,
          device.location!.longitude,
        ]);
      mapRef.current.fitBounds(bounds as L.LatLngBoundsExpression);
    }
  }, [devices]);

  return (
    <div className="map-container">
      <MapContainer
        center={center}
        zoom={zoom}
        ref={mapRef}
        className="map"
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        />
        {devices.map(
          (device) =>
            device.location && (
              <Marker
                key={device.imei}
                position={[
                  device.location.latitude,
                  device.location.longitude,
                ]}
              >
                <Popup>
                  <div className="device-popup">
                    <h3>Dispositivo {device.imei}</h3>
                    <p>Estado: {device.status}</p>
                    <p>Velocidad: {device.location.speed} km/h</p>
                    <p>Dirección: {device.location.heading}°</p>
                    <p>
                      Última actualización:{' '}
                      {new Date(device.lastUpdate).toLocaleString()}
                    </p>
                  </div>
                </Popup>
              </Marker>
            )
        )}
      </MapContainer>
    </div>
  );
};

export default Map; 