"""
ROT - Risk & Opportunity Tracker
Fase 5: Modulær struktur med CRUD-komplettering

Entry point for applikasjonen.
"""

import streamlit as st
from config import CUSTOM_CSS
from data import load_data, save_data, authenticate, get_default_users, hash_password

# Sider
from pages.dashboard import show_dashboard, show_needs_attention
from pages.actions import show_actions_overview
from pages.matrix import show_risk_matrix
from pages.hjelpemidler import show_hjelpemidler
from pages.add_risk import show_add_risk
from pages.projects import show_projects
from pages.export_pdf import show_export_pdf
from pages.users import show_users
from pages.admin import show_admin

# Konfigurasjon
st.set_page_config(
    page_title="ROT - Risk & Opportunity Tracker",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Styling
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def show_login():
    """Viser innloggingssiden"""
    st.markdown('<h1 class="main-title" style="text-align: center;">🎯 ROT</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #94a3b8;">Risk & Opportunity Tracker</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### Logg inn")
        username = st.text_input("Brukernavn")
        password = st.text_input("Passord", type="password")
        
        if st.button("Logg inn", use_container_width=True):
            data = load_data()
            users = data.get("users", get_default_users())
            if authenticate(username, password, users):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.user = users[username]
                st.rerun()
            else:
                st.error("Feil brukernavn eller passord")
        
        st.markdown("---")
        st.caption("Standard admin-innlogging: admin / admin123")


def main():
    """Hovedapplikasjon"""
    # Sjekk innlogging
    if 'logged_in' not in st.session_state or not st.session_state.logged_in:
        show_login()
        return
    
    # Last data
    if 'data' not in st.session_state:
        st.session_state.data = load_data()
    
    # Hent prefill-verdier fra Hjelpemidler
    prefill_type = st.session_state.get('prefill_type', None)
    prefill_method = st.session_state.get('prefill_method', None)
    prefill_question = st.session_state.get('prefill_question', None)
    
    data = st.session_state.data
    user = st.session_state.user
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 🎯 ROT")
        st.markdown("*Risk & Opportunity Tracker*")
        st.markdown(f"**{user.get('name', st.session_state.username)}**")
        role_label = "👑 Admin" if user.get("role") == "admin" else "👤 Oppdragsleder"
        st.caption(role_label)
        
        if st.button("Logg ut", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.user = None
            st.rerun()
        
        st.markdown("---")
        
        # Navigasjon
        nav_options = [
            "📊 Dashboard", 
            "⚠️ Trenger oppfølging", 
            "📋 Tiltaksoversikt",
            "🎯 Risikooversikt",
            "📚 Hjelpemidler",
            "➕ Ny risiko/mulighet", 
            "📁 Prosjekter",
            "📄 Eksporter PDF"
        ]
        if user.get("role") == "admin":
            nav_options.append("👥 Brukere")
            nav_options.append("⚙️ Administrasjon")
        
        # Hvis prefill er satt, gå til registrering
        default_index = 0
        if prefill_type:
            default_index = nav_options.index("➕ Ny risiko/mulighet")
        
        page = st.radio("Navigasjon", nav_options, index=default_index, label_visibility="collapsed")
        
        st.markdown("---")
        st.markdown("### Filtrering")
        
        # Prosjektfilter
        if user.get("role") == "admin":
            projects = [p["name"] for p in data.get("projects", [])]
        else:
            user_project_ids = user.get("projects", [])
            projects = [p["name"] for p in data.get("projects", []) if p["id"] in user_project_ids]
        
        selected_project = st.selectbox("Prosjekt", ["Alle prosjekter"] + projects)
        type_filter = st.selectbox("Type", ["Alle", "Risiko", "Mulighet"])
        owner_filter = st.selectbox("Eier", ["Alle", "Firma", "Kunde"])
        status_filter = st.selectbox("Status", ["Aktive", "Mitigerte", "Inntruffet", "Alle"])
        
        # Digital/KI filter
        show_digital_only = False
        if type_filter in ["Alle", "Mulighet"]:
            show_digital_only = st.checkbox("🤖 Kun Digitalisering/KI")
        
        sort_option = st.selectbox("Sorter etter", ["Score (høyest først)", "Eksponering (høyest først)", "Sist oppdatert", "Inaktive først"])
    
    # Routing til riktig side
    if page == "📊 Dashboard":
        show_dashboard(data, user, selected_project, type_filter, owner_filter, status_filter, sort_option, show_digital_only)
    elif page == "⚠️ Trenger oppfølging":
        show_needs_attention(data, user)
    elif page == "📋 Tiltaksoversikt":
        show_actions_overview(data, user)
    elif page == "🎯 Risikooversikt":
        show_risk_matrix(data, user, selected_project)
    elif page == "📚 Hjelpemidler":
        show_hjelpemidler(data, user)
    elif page == "➕ Ny risiko/mulighet":
        show_add_risk(data, user, prefill_type, prefill_method, prefill_question)
    elif page == "📁 Prosjekter":
        show_projects(data, user)
    elif page == "📄 Eksporter PDF":
        show_export_pdf(data, user)
    elif page == "👥 Brukere":
        show_users(data)
    elif page == "⚙️ Administrasjon":
        show_admin(data)


if __name__ == "__main__":
    main()
