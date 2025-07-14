import { RouteObject } from 'react-router-dom';
import { GeofenceManager } from '../components/Geofence';
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
      roles: ['admin', 'manager'],
    },
  },
];

export default GeofenceRoutes;
