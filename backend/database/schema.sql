-- Tabla de Usuarios y Autenticación
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de Módulos Educativos
CREATE TABLE IF NOT EXISTS modules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    order_num INTEGER NOT NULL
);

-- Tabla de Historial de Chat con la IA
CREATE TABLE IF NOT EXISTS chat_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    module_name TEXT NOT NULL,
    sender TEXT NOT NULL,
    message TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de Estado de Simulación Presidencial
CREATE TABLE IF NOT EXISTS simulation_state (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    country_name TEXT DEFAULT 'Nación Alpha',
    approval_rate REAL DEFAULT 50.0,
    inflation_rate REAL DEFAULT 4.5,
    fiscal_deficit REAL DEFAULT 2.0,
    turn_number INTEGER DEFAULT 1
);
