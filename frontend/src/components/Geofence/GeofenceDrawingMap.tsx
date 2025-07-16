import React, { useEffect, useRef, useState } from 'react';
import { MapContainer, TileLayer, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import 'leaflet-draw/dist/leaflet.draw.css';
import './GeofenceDrawingMap.css';
import 'leaflet-draw';
import { Box, Typography, Button, Alert } from '@mui/material';
import { RadioButtonUnchecked, CropSquare, ChangeHistory } from '@mui/icons-material';

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
}) => {
  const mapRef = useRef<L.Map>(null);
  const [hasError, setHasError] = useState(false);

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
        
        <DrawingControls 
          onGeometryCreated={onGeometryCreated}
          initialGeometry={initialGeometry}
        />
      </MapContainer>
    </Box>
  );
};

export default GeofenceDrawingMap; 