from .config import gc

# for multiline add-on
def help_string_for_actions_used():
    lines = []    
    if gc("modify_card"):
        s = '"card:" filter for card (type) names'
        lines.append(s)
    if gc("modify_deck"):
        s = '"deck:" filter by deck name'
        lines.append(s)
    if gc("modify_field"):
        s = '"field:" filter by field name'
        lines.append(s)
    if gc("modify_is"):
        s = '"is:" filter by card state'
        lines.append(s)
    if gc("modify_note"):
        s = '"note:" filter by note type (model) name'
        lines.append(s)
    if gc("modify_props"):
        s = '"prop:" filter by card properties (like due date, ease)'
        lines.append(s)
    if gc("modify_tag"):
        s = '"tag:" filter by tag'
        lines.append(s)
    if gc("custom tag&deck string 1"):
        s = f'"{gc("custom tag&deck string 1")}": filter by deck or tag'
        lines.append(s)
    if gc("custom tag&deck string 2"):
        s = f'"{gc("custom tag&deck string 2")}": filter by deck or tag'
        lines.append(s)
    if gc("date range dialog for added: string"):
        s = f'"{gc("date range dialog for added: string")}": date range dialog for date added'
        lines.append(s)
    if gc("date range dialog for rated: string"):
        s = f'"{gc("date range dialog for rated: string")}": date range dialog for date rated'
        lines.append(s)

    s = "<b>Browser quick insert add-on: words that open the filter dialog:</b>"
    s += "<ul>"
    for l in lines:
        s += "<li>" + l + "</li>"
    s += "</ul>"
    return s
