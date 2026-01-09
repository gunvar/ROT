"""
ROT - Brukerhåndtering
"""

import streamlit as st
from datetime import datetime
from data import save_data, hash_password

def show_users(data):
    st.markdown('<h1 class="main-title">Brukerhåndtering</h1>', unsafe_allow_html=True)
    
    users = data.get("users", {})
    projects = data.get("projects", [])
    
    st.markdown("### Legg til bruker")
    with st.form("new_user_form"):
        col1, col2 = st.columns(2)
        with col1:
            new_username = st.text_input("Brukernavn *")
            new_password = st.text_input("Passord *", type="password")
            new_name = st.text_input("Fullt navn")
        with col2:
            new_role = st.selectbox("Rolle", ["user", "admin"])
            if new_role == "user":
                new_projects = st.multiselect("Tilgang til prosjekter", options=[p["id"] for p in projects], format_func=lambda x: next((p["name"] for p in projects if p["id"] == x), x))
            else:
                new_projects = []
                st.info("Admin har tilgang til alle prosjekter")
        
        if st.form_submit_button("Opprett bruker"):
            if new_username and new_password:
                if new_username in users:
                    st.error("Brukernavn eksisterer allerede")
                else:
                    users[new_username] = {"password_hash": hash_password(new_password), "role": new_role, "name": new_name or new_username, "projects": new_projects, "created": datetime.now().isoformat()}
                    st.session_state.data["users"] = users
                    save_data(st.session_state.data)
                    st.success(f"Bruker '{new_username}' opprettet!")
                    st.rerun()
            else:
                st.error("Fyll ut brukernavn og passord")
    
    st.markdown("---")
    st.markdown("### Eksisterende brukere")
    
    for username, user_data in users.items():
        col1, col2, col3, col4 = st.columns([2, 1, 2, 1])
        with col1:
            role_icon = "👑" if user_data.get("role") == "admin" else "👤"
            st.markdown(f"**{role_icon} {user_data.get('name', username)}**")
            st.caption(f"@{username}")
        with col2:
            st.markdown(f"Rolle: **{user_data.get('role', 'user')}**")
        with col3:
            if user_data.get("role") == "user":
                user_projects = user_data.get("projects", [])
                project_names = [p["name"] for p in projects if p["id"] in user_projects]
                st.caption(f"Prosjekter: {', '.join(project_names) if project_names else 'Ingen'}")
            else:
                st.caption("Tilgang til alle prosjekter")
        with col4:
            if username != "admin" and username != st.session_state.username:
                if st.button("🗑️", key=f"delete_user_{username}"):
                    del st.session_state.data["users"][username]
                    save_data(st.session_state.data)
                    st.rerun()
        
        if user_data.get("role") == "user":
            with st.expander(f"Rediger tilgang for {username}"):
                current_projects = user_data.get("projects", [])
                updated_projects = st.multiselect("Prosjekter", options=[p["id"] for p in projects], default=current_projects, format_func=lambda x: next((p["name"] for p in projects if p["id"] == x), x), key=f"projects_{username}")
                if st.button("Oppdater tilgang", key=f"update_access_{username}"):
                    st.session_state.data["users"][username]["projects"] = updated_projects
                    save_data(st.session_state.data)
                    st.success("Tilgang oppdatert!")
                    st.rerun()
        st.markdown("---")
