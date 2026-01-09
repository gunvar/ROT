"""
ROT - Datafunksjoner og hjelpefunksjoner
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path

DATA_FILE = Path("data.json")

# --- AUTENTISERING ---
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_default_users():
    return {"admin": {"password_hash": hash_password("admin123"), "role": "admin", "name": "Administrator", "projects": []}}

def authenticate(username, password, users):
    if username in users and users[username]["password_hash"] == hash_password(password):
        return True
    return False

def check_project_access(user, project_id, data):
    if user["role"] == "admin":
        return True
    return project_id in user.get("projects", [])

# --- DATAFUNKSJONER ---
def load_data():
    if DATA_FILE.exists():
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if "users" not in data:
                data["users"] = get_default_users()
            return data
    return {"projects": [], "risks": [], "actions": [], "users": get_default_users()}

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)

def generate_id():
    return datetime.now().strftime("%Y%m%d%H%M%S%f")

# --- HJELPEFUNKSJONER ---
def get_inactive_days(last_updated):
    if not last_updated:
        return 999
    try:
        last_date = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
        return (datetime.now() - last_date.replace(tzinfo=None)).days
    except:
        return 999

def get_trend_indicator(risk):
    history = risk.get("score_history", [])
    if len(history) < 2:
        return "➖", "stable", 0
    current, previous = history[-1]["score"], history[-2]["score"]
    change = current - previous
    if current > previous:
        return "↗️", "up", change
    elif current < previous:
        return "↘️", "down", change
    return "➖", "stable", 0

def get_project_trend(project_id, data):
    project_risks = [r for r in data.get("risks", []) if r.get("project_id") == project_id and r.get("status") == "Aktiv"]
    if not project_risks:
        return "➖", "Ingen aktive risikoer"
    total_change = sum(get_trend_indicator(r)[2] for r in project_risks)
    if total_change > 0:
        return "↗️", f"Økt risiko (+{total_change})"
    elif total_change < 0:
        return "↘️", f"Redusert risiko ({total_change})"
    return "➖", "Stabil"

def get_status_index(status):
    statuses = ["Aktiv", "Mitigert", "Inntruffet"]
    try:
        return statuses.index(status)
    except:
        return 0

def filter_risks_by_access(risks, user, data):
    if user.get("role") == "admin":
        return risks
    return [r for r in risks if r.get("project_id") in user.get("projects", [])]

def get_project_name(project_id, data):
    project = next((p for p in data.get("projects", []) if p["id"] == project_id), None)
    return project["name"] if project else "Ukjent"

def get_project_by_id(project_id, data):
    return next((p for p in data.get("projects", []) if p["id"] == project_id), None)

def get_risk_title(risk_id, data):
    risk = next((r for r in data.get("risks", []) if r["id"] == risk_id), None)
    return risk.get("title", "Ukjent") if risk else "Ukjent"

def get_risk_by_id(risk_id, data):
    return next((r for r in data.get("risks", []) if r["id"] == risk_id), None)

def get_action_by_id(action_id, data):
    return next((a for a in data.get("actions", []) if a["id"] == action_id), None)

# --- PDF GENERERING ---
def generate_pdf_html(title, content, date_str):
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; color: #333; }}
            h1 {{ color: #1e3a5f; border-bottom: 2px solid #1e3a5f; padding-bottom: 10px; }}
            h2 {{ color: #2a5298; margin-top: 30px; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            th {{ background: #1e3a5f; color: white; padding: 12px; text-align: left; }}
            td {{ padding: 10px; border-bottom: 1px solid #ddd; }}
            tr:nth-child(even) {{ background: #f9f9f9; }}
            .header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; }}
            .date {{ color: #666; font-size: 0.9em; }}
            .score-high {{ background: #e63946; color: white; padding: 2px 8px; border-radius: 4px; }}
            .score-medium {{ background: #f4a261; color: white; padding: 2px 8px; border-radius: 4px; }}
            .score-low {{ background: #2a9d8f; color: white; padding: 2px 8px; border-radius: 4px; }}
            .status-open {{ color: #e63946; }}
            .status-done {{ color: #2a9d8f; }}
            .footer {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; font-size: 0.8em; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🎯 ROT - {title}</h1>
            <span class="date">Generert: {date_str}</span>
        </div>
        {content}
        <div class="footer">
            Risk & Opportunity Tracker | Generert {date_str}
        </div>
    </body>
    </html>
    """

def generate_top10_pdf_content(risks, data):
    if not risks:
        return "<p>Ingen aktive risikoer funnet.</p>"
    rows = ""
    for i, risk in enumerate(risks[:10], 1):
        score = risk.get("probability", 1) * risk.get("consequence", 1)
        project_name = get_project_name(risk.get("project_id"), data)
        exposure = risk.get("exposure", 0) or 0
        exposure_str = f"{exposure:,}".replace(",", " ") + " kr" if exposure else "-"
        score_class = "score-high" if score >= 16 else "score-medium" if score >= 9 else "score-low"
        type_icon = "⚠️" if risk.get("type") == "Risiko" else "💡"
        digital_tag = " 🤖" if risk.get("is_digital") else ""
        rows += f"<tr><td>{i}</td><td>{project_name}</td><td>{type_icon} {risk.get('title', '-')}{digital_tag}</td><td><span class=\"{score_class}\">{score}</span></td><td>{exposure_str}</td><td>{risk.get('owner', '-')}</td></tr>"
    return f"<h2>Topp 10 Risikoer og Muligheter</h2><table><tr><th>#</th><th>Prosjekt</th><th>Risiko/Mulighet</th><th>S×K</th><th>Eksponering</th><th>Eier</th></tr>{rows}</table>"

def generate_project_pdf_content(project, risks, actions, data):
    active_risks = [r for r in risks if r.get("status") == "Aktiv"]
    critical = [r for r in active_risks if r.get("probability", 1) * r.get("consequence", 1) >= 16]
    total_exposure = sum(r.get("exposure", 0) or 0 for r in active_risks)
    content = f"""
    <h2>Prosjektinformasjon</h2>
    <table><tr><td><strong>Oppdragsnummer:</strong></td><td>{project.get('number', '-')}</td></tr>
    <tr><td><strong>Prosjektnavn:</strong></td><td>{project.get('name', '-')}</td></tr>
    <tr><td><strong>Oppdragsleder:</strong></td><td>{project.get('ol', '-')}</td></tr>
    <tr><td><strong>Kontraktsverdi:</strong></td><td>{project.get('value', 0)} MNOK</td></tr></table>
    <h2>Risikooversikt</h2>
    <table><tr><td><strong>Aktive risikoer:</strong></td><td>{len(active_risks)}</td></tr>
    <tr><td><strong>Kritiske (S×K ≥ 16):</strong></td><td>{len(critical)}</td></tr>
    <tr><td><strong>Total eksponering:</strong></td><td>{total_exposure:,} kr</td></tr></table>
    """.replace(",", " ")
    if risks:
        rows = ""
        for risk in sorted(risks, key=lambda r: r.get("probability", 1) * r.get("consequence", 1), reverse=True):
            score = risk.get("probability", 1) * risk.get("consequence", 1)
            score_class = "score-high" if score >= 16 else "score-medium" if score >= 9 else "score-low"
            type_icon = "⚠️" if risk.get("type") == "Risiko" else "💡"
            rows += f"<tr><td>{type_icon} {risk.get('title', '-')}</td><td><span class=\"{score_class}\">{score}</span></td><td>{risk.get('status', '-')}</td><td>{risk.get('owner', '-')}</td></tr>"
        content += f"<h2>Alle risikoer og muligheter</h2><table><tr><th>Tittel</th><th>S×K</th><th>Status</th><th>Eier</th></tr>{rows}</table>"
    if actions:
        rows = ""
        for action in actions:
            risk = get_risk_by_id(action.get("risk_id"), data)
            risk_title = risk.get("title", "-") if risk else "-"
            status_icon = "✅" if action.get("status") == "Gjennomført" else "⏳"
            rows += f"<tr><td>{risk_title}</td><td>{action.get('description', '-')}</td><td>{action.get('responsible', '-')}</td><td>{action.get('deadline', '-')}</td><td>{status_icon} {action.get('status', '-')}</td></tr>"
        content += f"<h2>Tiltak</h2><table><tr><th>Risiko</th><th>Tiltak</th><th>Ansvarlig</th><th>Frist</th><th>Status</th></tr>{rows}</table>"
    return content

def generate_actions_pdf_content(actions, data):
    if not actions:
        return "<p>Ingen tiltak funnet.</p>"
    rows = ""
    for action in actions:
        risk = get_risk_by_id(action.get("risk_id"), data)
        risk_title = risk.get("title", "-") if risk else "-"
        project_name = get_project_name(risk.get("project_id"), data) if risk else "-"
        status_icon = "✅" if action.get("status") == "Gjennomført" else "⏳"
        deadline = action.get("deadline", "")
        deadline_display = deadline
        if deadline and action.get("status") == "Åpen":
            try:
                if datetime.strptime(deadline, "%Y-%m-%d").date() < datetime.now().date():
                    deadline_display = f"<span style='color: #e63946; font-weight: bold;'>{deadline} (FORFALT)</span>"
            except:
                pass
        rows += f"<tr><td>{project_name}</td><td>{risk_title}</td><td>{action.get('description', '-')}</td><td>{action.get('responsible', '-')}</td><td>{deadline_display}</td><td>{status_icon} {action.get('status', '-')}</td></tr>"
    return f"<h2>Tiltaksoversikt</h2><table><tr><th>Prosjekt</th><th>Risiko/Mulighet</th><th>Tiltak</th><th>Ansvarlig</th><th>Frist</th><th>Status</th></tr>{rows}</table>"
