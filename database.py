"""MySQL persistence layer for the Job Application Tracker.

Table and column names come only from server-side constants. User values are always
passed as query parameters; MySQL passwords belong in .env, never in source control.
"""

import os
from contextlib import contextmanager

import mysql.connector
from dotenv import load_dotenv

load_dotenv()

DB_NAME = os.getenv("DB_NAME", "job_tracker")

# Whitelists make dynamic CRUD safe: never accept arbitrary SQL identifiers.
TABLES = {
    "companies": {
        "id": "company_id",
        "columns": ["company_name", "industry", "city", "state", "website", "notes"],
        "listing": "SELECT * FROM companies ORDER BY company_name, company_id",
    },
    "jobs": {
        "id": "job_id",
        "columns": ["company_id", "job_title", "job_type", "salary_min", "salary_max",
                    "location", "description", "source_url", "requirements"],
        "listing": """SELECT j.*, c.company_name
                       FROM jobs j JOIN companies c ON c.company_id = j.company_id
                       ORDER BY j.job_id DESC""",
    },
    "applications": {
        "id": "application_id",
        "columns": ["job_id", "application_date", "status", "resume_version",
                    "cover_letter_sent", "follow_up_date", "notes", "interview_data"],
        "listing": """SELECT a.*, j.job_title, c.company_name
                       FROM applications a
                       JOIN jobs j ON j.job_id = a.job_id
                       JOIN companies c ON c.company_id = j.company_id
                       ORDER BY a.application_date DESC, a.application_id DESC""",
    },
    "contacts": {
        "id": "contact_id",
        "columns": ["company_id", "first_name", "last_name", "email", "phone", "job_title", "notes"],
        "listing": """SELECT t.*, c.company_name
                       FROM contacts t JOIN companies c ON c.company_id = t.company_id
                       ORDER BY t.contact_id DESC""",
    },
}


@contextmanager
def connection():
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=DB_NAME,
    )
    try:
        yield conn
    finally:
        conn.close()


def query(sql, params=(), *, one=False):
    with connection() as conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(sql, params)
            return cursor.fetchone() if one else cursor.fetchall()
        finally:
            cursor.close()


def write(sql, params=()):
    with connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(sql, params)
            conn.commit()
            return cursor.lastrowid if sql.lstrip().upper().startswith("INSERT") else cursor.rowcount
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()


def list_items(resource):
    return query(TABLES[resource]["listing"])


def get_item(resource, item_id):
    info = TABLES[resource]
    return query(f"SELECT * FROM {resource} WHERE {info['id']} = %s", (item_id,), one=True)


def create_item(resource, values):
    columns = [c for c in TABLES[resource]["columns"] if c in values]
    placeholders = ", ".join(["%s"] * len(columns))
    sql = f"INSERT INTO {resource} ({', '.join(columns)}) VALUES ({placeholders})"
    return write(sql, tuple(values[c] for c in columns))


def update_item(resource, item_id, values):
    columns = [c for c in TABLES[resource]["columns"] if c in values]
    sql = f"UPDATE {resource} SET {', '.join(c + ' = %s' for c in columns)} WHERE {TABLES[resource]['id']} = %s"
    return write(sql, tuple(values[c] for c in columns) + (item_id,))


def delete_item(resource, item_id):
    return write(f"DELETE FROM {resource} WHERE {TABLES[resource]['id']} = %s", (item_id,))


def selectable_companies():
    return query("SELECT company_id AS id, company_name AS title FROM companies ORDER BY company_name")


def selectable_jobs():
    return query("""SELECT j.job_id AS id, CONCAT(c.company_name, ' — ', j.job_title) AS title
                    FROM jobs j JOIN companies c ON c.company_id = j.company_id
                    ORDER BY c.company_name, j.job_title""")


def dashboard_data():
    stats = {}
    for table in TABLES:
        stats[table] = query(f"SELECT COUNT(*) AS total FROM {table}", one=True)["total"]
    recent = query("""SELECT a.application_id, a.application_date, a.status,
                             j.job_title, c.company_name
                      FROM applications a
                      JOIN jobs j ON j.job_id = a.job_id
                      JOIN companies c ON c.company_id = j.company_id
                      ORDER BY a.application_date DESC, a.application_id DESC LIMIT 8""")
    return stats, recent
