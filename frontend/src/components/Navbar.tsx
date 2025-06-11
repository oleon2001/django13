import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { AppDispatch, RootState } from '../store';
import { logout } from '../store/slices/authSlice';
import './Navbar.css';

const Navbar: React.FC = () => {
    const navigate = useNavigate();
    const dispatch = useDispatch<AppDispatch>();
    const { isAuthenticated } = useSelector((state: RootState) => state.auth);

    const handleLogout = async () => {
        await dispatch(logout());
        navigate('/login');
    };

    return (
        <nav className="navbar">
            <div className="navbar-brand">SkyGuard</div>
            {isAuthenticated && (
                <button className="navbar-logout" onClick={handleLogout}>
                    Cerrar Sesión
                </button>
            )}
        </nav>
    );
};

export default Navbar; 