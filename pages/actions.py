"""
ROT - Tiltaksoversikt
"""

import streamlit as st
from datetime import datetime
from data import (
    save_data, filter_risks_by_access, get_project_name, get_risk_by_id
)

def show_actions_overview(data, user):
    st.markdown('<h1 class="main-title">📋 Tiltaksoversikt</h1>', unsafe_allow_html=True)
    
    all_actions = data.get("actions", [])
    accessible_risks = filter_risks_by_access(data.get("risks", []), user, data)
    accessible_risk_ids = [r["id"] for r in accessible_risks]
    actions = [a for a in all_actions if a.get("risk_id") in accessible_risk_ids]
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        action_status_filter = st.selectbox("Status", ["Åpne", "Gjennomførte", "Alle"], key="action_status")
    with col2:
        project_options = ["Alle prosjekter"]
        if user.get("role") == "admin":
            project_options += [p["name"] for p in data.get("projects", [])]
        else:
            user_project_ids = user.get("projects", [])
            project_options += [p["name"] for p in data.get("projects", []) if p["id"] in user_project_ids]
        action_project_filter = st.selectbox("Prosjekt", project_options, key="action_project")
    with col3:
        all_responsibles = list(set(a.get("responsible", "") for a in actions if a.get("responsible")))
        responsible_filter = st.selectbox("Ansvarlig", ["Alle"] + sorted(all_responsibles), key="action_responsible")
    with col4:
        action_sort = st.selectbox("Sorter etter", ["Frist (nærmeste først)", "Frist (fjerneste først)", "Prosjekt", "Status"], key="action_sort")
    
    show_overdue = st.checkbox("Vis kun forfalte", key="show_overdue")
    
    # Filtrer tiltak
    filtered_actions = []
    for action in actions:
        if action_status_filter == "Åpne" and action.get("status") != "Åpen":
            continue
        if action_status_filter == "Gjennomførte" and action.get("status") != "Gjennomført":
            continue
        if action_project_filter != "Alle prosjekter":
            risk = get_risk_by_id(action.get("risk_id"), data)
            if risk:
                project_name = get_project_name(risk.get("project_id"), data)
                if project_name != action_project_filter:
                    continue
        if responsible_filter != "Alle" and action.get("responsible") != responsible_filter:
            continue
        if show_overdue:
            deadline = action.get("deadline", "")
            if deadline and action.get("status") == "Åpen":
                try:
                    if datetime.strptime(deadline, "%Y-%m-%d").date() >= datetime.now().date():
                        continue
                except:
                    continue
            else:
                continue
        filtered_actions.append(action)
    
    # Sortering
    def sort_actions(action):
        deadline = action.get("deadline", "9999-12-31")
        risk = get_risk_by_id(action.get("risk_id"), data)
        project_name = get_project_name(risk.get("project_id"), data) if risk else "ZZZ"
        if action_sort == "Frist (nærmeste først)":
            return deadline
        elif action_sort == "Frist (fjerneste først)":
            return deadline
        elif action_sort == "Prosjekt":
            return project_name
        elif action_sort == "Status":
            return 0 if action.get("status") == "Åpen" else 1
        return deadline
    
    filtered_actions.sort(key=sort_actions, reverse=(action_sort == "Frist (fjerneste først)"))
    
    # Statistikk
    open_actions = [a for a in filtered_actions if a.get("status") == "Åpen"]
    overdue_actions = []
    for a in open_actions:
        deadline = a.get("deadline", "")
        if deadline:
            try:
                if datetime.strptime(deadline, "%Y-%m-%d").date() < datetime.now().date():
                    overdue_actions.append(a)
            except:
                pass
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="stat-card"><div class="stat-number">{len(filtered_actions)}</div><div class="stat-label">Tiltak (filtrert)</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="stat-card"><div class="stat-number">{len(open_actions)}</div><div class="stat-label">Åpne</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="stat-card"><div class="stat-number" style="color: #e63946;">{len(overdue_actions)}</div><div class="stat-label">Forfalte</div></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    if not filtered_actions:
        st.info("Ingen tiltak funnet med valgte filtre.")
    else:
        for action in filtered_actions:
            risk = get_risk_by_id(action.get("risk_id"), data)
            risk_title = risk.get("title", "-") if risk else "-"
            project_name = get_project_name(risk.get("project_id"), data) if risk else "-"
            
            is_overdue = False
            deadline = action.get("deadline", "")
            if deadline and action.get("status") == "Åpen":
                try:
                    if datetime.strptime(deadline, "%Y-%m-%d").date() < datetime.now().date():
                        is_overdue = True
                except:
                    pass
            
            col1, col2, col3, col4, col5, col6 = st.columns([2, 2, 3, 1.5, 1.5, 1.5])
            
            with col1:
                st.markdown(f"**{project_name}**")
            with col2:
                st.markdown(f"*{risk_title[:30]}{'...' if len(risk_title) > 30 else ''}*")
            with col3:
                st.markdown(action.get("description", "-"))
            with col4:
                st.markdown(action.get("responsible", "-"))
            with col5:
                if is_overdue:
                    st.markdown(f"**:red[{deadline}]** ⚠️")
                else:
                    st.markdown(deadline or "-")
            with col6:
                if action.get("status") == "Åpen":
                    if st.button("⏳ Fullfør", key=f"complete_action_list_{action.get('id')}"):
                        for a in st.session_state.data["actions"]:
                            if a["id"] == action["id"]:
                                a["status"] = "Gjennomført"
                                a["completed_date"] = datetime.now().isoformat()
                        save_data(st.session_state.data)
                        st.rerun()
                else:
                    if st.button("↩️ Angre", key=f"undo_action_{action.get('id')}"):
                        for a in st.session_state.data["actions"]:
                            if a["id"] == action["id"]:
                                a["status"] = "Åpen"
                                a.pop("completed_date", None)
                        save_data(st.session_state.data)
                        st.rerun()
            
            st.markdown("---")
