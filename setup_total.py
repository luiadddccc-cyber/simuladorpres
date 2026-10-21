import os

files_content = {
    "requirements.txt": """fastapi>=0.100.0
uvicorn>=0.22.0
pydantic>=2.0
passlib[bcrypt]>=1.7.4
python-jose[cryptography]>=3.3.0
python-dotenv>=1.0.0
""",
    ".env": """SECRET_KEY=futuropres47_secret_key_super_segura
APP_PASSWORD=futuropres47
DATABASE_URL=sqlite:///./simulador.db
""",
    "Procfile": "web: uvicorn backend.app:app --host 0.0.0.0 --port \$PORT\n",
    "render.yaml": """services:
  - type: web
    name: simulador-presidencial
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn backend.app:app --host 0.0.0.0 --port \$PORT
    envVars:
      - key: APP_PASSWORD
        value: futuropres47
      - key: SECRET_KEY
        value: futuropres47_secret_key_super_segura
""",
    "backend/database/schema.sql": """-- Tabla de Usuarios y Autenticación
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
""",
    "backend/database/connection.py": """import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "../../simulador.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    if os.path.exists(schema_path):
        conn = get_db_connection()
        with open(schema_path, "r", encoding="utf-8") as f:
            conn.executescript(f.read())
        
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM modules")
        if cursor.fetchone()[0] == 0:
            modules_data = [
                ("1. Macroeconomía y PYMEs", "Control de inflación, tasas de interés y tejido productivo PYME.", 1),
                ("2. Finanzas Públicas y Planificación", "Presupuesto nacional, deuda soberana y asignación estratégica.", 2),
                ("3. Análisis y Escáner de Contratos", "Auditoría de concesiones, obra pública y blindaje legal.", 3),
                ("4. Simulación de Crisis Históricas", "Toma de decisiones bajo presión extrema y colapsos sistémicos.", 4),
                ("5. Psicología Social y Carisma", "Gestión de expectativas ciudadanas e influencia política.", 5),
                ("6. Oratoria y Registro Lingüístico", "Discursos de Estado, persuasión y comunicación estratégica.", 6),
                ("7. Microexpresiones y Comunicación No Verbal", "Lectura de gestos, lenguaje corporal y detección de engaño.", 7),
                ("8. Idiomas Extranjeros para Líderes", "Diplomacia internacional y vocabulario geopolítico clave.", 8)
            ]
            cursor.executemany("INSERT INTO modules (title, description, order_num) VALUES (?, ?, ?)", modules_data)
            conn.commit()
        conn.close()
        print("Base de datos e indicadores inicializados de forma correcta.")

if __name__ == "__main__":
    init_db()
""",
    "backend/routes/auth.py": """from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os

router = APIRouter()
VALID_PASSWORD = os.getenv("APP_PASSWORD", "futuropres47")

class LoginRequest(BaseModel):
    password: str

@router.post("/login")
def login(data: LoginRequest):
    if data.password == VALID_PASSWORD:
        return {"status": "success", "message": "Acceso concedido", "token": "session_futuropres47_valid"}
    raise HTTPException(status_code=401, detail="Contraseña incorrecta")
""",
    "backend/routes/simulation.py": """from fastapi import APIRouter
from backend.database.connection import get_db_connection

router = APIRouter()

@router.get("/state")
def get_state():
    conn = get_db_connection()
    state = conn.execute("SELECT * FROM simulation_state ORDER BY id DESC LIMIT 1").fetchone()
    if not state:
        conn.execute("INSERT INTO simulation_state (country_name, approval_rate, inflation_rate, fiscal_deficit, turn_number) VALUES ('Nación Alpha', 50.0, 4.5, 2.0, 1)")
        conn.commit()
        state = conn.execute("SELECT * FROM simulation_state ORDER BY id DESC LIMIT 1").fetchone()
    conn.close()
    return dict(state)
""",
    "backend/app.py": """from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from backend.routes.auth import router as auth_router
from backend.routes.simulation import router as sim_router
from backend.database.connection import init_db

app = FastAPI(title="Simulador Presidencial")
init_db()

app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])
app.include_router(sim_router, prefix="/api/sim", tags=["Simulation"])

frontend_path = os.path.join(os.path.dirname(__file__), "../frontend")
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

@app.get("/")
def read_root():
    return FileResponse(os.path.join(frontend_path, "index.html"))
""",
    "frontend/styles/main.css": """* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

body {
    background-color: #121214;
    color: #e1e1e6;
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
}

.login-container {
    background-color: #202024;
    padding: 2.5rem;
    border-radius: 12px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);
    width: 100%;
    max-width: 400px;
    text-align: center;
    border: 1px solid #29292e;
}

.login-container h1 {
    font-size: 1.5rem;
    margin-bottom: 0.5rem;
    color: #ffffff;
}

.login-container p {
    color: #a8a8b3;
    font-size: 0.9rem;
    margin-bottom: 1.5rem;
}

.input-group {
    margin-bottom: 1.5rem;
}

input[type="password"] {
    width: 100%;
    padding: 0.8rem 1rem;
    background-color: #121214;
    border: 1px solid #323238;
    border-radius: 6px;
    color: #ffffff;
    font-size: 1rem;
    outline: none;
    transition: border-color 0.2s;
}

input[type="password"]:focus {
    border-color: #00875f;
}

button {
    width: 100%;
    padding: 0.8rem;
    background-color: #00875f;
    color: #ffffff;
    border: none;
    border-radius: 6px;
    font-size: 1rem;
    font-weight: bold;
    cursor: pointer;
    transition: background-color 0.2s;
}

button:hover {
    background-color: #00b37e;
}

.error-message {
    color: #f75a68;
    margin-top: 1rem;
    font-size: 0.85rem;
    display: none;
}

.dashboard-container {
    display: none;
    width: 100vw;
    height: 100vh;
    background-color: #121214;
    color: #e1e1e6;
    flex-direction: column;
}

header {
    background-color: #202024;
    padding: 1rem 2rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid #29292e;
}

header h2 {
    color: #00b37e;
    font-size: 1.2rem;
}

.main-layout {
    display: flex;
    flex: 1;
    overflow: hidden;
}

aside {
    width: 280px;
    background-color: #16161a;
    border-right: 1px solid #29292e;
    padding: 1.5rem;
    overflow-y: auto;
}

aside h3 {
    font-size: 0.9rem;
    color: #a8a8b3;
    margin-bottom: 1rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.module-btn {
    display: block;
    width: 100%;
    padding: 0.75rem 1rem;
    background: transparent;
    color: #c4c4cc;
    border: none;
    text-align: left;
    border-radius: 6px;
    cursor: pointer;
    margin-bottom: 0.5rem;
    font-size: 0.9rem;
    transition: background 0.2s, color 0.2s;
}

.module-btn:hover {
    background-color: #202024;
    color: #ffffff;
}

.card {
    background-color: #202024;
    padding: 2rem;
    border-radius: 8px;
    border: 1px solid #29292e;
    margin-bottom: 1.5rem;
}

.card h3 {
    margin-bottom: 1rem;
    color: #ffffff;
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
    margin-top: 1rem;
}

.stat-box {
    background-color: #121214;
    padding: 1rem;
    border-radius: 6px;
    border: 1px solid #323238;
    text-align: center;
}

.stat-box span {
    font-size: 1.25rem;
    font-weight: bold;
    color: #00b37e;
}
""",
    "frontend/index.html": """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Simulador Presidencial - Centro de Mando</title>
    <link rel="stylesheet" href="/static/styles/main.css">
</head>
<body>

    <div class="login-container" id="loginCard">
        <h1>🏛️ Academia Presidencial</h1>
        <p>Introduce tu clave de acceso de Seguridad de Estado</p>
        
        <form id="loginForm">
            <div class="input-group">
                <input type="password" id="passwordInput" placeholder="Contraseña..." required>
            </div>
            <button type="submit">Ingresar al Sistema</button>
        </form>
        
        <div id="errorMessage" class="error-message">Contraseña incorrecta. Acceso denegado.</div>
    </div>

    <div class="dashboard-container" id="dashboardContainer">
        <header>
            <h2>🏛️ Centro de Mando Presidencial</h2>
            <button onclick="logout()" style="width: auto; padding: 0.5rem 1rem; background-color: #f75a68;">Cerrar Sesión</button>
        </header>
        <div class="main-layout">
            <aside>
                <h3>Módulos de Gobierno</h3>
                <button class="module-btn" onclick="loadModule(1)">1. Macroeconomía y PYMEs</button>
                <button class="module-btn" onclick="loadModule(2)">2. Finanzas Públicas</button>
                <button class="module-btn" onclick="loadModule(3)">3. Escáner de Contratos</button>
                <button class="module-btn" onclick="loadModule(4)">4. Crisis Históricas</button>
                <button class="module-btn" onclick="loadModule(5)">5. Psicología Social</button>
                <button class="module-btn" onclick="loadModule(6)">6. Oratoria de Estado</button>
                <button class="module-btn" onclick="loadModule(7)">7. Microexpresiones</button>
                <button class="module-btn" onclick="loadModule(8)">8. Idiomas Extranjeros</button>
            </aside>
            <main id="contentArea" style="flex: 1; padding: 2rem; overflow-y: auto;">
                <div class="card">
                    <h3>Bienvenido, Señor Presidente</h3>
                    <p>Seleccione un módulo en el panel izquierdo para iniciar la capacitación ejecutiva o supervise los indicadores macroeconómicos actuales de la nación.</p>
                    <div class="stats-grid">
                        <div class="stat-box">Aprobación<br><span id="statApproval">50%</span></div>
                        <div class="stat-box">Inflación<br><span id="statInflation">4.5%</span></div>
                        <div class="stat-box">Déficit Fiscal<br><span id="statDeficit">2.0%</span></div>
                    </div>
                </div>
            </main>
        </div>
    </div>

    <script src="/static/scripts/app.js"></script>
</body>
</html>
""",
    "frontend/scripts/app.js": """document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const password = document.getElementById('passwordInput').value;
    const errorMessage = document.getElementById('errorMessage');

    try {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ password })
        });

        if (response.ok) {
            const data = await response.json();
            localStorage.setItem('presidential_token', data.token);
            showDashboard();
        } else {
            errorMessage.style.display = 'block';
        }
    } catch (err) {
        console.error('Error al conectar:', err);
        alert('Error de conexión con el servidor.');
    }
});

function showDashboard() {
    document.getElementById('loginCard').style.display = 'none';
    document.getElementById('dashboardContainer').style.display = 'flex';
    fetchSimulationState();
}

function logout() {
    localStorage.removeItem('presidential_token');
    location.reload();
}

async function fetchSimulationState() {
    try {
        const res = await fetch('/api/sim/state');
        if (res.ok) {
            const state = await res.json();
            document.getElementById('statApproval').innerText = state.approval_rate + '%';
            document.getElementById('statInflation').innerText = state.inflation_rate + '%';
            document.getElementById('statDeficit').innerText = state.fiscal_deficit + '%';
        }
    } catch (e) {
        console.error('Error al cargar estado', e);
    }
}

function loadModule(id) {
    const contentArea = document.getElementById('contentArea');
    contentArea.innerHTML = `
        <div class="card">
            <h3>Módulo Ejecutivo #${id} en Curso</h3>
            <p>Aquí se cargará la lección interactiva, los casos de estudio, análisis de contratos o simuladores correspondientes al pilar seleccionado con retroalimentación de IA en tiempo real.</p>
        </div>
    `;
}

window.onload = () => {
    if (localStorage.getItem('presidential_token')) {
        showDashboard();
    }
};
"""
}

for filepath, content in files_content.items():
    dirname = os.path.dirname(filepath)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

print("¡Archivos de despliegue en la nube generados con éxito!")