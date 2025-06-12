// Si estás usando React 17+ y no necesitas importar React explícitamente
// Elimina la línea de importación de React si no la estás usando directamente

// Si necesitas usar React, asegúrate de usarlo en el componente
// Por ejemplo:
// const Profile: React.FC = () => {
//   return <div>Profile Page</div>;
// };

const Profile = () => {
  return (
    <div className="profile-page">
      <h1>Profile Page</h1>
      <p>This is the user profile page</p>
    </div>
  );
};

export default Profile;