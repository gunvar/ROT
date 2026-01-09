"""
ROT - Administrasjon
"""

import streamlit as st
import json
from data import save_data, get_default_users

def show_admin(data):
    st.markdown('<h1 class="main-title">Administrasjon</h1>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Statistikk")
        total_projects = len(data.get("projects", []))
        total_risks = len(data.get("risks", []))
        total_actions = len(data.get("actions", []))
        total_users = len(data.get("users", {}))
        occurred_risks = [r for r in data.get("risks", []) if r.get("status") == "Inntruffet"]
        digital_opportunities = [r for r in data.get("risks", []) if r.get("is_digital")]
        total_actual_cost = sum(r.get("actual_cost", 0) or 0 for r in occurred_risks)
        
        st.markdown(f"""
        - **Prosjekter:** {total_projects}
        - **Risikoer/muligheter:** {total_risks}
        - **Tiltak:** {total_actions}
        - **Brukere:** {total_users}
        - **Inntruffet risikoer:** {len(occurred_risks)}
        - **Digital/KI-muligheter:** {len(digital_opportunities)}
        - **Total faktisk kostnad:** {total_actual_cost:,} kr
        """.replace(",", " "))
    
    with col2:
        st.markdown("### 🔧 Verktøy")
        st.download_button(label="📥 Eksporter data (JSON)", data=json.dumps(data, indent=2, ensure_ascii=False), file_name="rot_backup.json", mime="application/json", use_container_width=True)
        
        st.markdown("---")
        uploaded_file = st.file_uploader("📤 Importer data", type="json")
        if uploaded_file:
            try:
                imported_data = json.load(uploaded_file)
                if st.button("Bekreft import", use_container_width=True):
                    st.session_state.data = imported_data
                    save_data(imported_data)
                    st.success("Data importert!")
                    st.rerun()
            except Exception as e:
                st.error(f"Feil ved import: {e}")
        
        st.markdown("---")
        st.markdown("### ⚠️ Faresone")
        with st.expander("Nullstill alle data"):
            st.warning("Dette vil slette ALLE data permanent!")
            confirm = st.text_input("Skriv 'SLETT ALT' for å bekrefte")
            if st.button("Nullstill", type="secondary"):
                if confirm == "SLETT ALT":
                    st.session_state.data = {"projects": [], "risks": [], "actions": [], "users": get_default_users()}
                    save_data(st.session_state.data)
                    st.success("Data nullstilt!")
                    st.rerun()
                else:
                    st.error("Feil bekreftelse")
