"""
ROT - Prosjekter (FASE 5: Med ekspanderbar liste og redigeringsmulighet)
"""

import streamlit as st
from datetime import datetime
from data import save_data, generate_id, get_project_trend, get_inactive_days, get_trend_indicator
from pages.dashboard import display_risk_card

def show_projects(data, user):
    st.markdown('<h1 class="main-title">Prosjekter</h1>', unsafe_allow_html=True)
    
    if user.get("role") == "admin":
        st.markdown("### Legg til prosjekt")
        with st.form("new_project_form"):
            col1, col2, col3 = st.columns(3)
            with col1:
                project_number = st.text_input("Oppdragsnummer *", placeholder="F.eks. 5123456")
            with col2:
                project_name = st.text_input("Prosjektnavn *", placeholder="F.eks. E39 Rogfast")
            with col3:
                project_value = st.number_input("Kontraktsverdi (MNOK)", min_value=0.0, step=0.5)
            project_ol = st.text_input("Oppdragsleder", placeholder="Navn på ansvarlig OL")
            
            if st.form_submit_button("Legg til prosjekt"):
                if project_number and project_name:
                    new_project = {"id": generate_id(), "number": project_number, "name": project_name, "value": project_value, "ol": project_ol, "created": datetime.now().isoformat()}
                    st.session_state.data["projects"].append(new_project)
                    save_data(st.session_state.data)
                    st.success(f"Prosjekt '{project_name}' lagt til!")
                    st.rerun()
                else:
                    st.error("Fyll ut oppdragsnummer og prosjektnavn")
        st.markdown("---")
    
    st.markdown("### Prosjektoversikt")
    
    if user.get("role") == "admin":
        projects = data.get("projects", [])
    else:
        user_project_ids = user.get("projects", [])
        projects = [p for p in data.get("projects", []) if p["id"] in user_project_ids]
    
    if not projects:
        st.info("Ingen prosjekter å vise.")
    else:
        for project in projects:
            project_risks = [r for r in data.get("risks", []) if r.get("project_id") == project["id"]]
            active_risks = [r for r in project_risks if r.get("status") == "Aktiv"]
            critical_risks = [r for r in active_risks if r.get("probability", 1) * r.get("consequence", 1) >= 16]
            total_exposure = sum(r.get("exposure", 0) or 0 for r in active_risks)
            exposure_mnok = total_exposure / 1000000
            
            project_risk_ids = [r["id"] for r in project_risks]
            open_actions = [a for a in data.get("actions", []) if a.get("risk_id") in project_risk_ids and a.get("status") == "Åpen"]
            
            if project_risks:
                last_updates = [r.get("last_updated") for r in project_risks if r.get("last_updated")]
                last_update = max(last_updates)[:10] if last_updates else "Aldri"
            else:
                last_update = "Ingen risikoer"
            
            trend_icon, trend_text = get_project_trend(project["id"], data)
            
            # Prosjektkort
            st.markdown(f"""
            <div class="project-card">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div>
                        <h3 style="margin: 0; color: #f1f5f9;">{project['number']} – {project['name']}</h3>
                        <p style="color: #94a3b8; margin: 0.25rem 0;">OL: {project.get('ol', 'Ikke angitt')} | Kontraktsverdi: {project.get('value', 0)} MNOK</p>
                    </div>
                    <div style="text-align: right;">
                        <span style="font-size: 1.5rem;">{trend_icon}</span>
                        <p style="color: #94a3b8; margin: 0; font-size: 0.8rem;">{trend_text}</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Statistikk
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.metric("Kritiske (S×K ≥ 16)", len(critical_risks))
            with col2:
                st.metric("Eksponering", f"{exposure_mnok:.2f} MNOK")
            with col3:
                st.metric("Åpne tiltak", len(open_actions))
            with col4:
                st.metric("Sist oppdatert", last_update)
            with col5:
                # FASE 5: Rediger og slett-knapper
                col_edit, col_delete = st.columns(2)
                with col_edit:
                    if st.button("✏️", key=f"edit_project_{project['id']}", help="Rediger prosjekt"):
                        st.session_state[f"editing_project_{project['id']}"] = True
                        st.rerun()
                with col_delete:
                    if user.get("role") == "admin":
                        if st.button("🗑️", key=f"delete_project_{project['id']}", help="Slett prosjekt"):
                            if project_risks:
                                st.error("Kan ikke slette prosjekt med risikoer")
                            else:
                                st.session_state[f"confirm_delete_project_{project['id']}"] = True
                                st.rerun()
            
            # FASE 5: Bekreft sletting av prosjekt
            if st.session_state.get(f"confirm_delete_project_{project['id']}", False):
                st.warning("⚠️ Er du sikker på at du vil slette dette prosjektet?")
                col_yes, col_no = st.columns(2)
                with col_yes:
                    if st.button("Ja, slett", key=f"confirm_del_project_{project['id']}"):
                        st.session_state.data["projects"] = [p for p in data.get("projects", []) if p["id"] != project["id"]]
                        save_data(st.session_state.data)
                        st.session_state[f"confirm_delete_project_{project['id']}"] = False
                        st.success("Prosjekt slettet!")
                        st.rerun()
                with col_no:
                    if st.button("Nei, avbryt", key=f"cancel_del_project_{project['id']}"):
                        st.session_state[f"confirm_delete_project_{project['id']}"] = False
                        st.rerun()
            
            # FASE 5: Redigeringsskjema for prosjekt
            if st.session_state.get(f"editing_project_{project['id']}", False):
                with st.form(key=f"edit_project_form_{project['id']}"):
                    st.markdown("**Rediger prosjekt:**")
                    col1, col2 = st.columns(2)
                    with col1:
                        new_number = st.text_input("Oppdragsnummer", value=project.get("number", ""))
                        new_name = st.text_input("Prosjektnavn", value=project.get("name", ""))
                    with col2:
                        new_ol = st.text_input("Oppdragsleder", value=project.get("ol", ""))
                        new_value = st.number_input("Kontraktsverdi (MNOK)", min_value=0.0, value=float(project.get("value", 0)), step=0.5)
                    
                    col_save, col_cancel = st.columns(2)
                    with col_save:
                        if st.form_submit_button("💾 Lagre endringer"):
                            for p in st.session_state.data["projects"]:
                                if p["id"] == project["id"]:
                                    p["number"] = new_number
                                    p["name"] = new_name
                                    p["ol"] = new_ol
                                    p["value"] = new_value
                            save_data(st.session_state.data)
                            st.session_state[f"editing_project_{project['id']}"] = False
                            st.success("Prosjekt oppdatert!")
                            st.rerun()
                    with col_cancel:
                        if st.form_submit_button("❌ Avbryt"):
                            st.session_state[f"editing_project_{project['id']}"] = False
                            st.rerun()
            
            # FASE 5: Ekspanderbar liste med prosjektets risikoer
            if project_risks:
                with st.expander(f"📋 Vis alle risikoer og muligheter ({len(project_risks)} stk)"):
                    # Sorter etter score
                    sorted_risks = sorted(project_risks, key=lambda r: r.get("probability", 1) * r.get("consequence", 1), reverse=True)
                    
                    for risk in sorted_risks:
                        display_risk_card(risk, data, user)
            
            st.markdown("---")
