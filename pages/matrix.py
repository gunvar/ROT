"""
ROT - Risikooversikt (kategorisert liste)
"""

import streamlit as st
from data import filter_risks_by_access, get_project_name

def show_risk_matrix(data, user, project_filter):
    st.markdown('<h1 class="main-title">🎯 Risikooversikt</h1>', unsafe_allow_html=True)
    
    risks = filter_risks_by_access(data.get("risks", []), user, data)
    active_risks = [r for r in risks if r.get("status") == "Aktiv" and r.get("type") == "Risiko"]
    
    if project_filter != "Alle prosjekter":
        active_risks = [r for r in active_risks if get_project_name(r.get("project_id"), data) == project_filter]
    
    st.markdown(f"**Viser {len(active_risks)} aktive risikoer**" + (f" for {project_filter}" if project_filter != "Alle prosjekter" else ""))
    
    # Fargeskala
    st.markdown("---")
    st.markdown("### Fargeskala (Sannsynlighet × Konsekvens)")
    leg_cols = st.columns(5)
    colors_info = [
        ("#2a9d8f", "🟢 1-3", "Svært lav"),
        ("#a8dadc", "🔵 4-8", "Lav"),
        ("#e9c46a", "🟡 9-14", "Middels"),
        ("#f4a261", "🟠 15-19", "Høy"),
        ("#e63946", "🔴 20-25", "Kritisk")
    ]
    for i, (color, icon_label, text) in enumerate(colors_info):
        with leg_cols[i]:
            st.markdown(f'<div style="background: {color}; color: white; padding: 10px; border-radius: 8px; text-align: center;"><strong>{icon_label}</strong><br><small>{text}</small></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Grupper risikoer etter score
    score_groups = {
        "critical": {"name": "🔴 Kritisk (20-25)", "color": "#e63946", "risks": [], "min": 20, "max": 25},
        "high": {"name": "🟠 Høy (15-19)", "color": "#f4a261", "risks": [], "min": 15, "max": 19},
        "medium": {"name": "🟡 Middels (9-14)", "color": "#e9c46a", "risks": [], "min": 9, "max": 14},
        "low": {"name": "🔵 Lav (4-8)", "color": "#a8dadc", "risks": [], "min": 4, "max": 8},
        "very_low": {"name": "🟢 Svært lav (1-3)", "color": "#2a9d8f", "risks": [], "min": 1, "max": 3}
    }
    
    for risk in active_risks:
        score = risk.get("probability", 1) * risk.get("consequence", 1)
        if score >= 20:
            score_groups["critical"]["risks"].append(risk)
        elif score >= 15:
            score_groups["high"]["risks"].append(risk)
        elif score >= 9:
            score_groups["medium"]["risks"].append(risk)
        elif score >= 4:
            score_groups["low"]["risks"].append(risk)
        else:
            score_groups["very_low"]["risks"].append(risk)
    
    # Vis statistikk
    col1, col2, col3, col4, col5 = st.columns(5)
    cols = [col1, col2, col3, col4, col5]
    for i, (key, group) in enumerate(score_groups.items()):
        with cols[i]:
            count = len(group["risks"])
            st.markdown(f'<div class="stat-card" style="border-left: 4px solid {group["color"]};"><div class="stat-number">{count}</div><div class="stat-label" style="font-size: 0.7rem;">{group["name"].split(" ")[0]}</div></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### Risikoer per nivå")
    
    # Vis lister for hver gruppe
    for key, group in score_groups.items():
        group_risks = group["risks"]
        count = len(group_risks)
        
        if count > 0:
            with st.expander(f"{group['name']} — {count} risiko{'er' if count != 1 else ''}", expanded=(key in ["critical", "high"])):
                sorted_risks = sorted(group_risks, key=lambda r: r.get("probability", 1) * r.get("consequence", 1), reverse=True)
                
                for risk in sorted_risks:
                    project_name = get_project_name(risk.get("project_id"), data)
                    score = risk.get("probability", 1) * risk.get("consequence", 1)
                    prob = risk.get("probability", "-")
                    cons = risk.get("consequence", "-")
                    
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #1a2332 0%, #0f1419 100%); 
                                border-radius: 8px; padding: 1rem; margin-bottom: 0.5rem; 
                                border-left: 4px solid {group['color']};">
                        <div style="display: flex; justify-content: space-between; align-items: start;">
                            <div>
                                <strong style="color: #f1f5f9;">⚠️ {risk.get('title', 'Uten tittel')}</strong>
                                <p style="color: #94a3b8; margin: 0.25rem 0 0 0; font-size: 0.85rem;">{project_name}</p>
                            </div>
                            <div style="text-align: right;">
                                <span style="background: {group['color']}; color: white; padding: 0.2rem 0.5rem; border-radius: 12px; font-weight: 700; font-size: 0.85rem;">S×K: {score}</span>
                                <p style="color: #64748b; margin: 0.25rem 0 0 0; font-size: 0.75rem;">S:{prob} × K:{cons} | Eier: {risk.get('owner', '-')}</p>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            with st.expander(f"{group['name']} — 0 risikoer"):
                st.markdown("*Ingen risikoer i denne kategorien*")
    
    # Oppsummering
    st.markdown("---")
    if not active_risks:
        st.success("✅ Ingen aktive risikoer registrert!")
    else:
        critical_count = len(score_groups["critical"]["risks"])
        high_count = len(score_groups["high"]["risks"])
        if critical_count > 0:
            st.warning(f"⚠️ **{critical_count} kritisk{'e' if critical_count != 1 else ''} risiko{'er' if critical_count != 1 else ''}** krever umiddelbar oppmerksomhet!")
        elif high_count > 0:
            st.info(f"📊 **{high_count} høy{'e' if high_count != 1 else ''} risiko{'er' if high_count != 1 else ''}** bør følges opp.")
