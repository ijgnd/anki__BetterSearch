from aqt import mw

from .config import conf_to_key, gc, shiftdown, ctrldown, altdown, metadown


def cardnames(col):
    cards = set()
    for m in col.models.all():
        for t in m['tmpls']:
            cards.add(t['name'])
    return list(cards)


def decknames(col, also_include_filtered, prepend_with_deck=False):
    decks = col.decks.allNames(dyn=also_include_filtered)
    # also_include_filtered only True in the browser but not in the Create Filtered Deck dialog
    # Filtered decks can't include filtered decks so I don't want "filtered" for those.
    if also_include_filtered:  
        decks += ["filtered"]
    if prepend_with_deck:
        decks = ["deck:" + d  for d in decks]
    return sorted(decks)


def tags(col, prepend_with_tag=False):
    tags = col.tags.all() + ["none"]
    if prepend_with_tag:  # for xx1 and xx2
        tags =  ["tag:" + t for t in tags]
    return sorted(tags)


def is_values():
    return [
        "is:due",
        "is:new",
        "is:learn",
        "is:review",
        "is:suspended",
        "is:buried",
        "is:learn is:review",
        "-is:learn is:review",
        "is:learn -is:review",
    ]


def is_values_with_explanations():
    return {
    "is:due (review cards and learning cards waiting to be studied)" : "is:due",
    "is:new (new cards)" : "is:new",
    "is:learn (cards in learning)" : "is:learn",
    "is:review (reviews (both due and not due) and lapsed cards)" : "is:review",
    "is:suspended (cards that have been manually suspended)" : "is:suspended",
    "is:buried (cards that have been buried, either automatically (siblings) or manually)" : "is:buried",
    "is:learn is:review (cards that have lapsed and are awaiting relearning)" : "is:learn is:review",
    "-is:learn is:review (review cards, not including lapsed cards)" : "-is:learn is:review",
    "is:learn -is:review (cards that are in learning for the first time)" : "is:learn -is:review",
    }


def props():
    return {
        "prop:due=-1 - cards due yesterday that haven't been answered yet": "prop:due=",
        "prop:due=1 - cards due tomorrow": "prop:due=",
        "prop:due>-1 prop:due<1 - cards due between yesterday and tomorrow": "prop:due> prop:due<",
        "prop:ease!=2.5 - cards easier or harder than default": "prop:ease!=",
        "prop:ivl>=10 - cards with interval of 10 days or more": "prop:ivl>=",
        "prop:lapses>3 - cards that have moved into relearning more than 3 times": "prop:lapses>",
        "prop:reps<10 - cards that have been answered less than 10 times": "prop:reps<",
    }


def fieldnames():
    fieldnames = set()
    for model in mw.col.models.all():
        for t in model["flds"]:
            fieldnames.add(t["name"] + ":")
    return list(fieldnames)


def overrides():
    # 4 Modifiers = 4 Overrides
    #   SHIFT: override autosearch default
    #   META : override add * default  # originally Ctrl 
    #   ALT  : negate
    #   CTRL : insert current text only : already used in dialog
    lineonly = False
    if conf_to_key[gc("modifier for insert current text only")]():
        lineonly = True
    override_autosearch_default = False
    if conf_to_key[gc("modifier for override autosearch default")]():
        override_autosearch_default = True
    override_add_star = False
    if conf_to_key[gc("modifier for override add * default")]():
        override_add_star = True
    negate = False
    if conf_to_key[gc("modifier for negate")]():
        negate = True
    # print(f"ctrl - lineonly is {lineonly}")
    # print(f"shift - override_autosearch_default is {override_autosearch_default}")
    # print(f"meta - override_add_star is {override_add_star}")
    # print(f"alt - negate is {negate}")
    return lineonly, override_autosearch_default, override_add_star, negate


field_infotext = (
"<b>"
"This dialog only inserts the field name to search. After closing the dialog you <br>"
"must enter the actual search term for the field.</b><br>"
"When searching fields keep in mind that searching on fields requires an 'exact match' by default.<br>"
"Examples from the manual:<br><br>"
"front:dog<br>"
'&nbsp;&nbsp;&nbsp;&nbsp;find notes with a field named "Front" of exactly “dog”. A field that says “a dog” will not match.<br>'
'front:*dog*<br>'
'&nbsp;&nbsp;&nbsp;&nbsp;find notes with a field named "Front" containing dog somewhere<br>'
'front:<br>'
'&nbsp;&nbsp;&nbsp;&nbsp;find notes that have an empty field named "Front"<br>'
'front:_*<br>'
'&nbsp;&nbsp;&nbsp;&nbsp;find notes that have a non-empty field named "Front"<br>'
'front:*<br>'
'&nbsp;&nbsp;&nbsp;&nbsp;find notes that have a field named "Front", empty or not<br>'
'fr*:text<br>'
'&nbsp;&nbsp;&nbsp;&nbsp;find notes in a field whose name is starting with “fr”<br>'
)
