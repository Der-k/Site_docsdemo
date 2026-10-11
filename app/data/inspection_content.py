"""Inspection templates (construction / energy sites) and the seeded inspection findings."""


def _i(item_id, category, text, priority="Medium"):
    return {"id": item_id, "category": category, "text": text, "priority": priority}


TEMPLATES = [
    {"id": "T1", "title": "Weekly Site Safety Inspection", "description": "General walk-round for active construction and energy project sites.", "items": [
        _i("T1-01", "PPE", "Hard hats, safety boots and hi-vis worn by everyone in work areas"),
        _i("T1-02", "Housekeeping", "Work areas tidy and walkways clear", "Low"),
        _i("T1-03", "Working at height", "Guardrails and edge protection in place and undamaged", "High"),
        _i("T1-04", "Working at height", "Ladders and scaffolds inspected and tagged"),
        _i("T1-05", "Lifting", "Lifting equipment certified and exclusion zones marked", "High"),
        _i("T1-06", "Electrical", "Leads, panels and portable equipment free from damage", "High"),
        _i("T1-07", "Emergency", "Emergency contact numbers and muster point displayed", "Low"),
        _i("T1-08", "Fire", "Fire extinguishers available and in date"),
        _i("T1-09", "Environment", "Spill kits stocked and waste stored correctly"),
        _i("T1-10", "Permits", "Permits to work current and displayed"),
    ]},
    {"id": "T2", "title": "PPE and Certification Check", "description": "Checks PPE condition and that worker certificates are valid.", "items": [
        _i("T2-01", "PPE", "PPE issued and in good condition"),
        _i("T2-02", "Certification", "Worker certificates valid for the tasks being done", "High"),
        _i("T2-03", "Induction", "Site induction records up to date", "Medium"),
        _i("T2-04", "PPE", "Respiratory protection fit-tested where required"),
        _i("T2-05", "PPE", "Hearing protection available at noisy work areas", "Low"),
        _i("T2-06", "First aid", "First aid kits stocked and first aiders identified"),
    ]},
    {"id": "T3", "title": "Fire and Housekeeping Inspection", "description": "Fire precautions, exits and general housekeeping.", "items": [
        _i("T3-01", "Fire", "Fire extinguishers in date and accessible"),
        _i("T3-02", "Fire", "Fire extinguisher signage in place"),
        _i("T3-03", "Exits", "Exit routes clear and lit", "High"),
        _i("T3-04", "Storage", "Combustible materials stored correctly"),
        _i("T3-05", "Hot work", "Hot work permits displayed where work is under way"),
        _i("T3-06", "Emergency", "Muster point signs visible", "Low"),
    ]},
]

# inspection id -> (failed item, observation, linked corrective action id already in the seed)
SEED_FAILS = {
    "INS-01": ("T1-03", "Section of guardrail damaged on the level 2 walkway.", "ACT-07"),
    "INS-02": ("T2-02", "Two First Aid certificates expired.", "ACT-05"),
    "INS-03": ("T3-02", "Extinguisher point near the fabrication bay has no sign.", "ACT-06"),
    "INS-04": ("T1-07", "Emergency contact board out of date.", "ACT-08"),
}
