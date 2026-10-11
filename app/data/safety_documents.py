"""Sample safety documents for the demo assistant (fictional, short)."""
DOCUMENTS = [
    {"id": "D1", "title": "PPE Standard", "chunks": [
        "Minimum PPE in all work areas: hard hat, safety boots, high-visibility vest and safety glasses. Add gloves and hearing protection where the task requires them.",
        "PPE required for working at height: full-body harness with shock-absorbing lanyard, hard hat with chin strap, safety boots and gloves. Inspect the harness before every use and tag out damaged equipment.",
        "Electrical work PPE: insulated gloves rated for the voltage, arc-rated clothing where required, and insulated tools.",
    ]},
    {"id": "D2", "title": "Working at Height Procedure", "chunks": [
        "Work at height needs an approved permit, a trained and authorised worker, and a rescue plan agreed before work starts.",
        "Guardrails or edge protection must be in place. Keep three points of contact on ladders and secure all tools against falling. Keep the area below clear.",
        "Stop work at height in high wind, lightning or heavy rain, and report the conditions to the supervisor.",
    ]},
    {"id": "D3", "title": "Emergency Response Procedure", "chunks": [
        "Emergency procedure: on hearing the alarm stop work, make equipment safe, leave by the nearest exit and go to the muster point. Do not collect belongings. Wait for the head count.",
        "For an injury call the emergency number, give your location and what happened, send someone to meet responders, and do not move the casualty unless they are in danger.",
        "For a fire raise the alarm, use an extinguisher only if it is safe and you are trained, and evacuate if the fire grows.",
    ]},
    {"id": "D4", "title": "Electrical Safety and Lock-out", "chunks": [
        "Treat all conductors as live until isolated, tested and locked out. Each worker fits their own lock and tag and only that worker removes it.",
        "Keep safe distances from overhead lines. Use inspected, insulated tools and remove damaged leads from service immediately.",
    ]},
    {"id": "D5", "title": "Hot Work and Fire Safety", "chunks": [
        "Hot work such as welding or cutting needs a signed permit. Clear or cover combustible materials within 10 metres.",
        "Keep a fire watcher with an extinguisher during hot work and for 30 minutes after it finishes.",
    ]},
]
