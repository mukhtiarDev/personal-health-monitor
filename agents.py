import os
import database
import numpy as np

# Load thresholds from environment
HR_ANOMALY_THRESHOLD = float(os.getenv("HEART_RATE_ANOMALY_THRESHOLD", 120))
HR_CRITICAL_THRESHOLD = float(os.getenv("HEART_RATE_CRITICAL_THRESHOLD", 160))

class TrendAnalyzerAgent:
    """
    Analyzes new health metrics, logs findings, and requests approvals
    for critical anomalies (LRO).
    """
    def __init__(self):
        self.name = "TrendAnalyzerAgent"

    def run(self, db_conn):
        """Main execution method for the agent"""
        try:
            # 1. Get new data
            new_metrics = database.get_unprocessed_metrics(db_conn)
            if not new_metrics:
                return # No work to do
            
            print(f"[{self.name}] Found {len(new_metrics)} new metrics to analyze.")

            for metric in new_metrics:
                metric_id = metric['id']
                hr = metric['heart_rate']
                
                # 2. Long Memory Recall (Example)
                # An advanced version would query all historical data here
                # e.g., "SELECT AVG(heart_rate) FROM metrics WHERE strftime('%H', timestamp) = strftime('%H', ?)"
                # For this demo, we do stateless analysis.
                
                # 3. Analyze Data
                if hr >= HR_CRITICAL_THRESHOLD:
                    # 4.a. LRO / Human Approval Request
                    print(f"[{self.name}] CRITICAL anomaly detected! (HR: {hr}). Requesting approval.")
                    action_desc = (
                        f"CRITICAL: Heart rate at {hr:.1f} bpm detected. "
                        f"Recommend escalating to emergency contact/doctor."
                    )
                    database.create_approval_request(
                        conn=db_conn,
                        agent_name=self.name,
                        action_description=action_desc,
                        metric_id=metric_id,
                        priority='critical'
                    )
                    # Also log it
                    database.log_agent_action(db_conn, self.name, action_desc, 'critical')

                elif hr >= HR_ANOMALY_THRESHOLD:
                    # 4.b. Standard Anomaly Log
                    print(f"[{self.name}] WARNING anomaly detected. (HR: {hr}). Logging.")
                    msg = f"High heart rate detected: {hr:.1f} bpm. Recommend rest and monitoring."
                    database.log_agent_action(db_conn, self.name, msg, 'warning')
                
                # 5. Mark as processed
                database.mark_metric_processed(db_conn, metric_id)
        
        except Exception as e:
            print(f"[{self.name}] ERROR: {e}")

class EscalationAgent:
    """
    Acts on human-approved requests (A2A communication).
    """
    def __init__(self):
        self.name = "EscalationAgent"

    def run(self, db_conn):
        """Main execution method"""
        try:
            # 1. A2A: Read "approved" messages from the TrendAnalyzerAgent
            approved_requests = database.get_approved_requests(db_conn)
            if not approved_requests:
                return # No work to do

            print(f"[{self.name}] Found {len(approved_requests)} approved requests to escalate.")

            for req in approved_requests:
                # 2. Simulate Escalation
                print(f"[{self.name}] ESCALATING: Simulating email to doctor for approval {req['id']}...")
                
                # 3. Log the escalation
                log_msg = f"ACTION: Escalation approved by user. (Simulated email to doctor for: {req['action_description']})"
                database.log_agent_action(db_conn, self.name, log_msg, 'critical')
                
                # 4. Mark as processed
                database.update_approval_status(db_conn, req['id'], 'escalated')
        
        except Exception as e:
            print(f"[{self.name}] ERROR: {e}")