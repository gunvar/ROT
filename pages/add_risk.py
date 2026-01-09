"""
ROT - Ny risiko/mulighet
"""

import streamlit as st
from datetime import datetime
from data import save_data, generate_id
from config import DISCOVERY_METHODS

def show_add_risk(data, user, prefill_type=None, prefill_method=None, prefill_question=None):
    st.markdown('<h1 class="main-title">Ny risiko/mulighet</h1>', unsafe_allow_html=True)
    
    # Vis info om prefill
    if prefill_type and prefill_method:
        st.info(f"📚 Registrerer fra Hjelpemidler: **{prefill_method}**")
        if st.button("✕ Fjern forhåndsutfylling"):
            st.session_state.prefill_type = None
            st.session_state.prefill_method = None
            st.session_state.prefill_question = None
            st.session_state.pop('prefill_digital', None)
            st.rerun()
    
    if user.get("role") == "admin":
        projects = data.get("projects", [])
    else:
        user_project_ids = user.get("projects", [])
        projects = [p for p in data.get("projects", []) if p["id"] in user_project_ids]
    
    if not projects:
        st.warning("Du har ikke tilgang til noen prosjekter. Kontakt administrator.")
        return
    
    with st.form("new_risk_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            project_id = st.selectbox("Prosjekt *", options=[p["id"] for p in projects], format_func=lambda x: next((p["name"] for p in projects if p["id"] == x), x))
            title = st.text_input("Tittel *", placeholder="Kort beskrivende tittel")
            
            type_options = ["Risiko", "Mulighet"]
            type_index = type_options.index(prefill_type) if prefill_type in type_options else 0
            risk_type = st.selectbox("Type *", type_options, index=type_index)
            
            owner = st.selectbox("Eier *", ["Firma", "Kunde"])
            tags = st.multiselect("Tags", ["Økonomi", "Ressurs", "Teknisk", "Juridisk", "Kvalitet", "HMS", "Fremdrift"])
            
            is_digital = False
            if risk_type == "Mulighet":
                default_digital = st.session_state.get('prefill_digital', False)
                is_digital = st.checkbox("🤖 Digitalisering/KI-potensial", value=default_digital)
        
        with col2:
            probability = st.select_slider("Sannsynlighet *", options=[1, 2, 3, 4, 5], value=3)
            consequence = st.select_slider("Konsekvens *", options=[1, 2, 3, 4, 5], value=3)
            exposure = st.number_input("Økonomisk eksponering (kr)", min_value=0, step=100000)
            st.markdown(f"**Risikoscore:** {probability * consequence}")
            
            method_index = 0
            if prefill_method and prefill_method in DISCOVERY_METHODS:
                method_index = DISCOVERY_METHODS.index(prefill_method)
            discovery_method = st.selectbox("Identifisert via", DISCOVERY_METHODS, index=method_index)
        
        default_desc = ""
        if prefill_question:
            default_desc = f"Spørsmål: {prefill_question}\n\nSvar/Beskrivelse: "
        description = st.text_area("Beskrivelse *", value=default_desc, placeholder="Beskriv risikoen/muligheten...", height=120)
        
        submitted = st.form_submit_button("Registrer risiko/mulighet", use_container_width=True)
        
        if submitted:
            if not title or not description:
                st.error("Fyll ut alle obligatoriske felt (merket med *)")
            else:
                new_risk = {
                    "id": generate_id(),
                    "project_id": project_id,
                    "title": title,
                    "description": description,
                    "type": risk_type,
                    "owner": owner,
                    "tags": tags,
                    "probability": probability,
                    "consequence": consequence,
                    "exposure": exposure if exposure > 0 else None,
                    "status": "Aktiv",
                    "created": datetime.now().isoformat(),
                    "last_updated": datetime.now().isoformat(),
                    "created_by": st.session_state.username,
                    "discovery_method": discovery_method if discovery_method != "(Ikke angitt)" else None,
                    "is_digital": is_digital if risk_type == "Mulighet" else False,
                    "score_history": [{"date": datetime.now().isoformat(), "score": probability * consequence, "probability": probability, "consequence": consequence}]
                }
                st.session_state.data["risks"].append(new_risk)
                save_data(st.session_state.data)
                
                st.session_state.prefill_type = None
                st.session_state.prefill_method = None
                st.session_state.prefill_question = None
                st.session_state.pop('prefill_digital', None)
                
                st.success(f"✅ {risk_type} '{title}' er registrert!")
                st.balloons()
