"""Training sections and quiz questions for each induction (fictional sample content)."""


def _q(q, options, answer):
    return {"q": q, "options": options, "answer": answer}


CONTENT = {
    "I1": {"pass_mark": 80, "sections": [
        {"title": "Sign in and site rules", "body": "Everyone signs in and out every day at the site gate. Stay on marked walkways, obey signs and follow your supervisor's instructions. Alcohol and drugs are not permitted on site."},
        {"title": "Personal protective equipment", "body": "Hard hat, safety boots, high-visibility vest and safety glasses are required at all times in work areas. Add gloves, hearing protection or a harness when the task needs them. Replace damaged PPE before you start work."},
        {"title": "Hazards and reporting", "body": "Report every hazard, near miss and injury to your supervisor straight away, however small. You may stop work if a task is unsafe. Never remove guards, barriers or tags."},
        {"title": "Emergencies", "body": "Learn the alarm sound and your muster point. Stop work, make your area safe and go to the muster point without collecting belongings. Wait there for the head count."},
    ], "quiz": [
        _q("When must you sign in and out?", ["Only on your first day", "Every day at the site gate", "Only when leaving early", "Never"], 1),
        _q("Which items are required at all times in work areas?", ["Hard hat only", "Gloves and a harness", "Hard hat, boots, high-visibility vest and glasses", "No PPE if the task is short"], 2),
        _q("You notice a near miss. What do you do?", ["Ignore it", "Report it to your supervisor straight away", "Tell a friend", "Wait for the weekly meeting"], 1),
        _q("May you stop work if a task is unsafe?", ["No", "Only with written permission", "Only after finishing the task", "Yes"], 3),
        _q("When the alarm sounds you should:", ["Collect your belongings first", "Keep working until told", "Go to the muster point and wait for the head count", "Go home"], 2),
    ]},
    "I2": {"pass_mark": 60, "sections": [
        {"title": "Before you climb", "body": "Work at height only if you are trained and your supervisor has approved the task. Inspect your harness, lanyard and anchor point before every use, and check the weather."},
        {"title": "Staying safe up there", "body": "Keep three points of contact on ladders, stay within guardrails and never work beneath others. Secure tools so they cannot fall. Know the rescue plan before you start."},
    ], "quiz": [
        _q("A harness must be inspected:", ["Weekly", "After an incident only", "Before every use", "Only when new"], 2),
        _q("A dropped tool is best prevented by:", ["Shouting a warning", "Securing tools with lanyards", "Working faster", "Wearing gloves"], 1),
        _q("Where should others stand while you work overhead?", ["Directly below", "Next to the ladder only", "Anywhere", "Outside the marked drop zone"], 3),
    ]},
    "I3": {"pass_mark": 60, "sections": [
        {"title": "Isolation and lock-out", "body": "Treat every conductor as live until it is isolated, tested and locked out with your own lock and tag. Only the person who fitted a lock removes it."},
        {"title": "Safe distances and tools", "body": "Keep clear of overhead lines and use only inspected, insulated tools. Report damaged cables immediately and take them out of use."},
    ], "quiz": [
        _q("Until proven isolated, treat a conductor as:", ["Dead", "Live", "Low risk", "Someone else's problem"], 1),
        _q("Who removes your lock-out lock?", ["Any supervisor", "The next shift", "Maintenance", "You, the person who fitted it"], 3),
        _q("A damaged cable should be:", ["Taped and used", "Left for later", "Reported and taken out of use", "Hidden"], 2),
    ]},
    "I4": {"pass_mark": 60, "sections": [
        {"title": "Permits and preparation", "body": "Hot work needs a signed permit. Clear combustible materials within 10 metres or cover them with fire blankets before you start."},
        {"title": "Fire watch", "body": "Keep a fire watcher with an extinguisher during the work and for 30 minutes after it stops."},
    ], "quiz": [
        _q("Hot work requires:", ["A verbal okay", "No paperwork", "A friend nearby", "A signed permit"], 3),
        _q("Fire watch continues after the work stops for:", ["No time", "30 minutes", "1 minute", "Until lunch"], 1),
        _q("Combustible materials near hot work should be:", ["Left in place", "Wetted slightly", "Cleared or covered", "Ignored"], 2),
    ]},
    "I5": {"pass_mark": 60, "sections": [
        {"title": "Alarms and muster points", "body": "Know the alarm tones, your muster point and the nearest exit route. Do not use lifts during an evacuation."},
        {"title": "First response", "body": "Call the emergency number, give your location and what happened, and do not move an injured person unless they are in danger."},
    ], "quiz": [
        _q("First step when someone is injured:", ["Move them quickly", "Take a photo", "Call the emergency number and give your location", "Leave the area"], 2),
        _q("Where do you go when the alarm sounds?", ["Your car", "The site office", "Home", "The muster point"], 3),
        _q("A good emergency call includes:", ["Your location and what happened", "Only your name", "A joke", "Nothing"], 0),
    ]},
}
