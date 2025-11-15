import time
import os
import database
import numpy as np
import random
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
SIMULATOR_SLEEP_INTERVAL = int(os.getenv("SIMULATOR_SLEEP_INTERVAL", 3))

def generate_health_data():
    """Generates a new health data point"""
    
    # Base normal heart rate
    heart_rate = np.random.normal(75, 10) 
    
    # 10% chance of an anomaly
    if random.random() < 0.1:
        heart_rate = np.random.normal(130, 5) # Anomaly
        
    # 5% chance of a critical anomaly
    if random.random() < 0.05:
        heart_rate = np.random.normal(165, 5) # Critical
        
    steps = random.randint(10, 50)
    
    return heart_rate, steps

def main_simulator():
    """Main loop for the data simulator"""
    
    print("--- Starting Health Data Simulator (Process 1) ---")
    print(f"Database: {os.getenv('DB_FILE')}")
    print(f"Simulating new data every {SIMULATOR_SLEEP_INTERVAL} seconds...")
    print("Press Ctrl+C to stop.")
    
    # Ensure DB is initialized
    database.init_db()
    
    db_conn = database.create_connection()
    if db_conn is None:
        print("Error! Cannot connect to database. Exiting.")
        return

    try:
        while True:
            hr, steps = generate_health_data()
            now = datetime.now()
            
            try:
                database.add_metric(db_conn, now, hr, steps)
                print(f"[{now.isoformat()}] SIM: Added metric - HR: {hr:.1f} bpm, Steps: {steps}")
            except Exception as e:
                print(f"SIM: Error writing to database: {e}")
            
            time.sleep(SIMULATOR_SLEEP_INTERVAL)
            
    except KeyboardInterrupt:
        print("\nSIM: Stopping simulator...")
    finally:
        if db_conn:
            db_conn.close()
        print("SIM: Simulator shut down.")

if __name__ == "__main__":
    main_simulator()