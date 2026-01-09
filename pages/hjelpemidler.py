"""
ROT - Hjelpemidler
"""

import streamlit as st
from config import HJELPEMIDLER

def show_hjelpemidler(data, user):
    st.markdown('<h1 class="main-title">📚 Hjelpemidler</h1>', unsafe_allow_html=True)
    st.markdown("Metodikk og spørsmål for å identifisere risikoer og muligheter under mentorpraten.")
    
    st.markdown("---")
    
    # Seksjon A: Risikofasilitering
    st.markdown("## 🔴 Seksjon A: Risikofasilitering")
    st.markdown("*The Skeptic's Corner - Finn det som kan gå galt*")
    
    for method_name, method_data in HJELPEMIDLER["risiko"].items():
        with st.expander(f"**{method_name}**"):
            st.markdown(f"*{method_data['beskrivelse']}*")
            st.markdown("---")
            
            for i, sporsmal in enumerate(method_data["sporsmal"]):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"""
                    <div class="question-item">
                        <strong>{i+1}.</strong> {sporsmal}
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    if st.button("➕ Registrer", key=f"reg_risk_{method_name}_{i}"):
                        st.session_state.prefill_type = "Risiko"
                        st.session_state.prefill_method = method_name
                        st.session_state.prefill_question = sporsmal
                        st.rerun()
    
    st.markdown("---")
    
    # Seksjon B: Mulighetsidentifisering
    st.markdown("## 💡 Seksjon B: Mulighetsidentifisering")
    st.markdown("*The Innovation Lab - Finn det som kan gjøres bedre*")
    
    for method_name, method_data in HJELPEMIDLER["mulighet"].items():
        with st.expander(f"**{method_name}**"):
            st.markdown(f"*{method_data['beskrivelse']}*")
            st.markdown("---")
            
            for i, sporsmal in enumerate(method_data["sporsmal"]):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"""
                    <div class="question-item">
                        <strong>{i+1}.</strong> {sporsmal}
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    if st.button("➕ Registrer", key=f"reg_opp_{method_name}_{i}"):
                        st.session_state.prefill_type = "Mulighet"
                        st.session_state.prefill_method = method_name
                        st.session_state.prefill_question = sporsmal
                        if method_name == "Digitaliserings-radar":
                            st.session_state.prefill_digital = True
                        st.rerun()
    
    st.markdown("---")
    st.info("💡 **Tips:** Klikk på '➕ Registrer' ved et spørsmål for å gå direkte til registreringsskjemaet med metoden forhåndsvalgt.")
