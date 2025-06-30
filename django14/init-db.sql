-- Crear la base de datos falkun si no existe
CREATE DATABASE falkun;

-- Conectar a la base de datos falkun
\c falkun;

-- Habilitar la extensión PostGIS
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

-- Crear usuario específico para Django si es necesario
-- CREATE USER django_user WITH PASSWORD 'django_password';
-- GRANT ALL PRIVILEGES ON DATABASE falkun TO django_user;
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO django_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO django_user; 