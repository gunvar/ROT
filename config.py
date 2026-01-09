"""
ROT - Konfigurasjon og konstanter
"""

# Discovery methods for tagging
DISCOVERY_METHODS = [
    "(Ikke angitt)",
    "Pre-Mortem",
    "De 5 skarpe spørsmålene",
    "Leveransesjekkpunkter",
    "Elon Musks Algoritme",
    "Digitaliserings-radar",
    "Mentorprat (generell)",
    "Egenidentifisert"
]

# Hjelpemidler-innhold
HJELPEMIDLER = {
    "risiko": {
        "Pre-Mortem": {
            "beskrivelse": "Se for deg at vi er 6 måneder frem i tid og prosjektet har feilet totalt. Hva skjedde?",
            "sporsmal": [
                "Hvilken teknisk antakelse sviktet?",
                "Hvilken kontraktuell endring (VEM) ble ikke fanget opp?",
                "Hvem i teamet forsvant, og hvorfor var det kritisk?"
            ]
        },
        "De 5 skarpe spørsmålene": {
            "beskrivelse": "Bruk disse som diskusjonsstartere i mentorpraten.",
            "sporsmal": [
                "Hva er den ene tingen som kan stoppe prosjektet i morgen?",
                "Hvor kommer det største potensielle økonomiske tapet fra?",
                "Hva er kunden mest misfornøyd med (uten at de har sagt det)?",
                "Hvilken uavklart diskusjon gruer du deg mest til å ta med kunden?",
                "Hvem sitter på kritisk kunnskap som ikke er delt?"
            ]
        },
        "Leveransesjekkpunkter": {
            "beskrivelse": "Kvalitets- og leveranserisiko for konsulenttjenester.",
            "sporsmal": [
                "Har kunden sett og godkjent forutsetningene våre?",
                "Finnes det et dokument vi skal levere som ingen har begynt på?",
                "Hvem skal kvalitetssikre leveransen, og har de tid?",
                "Hva skjer hvis kunden sier 'dette var ikke det vi ba om'?"
            ]
        }
    },
    "mulighet": {
        "Elon Musks Algoritme": {
            "beskrivelse": "5 steg for effektivisering og økt dekningsgrad.",
            "sporsmal": [
                "Gjør kravene mindre dumme: Hvem satte kravet? Er det nødvendig?",
                "Slett deler eller prosesser: Hva kan fjernes uten å påvirke verdien?",
                "Forenkle/Optimaliser: Hvordan gjøre det gjenværende mer effektivt?",
                "Akselerer: Hvordan kan vi øke farten på ledetiden?",
                "Automatiser: Hva kan settes strøm på (først etter steg 1-4)?"
            ]
        },
        "Digitaliserings-radar": {
            "beskrivelse": "Finn oppgaver med høy gjentakelse og lav kreativ verdi.",
            "sporsmal": [
                "Hva i dette prosjektet føles som 'copy-paste'-arbeid?",
                "Kan vi bruke KI for å generere førsteutkast til rapporter eller analyser?",
                "Kan vi automatisere samsvarskontroll mot standarder/håndbøker?"
            ]
        }
    }
}

# CSS Styling
CUSTOM_CSS = """
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .main .block-container { padding-top: 2rem; max-width: 1400px; }
    .stat-card {
        background: linear-gradient(135deg, #1a2332 0%, #0f1419 100%);
        border-radius: 12px; padding: 1.5rem; text-align: center; border: 1px solid #2a3a4a;
    }
    .stat-number { font-size: 2.5rem; font-weight: 800; color: #f1f5f9; }
    .stat-label { color: #94a3b8; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px; }
    .main-title {
        font-size: 2.5rem; font-weight: 800;
        background: linear-gradient(135deg, #f1f5f9 0%, #94a3b8 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0.5rem;
    }
    .stButton > button {
        background: linear-gradient(135deg, #1e3a5f 0%, #2a5298 100%);
        color: white; border: none; border-radius: 8px; padding: 0.5rem 1.5rem; font-weight: 600;
    }
    .project-card {
        background: linear-gradient(135deg, #1a2332 0%, #0f1419 100%);
        border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem; border: 1px solid #2a3a4a;
    }
    .method-card {
        background: linear-gradient(135deg, #1a2332 0%, #0f1419 100%);
        border-radius: 8px; padding: 1rem; margin: 0.5rem 0; border-left: 3px solid #2a9d8f;
    }
    .question-item {
        background: #0f1419; padding: 0.75rem; border-radius: 6px; margin: 0.5rem 0;
        border: 1px solid #2a3a4a;
    }
    .risk-item {
        background: linear-gradient(135deg, #1a2332 0%, #0f1419 100%);
        border-radius: 8px; padding: 1rem; margin: 0.5rem 0; border: 1px solid #2a3a4a;
        cursor: pointer;
    }
    .risk-item:hover {
        border-color: #3a4a5a;
    }
</style>
"""
