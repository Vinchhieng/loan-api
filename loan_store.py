"""SQLite-backed educational application workflow; every seeded profile is fictional."""
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone


def now():
    return datetime.now(timezone.utc).isoformat()


class LoanStore:
    def __init__(self, path):
        self.path = path
        with self.connection() as db:
            db.executescript('''
                CREATE TABLE IF NOT EXISTS borrowers (
                    id INTEGER PRIMARY KEY, province TEXT NOT NULL,
                    monthly_income_usd REAL NOT NULL, previous_loans INTEGER NOT NULL,
                    late_payments INTEGER NOT NULL);
                CREATE TABLE IF NOT EXISTS applications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    borrower_id INTEGER NOT NULL REFERENCES borrowers(id),
                    amount_usd INTEGER NOT NULL CHECK(amount_usd BETWEEN 100 AND 5000),
                    term_months INTEGER NOT NULL CHECK(term_months IN (3,6,12,18,24)),
                    status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending','approved','rejected')),
                    submitted_at TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS risk_predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    application_id INTEGER NOT NULL REFERENCES applications(id),
                    default_probability REAL NOT NULL, model_version TEXT NOT NULL,
                    created_at TEXT NOT NULL);
            ''')
            # Explicit demo enrichment supplies Module 5 inputs missing from the earlier SQL lesson.
            db.executemany('INSERT OR IGNORE INTO borrowers VALUES (?,?,?,?,?)', [
                (1, 'Battambang', 350.0, 1, 0), (2, 'Siem Reap', 550.0, 2, 0),
                (3, 'Battambang', 300.0, 1, 2), (4, 'Kampot', 600.0, 3, 0)])

    @contextmanager
    def connection(self):
        db = sqlite3.connect(self.path, timeout=10)
        db.row_factory = sqlite3.Row
        db.execute('PRAGMA foreign_keys=ON')
        try:
            with db:
                yield db
        finally:
            db.close()

    def borrower(self, borrower_id):
        with self.connection() as db:
            row = db.execute('SELECT * FROM borrowers WHERE id=?', (borrower_id,)).fetchone()
            return dict(row) if row else None

    def create(self, values):
        with self.connection() as db:
            cursor = db.execute('INSERT INTO applications (borrower_id, amount_usd, term_months, submitted_at) VALUES (?,?,?,?)',
                                (values['borrower_id'], values['amount_usd'], values['term_months'], now()))
            return dict(db.execute('SELECT * FROM applications WHERE id=?', (cursor.lastrowid,)).fetchone())

    def get(self, application_id):
        with self.connection() as db:
            row = db.execute('SELECT * FROM applications WHERE id=?', (application_id,)).fetchone()
            return dict(row) if row else None

    def list(self, limit, after=None, status=None, province=None, borrower_id=None):
        clauses, values = [], []
        for condition, value in [('a.id > ?', after), ('a.status = ?', status),
                                 ('b.province = ?', province), ('a.borrower_id = ?', borrower_id)]:
            if value is not None:
                clauses.append(condition)
                values.append(value)
        where = ' WHERE ' + ' AND '.join(clauses) if clauses else ''
        with self.connection() as db:
            rows = db.execute('SELECT a.* FROM applications a JOIN borrowers b ON a.borrower_id=b.id' +
                              where + ' ORDER BY a.id LIMIT ?', [*values, limit + 1]).fetchall()
            items = [dict(row) for row in rows[:limit]]
            return {'items': items, 'next_cursor': items[-1]['id'] if len(rows) > limit else None}

    def decide(self, application_id, status):
        with self.connection() as db:
            cursor = db.execute("UPDATE applications SET status=? WHERE id=? AND status='pending'", (status, application_id))
            row = db.execute('SELECT * FROM applications WHERE id=?', (application_id,)).fetchone()
            return cursor.rowcount, dict(row) if row else None

    def prediction(self, application_id, probability, version):
        with self.connection() as db:
            cursor = db.execute('INSERT INTO risk_predictions (application_id,default_probability,model_version,created_at) VALUES (?,?,?,?)',
                                (application_id, probability, version, now()))
            return dict(db.execute('SELECT * FROM risk_predictions WHERE id=?', (cursor.lastrowid,)).fetchone())
