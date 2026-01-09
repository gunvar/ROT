"""
ROT - Dashboard
"""

import streamlit as st
from datetime import datetime
from data import (
    save_data, generate_id, get_inactive_days, get_trend_indicator,
    filter_risks_by_access, get_project_name, get_risk_by_id,
    check_project_access, get_status_index
)

def show_dashboard(data, user, project_filter, type_filter, owner_filter, status_filter, sort_option, show_digital_only=False):
    st.markdown('<h1 class="main-title">Risk & Opportunity Tracker</h1>', unsafe_allow_html=True)
    
    risks = filter_risks_by_access(data.get("risks", []), user, data)
    filtered_risks = []
    
    for risk in risks:
        if project_filter != "Alle prosjekter":
            project = next((p for p in data.get("projects", []) if p["id"] == risk.get("project_id")), None)
            if not project or project["name"] != project_filter:
                continue
        if type_filter != "Alle" and risk.get("type") != type_filter:
            continue
        if owner_filter != "Alle" and risk.get("owner") != owner_filter:
            continue
        if status_filter == "Aktive" and risk.get("status") != "Aktiv":
            continue
        elif status_filter == "Mitigerte" and risk.get("status") != "Mitigert":
            continue
        elif status_filter == "Inntruffet" and risk.get("status") != "Inntruffet":
            continue
        if show_digital_only and not risk.get("is_digital"):
            continue
        filtered_risks.append(risk)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    all_active = [r for r in filtered_risks if r.get("status") == "Aktiv"]
    active_risks = [r for r in all_active if r.get("type") == "Risiko"]
    active_opportunities = [r for r in all_active if r.get("type") == "Mulighet"]
    critical_risks = [r for r in active_risks if r.get("probability", 1) * r.get("consequence", 1) >= 16]
    digital_opportunities = [r for r in active_opportunities if r.get("is_digital")]
    total_exposure = sum(r.get("exposure", 0) or 0 for r in all_active)
    exposure_mnok = total_exposure / 1000000
    
    with col1:
        st.markdown(f'<div class="stat-card"><div class="stat-number">{len(active_risks)}</div><div class="stat-label">Aktive risikoer</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="stat-card"><div class="stat-number">{len(active_opportunities)}</div><div class="stat-label">Aktive muligheter</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="stat-card"><div class="stat-number" style="color: #e63946;">{len(critical_risks)}</div><div class="stat-label">Kritiske (S×K ≥ 16)</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="stat-card"><div class="stat-number" style="color: #9333ea;">{len(digital_opportunities)}</div><div class="stat-label">🤖 Digital/KI</div></div>', unsafe_allow_html=True)
    with col5:
        st.markdown(f'<div class="stat-card"><div class="stat-number">{exposure_mnok:.1f}</div><div class="stat-label">Eksponering (MNOK)</div></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("## 🔥 Topp 10 Risikoer og Muligheter")
    
    def sort_key(risk):
        score = risk.get("probability", 1) * risk.get("consequence", 1)
        exposure = risk.get("exposure", 0) or 0
        inactive_days = get_inactive_days(risk.get("last_updated"))
        if sort_option == "Score (høyest først)":
            return (score * 1000000) + exposure
        elif sort_option == "Eksponering (høyest først)":
            return exposure
        elif sort_option == "Sist oppdatert":
            return -inactive_days
        elif sort_option == "Inaktive først":
            return inactive_days
        return score
    
    active_items = [r for r in filtered_risks if r.get("status") == "Aktiv"]
    sorted_risks = sorted(active_items, key=sort_key, reverse=True)[:10]
    
    if not sorted_risks:
        st.info("Ingen aktive risikoer eller muligheter funnet med valgte filtre.")
    
    for risk in sorted_risks:
        display_risk_card(risk, data, user)


def show_needs_attention(data, user):
    st.markdown('<h1 class="main-title">⚠️ Trenger oppfølging</h1>', unsafe_allow_html=True)
    
    risks = filter_risks_by_access(data.get("risks", []), user, data)
    inactive_risks = []
    
    for risk in risks:
        if risk.get("status") != "Aktiv":
            continue
        inactive_days = get_inactive_days(risk.get("last_updated"))
        if inactive_days >= 28:
            risk["_inactive_days"] = inactive_days
            inactive_risks.append(risk)
    
    inactive_risks.sort(key=lambda r: r.get("_inactive_days", 0), reverse=True)
    
    col1, col2, col3 = st.columns(3)
    critical_inactive = [r for r in inactive_risks if r.get("_inactive_days", 0) >= 56]
    warning_inactive = [r for r in inactive_risks if 28 <= r.get("_inactive_days", 0) < 56]
    
    with col1:
        st.markdown(f'<div class="stat-card"><div class="stat-number" style="color: #e63946;">{len(critical_inactive)}</div><div class="stat-label">Kritisk (8+ uker)</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="stat-card"><div class="stat-number" style="color: #e9c46a;">{len(warning_inactive)}</div><div class="stat-label">Varsel (4-8 uker)</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="stat-card"><div class="stat-number">{len(inactive_risks)}</div><div class="stat-label">Totalt inaktive</div></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    if not inactive_risks:
        st.success("✅ Alle aktive risikoer er oppdatert de siste 4 ukene!")
    else:
        if critical_inactive:
            st.markdown("### 🔴 Kritisk - Ikke oppdatert på 8+ uker")
            for risk in critical_inactive:
                display_risk_card(risk, data, user, show_inactive_badge=True)
        if warning_inactive:
            st.markdown("### 🟡 Varsel - Ikke oppdatert på 4-8 uker")
            for risk in warning_inactive:
                display_risk_card(risk, data, user, show_inactive_badge=True)


def display_risk_card(risk, data, user, show_inactive_badge=False, show_edit_button=False):
    """Viser et risikokort med alle detaljer og handlinger"""
    if not check_project_access(user, risk.get("project_id"), data):
        return
    
    project = next((p for p in data.get("projects", []) if p["id"] == risk.get("project_id")), None)
    project_name = project["name"] if project else "Ukjent prosjekt"
    score = risk.get("probability", 1) * risk.get("consequence", 1)
    
    if score >= 20:
        score_color = "#e63946"
    elif score >= 12:
        score_color = "#f4a261"
    elif score >= 6:
        score_color = "#e9c46a"
    else:
        score_color = "#2a9d8f"
    
    trend_icon, _, _ = get_trend_indicator(risk)
    
    inactive_days = get_inactive_days(risk.get("last_updated"))
    inactive_html = ""
    if show_inactive_badge or inactive_days >= 28:
        if inactive_days >= 56:
            inactive_html = f'<span style="background: #e63946; color: white; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.75rem; margin-left: 0.5rem;">⚠️ {inactive_days} dager</span>'
        elif inactive_days >= 28:
            inactive_html = f'<span style="background: #e9c46a; color: #1a1a1a; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.75rem; margin-left: 0.5rem;">⚠️ {inactive_days} dager</span>'
    
    actions = [a for a in data.get("actions", []) if a.get("risk_id") == risk.get("id") and a.get("status") == "Åpen"]
    
    exposure_text = ""
    if risk.get("exposure"):
        exposure_text = f" | Eksponering: {risk.get('exposure'):,} kr".replace(",", " ")
    
    type_icon = "⚠️" if risk.get("type") == "Risiko" else "💡"
    
    digital_badge = ""
    if risk.get("is_digital"):
        digital_badge = '<span style="background: #9333ea; color: white; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.75rem; margin-left: 0.5rem;">🤖 Digital/KI</span>'
    
    status = risk.get("status", "Aktiv")
    
    if status == "Inntruffet":
        border_color = "#9333ea"
    elif status == "Mitigert":
        border_color = "#64748b"
    elif risk.get("type") == "Mulighet":
        border_color = "#2a9d8f"
    else:
        border_color = "#e63946"
    
    status_badge = ""
    if status == "Inntruffet":
        actual_cost = risk.get("actual_cost", 0)
        if actual_cost:
            status_badge = f'<span style="background: #9333ea; color: white; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.75rem; margin-left: 0.5rem;">Faktisk kostnad: {actual_cost:,} kr</span>'.replace(",", " ")
        else:
            status_badge = '<span style="background: #9333ea; color: white; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.75rem; margin-left: 0.5rem;">INNTRUFFET</span>'
    elif status == "Mitigert":
        status_badge = '<span style="background: #2a9d8f; color: white; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.75rem; margin-left: 0.5rem;">MITIGERT</span>'
    
    with st.container():
        card_html = f"""<div style="background: linear-gradient(135deg, #1a2332 0%, #0f1419 100%); border-radius: 12px; padding: 1.5rem; margin-bottom: 0.5rem; border-left: 4px solid {border_color}; box-shadow: 0 4px 20px rgba(0,0,0,0.3);">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.5rem;">
                <div style="font-size: 0.85rem; color: #94a3b8;">{project_name}{inactive_html}{status_badge}{digital_badge}</div>
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="background: {score_color}; color: white; padding: 0.25rem 0.75rem; border-radius: 20px; font-weight: 700; font-size: 0.9rem;">S×K: {score}</span>
                    <span style="font-size: 1.2rem;">{trend_icon}</span>
                </div>
            </div>
            <h3 style="margin: 0.5rem 0; color: #f1f5f9;">{type_icon} {risk.get('title', 'Uten tittel')}</h3>
            <p style="color: #94a3b8; margin-bottom: 0.5rem;">{risk.get('description', '')}</p>
            <div style="font-size: 0.85rem; color: #64748b;">S: {risk.get('probability', '-')} | K: {risk.get('consequence', '-')}{exposure_text} | Eier: {risk.get('owner', '-')} | Tags: {', '.join(risk.get('tags', []) or ['Ingen'])}</div>
        </div>"""
        
        st.markdown(card_html, unsafe_allow_html=True)
        
        if status == "Aktiv":
            if actions:
                action = actions[0]
                deadline = action.get("deadline", "Ingen frist")
                st.info(f"**Neste handling:** {action.get('description', '')} ({action.get('responsible', 'Ikke tildelt')}, {deadline})")
            else:
                st.caption("Ingen åpne tiltak")
    
    with st.expander("📋 Detaljer og tiltak"):
        _show_risk_details(risk, data, user)


def _show_risk_details(risk, data, user):
    """Viser detaljer og redigeringsmuligheter for en risiko"""
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("#### Tiltak")
        risk_actions = [a for a in data.get("actions", []) if a.get("risk_id") == risk.get("id")]
        
        if risk_actions:
            for action in risk_actions:
                status_icon = "✅" if action.get("status") == "Gjennomført" else "⏳"
                st.markdown(f"{status_icon} **{action.get('description', '')}** – {action.get('responsible', 'Ikke tildelt')} ({action.get('deadline', 'Ingen frist')})")
                
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    if action.get("status") == "Åpen":
                        if st.button("✓ Fullfør", key=f"complete_{action.get('id')}"):
                            for a in st.session_state.data["actions"]:
                                if a["id"] == action["id"]:
                                    a["status"] = "Gjennomført"
                                    a["completed_date"] = datetime.now().isoformat()
                            save_data(st.session_state.data)
                            st.rerun()
                with col_b:
                    if action.get("status") == "Gjennomført":
                        if st.button("↩️ Angre", key=f"undo_{action.get('id')}"):
                            for a in st.session_state.data["actions"]:
                                if a["id"] == action["id"]:
                                    a["status"] = "Åpen"
                                    a.pop("completed_date", None)
                            save_data(st.session_state.data)
                            st.rerun()
                with col_c:
                    # FASE 5: Rediger tiltak
                    if st.button("✏️ Rediger", key=f"edit_action_{action.get('id')}"):
                        st.session_state[f"editing_action_{action.get('id')}"] = True
                        st.rerun()
                
                # Vis redigeringsskjema hvis aktiv
                if st.session_state.get(f"editing_action_{action.get('id')}", False):
                    with st.form(key=f"edit_action_form_{action.get('id')}"):
                        new_desc = st.text_input("Beskrivelse", value=action.get("description", ""))
                        new_resp = st.text_input("Ansvarlig", value=action.get("responsible", ""))
                        new_deadline = st.date_input("Frist", value=datetime.strptime(action.get("deadline", "2025-01-01"), "%Y-%m-%d").date() if action.get("deadline") else datetime.now().date())
                        
                        col_save, col_cancel, col_delete = st.columns(3)
                        with col_save:
                            if st.form_submit_button("💾 Lagre"):
                                for a in st.session_state.data["actions"]:
                                    if a["id"] == action["id"]:
                                        a["description"] = new_desc
                                        a["responsible"] = new_resp
                                        a["deadline"] = str(new_deadline)
                                save_data(st.session_state.data)
                                st.session_state[f"editing_action_{action.get('id')}"] = False
                                st.rerun()
                        with col_cancel:
                            if st.form_submit_button("❌ Avbryt"):
                                st.session_state[f"editing_action_{action.get('id')}"] = False
                                st.rerun()
                        with col_delete:
                            if st.form_submit_button("🗑️ Slett"):
                                st.session_state[f"confirm_delete_action_{action.get('id')}"] = True
                    
                    # Bekreft sletting av tiltak
                    if st.session_state.get(f"confirm_delete_action_{action.get('id')}", False):
                        st.warning("⚠️ Er du sikker på at du vil slette dette tiltaket?")
                        col_yes, col_no = st.columns(2)
                        with col_yes:
                            if st.button("Ja, slett", key=f"confirm_del_action_{action.get('id')}"):
                                st.session_state.data["actions"] = [a for a in st.session_state.data["actions"] if a["id"] != action["id"]]
                                save_data(st.session_state.data)
                                st.session_state[f"editing_action_{action.get('id')}"] = False
                                st.session_state[f"confirm_delete_action_{action.get('id')}"] = False
                                st.rerun()
                        with col_no:
                            if st.button("Nei, avbryt", key=f"cancel_del_action_{action.get('id')}"):
                                st.session_state[f"confirm_delete_action_{action.get('id')}"] = False
                                st.rerun()
        else:
            st.markdown("*Ingen tiltak registrert*")
        
        if risk.get("status") == "Aktiv":
            st.markdown("---")
            st.markdown("**Legg til tiltak:**")
            new_action_desc = st.text_input("Beskrivelse", key=f"action_desc_{risk.get('id')}")
            new_action_resp = st.text_input("Ansvarlig", key=f"action_resp_{risk.get('id')}")
            new_action_deadline = st.date_input("Frist", key=f"action_deadline_{risk.get('id')}")
            
            if st.button("Legg til tiltak", key=f"add_action_{risk.get('id')}"):
                if new_action_desc:
                    new_action = {
                        "id": generate_id(),
                        "risk_id": risk.get("id"),
                        "description": new_action_desc,
                        "responsible": new_action_resp,
                        "deadline": str(new_action_deadline),
                        "status": "Åpen",
                        "created": datetime.now().isoformat()
                    }
                    st.session_state.data["actions"].append(new_action)
                    for r in st.session_state.data["risks"]:
                        if r["id"] == risk["id"]:
                            r["last_updated"] = datetime.now().isoformat()
                    save_data(st.session_state.data)
                    st.success("Tiltak lagt til!")
                    st.rerun()
    
    with col2:
        st.markdown("#### Oppdater risiko")
        
        # FASE 5: Rediger risiko-knapp
        if st.button("✏️ Rediger risiko", key=f"edit_risk_btn_{risk.get('id')}"):
            st.session_state[f"editing_risk_{risk.get('id')}"] = True
            st.rerun()
        
        # Vis redigeringsskjema for risiko
        if st.session_state.get(f"editing_risk_{risk.get('id')}", False):
            with st.form(key=f"edit_risk_form_{risk.get('id')}"):
                st.markdown("**Rediger risiko:**")
                new_title = st.text_input("Tittel", value=risk.get("title", ""))
                new_description = st.text_area("Beskrivelse", value=risk.get("description", ""))
                new_owner = st.selectbox("Eier", ["Firma", "Kunde"], index=0 if risk.get("owner") == "Firma" else 1)
                new_tags = st.multiselect("Tags", ["Økonomi", "Ressurs", "Teknisk", "Juridisk", "Kvalitet", "HMS", "Fremdrift"], default=risk.get("tags", []))
                new_exposure = st.number_input("Eksponering (kr)", min_value=0, value=risk.get("exposure", 0) or 0, step=10000)
                
                if risk.get("type") == "Mulighet":
                    new_is_digital = st.checkbox("🤖 Digitalisering/KI", value=risk.get("is_digital", False))
                else:
                    new_is_digital = False
                
                col_save, col_cancel = st.columns(2)
                with col_save:
                    if st.form_submit_button("💾 Lagre endringer"):
                        for r in st.session_state.data["risks"]:
                            if r["id"] == risk["id"]:
                                r["title"] = new_title
                                r["description"] = new_description
                                r["owner"] = new_owner
                                r["tags"] = new_tags
                                r["exposure"] = new_exposure if new_exposure > 0 else None
                                r["is_digital"] = new_is_digital
                                r["last_updated"] = datetime.now().isoformat()
                        save_data(st.session_state.data)
                        st.session_state[f"editing_risk_{risk.get('id')}"] = False
                        st.success("Risiko oppdatert!")
                        st.rerun()
                with col_cancel:
                    if st.form_submit_button("❌ Avbryt"):
                        st.session_state[f"editing_risk_{risk.get('id')}"] = False
                        st.rerun()
        
        # Score-oppdatering
        new_prob = st.selectbox("Sannsynlighet", [1,2,3,4,5], index=risk.get("probability", 3)-1, key=f"prob_{risk.get('id')}")
        new_cons = st.selectbox("Konsekvens", [1,2,3,4,5], index=risk.get("consequence", 3)-1, key=f"cons_{risk.get('id')}")
        
        status_options = ["Aktiv", "Mitigert", "Inntruffet"]
        current_status_index = get_status_index(risk.get("status", "Aktiv"))
        new_status = st.selectbox("Status", status_options, index=current_status_index, key=f"status_{risk.get('id')}")
        
        actual_cost = None
        occurred_date = None
        if new_status == "Inntruffet":
            st.markdown("---")
            st.markdown("**Inntruffet-detaljer:**")
            actual_cost = st.number_input("Faktisk kostnad (kr)", min_value=0, value=risk.get("actual_cost", 0) or 0, step=10000, key=f"actual_cost_{risk.get('id')}")
            occurred_date = st.date_input("Dato inntruffet", value=datetime.now().date(), key=f"occurred_date_{risk.get('id')}")
        
        if st.button("Oppdater score/status", key=f"update_{risk.get('id')}"):
            for r in st.session_state.data["risks"]:
                if r["id"] == risk["id"]:
                    old_score = r.get("probability", 1) * r.get("consequence", 1)
                    new_score = new_prob * new_cons
                    
                    if old_score != new_score:
                        if "score_history" not in r:
                            r["score_history"] = []
                        r["score_history"].append({
                            "date": datetime.now().isoformat(),
                            "score": new_score,
                            "probability": new_prob,
                            "consequence": new_cons
                        })
                    
                    r["probability"] = new_prob
                    r["consequence"] = new_cons
                    r["status"] = new_status
                    r["last_updated"] = datetime.now().isoformat()
                    
                    if new_status == "Inntruffet":
                        r["actual_cost"] = actual_cost
                        r["occurred_date"] = str(occurred_date) if occurred_date else None
            
            save_data(st.session_state.data)
            st.success("Risiko oppdatert!")
            st.rerun()
        
        # FASE 5: Slett risiko
        st.markdown("---")
        if st.button("🗑️ Slett risiko", key=f"delete_risk_btn_{risk.get('id')}", type="secondary"):
            st.session_state[f"confirm_delete_risk_{risk.get('id')}"] = True
            st.rerun()
        
        if st.session_state.get(f"confirm_delete_risk_{risk.get('id')}", False):
            st.warning("⚠️ Er du sikker? Dette sletter også alle tilhørende tiltak!")
            col_yes, col_no = st.columns(2)
            with col_yes:
                if st.button("Ja, slett", key=f"confirm_del_risk_{risk.get('id')}"):
                    # Slett tilhørende tiltak
                    st.session_state.data["actions"] = [a for a in st.session_state.data["actions"] if a.get("risk_id") != risk["id"]]
                    # Slett risiko
                    st.session_state.data["risks"] = [r for r in st.session_state.data["risks"] if r["id"] != risk["id"]]
                    save_data(st.session_state.data)
                    st.session_state[f"confirm_delete_risk_{risk.get('id')}"] = False
                    st.success("Risiko slettet!")
                    st.rerun()
            with col_no:
                if st.button("Nei, avbryt", key=f"cancel_del_risk_{risk.get('id')}"):
                    st.session_state[f"confirm_delete_risk_{risk.get('id')}"] = False
                    st.rerun()
        
        # Discovery method
        if risk.get("discovery_method"):
            st.markdown("---")
            st.markdown(f"**Identifisert via:** {risk.get('discovery_method')}")
        
        # Score-historikk
        if risk.get("score_history") and len(risk.get("score_history", [])) > 1:
            st.markdown("---")
            st.markdown("**Score-historikk:**")
            history = risk.get("score_history", [])[-6:]
            cols = st.columns(len(history))
            for i, entry in enumerate(history):
                score_val = entry.get('score', 0)
                date_str = entry.get("date", "")[:10]
                if score_val >= 20:
                    color = "🔴"
                elif score_val >= 12:
                    color = "🟠"
                elif score_val >= 6:
                    color = "🟡"
                else:
                    color = "🟢"
                with cols[i]:
                    st.markdown(f"{color} **{score_val}**")
                    st.caption(date_str[5:] if len(date_str) > 5 else date_str)
