from fastapi import APIRouter
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
