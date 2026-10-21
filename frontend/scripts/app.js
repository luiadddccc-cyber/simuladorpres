document.getElementById('loginForm').addEventListener('submit', async (e) => {
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
