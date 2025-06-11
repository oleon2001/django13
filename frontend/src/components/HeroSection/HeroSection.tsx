import React from 'react';
import './HeroSection.css';

export const HeroSection: React.FC = () => {
  return (
    <section className="hero-section">
      <div className="hero-content">
        <img src="/static/img/skyguard.png" alt="Skyguard Logo" className="falkon-logo" />
        <h1>¡Recupera lo que pierdes!</h1>
        <h2>Protege tu flotilla</h2>
        <p>
          Evita El Robo De Boletos Y Optimiza Tus Ingresos Con
          Nuestra Tecnología De Conteo Y Rastreo.
        </p>
        <button className="demo-button">Solicita una Demostración</button>
      </div>
    </section>
  );
}; 