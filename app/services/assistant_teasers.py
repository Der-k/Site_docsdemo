"""Short, rotating prompts shown next to the chat bubble. Each one is something the assistant can really do.
send=True: clicking it sends the prompt. send=False: clicking fills the input so the user can edit it first."""


def _t(text, prompt, send=True):
    return {"text": text, "prompt": prompt, "send": send}


BY_PAGE = {
    "/": [_t("Want a quick safety status? Ask me what's overdue.", "What's overdue?"),
          _t("I can summarize the latest incident for you.", "Summarize the latest incident."),
          _t("Curious which certifications are expiring? Just ask.", "Which certifications are expiring?")],
    "/workforce": [_t("Need to move someone? Try \"move Brian Mwangi to Eastgate\".", "move Brian Mwangi to Eastgate", False),
                   _t("Ask me which certifications are expiring soon.", "Which certifications are expiring?")],
    "/sites": [_t("Ask me what's overdue across your sites.", "What's overdue?"),
               _t("Want the latest inspection findings? I'll summarize them.", "What safety issues were identified during the latest inspection?")],
    "/inductions": [_t("Not sure what PPE is needed? Ask me.", "What PPE is required for working at height?"),
                    _t("Check the emergency procedure before you start. I can show it.", "What is the emergency procedure?")],
    "/inspections": [_t("I can summarize the latest inspection in seconds.", "What safety issues were identified during the latest inspection?"),
                     _t("Spotted something on site? I can prepare an incident report.", "report a near miss at Harbour: ", False)],
    "/incidents": [_t("Want a summary of the latest incident? Just ask.", "Summarize the latest incident."),
                   _t("Say \"close INC-02\" and I'll prepare it for you to confirm.", "close INC-02", False)],
    "/actions": [_t("Ask \"What's overdue?\" and I'll list it for you.", "What's overdue?"),
                 _t("Finished a task? Say \"mark ACT-05 as completed\".", "mark ACT-05 as completed", False)],
}
GENERIC = [_t("Hi! I'm your safety assistant. Ask me anything.", "What PPE is required for working at height?"),
           _t("Questions about site procedures? I'm here to help.", "What is the emergency procedure?")]


def teasers_for(path):
    key = max((k for k in BY_PAGE if k != "/" and path.startswith(k)), key=len, default="/" if path == "/" else None)
    return BY_PAGE.get(key, []) + GENERIC
