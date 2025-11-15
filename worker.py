import time
import os
import database
from agents import TrendAnalyzerAgent, EscalationAgent
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
WORKER_SLEEP_INTERVAL = int(os.getenv("WORKER_SLEEP_INTERVAL", 5))

def main_worker():
    """
    Main loop for the agent coordinator.
    Implements an MCP (Multi-Agent Coordinated Plan) as a sequential pipeline.
    """
    
    print("--- Starting Agent Worker (Process 2) ---")
    print(f"Database: {os.getenv('DB_FILE')}")
    print(f"Running agent loop every {WORKER_SLEEP_INTERVAL} seconds...")
    print("Press Ctrl+C to stop.")
    
    # Ensure DB is initialized
    database.init_db()
    
    db_conn = database.create_connection()
    if db_conn is None:
        print("Error! Cannot connect to database. Exiting.")
        return

    # Initialize agents
    trend_analyzer = TrendAnalyzerAgent()
    escalation_agent = EscalationAgent()

    try:
        while True:
            print(f"\n[{datetime.now().isoformat()}] WORKER: Starting agent cycle...")
            
            # --- MCP Phase 1: Analyze new data ---
            print(f"[{datetime.now().isoformat()}] WORKER: Running TrendAnalyzerAgent...")
            trend_analyzer.run(db_conn)
            
            # --- MCP Phase 2: Action approved escalations (A2A) ---
            print(f"[{datetime.now().isoformat()}] WORKER: Running EscalationAgent...")
            escalation_agent.run(db_conn)
            
            print(f"[{datetime.now().isoformat()}] WORKER: Cycle complete. Sleeping...")
            time.sleep(WORKER_SLEEP_INTERVAL)
            
    except KeyboardInterrupt:
        print("\nWORKER: Stopping agent worker...")
    finally:
        if db_conn:
            db_conn.close()
        print("WORKER: Agent worker shut down.")

if __name__ == "__main__":
    main_worker()