// Si estás usando React 17+ y no necesitas importar React explícitamente
// Elimina la línea de importación de React si no la estás usando directamente

// Si necesitas usar React, asegúrate de usarlo en el componente
// Por ejemplo:
// const Profile: React.FC = () => {
//   return <div>Profile Page</div>;
// };

import React from 'react';
import { useTranslation } from 'react-i18next';

const Profile: React.FC = () => {
  const { t } = useTranslation();
  
  return (
    <div className="profile-page">
      <h1>{t('profile.title')}</h1>
      <p>{t('profile.description')}</p>
    </div>
  );
};

export default Profile;