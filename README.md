Personal Health Monitoring System (Multi-Agent)

This project is a real-time, multi-agent system for monitoring personal health data. It simulates collecting data from a wearable, having AI agents analyze it, and presenting it on a live dashboard with a human-in-the-loop approval system.

Project Features

Real-Time Simulation: Three separate processes run concurrently: a data simulator, an agent worker, and a UI dashboard.

A2A Communication: Agents communicate asynchronously using a SQLite database as a message queue (e.g., TrendAnalyzer creates an approval row, which EscalationAgent reads).

MCP (Coordinated Plan): The worker.py implements a sequential pipeline (a form of round-robin), running the TrendAnalyzer first, then the EscalationAgent.

LRO with Human Approval: The TrendAnalyzer detects critical anomalies (e.g., heart rate > 160) and creates an approval request. This request appears on the dashboard, and a human user must click "Approve" before the EscalationAgent (simulates) contacting a doctor.

Long Memory Recall: The TrendAnalyzer can query the entire history of the metrics table in the SQLite database to identify long-term trends.

Observability: A Streamlit dashboard shows live graphs of metrics, a real-time log of all agent actions, and a list of pending approvals.

File Structure

/personal-health-monitor/
├── .env
├── requirements.txt
├── database.py         # Handles all SQLite database setup and functions
├── agents.py           # Contains the logic for each agent
├── simulator.py        # Process 1: The "wearable" data feed
├── worker.py           # Process 2: The "agent brain" coordinator
└── ui.py               # Process 3: The Streamlit dashboard


Setup Instructions

Create Project Folder: Create a new folder named personal-health-monitor.

Create Files: Inside that folder, create all the files listed above (.env, requirements.txt, database.py, agents.py, simulator.py, worker.py, ui.py) and copy-paste their contents from the provided code.

Create Python Environment (Recommended):

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate


Install Dependencies:

pip install -r requirements.txt


How to Run (The "Real-Time" Part)

You must run three separate terminals (or Command Prompts) at the same time.

Terminal 1: Run the Data Simulator

This script acts as your "smart watch," feeding new data into the system every 3 seconds.

python simulator.py


You will see it print messages like "SIM: Added metric..."

Terminal 2: Run the Agent Worker

This script is the "brain" of the operation. It runs the agents in a loop, watching for new data to analyze.

python worker.py


You will see it print messages like "WORKER: Running TrendAnalyzerAgent..."

Terminal 3: Run the Streamlit UI

This script launches the web dashboard.

streamlit run ui.py


This will automatically open the dashboard in your web browser. The dashboard will auto-refresh every 5 seconds.

You can now interact with the system:

Watch the "Live Metrics" graph update as the Simulator adds data.

Watch the "Agent Log" update as the Worker analyzes the data.

When a critical alert happens (e.g., heart rate > 160), watch an item appear in "Pending Approvals."

Click the "Approve" button, and you will see the Worker log that the EscalationAgent has (simulated) contacting a doctor.
