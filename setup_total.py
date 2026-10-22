import os

# Definición de la estructura de archivos y contenidos completos del proyecto
files_content = {
    # -------------------------------------------------------------------------
    # 1. BASE DE DATOS Y ESQUEMA
    # -------------------------------------------------------------------------
    "backend/base_de_datos/schema.sql": """
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS metricas_presidenciales (
    user_id INTEGER PRIMARY KEY,
    aprobacion_popular REAL DEFAULT 50.0,
    salud_economica REAL DEFAULT 50.0,
    gobernabilidad_congreso REAL DEFAULT 50.0,
    control_corrupcion REAL DEFAULT 50.0,
    FOREIGN KEY(user_id) REFERENCES usuarios(id)
);
""",

    "backend/base_de_datos/connection.py": """
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "../../simulador.db")

def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    with open(schema_path, "r", encoding="utf-8") as f:
        cursor.executescript(f.read())
    conn.commit()
    conn.close()
""",

    # -------------------------------------------------------------------------
    # 2. RUTAS DE AUTENTICACIÓN
    # -------------------------------------------------------------------------
    "backend/rutas/auth.py": """
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
import sqlite3
from backend.base_de_datos.connection import get_db

router = APIRouter()

class UserAuth(BaseModel):
    usuario: str
    password: str

@router.post("/register")
def register(user: UserAuth, db=Depends(get_db)):
    cursor = db.cursor()
    try:
        cursor.execute("INSERT INTO usuarios (usuario, password) VALUES (?, ?)", (user.usuario, user.password))
        db.commit()
        user_id = cursor.lastrowid
        # Inicializar métricas para el nuevo usuario
        cursor.execute("INSERT INTO metricas_presidenciales (user_id) VALUES (?)", (user_id,))
        db.commit()
        return {"mensaje": "Usuario registrado exitosamente", "user_id": user_id}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="El nombre de usuario ya existe")

@router.post("/login")
def login(user: UserAuth, db=Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT id, password FROM usuarios WHERE usuario = ?", (user.usuario,))
    row = cursor.fetchone()
    if not row or row[1] != user.password:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    
    user_id = row[0]
    # Verificar que existan sus métricas
    cursor.execute("SELECT user_id FROM metricas_presidenciales WHERE user_id = ?", (user_id,))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO metricas_presidenciales (user_id) VALUES (?)", (user_id,))
        db.commit()

    return {"mensaje": "Inicio de sesión exitoso", "token": f"token_presidencial_{user_id}", "user_id": user_id}
""",

    # -------------------------------------------------------------------------
    # 3. RUTAS DE SIMULACIÓN Y MÉTRICAS VIVAS
    # -------------------------------------------------------------------------
    "backend/rutas/simulation.py": """
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from backend.base_de_datos.connection import get_db

router = APIRouter()

class OpcionDecision(BaseModel):
    user_id: int
    delta_aprobacion: float
    delta_economia: float
    delta_congreso: float
    delta_corrupcion: float

@router.get("/modulos")
def get_modulos():
    return [
        {"id": 1, "nombre": "1. Macroeconomía y PYMEs", "descripcion": "Gestión de inflación, empleo, gasto público e incentivos a pequeñas y medianas empresas."},
        {"id": 2, "nombre": "2. Finanzas Públicas", "descripcion": "Presupuesto nacional, deuda soberana, política tributaria y equilibrio fiscal."},
        {"id": 3, "nombre": "3. Escáner de Contratos", "descripcion": "Auditoría de licitaciones públicas, análisis documental y prevención de sobreprecio."},
        {"id": 4, "nombre": "4. Crisis Históricas", "descripcion": "Simulación táctica de contingencias pasadas y toma de decisiones bajo alta presión."},
        {"id": 5, "nombre": "5. Psicología Social", "descripcion": "Comprensión del comportamiento colectivo, opinión pública y cohesión social."},
        {"id": 6, "nombre": "6. Oratoria de Estado", "descripcion": "Estrategias de comunicación gubernamental, discursos solemnes y debates clave."},
        {"id": 7, "nombre": "7. Microexpresiones", "descripcion": "Análisis no verbal para la detección de incongruencias en reuniones diplomáticas o ministeriales."},
        {"id": 8, "nombre": "8. Idiomas Extranjeros", "descripcion": "Terminología geopolítica, negociación multilateral y diplomacia internacional."}
    ]

@router.get("/metricas/{user_id}")
def obtener_metricas(user_id: int, db=Depends(get_db)):
    cursor = db.cursor()
    cursor.execute(
        "SELECT aprobacion_popular, salud_economica, gobernabilidad_congreso, control_corrupcion FROM metricas_presidenciales WHERE user_id = ?", 
        (user_id,)
    )
    row = cursor.fetchone()
    
    if not row:
        cursor.execute("INSERT INTO metricas_presidenciales (user_id) VALUES (?)", (user_id,))
        db.commit()
        return {"aprobacion": 50.0, "economia": 50.0, "congreso": 50.0, "corrupcion": 50.0}
        
    return {
        "aprobacion": row[0],
        "economia": row[1],
        "congreso": row[2],
        "corrupcion": row[3]
    }

@router.post("/metricas/impacto")
def aplicar_impacto(decision: OpcionDecision, db=Depends(get_db)):
    cursor = db.cursor()
    cursor.execute(
        "SELECT aprobacion_popular, salud_economica, gobernabilidad_congreso, control_corrupcion FROM metricas_presidenciales WHERE user_id = ?", 
        (decision.user_id,)
    )
    actual = cursor.fetchone()
    
    if not actual:
        cursor.execute("INSERT INTO metricas_presidenciales (user_id) VALUES (?)", (decision.user_id,))
        db.commit()
        actual = (50.0, 50.0, 50.0, 50.0)

    # Limitar las métricas para que no bajen de 0% ni suban de 100%
    nueva_aprobacion = max(0.0, min(100.0, actual[0] + decision.delta_aprobacion))
    nueva_economia = max(0.0, min(100.0, actual[1] + decision.delta_economia))
    nuevo_congreso = max(0.0, min(100.0, actual[2] + decision.delta_congreso))
    nuevo_corrupcion = max(0.0, min(100.0, actual[3] + decision.delta_corrupcion))

    cursor.execute(\"\"\"
        UPDATE metricas_presidenciales 
        SET aprobacion_popular = ?, salud_economica = ?, gobernabilidad_congreso = ?, control_corrupcion = ?
        WHERE user_id = ?
    \"\"\", (nueva_aprobacion, nueva_economia, nuevo_congreso, nuevo_corrupcion, decision.user_id))
    db.commit()

    return {
        "mensaje": "Métricas actualizadas",
        "metricas": {
            "aprobacion": nueva_aprobacion,
            "economia": nueva_economia,
            "congreso": nuevo_congreso,
            "corrupcion": nuevo_corrupcion
        }
    }
""",

    # -------------------------------------------------------------------------
    # 4. APLICACIÓN PRINCIPAL (FASTAPI)
    # -------------------------------------------------------------------------
    "backend/app.py": """
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from backend.base_de_datos.connection import init_db
from backend.rutas.auth import router as auth_router
from backend.rutas.simulation import router as sim_router

app = FastAPI(title="Simulador de Entrenamiento Presidencial")

# Inicializar Base de Datos al arrancar
@app.on_event("startup")
def startup_event():
    init_db()

# Incluir Rutas
app.include_router(auth_router, prefix="/api/auth", tags=["Autenticación"])
app.include_router(sim_router, prefix="/api/simulation", tags=["Simulación"])

# Servir Frontend
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "../frontend")
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

@app.get("/")
def read_root():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))
""",

    # -------------------------------------------------------------------------
    # 5. VISTA FRONTEND (HTML) CON TABLERO HUD DE MÉTRICAS
    # -------------------------------------------------------------------------
    "frontend/index.html": """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Simulador de Entrenamiento Presidencial</title>
    <link rel="stylesheet" href="/static/estilos/main.css">
</head>
<body>
    <div id="auth-screen" class="auth-container">
        <div class="auth-box">
            <h2>🏛️ Acceso Presidencial</h2>
            <input type="text" id="username" placeholder="Usuario de Estado">
            <input type="password" id="password" placeholder="Clave de Seguridad">
            <div class="auth-buttons">
                <button onclick="login()">Ingresar</button>
                <button onclick="register()" class="btn-secondary">Registrar Credenciales</button>
            </div>
            <p id="auth-error" class="error-msg"></p>
        </div>
    </div>

    <div id="dashboard-screen" class="dashboard-container" style="display: none;">
        <header class="header">
            <h1>🏛️ Centro de Mando Presidencial</h1>
            <button onclick="logout()" class="btn-logout">Cerrar Sesión</button>
        </header>

        <!-- BARRA FLOTANTE HUD DE MÉTRICAS VIVAS -->
        <div id="hud-presidencial" class="hud-container">
            <div class="metric-card">
                <span class="metric-label">👥 Aprobación Popular</span>
                <div class="progress-bar"><div id="bar-aprobacion" style="width: 50%;"></div></div>
                <span id="val-aprobacion" class="metric-value">50%</span>
            </div>
            <div class="metric-card">
                <span class="metric-label">📈 Salud Económica</span>
                <div class="progress-bar"><div id="bar-economia" style="width: 50%;"></div></div>
                <span id="val-economia" class="metric-value">50%</span>
            </div>
            <div class="metric-card">
                <span class="metric-label">🏛️ Apoyo Congreso</span>
                <div class="progress-bar"><div id="bar-congreso" style="width: 50%;"></div></div>
                <span id="val-congreso" class="metric-value">50%</span>
            </div>
            <div class="metric-card">
                <span class="metric-label">🔍 Control Corrupción</span>
                <div class="progress-bar"><div id="bar-corrupcion" style="width: 50%;"></div></div>
                <span id="val-corrupcion" class="metric-value">50%</span>
            </div>
        </div>

        <div class="main-layout">
            <aside class="sidebar">
                <h3>MÓDULOS DE GOBIERNO</h3>
                <ul id="modulos-list"></ul>
            </aside>
            <main class="content-area" id="content-area">
                <div class="card">
                    <h3>Seleccione un Módulo Presidencial</h3>
                    <p>Cargue las lecciones interactivas, casos de estudio y simulaciones dinámicas para comenzar.</p>
                </div>
            </main>
        </div>
    </div>

    <script src="/static/scripts/app.js"></script>
</body>
</html>
""",

    # -------------------------------------------------------------------------
    # 6. ESTILOS CSS CON TEMA OSCURO
    # -------------------------------------------------------------------------
    "frontend/estilos/main.css": """
* { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
body { background-color: #0f1216; color: #e2e8f0; }

/* Autenticación */
.auth-container { display: flex; justify-content: center; align-items: center; height: 100vh; background-color: #0b0d10; }
.auth-box { background-color: #1a1e24; padding: 40px; border-radius: 8px; border: 1px solid #2a313d; width: 360px; text-align: center; }
.auth-box h2 { margin-bottom: 20px; color: #319795; }
.auth-box input { width: 100%; padding: 12px; margin: 10px 0; background-color: #0f1216; border: 1px solid #2a313d; color: white; border-radius: 4px; }
.auth-buttons { display: flex; gap: 10px; margin-top: 15px; }
button { flex: 1; padding: 10px; background-color: #319795; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; }
button:hover { background-color: #2c7a7b; }
.btn-secondary { background-color: #4a5568; }
.btn-secondary:hover { background-color: #2d3748; }
.error-msg { color: #e53e3e; font-size: 0.85rem; margin-top: 10px; }

/* Dashboard */
.dashboard-container { padding: 20px; max-width: 1400px; margin: 0 auto; }
.header { display: flex; justify-content: space-between; align-items: center; padding-bottom: 15px; border-bottom: 1px solid #2a313d; margin-bottom: 15px; }
.header h1 { color: #319795; font-size: 1.5rem; }
.btn-logout { background-color: #e53e3e; width: auto; padding: 8px 16px; }

/* HUD de Métricas Presidenciales */
.hud-container { display: flex; justify-content: space-around; background-color: #1a1e24; border: 1px solid #2a313d; border-radius: 8px; padding: 12px; margin-bottom: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.3); }
.metric-card { display: flex; flex-direction: column; align-items: center; width: 22%; }
.metric-label { font-size: 0.85rem; color: #a0aec0; margin-bottom: 6px; }
.progress-bar { width: 100%; height: 10px; background-color: #2d3748; border-radius: 5px; overflow: hidden; }
.progress-bar div { height: 100%; background-color: #319795; transition: width 0.5s ease-in-out; }
.metric-value { font-size: 0.9rem; font-weight: bold; color: #e2e8f0; margin-top: 4px; }

/* Layout */
.main-layout { display: flex; gap: 20px; }
.sidebar { width: 300px; background-color: #1a1e24; padding: 20px; border-radius: 8px; border: 1px solid #2a313d; }
.sidebar h3 { font-size: 0.9rem; color: #718096; margin-bottom: 15px; }
.sidebar ul { list-style: none; }
.sidebar li { padding: 12px; border-radius: 4px; margin-bottom: 8px; cursor: pointer; background-color: #0f1216; border: 1px solid #2a313d; font-size: 0.95rem; }
.sidebar li:hover { border-color: #319795; color: #319795; }
.content-area { flex: 1; }
.card { background-color: #1a1e24; padding: 25px; border-radius: 8px; border: 1px solid #2a313d; }
.card h3 { color: #319795; margin-bottom: 10px; }
""",

    # -------------------------------------------------------------------------
    # 7. LOGICA DE INTERACCIÓN EN EL CLIENTE (JAVASCRIPT)
    # -------------------------------------------------------------------------
    "frontend/scripts/app.js": """
let currentUserId = null;

async function login() {
    const u = document.getElementById('username').value;
    const p = document.getElementById('password').value;
    const err = document.getElementById('auth-error');
    err.innerText = '';
    
    try {
        const res = await fetch('/api/auth/login', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({usuario: u, password: p})
        });
        const data = await res.json();
        if(!res.ok) throw new Error(data.detail || 'Error de autenticación');
        
        localStorage.setItem('presidential_token', data.token);
        localStorage.setItem('presidential_user_id', data.user_id);
        currentUserId = data.user_id;
        
        showDashboard();
    } catch(e) {
        err.innerText = e.message;
    }
}

async function register() {
    const u = document.getElementById('username').value;
    const p = document.getElementById('password').value;
    const err = document.getElementById('auth-error');
    err.innerText = '';

    try {
        const res = await fetch('/api/auth/register', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({usuario: u, password: p})
        });
        const data = await res.json();
        if(!res.ok) throw new Error(data.detail || 'Error al registrar');
        alert('Registro exitoso. Inicie sesión.');
    } catch(e) {
        err.innerText = e.message;
    }
}

function logout() {
    localStorage.removeItem('presidential_token');
    localStorage.removeItem('presidential_user_id');
    document.getElementById('dashboard-screen').style.display = 'none';
    document.getElementById('auth-screen').style.display = 'flex';
}

function showDashboard() {
    document.getElementById('auth-screen').style.display = 'none';
    document.getElementById('dashboard-screen').style.display = 'block';
    currentUserId = localStorage.getItem('presidential_user_id');
    loadMetrics();
    loadModulos();
}

async function loadMetrics() {
    if(!currentUserId) return;
    try {
        const res = await fetch(`/api/simulation/metricas/${currentUserId}`);
        const data = await res.json();
        
        updateMetricBar('aprobacion', data.aprobacion);
        updateMetricBar('economia', data.economia);
        updateMetricBar('congreso', data.congreso);
        updateMetricBar('corrupcion', data.corrupcion);
    } catch(e) {
        console.error('Error cargando métricas:', e);
    }
}

function updateMetricBar(metricKey, value) {
    const valRounded = Math.round(value);
    const bar = document.getElementById(`bar-${metricKey}`);
    const valText = document.getElementById(`val-${metricKey}`);
    if(bar && valText) {
        bar.style.width = `${valRounded}%`;
        valText.innerText = `${valRounded}%`;
        
        // Cambiar color de barra según rendimiento
        if(valRounded < 30) {
            bar.style.backgroundColor = '#e53e3e'; // Rojo (Crítico)
        } else if(valRounded < 60) {
            bar.style.backgroundColor = '#dd6b20'; // Naranja (Atención)
        } else {
            bar.style.backgroundColor = '#319795'; // Verde Presidencial (Estable)
        }
    }
}

async function loadModulos() {
    try {
        const res = await fetch('/api/simulation/modulos');
        const modulos = await res.json();
        const list = document.getElementById('modulos-list');
        list.innerHTML = '';
        
        modulos.forEach(m => {
            const li = document.createElement('li');
            li.innerText = m.nombre;
            li.onclick = () => selectModulo(m);
            list.appendChild(li);
        });
    } catch(e) {
        console.error('Error cargando módulos:', e);
    }
}

function selectModulo(m) {
    const area = document.getElementById('content-area');
    area.innerHTML = `
        <div class="card">
            <h3>${m.nombre} en Curso</h3>
            <p>${m.descripcion}</p>
            <br>
            <hr style="border-color: #2a313d;"><br>
            <h4>Simulador Táctico de Decisiones</h4>
            <p style="font-size: 0.9rem; color: #a0aec0; margin-top: 5px;">Tome una medida de gobierno para observar el impacto directo en las métricas de Estado:</p>
            <br>
            <button onclick="tomarDecision(5, -5, -2, 0)">Tomar Medida Popular (+5% Aprobación, -5% Economía)</button>
            <button onclick="tomarDecision(-8, 10, 5, 0)" class="btn-secondary" style="margin-left: 10px;">Aplicar Ajuste Fiscal (-8% Aprobación, +10% Economía)</button>
        </div>
    `;
}

async function tomarDecision(dA, dE, dC, dCorr) {
    if(!currentUserId) return;
    try {
        const res = await fetch('/api/simulation/metricas/impacto', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                user_id: parseInt(currentUserId),
                delta_aprobacion: dA,
                delta_economia: dE,
                delta_congreso: dC,
                delta_corrupcion: dCorr
            })
        });
        const data = await res.json();
        if(res.ok) {
            loadMetrics(); // Recargar barras con animación inmediata
        }
    } catch(e) {
        console.error('Error aplicando decisión:', e);
    }
}

window.onload = () => {
    if (localStorage.getItem('presidential_token')) {
        showDashboard();
    }
};
""",

    # -------------------------------------------------------------------------
    # 8. ARCHIVOS DE DESPLIEGUE Y DEPENDENCIAS
    # -------------------------------------------------------------------------
    "requirements.txt": """fastapi==0.110.0
uvicorn==0.28.0
pydantic==2.6.4
""",

    "Procfile": "web: uvicorn backend.app:app --host 0.0.0.0 --port \$PORT",

    "render.yaml": """
services:
  - type: web
    name: simuladorpres
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn backend.app:app --host 0.0.0.0 --port \$PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.10.0
""",

    "README.md": "# Simulador de Entrenamiento Presidencial\nPlataforma de alta dirección de Estado con simulación de métricas en tiempo real."
}

# Ejecución para escribir los archivos en disco
for filepath, content in files_content.items():
    dirname = os.path.dirname(filepath)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

print("¡Archivos de actualización generados con éxito!")
