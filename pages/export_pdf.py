"""
ROT - PDF Eksport
"""

import streamlit as st
from datetime import datetime
from data import (
    filter_risks_by_access, generate_pdf_html, 
    generate_top10_pdf_content, generate_project_pdf_content, generate_actions_pdf_content
)

def show_export_pdf(data, user):
    st.markdown('<h1 class="main-title">📄 Eksporter PDF</h1>', unsafe_allow_html=True)
    st.markdown("Velg hva du vil eksportere som PDF/HTML-rapport.")
    
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    st.markdown("### 1. Topp 10 Risikoer og Muligheter")
    if st.button("Generer Topp 10 rapport", key="export_top10"):
        risks = filter_risks_by_access(data.get("risks", []), user, data)
        active_risks = [r for r in risks if r.get("status") == "Aktiv"]
        sorted_risks = sorted(active_risks, key=lambda r: (r.get("probability", 1) * r.get("consequence", 1), r.get("exposure", 0) or 0), reverse=True)[:10]
        content = generate_top10_pdf_content(sorted_risks, data)
        html = generate_pdf_html("Topp 10 Rapport", content, date_str)
        st.download_button(label="📥 Last ned rapport (HTML)", data=html, file_name=f"ROT_Topp10_{datetime.now().strftime('%Y%m%d')}.html", mime="text/html")
    
    st.markdown("---")
    st.markdown("### 2. Prosjektrapport")
    
    if user.get("role") == "admin":
        projects = data.get("projects", [])
    else:
        projects = [p for p in data.get("projects", []) if p["id"] in user.get("projects", [])]
    
    if projects:
        selected_project_id = st.selectbox("Velg prosjekt", options=[p["id"] for p in projects], format_func=lambda x: next((p["name"] for p in projects if p["id"] == x), x), key="export_project")
        if st.button("Generer prosjektrapport", key="export_project_btn"):
            project = next((p for p in projects if p["id"] == selected_project_id), None)
            if project:
                project_risks = [r for r in data.get("risks", []) if r.get("project_id") == selected_project_id]
                project_actions = [a for a in data.get("actions", []) if a.get("risk_id") in [r["id"] for r in project_risks]]
                content = generate_project_pdf_content(project, project_risks, project_actions, data)
                html = generate_pdf_html(f"Prosjektrapport - {project.get('name')}", content, date_str)
                st.download_button(label="📥 Last ned rapport (HTML)", data=html, file_name=f"ROT_{project.get('number')}_{datetime.now().strftime('%Y%m%d')}.html", mime="text/html")
    
    st.markdown("---")
    st.markdown("### 3. Tiltaksoversikt")
    action_filter = st.selectbox("Filtrer tiltak", ["Alle", "Kun åpne", "Kun forfalte"], key="export_action_filter")
    if st.button("Generer tiltaksoversikt", key="export_actions"):
        all_actions = data.get("actions", [])
        accessible_risks = filter_risks_by_access(data.get("risks", []), user, data)
        actions = [a for a in all_actions if a.get("risk_id") in [r["id"] for r in accessible_risks]]
        if action_filter == "Kun åpne":
            actions = [a for a in actions if a.get("status") == "Åpen"]
        elif action_filter == "Kun forfalte":
            actions = [a for a in actions if a.get("status") == "Åpen" and a.get("deadline") and datetime.strptime(a.get("deadline"), "%Y-%m-%d").date() < datetime.now().date()]
        actions.sort(key=lambda a: a.get("deadline", "9999-12-31"))
        content = generate_actions_pdf_content(actions, data)
        html = generate_pdf_html("Tiltaksoversikt", content, date_str)
        st.download_button(label="📥 Last ned rapport (HTML)", data=html, file_name=f"ROT_Tiltak_{datetime.now().strftime('%Y%m%d')}.html", mime="text/html")
    
    st.markdown("---")
    st.info("💡 Åpne HTML-filen i nettleseren og bruk Ctrl+P → 'Save as PDF'")
