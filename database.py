import sqlite3
from datetime import datetime
from typing import List, Tuple, Optional

class Database:
    def __init__(self, db_path: str = "service_hub.db"):
        self.db_path = db_path
        self._init_db()
    
    def _get_conn(self):
        return sqlite3.connect(self.db_path)
    
    def _init_db(self):
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS providers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                service_type TEXT NOT NULL,
                coverage_area TEXT NOT NULL,
                contact TEXT NOT NULL,
                reliability_score INTEGER DEFAULT 5
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_type TEXT NOT NULL,
                location TEXT NOT NULL,
                description TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                created_at TEXT NOT NULL
            )
        """)
        
        conn.commit()
        conn.close()
    
    def add_provider(self, name: str, service_type: str, coverage_area: str, contact: str) -> int:
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO providers (name, service_type, coverage_area, contact) VALUES (?, ?, ?, ?)",
            (name, service_type.lower(), coverage_area.lower(), contact)
        )
        provider_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return provider_id
    
    def get_providers(self, service_type: Optional[str] = None) -> List[Tuple]:
        conn = self._get_conn()
        cursor = conn.cursor()
        
        if service_type:
            cursor.execute(
                "SELECT * FROM providers WHERE service_type = ? ORDER BY reliability_score DESC",
                (service_type.lower(),)
            )
        else:
            cursor.execute("SELECT * FROM providers ORDER BY reliability_score DESC")
        
        providers = cursor.fetchall()
        conn.close()
        return providers
    
    def update_provider_reliability(self, provider_id: int, score: int):
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE providers SET reliability_score = ? WHERE id = ?",
            (score, provider_id)
        )
        conn.commit()
        conn.close()
    
    def add_lead(self, service_type: str, location: str, description: str) -> int:
        conn = self._get_conn()
        cursor = conn.cursor()
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO leads (service_type, location, description, created_at) VALUES (?, ?, ?, ?)",
            (service_type.lower(), location.lower(), description, created_at)
        )
        lead_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return lead_id
    
    def get_leads(self, status: str = "pending") -> List[Tuple]:
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM leads WHERE status = ? ORDER BY created_at DESC",
            (status,)
        )
        leads = cursor.fetchall()
        conn.close()
        return leads
    
    def match_lead(self, lead_id: int) -> List[Tuple]:
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute("SELECT service_type, location FROM leads WHERE id = ?", (lead_id,))
        lead = cursor.fetchone()
        
        if not lead:
            conn.close()
            return []
        
        service_type, location = lead
        
        cursor.execute(
            """SELECT id, name, reliability_score, contact 
               FROM providers 
               WHERE service_type = ? AND coverage_area LIKE ?
               ORDER BY reliability_score DESC""",
            (service_type, f"%{location}%")
        )
        
        matches = cursor.fetchall()
        
        if matches:
            cursor.execute("UPDATE leads SET status = 'matched' WHERE id = ?", (lead_id,))
            conn.commit()
        
        conn.close()
        return matches
    
    def update_lead_status(self, lead_id: int, status: str):
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("UPDATE leads SET status = ? WHERE id = ?", (status, lead_id))
        conn.commit()
        conn.close()
    
    def get_stats(self) -> dict:
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM providers")
        providers = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM leads")
        leads = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM leads WHERE status = 'pending'")
        pending_leads = cursor.fetchone()[0]
        
        cursor.execute("SELECT AVG(reliability_score) FROM providers")
        avg_reliability = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            "providers": providers,
            "leads": leads,
            "pending_leads": pending_leads,
            "avg_reliability": avg_reliability
        }
