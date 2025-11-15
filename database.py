import sqlite3
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
DB_FILE = os.getenv("DB_FILE", "health_data.db")

def create_connection():
    """ create a database connection to the SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE, check_same_thread=False) # Allow multi-process access
        conn.row_factory = sqlite3.Row # Enable dict-like row access
        return conn
    except sqlite3.Error as e:
        print(e)
    return conn

def init_db():
    """Initialize the database and create tables"""
    conn = create_connection()
    if conn is None:
        print("Error! cannot create the database connection.")
        return
        
    cursor = conn.cursor()
    
    # --- Metrics Table ---
    # Stores raw data from the simulator
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME NOT NULL,
        heart_rate REAL NOT NULL,
        steps INTEGER NOT NULL,
        status TEXT NOT NULL DEFAULT 'new' -- 'new', 'processed'
    );
    """)
    
    # --- Agent Log Table ---
    # Stores all agent actions for observability
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS agent_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME NOT NULL,
        agent_name TEXT NOT NULL,
        message TEXT NOT NULL,
        priority TEXT NOT NULL DEFAULT 'info' -- 'info', 'warning', 'critical'
    );
    """)
    
    # --- Approvals Table ---
    # Handles the LRO (Human-in-the-Loop) flow
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS approvals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME NOT NULL,
        agent_name TEXT NOT NULL,
        action_description TEXT NOT NULL,
        priority TEXT NOT NULL DEFAULT 'critical',
        metric_id INTEGER,
        status TEXT NOT NULL DEFAULT 'pending', -- 'pending', 'approved', 'rejected', 'escalated'
        FOREIGN KEY (metric_id) REFERENCES metrics (id)
    );
    """)
    
    conn.commit()
    conn.close()
    print(f"Database '{DB_FILE}' initialized successfully.")

# --- Functions to ADD data ---

def add_metric(conn, timestamp, heart_rate, steps):
    """Add a new metric reading from the simulator"""
    sql = ''' INSERT INTO metrics(timestamp, heart_rate, steps, status)
              VALUES(?,?,?,'new') '''
    cursor = conn.cursor()
    cursor.execute(sql, (timestamp, heart_rate, steps))
    conn.commit()
    return cursor.lastrowid

def log_agent_action(conn, agent_name, message, priority='info'):
    """Log an action taken by an agent"""
    sql = ''' INSERT INTO agent_log(timestamp, agent_name, message, priority)
              VALUES(?,?,?,?) '''
    cursor = conn.cursor()
    cursor.execute(sql, (datetime.now(), agent_name, message, priority))
    conn.commit()

def create_approval_request(conn, agent_name, action_description, metric_id, priority='critical'):
    """Create a new approval request for an LRO"""
    sql = ''' INSERT INTO approvals(timestamp, agent_name, action_description, metric_id, priority, status)
              VALUES(?,?,?,?,?,'pending') '''
    cursor = conn.cursor()
    cursor.execute(sql, (datetime.now(), agent_name, action_description, metric_id, priority))
    conn.commit()

# --- Functions to GET data ---

def get_unprocessed_metrics(conn):
    """Get all metrics that have not been analyzed yet"""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM metrics WHERE status = 'new' ORDER BY timestamp")
    return cursor.fetchall()

def get_recent_metrics_df(conn, limit=100):
    """Get recent metrics as a Pandas DataFrame for graphing"""
    try:
        import pandas as pd
        df = pd.read_sql_query(f"SELECT timestamp, heart_rate, steps FROM metrics ORDER BY timestamp DESC LIMIT {limit}", conn)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values(by='timestamp')
        return df.set_index('timestamp')
    except Exception as e:
        print(f"Error getting metrics as df: {e}")
        return pd.DataFrame(columns=['timestamp', 'heart_rate', 'steps']).set_index('timestamp')

def get_agent_logs_df(conn, limit=20):
    """Get recent agent logs as a Pandas DataFrame for display"""
    try:
        import pandas as pd
        df = pd.read_sql_query("SELECT timestamp, agent_name, message, priority FROM agent_log ORDER BY timestamp DESC LIMIT 20", conn)
        return df
    except Exception as e:
        print(f"Error getting logs as df: {e}")
        return pd.DataFrame(columns=['timestamp', 'agent_name', 'message', 'priority'])

def get_pending_approvals(conn):
    """Get all approvals that are 'pending'"""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM approvals WHERE status = 'pending' ORDER BY timestamp")
    return cursor.fetchall()

def get_approved_requests(conn):
    """Get all approvals that are 'approved' but not yet 'escalated'"""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM approvals WHERE status = 'approved' ORDER BY timestamp")
    return cursor.fetchall()

# --- Functions to UPDATE data ---

def mark_metric_processed(conn, metric_id):
    """Mark a metric as 'processed' after analysis"""
    sql = "UPDATE metrics SET status = 'processed' WHERE id = ?"
    cursor = conn.cursor()
    cursor.execute(sql, (metric_id,))
    conn.commit()

def update_approval_status(conn, approval_id, status):
    """Update the status of an approval request (e.g., 'approved', 'rejected', 'escalated')"""
    sql = "UPDATE approvals SET status = ? WHERE id = ?"
    cursor = conn.cursor()
    cursor.execute(sql, (status, approval_id))
    conn.commit()

if __name__ == '__main__':
    # This allows you to run `python database.py` once to create the file
    init_db()