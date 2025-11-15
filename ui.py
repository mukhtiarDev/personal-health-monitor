import streamlit as st
import database
import time
from datetime import datetime

# --- Page Config ---
st.set_page_config(
    page_title="Personal Health Monitor",
    page_icon="❤️",
    layout="wide"
)

# --- Database Connection ---
# Use a session-wide connection
@st.cache_resource
def get_db_connection():
    return database.create_connection()

conn = get_db_connection()

# --- Page Title ---
st.title("❤️ Personal Health Monitoring System")
st.caption(f"Live dashboard connected to `{database.DB_FILE}`. Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# --- Main Layout ---
col_metrics, col_actions = st.columns([2, 1])

with col_metrics:
    st.header("📈 Live Metrics")
    st.markdown("This chart shows the most recent health data being fed by the `simulator.py`.")
    
    # --- Live Metrics Chart ---
    chart_placeholder = st.empty()
    
    try:
        metrics_df = database.get_recent_metrics_df(conn, limit=100)
        if not metrics_df.empty:
            st.line_chart(metrics_df['heart_rate'], use_container_width=True)
        else:
            st.info("Waiting for data from simulator...")
    except Exception as e:
        st.error(f"Could not load chart: {e}")

    st.subheader("Raw Data Table (Last 10)")
    try:
        logs_df_raw = database.get_recent_metrics_df(conn, limit=10)
        st.dataframe(logs_df_raw.sort_index(ascending=False), use_container_width=True)
    except Exception as e:
        st.error(f"Could not load raw data: {e}")


with col_actions:
    st.header("🤖 Agent Dashboard")

    # --- Pending Approvals (LRO) ---
    st.subheader("⚠️ Pending Approvals (LRO)")
    st.markdown("Agents require your approval for critical actions (from `worker.py`).")
    
    pending_approvals = database.get_pending_approvals(conn)
    
    if not pending_approvals:
        st.success("No pending approvals. All systems normal.")
    
    for item in pending_approvals:
        item_id = item['id']
        with st.container(border=True):
            st.error(f"**Action Required:** {item['action_description']}")
            st.caption(f"Agent: {item['agent_name']} | Time: {item['timestamp']}")
            
            c1, c2 = st.columns(2)
            with c1:
                if st.button(f"Approve (ID: {item_id})", key=f"approve_{item_id}", use_container_width=True, type="primary"):
                    database.update_approval_status(conn, item_id, 'approved')
                    st.toast(f"Approved request {item_id}!")
                    st.rerun() # Force UI refresh
            with c2:
                if st.button(f"Reject (ID: {item_id})", key=f"reject_{item_id}", use_container_width=True):
                    database.update_approval_status(conn, item_id, 'rejected')
                    st.toast(f"Rejected request {item_id}!")
                    st.rerun() # Force UI refresh

    # --- Agent Log (Observability) ---
    st.subheader("📄 Agent Log (Observability)")
    st.markdown("Live log of all actions taken by agents in `worker.py`.")
    
    log_placeholder = st.empty()
    try:
        logs_df = database.get_agent_logs_df(conn, limit=20)
        log_placeholder.dataframe(logs_df, use_container_width=True, height=400)
    except Exception as e:
        log_placeholder.error(f"Could not load agent logs: {e}")


# --- Auto-Refresh ---
# This re-runs the script from top to bottom every 5 seconds
st.rerun(ttl=5)