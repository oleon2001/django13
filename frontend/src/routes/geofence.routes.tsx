import { RouteObject } from 'react-router-dom';
import { GeofenceManager, DeviceBehaviorAnalysis } from '../components/Geofence';
import { useTranslation } from 'react-i18next';
import PrivateRoute from '../components/PrivateRoute';

const GeofenceRoutes: RouteObject[] = [
  {
    path: '/geofences',
    element: (
      <PrivateRoute>
        <GeofenceManager />
      </PrivateRoute>
    ),
    handle: {
      title: () => {
        // eslint-disable-next-line react-hooks/rules-of-hooks
        const { t } = useTranslation();
        return t('geofence.title');
      },
      breadcrumb: () => {
        // eslint-disable-next-line react-hooks/rules-of-hooks
        const { t } = useTranslation();
        return t('geofence.title');
      },
      roles: ['admin', 'manager', 'user'],
    },
  },
  {
    path: '/geofences/analytics/:deviceId',
    element: (
      <PrivateRoute>
        <DeviceBehaviorAnalysis deviceId={""} />
      </PrivateRoute>
    ),
    handle: {
      title: () => 'Análisis Comportamental ML',
      breadcrumb: () => 'Análisis ML',
      roles: ['admin', 'manager'],
    },
  },
];

export default GeofenceRoutes;
