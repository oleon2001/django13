import React, { useEffect, useRef, useState } from 'react';
import { MapContainer, TileLayer, useMap, Circle, Polygon, Tooltip } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { Geofence } from '../../services/geofenceService';
import { Box, Typography } from '@mui/material';

// Fix para los iconos de Leaflet en producción
// @ts-ignore
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

interface GeofenceMapProps {
  geofences: Geofence[];
  center?: [number, number];
  zoom?: number;
  height?: string | number;
  onGeofenceClick?: (geofence: Geofence) => void;
  selectedGeofenceId?: number | null;
  onGeometryCreated?: (geometry: any) => void;
  initialGeometry?: any;
}

const DEFAULT_CENTER: [number, number] = [19.4326, -99.1332]; // CDMX
const DEFAULT_ZOOM = 12;

// Componente para ajustar la vista del mapa según las geocercas
const MapBoundsUpdater: React.FC<{ geofences: Geofence[] }> = ({ geofences }) => {
  const map = useMap();

  useEffect(() => {
    if (geofences.length === 0) return;

    const bounds = L.latLngBounds(
      geofences.flatMap(geofence => {
        const { geometry } = geofence;
        if (geometry.type === 'circle') {
          const [center, radius] = geometry.coordinates as [L.LatLngExpression, number];
          const centerPoint = L.latLng(center as L.LatLngTuple);
          const radiusInDegrees = radius / 111320; // Convertir metros a grados (aproximado)
          return [
            [centerPoint.lat - radiusInDegrees, centerPoint.lng - radiusInDegrees],
            [centerPoint.lat + radiusInDegrees, centerPoint.lng + radiusInDegrees],
          ];
        } else {
          // Para polígonos y rectángulos
          return geometry.coordinates as [number, number][];
        }
      })
    );

    // Ajustar el zoom para mostrar todas las geocercas con un poco de padding
    map.fitBounds(bounds, { padding: [50, 50] });
  }, [geofences, map]);

  return null;
};

// Componente para renderizar una geocerca en el mapa
const GeofenceLayer: React.FC<{ 
  geofence: Geofence;
  isSelected?: boolean;
  onClick?: (geofence: Geofence) => void;
}> = ({ geofence, isSelected = false, onClick }) => {
  const { name, geometry, is_active, color = '#3388ff', stroke_width = 2, stroke_color = '#3388ff' } = geofence;
  const fillOpacity = is_active ? 0.2 : 0.1;
  const weight = isSelected ? stroke_width + 2 : stroke_width;
  const dashArray = is_active ? undefined : '5, 5';

  const handleClick = () => {
    if (onClick) {
      onClick(geofence);
    }
  };

  const renderGeometry = () => {
    if (geometry.type === 'circle') {
      const [center, radius] = geometry.coordinates as [L.LatLngExpression, number];
      return (
        <Circle
          center={center}
          radius={radius}
          pathOptions={{
            color: isSelected ? '#ff0000' : stroke_color,
            weight,
            opacity: 1,
            fillColor: color,
            fillOpacity: fillOpacity,
            dashArray,
          }}
          eventHandlers={{
            click: handleClick,
          }}
        >
          <Tooltip direction="top" offset={[0, -10]} opacity={1} permanent>
            <div>
              <strong>{name}</strong>
              <div>Radio: {Math.round(radius)}m</div>
              <div>Estado: {is_active ? 'Activo' : 'Inactivo'}</div>
            </div>
          </Tooltip>
        </Circle>
      );
    } else {
      // Para polígonos y rectángulos
      return (
        <Polygon
          positions={geometry.coordinates as L.LatLngExpression[]}
          pathOptions={{
            color: isSelected ? '#ff0000' : stroke_color,
            weight,
            opacity: 1,
            fillColor: color,
            fillOpacity: fillOpacity,
            dashArray,
          }}
          eventHandlers={{
            click: handleClick,
          }}
        >
          <Tooltip direction="top" offset={[0, -10]} opacity={1} permanent>
            <div>
              <strong>{name}</strong>
              <div>Estado: {is_active ? 'Activo' : 'Inactivo'}</div>
            </div>
          </Tooltip>
        </Polygon>
      );
    }
  };

  return <>{renderGeometry()}</>;
};

const GeofenceMap: React.FC<GeofenceMapProps> = ({
  geofences = [],
  center = DEFAULT_CENTER,
  zoom = DEFAULT_ZOOM,
  height = '100%',
  onGeofenceClick,
  selectedGeofenceId,
}) => {
  const mapRef = useRef<L.Map>(null);
  const [hasError, setHasError] = useState(false);

  // Manejar errores de carga del mapa
  useEffect(() => {
    const handleMapError = () => {
      setHasError(true);
    };

    // @ts-ignore
    window.addEventListener('error', handleMapError);
    return () => {
      // @ts-ignore
      window.removeEventListener('error', handleMapError);
    };
  }, []);

  if (hasError) {
    return (
      <Box 
        height={height} 
        display="flex" 
        alignItems="center" 
        justifyContent="center"
        bgcolor="#f5f5f5"
        borderRadius={1}
      >
        <Typography color="error">
          Error al cargar el mapa. Por favor, intente recargar la página.
        </Typography>
      </Box>
    );
  }

  return (
    <Box height={height} width="100%" position="relative">
      <MapContainer
        center={center}
        zoom={zoom}
        style={{ height: '100%', width: '100%', borderRadius: '4px' }}
        ref={mapRef}
        zoomControl={true}
        doubleClickZoom={true}
        closePopupOnClick={true}
        dragging={true}
        zoomSnap={0.5}
        zoomDelta={0.5}
        trackResize={true}
        touchZoom={true}
        scrollWheelZoom={true}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        />
        
        {geofences.length > 0 && <MapBoundsUpdater geofences={geofences} />}
        
        {geofences.map(geofence => (
          <GeofenceLayer
            key={geofence.id}
            geofence={geofence}
            isSelected={selectedGeofenceId === geofence.id}
            onClick={onGeofenceClick}
          />
        ))}
      </MapContainer>
    </Box>
  );
};

// Exportación nombrada para facilitar las importaciones
export { GeofenceMap };

export default GeofenceMap;
