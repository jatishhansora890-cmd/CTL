import streamlit as st
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore
import json

# 1. Database Connection (Secure)
@st.cache_resource
def get_db():
    if not firebase_admin._apps:
        try:
            # Vercel will look for this in its Environment Variables
            key_dict = json.loads(st.secrets["FIREBASE_KEY"])
            cred = credentials.Certificate(key_dict)
            firebase_admin.initialize_app(cred)
        except Exception as e:
            st.error(f"Database Error: {e}")
            return None
    return firestore.client()

db = get_db()

st.set_page_config(page_title="Slitting Tracker", layout="wide")
st.title("🏭 Slitting Machine Production Tracker")

if db is None:
    st.warning("Awaiting database credentials...")
    st.stop()

tab_worker, tab_admin = st.tabs(["Worker Interface", "Admin Dashboard"])

# --- ADMIN: Master Data ---
with tab_admin:
    st.header("Admin: Set Cutting Rules")
    with st.form("add_rule"):
        col1, col2 = st.columns(2)
        in_w = col1.number_input("Coil Width (mm)", min_value=0.0)
        out_s = col2.text_input("Allowed CTL Size (e.g. 767*1283 mm)")
        if st.form_submit_button("Save Rule"):
            db.collection("rules").add({"coil_width": in_w, "ctl_size": out_s})
            st.success(f"Saved: {in_w}mm -> {out_s}")

# --- WORKER: Shop Floor Logic ---
with tab_worker:
    st.header("1. Coil Intake")
    cam = st.camera_input("Scan Tag")
    if cam:
        # Prototype Mock: In future, we add OCR here
        st.session_state.detected_w = 776.0
        st.info(f"Detected: {st.session_state.detected_w} mm")

    if 'detected_w' in st.session_state:
        st.header("2. Production Entry")
        w = st.session_state.detected_w
        rules = db.collection("rules").where("coil_width", "==", w).stream()
        options = [r.to_dict()['ctl_size'] for r in rules]
        
        if options:
            sel = st.selectbox("Select CTL Size", options)
            qty = st.number_input("Count", min_value=1)
            if st.button("Log Production"):
                db.collection("production_logs").add({
                    "timestamp": firestore.SERVER_TIMESTAMP,
                    "width": w,
                    "size": sel,
                    "qty": qty
                })
                st.success("Data Logged!")
                del st.session_state.detected_w
        else:
            st.error(f"No rule for {w}mm. Contact Admin.")
