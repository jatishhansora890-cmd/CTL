import streamlit as st
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore
import json

# --- 1. FIREBASE SETUP ---
@st.cache_resource
def get_db():
    if not firebase_admin._apps:
        try:
            # This looks for the 'Secret' you added in Streamlit settings
            key_dict = json.loads(st.secrets["FIREBASE_KEY"])
            cred = credentials.Certificate(key_dict)
            firebase_admin.initialize_app(cred)
        except Exception as e:
            st.error(f"Database Config Missing: {e}")
            return None
    return firestore.client()

db = get_db()

# --- 2. APP UI ---
st.set_page_config(page_title="Slitting Tracker", layout="wide")
st.title("🏭 Slitting Machine Production Tracker")

if db is None:
    st.warning("Please add your FIREBASE_KEY in 'Advanced Settings > Secrets'.")
    st.stop()

tab_op, tab_admin = st.tabs(["Worker Interface", "Admin Dashboard"])

# --- ADMIN TAB ---
with tab_admin:
    st.header("Admin: Set Cutting Rules")
    with st.form("rule_form"):
        col1, col2 = st.columns(2)
        in_width = col1.number_input("Coil Width (mm)", min_value=0.0)
        out_size = col2.text_input("Allowed CTL Size (e.g. 767*1283)")
        if st.form_submit_button("SAVE RULE"):
            db.collection("rules").add({"coil_width": in_width, "ctl_size": out_size})
            st.success("Rule Saved!")

# --- WORKER TAB ---
with tab_op:
    st.header("1. Coil Intake")
    cam_image = st.camera_input("Scan Coil Tag")
    if cam_image:
        # Mock detection for prototype
        st.session_state.current_width = 776.0
        st.success(f"Detected Width: {st.session_state.current_width}mm")

    if 'current_width' in st.session_state:
        st.header("2. Production Entry")
        w = st.session_state.current_width
        rules = db.collection("rules").where("coil_width", "==", w).stream()
        options = [r.to_dict()['ctl_size'] for r in rules]
        
        if options:
            selected = st.selectbox("Select CTL Size", options)
            count = st.number_input("Production Count", min_value=1)
            if st.button("SUBMIT LOG"):
                db.collection("production_logs").add({
                    "timestamp": firestore.SERVER_TIMESTAMP,
                    "width": w,
                    "ctl_size": selected,
                    "count": count
                })
                st.success("Logged Successfully!")
        else:
            st.error(f"No rules found for {w}mm.")
