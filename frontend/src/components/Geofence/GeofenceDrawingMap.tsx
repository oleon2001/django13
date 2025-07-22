import React, { useEffect, useRef, useState } from 'react';
import { MapContainer, TileLayer, useMap, Marker, Tooltip } from 'react-leaflet';
import L, { Icon } from 'leaflet';
import 'leaflet/dist/leaflet.css';
import 'leaflet-draw/dist/leaflet.draw.css';
import './GeofenceDrawingMap.css';
import 'leaflet-draw';
import { Box, Typography, Button, Alert } from '@mui/material';
import { RadioButtonUnchecked, CropSquare, ChangeHistory } from '@mui/icons-material';
import { Device } from '../../types';
import { TextField, InputAdornment, List, ListItem, ListItemText } from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import gpsIconUrl from '../../assets/gps-device.png'; // Asegúrate de tener este icono en assets

// Fix para los iconos de Leaflet en producción
// @ts-ignore
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

interface GeofenceDrawingMapProps {
  center?: [number, number];
  zoom?: number;
  height?: string | number;
  onGeometryCreated: (geometry: any) => void;
  initialGeometry?: any;
  devices?: Device[];
  selectedDeviceIds?: number[];
  onCenterChange?: (coords: [number, number]) => void; // NUEVO
}

const DEFAULT_CENTER: [number, number] = [19.4326, -99.1332]; // CDMX
const DEFAULT_ZOOM = 12;

// Componente interno para manejar las herramientas de dibujo
const DrawingControls: React.FC<{
  onGeometryCreated: (geometry: any) => void;
  initialGeometry?: any;
}> = ({ onGeometryCreated, initialGeometry }) => {
  const map = useMap();
  const drawnItemsRef = useRef<L.FeatureGroup | null>(null);
  const drawControlRef = useRef<L.Control.Draw | null>(null);

  useEffect(() => {
    // Crear grupo para las formas dibujadas
    const drawnItems = new L.FeatureGroup();
    drawnItemsRef.current = drawnItems;
    map.addLayer(drawnItems);

    // Configuración de las herramientas de dibujo
    const drawControl = new L.Control.Draw({
      position: 'topright',
      draw: {
        // Habilitamos todas las herramientas que necesitamos
        circle: {
          shapeOptions: {
            color: '#3388ff',
            weight: 2,
            fillOpacity: 0.2,
          },
          showRadius: true,
          metric: true,
          feet: false,
        },
        polygon: {
          allowIntersection: false,
          drawError: {
            color: '#e1e100',
            message: '<strong>Error:</strong> Las líneas no pueden cruzarse!',
          },
          shapeOptions: {
            color: '#3388ff',
            weight: 2,
            fillOpacity: 0.2,
          },
        },
        rectangle: {
          shapeOptions: {
            color: '#3388ff',
            weight: 2,
            fillOpacity: 0.2,
          },
        },
        // Deshabilitamos las que no necesitamos
        polyline: false,
        marker: false,
        circlemarker: false,
      },
      edit: {
        featureGroup: drawnItems,
        remove: true,
        edit: {},
      },
    });

    drawControlRef.current = drawControl;
    map.addControl(drawControl);

    // Función para convertir la geometría
    const convertToGeometry = (layer: any, layerType: string) => {
      let geometry: any = null;

      if (layerType === 'circle') {
        const center = layer.getLatLng();
        const radius = layer.getRadius();
        geometry = {
          type: 'circle',
          coordinates: [[center.lat, center.lng], radius],
        };
      } else if (layerType === 'polygon' || layerType === 'rectangle') {
        const latLngs = layer.getLatLngs();
        // Para polígonos simples, tomamos el primer array
        const coordinates = (Array.isArray(latLngs[0]) ? latLngs[0] : latLngs).map((latLng: L.LatLng) => [
          latLng.lat,
          latLng.lng,
        ]);
        geometry = {
          type: layerType,
          coordinates: coordinates,
        };
      }

      return geometry;
    };

    // Manejar eventos de dibujo
    const handleDrawCreated = (e: any) => {
      const layer = e.layer;
      const type = e.layerType;

      // Limpiar capas anteriores (solo permitimos una geocerca a la vez)
      drawnItems.clearLayers();
      drawnItems.addLayer(layer);

      // Convertir a formato de geometría
      const geometry = convertToGeometry(layer, type);
      if (geometry) {
        onGeometryCreated(geometry);
      }
    };

    const handleDrawEdited = (e: any) => {
      const layers = e.layers;
      layers.eachLayer((layer: any) => {
        let layerType = 'polygon'; // por defecto
        
        if (layer instanceof L.Circle) {
          layerType = 'circle';
        } else if (layer instanceof L.Rectangle) {
          layerType = 'rectangle';
        }

        const geometry = convertToGeometry(layer, layerType);
        if (geometry) {
          onGeometryCreated(geometry);
        }
      });
    };

    const handleDrawDeleted = () => {
      onGeometryCreated(null);
    };

    // Registrar eventos
    map.on(L.Draw.Event.CREATED, handleDrawCreated);
    map.on(L.Draw.Event.EDITED, handleDrawEdited);
    map.on(L.Draw.Event.DELETED, handleDrawDeleted);

    // Cargar geometría inicial si existe
    if (initialGeometry) {
      let layer: L.Layer | null = null;

      try {
        if (initialGeometry.type === 'circle') {
          const [center, radius] = initialGeometry.coordinates;
          layer = L.circle([center[0], center[1]], {
            radius: radius,
            color: '#3388ff',
            weight: 2,
            fillOpacity: 0.2,
          });
        } else if (initialGeometry.type === 'polygon') {
          const coordinates = initialGeometry.coordinates.map((coord: number[]) => [coord[0], coord[1]] as [number, number]);
          layer = L.polygon(coordinates, {
            color: '#3388ff',
            weight: 2,
            fillOpacity: 0.2,
          });
        } else if (initialGeometry.type === 'rectangle') {
          const coordinates = initialGeometry.coordinates.map((coord: number[]) => [coord[0], coord[1]] as [number, number]);
          // Para rectángulos, crear usando los puntos como polígono
          layer = L.polygon(coordinates, {
            color: '#3388ff',
            weight: 2,
            fillOpacity: 0.2,
          });
        }

        if (layer) {
          drawnItems.addLayer(layer);
          // Ajustar vista para mostrar la geometría
          setTimeout(() => {
            if (drawnItems.getLayers().length > 0) {
              const bounds = drawnItems.getBounds();
              if (bounds.isValid()) {
                map.fitBounds(bounds, { padding: [20, 20] });
              }
            }
          }, 100);
        }
      } catch (error) {
        console.error('Error cargando geometría inicial:', error);
      }
    }

    // Cleanup
    return () => {
      map.off(L.Draw.Event.CREATED, handleDrawCreated);
      map.off(L.Draw.Event.EDITED, handleDrawEdited);
      map.off(L.Draw.Event.DELETED, handleDrawDeleted);
      
      if (drawControlRef.current) {
        map.removeControl(drawControlRef.current);
      }
      if (drawnItemsRef.current) {
        map.removeLayer(drawnItemsRef.current);
      }
    };
  }, [map, onGeometryCreated, initialGeometry]);

  return null;
};

// Componente principal
const GeofenceDrawingMap: React.FC<GeofenceDrawingMapProps> = ({
  center = DEFAULT_CENTER,
  zoom = DEFAULT_ZOOM,
  height = '100%',
  onGeometryCreated,
  initialGeometry,
  devices = [],
  selectedDeviceIds = [],
  onCenterChange, // NUEVO
}) => {
  const mapRef = useRef<L.Map>(null);
  const [hasError, setHasError] = useState(false);
  const [search, setSearch] = useState('');
  const [searchResults, setSearchResults] = useState<any[]>([]);

  // Manejar errores de carga del mapa
  useEffect(() => {
    const handleMapError = () => {
      setHasError(true);
    };

    window.addEventListener('error', handleMapError);
    return () => {
      window.removeEventListener('error', handleMapError);
    };
  }, []);

  // Buscar ubicación con Nominatim
  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!search) return;
    try {
      const res = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(search)}`);
      const data = await res.json();
      setSearchResults(data);
    } finally {
      // setSearchLoading(false); // Eliminado
    }
  };

  const handleResultClick = (result: any) => {
    if (mapRef.current && result.lat && result.lon) {
      const coords: [number, number] = [parseFloat(result.lat), parseFloat(result.lon)];
      mapRef.current.setView(coords, 16);
      setSearchResults([]);
      setSearch('');
      if (onCenterChange) {
        onCenterChange(coords);
      }
    }
  };

  // Icono personalizado para dispositivos
  const deviceIcon = new Icon({
    iconUrl: gpsIconUrl,
    iconSize: [32, 32],
    iconAnchor: [16, 32],
    popupAnchor: [0, -32],
  });

  if (hasError) {
    return (
      <Box 
        height={height} 
        display="flex" 
        flexDirection="column"
        alignItems="center" 
        justifyContent="center"
        bgcolor="#f5f5f5"
        borderRadius={1}
        p={2}
      >
        <Typography color="error" gutterBottom>
          Error al cargar el mapa. Por favor, intente recargar la página.
        </Typography>
        <Button 
          variant="outlined" 
          onClick={() => window.location.reload()}
          size="small"
        >
          Recargar
        </Button>
      </Box>
    );
  }

  const getInstructionText = () => {
    return 'Usa las herramientas de la esquina superior derecha para dibujar: círculo, polígono o rectángulo';
  };

  return (
    <Box height={height} width="100%" position="relative">
      {/* Barra de búsqueda textual */}
      <form onSubmit={handleSearch} style={{ position: 'absolute', top: 8, left: 8, right: 60, zIndex: 1200 }}>
        <TextField
          value={search}
          onChange={e => setSearch(e.target.value)}
          placeholder="Buscar dirección o lugar..."
          size="small"
          fullWidth
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
          }}
        />
        {searchResults.length > 0 && (
          <List sx={{ bgcolor: 'background.paper', maxHeight: 200, overflow: 'auto', position: 'absolute', width: '100%', zIndex: 1300 }}>
            {searchResults.map((result, idx) => (
              <ListItem button key={idx} onClick={() => handleResultClick(result)}>
                <ListItemText primary={result.display_name} />
              </ListItem>
            ))}
          </List>
        )}
      </form>
      {/* Instrucciones de dibujo */}
      <Alert 
        severity="info" 
        sx={{ 
          position: 'absolute', 
          top: 8, 
          left: 8, 
          right: 60,
          zIndex: 1000,
          fontSize: '0.75rem',
          py: 0.5,
        }}
      >
        <Box display="flex" alignItems="center" gap={1} flexWrap="wrap">
          <RadioButtonUnchecked fontSize="small" color="primary" />
          <Typography variant="caption">Círculo</Typography>
          <ChangeHistory fontSize="small" color="primary" />
          <Typography variant="caption">Polígono</Typography>
          <CropSquare fontSize="small" color="primary" />
          <Typography variant="caption">Rectángulo</Typography>
        </Box>
        <Typography variant="caption" sx={{ display: 'block', mt: 0.5 }}>
          {getInstructionText()}
        </Typography>
      </Alert>

      <MapContainer
        center={center}
        zoom={zoom}
        style={{ height: '100%', width: '100%', borderRadius: '4px' }}
        ref={mapRef}
        zoomControl={true}
        doubleClickZoom={false} // Deshabilitamos para no interferir con el dibujo de polígonos
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
        
        {/* Mostrar dispositivos como marcadores */}
        {devices.map(device => device.position && (
          <Marker
            key={device.id}
            position={[device.position.latitude, device.position.longitude]}
            icon={deviceIcon}
            eventHandlers={{
              click: () => {
                if (mapRef.current) {
                  mapRef.current.setView([device.position!.latitude, device.position!.longitude], 16);
                }
              },
            }}
          >
            <Tooltip direction="top" offset={[0, -10]} opacity={1} permanent={selectedDeviceIds.includes(device.id!)}>
              <div>
                <strong>{device.name || `Device ${device.imei}`}</strong>
                <div>IMEI: {device.imei}</div>
                <div>Status: {device.connection_status || 'OFFLINE'}</div>
              </div>
            </Tooltip>
          </Marker>
        ))}
        <DrawingControls 
          onGeometryCreated={onGeometryCreated}
          initialGeometry={initialGeometry}
        />
      </MapContainer>
    </Box>
  );
};

export default GeofenceDrawingMap; 