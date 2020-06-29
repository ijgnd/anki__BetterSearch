from anki.utils import pointVersion

from .config import gc
from .dialog__date import DateRangeDialog
from .fuzzy_panel import FilterDialog
from .helpers import (
    # this is the order in helpers.py
    cardnames,
    decknames,
    tags,
    is_values,
    is_values_with_explanations,
    props,
    fieldnames,
    overrides,
    field_infotext,
)

def onSearchEditTextChange(parent, move_dialog_in_browser, include_filtered_in_deck, func_gettext, func_settext, mw, col, arg):
    vals = False
    c1 = gc("custom tag&deck string 1", "")
    xx1 = c1 and arg[-len(c1):] == c1
    c2 = gc("custom tag&deck string 2", "")
    xx2 = c2 and arg[-len(c2):] == c2
    da = gc("date range dialog for added: string")
    da_match = da and arg[-len(da):] == da
    dr = gc("date range dialog for rated: string")
    dr_match = da and arg[-len(dr):] == dr   
    # vals = (0 remove some characters from the right of searchboxstring, 
    #         1 InsertSpaceAtPos, 
    #         2 UseFilterDialogValue: if True (use a string that describes it) is True, if list is False
    #         3 FilterDialogLines
    #         4 surround search with ""
    #         5 infotext
    #         6 windowtitle
    #         7 show_prepend_minus_button
    #        )
    # I deliberately use "dr" because usually you won't need a date picker dialog
    if dr_match:
        d = DateRangeDialog(parent, "rated")
        if d.exec():
            TriggerSearchAfter = gc("modify: window opened by search strings triggers search by default")
            lineonly, override_autosearch_default, override_add_star, negate = overrides()
            if override_autosearch_default:
                TriggerSearchAfter ^= True
            func_settext(func_gettext()[:len(dr)] + "  " + d.searchtext)
            return (True, TriggerSearchAfter)
    # I deliberately use "da" because usually you won't need a date picker dialog 
    if da_match:
        d = DateRangeDialog(parent, "added")
        if d.exec():
            TriggerSearchAfter = gc("modify: window opened by search strings triggers search by default")
            lineonly, override_autosearch_default, override_add_star, negate = overrides()
            if override_autosearch_default:
                TriggerSearchAfter ^= True
            func_settext(func_gettext()[:-len(da)] + "  " + d.searchtext)
            return (True, override_autosearch_default)
    if arg[-6:] == "field:":
        if gc("modify_field"):
            vals = (-6, -6, False, fieldnames(), True, field_infotext, "Anki: Select field to search", True)
        allowstar = False          
    if arg[-5:] == "prop:":
        if gc("modify_props"):
            infotxt = "<b>After closing the dialog you must adjust what's inserted with your numbers</b>"
            vals = (False, -5, "prop", props(), False, infotxt, "Anki: Select properties to search", True)
        allowstar = False
    if arg[-3:] == "is:":
        if gc("modify_is"):
            if gc("modify_is__show_explanations"):
                vals = (False, -3, "is_with_explanations", is_values_with_explanations(), False, False, "Anki: Search by Card State", True)
            else:
                vals = (-3, -3, False, is_values(), False, False, "Anki: Search by Card State", True)
        allowstar = False
    if arg[-4:] == "tag:":
        if gc("modify_tag"):
            vals = (False, -4, False, tags(col), False, False, "Anki: Select tag to search", True)
        allowstar = True
    elif arg[-5:] == "note:":
        if gc("modify_note"):
            vals = (False, -5, False, col.models.allNames(), True, False, "Anki: Select Note Type to search", True)
        allowstar = False if pointVersion() < 24 else True
    elif arg[-5:] == "card:":
        if gc("modify_card"):
            vals = (False, -5, False, cardnames(col), True, False, "Anki: Select Card (Type) Name to search", True)
        allowstar = False if pointVersion() < 24 else True      
    elif arg[-4:] == "cfn:":  # cards from note
        d = {}
        for m in col.models.all():
            modelname = m['name']
            for t in m['tmpls']:
                d[t['name'] + " (" + modelname + ")"] = (t['name'], modelname)
        vals = (False, -4, "cfn", d, True, False, "Anki: Select Card (Type) Name from selected Note Type", False)
        allowstar = False
    if arg[-4:] == "ffn:":
        ffn_infotext = (
"<b>"
"Besides the note type name this dialog only inserts the field name to search. After closing <br>"
"the dialog you must enter the actual search term for the field.<br>"
"</b>"
        )
        d = {}
        for m in col.models.all():
            modelname = m['name']
            for f in m['flds']:
                d[f['name'] + " (" + modelname + ")"] = (f['name'], modelname)
        vals = (False, -4, "ffn", d, True, ffn_infotext, "Anki: Select Field to search from selected Note Type", False)
        allowstar = False
    elif arg[-5:] == "deck:":
        if gc("modify_deck"):
            vals = (False, -5, False, decknames(col, include_filtered_in_deck), True, False, "Anki: Select Deck to search", True)
        allowstar = True
    elif xx1:
        alltags = ["tag:" + t for t in tags(col)]
        decks = ["deck:" + d  for d in decknames(col, include_filtered_in_deck)]
        vals = (-len(c1), 0, False, alltags + decks, True, False, "Anki: Select from decks and tags", True)
        allowstar = True
    elif xx2:
        alltags = ["tag:" + t for t in tags(col)]
        decks = ["deck:" + d  for d in decknames(col, include_filtered_in_deck)]
        vals = (-len(c2), 0, False, alltags + decks, True, False, "Anki: Select from decks and tags", True)
        allowstar = True

    if vals:
        if gc("autoadjust FilterDialog position", True):
            adjPos = True
        else:
            adjPos = False
        d = FilterDialog(
            parent=parent,
            parent_is_browser=move_dialog_in_browser,
            values=vals[3],
            windowtitle=vals[6],
            adjPos=adjPos,
            allowstar=allowstar,
            infotext=vals[5],
            show_prepend_minus_button=vals[7]
        )
        if d.exec():
            # print('###############################')
            lineonly, override_autosearch_default, override_add_star, negate = overrides()
            if d.lineonly:
                lineonly = True
            # print(f"d.selkey is {d.selkey}")
            # print(f"d.inputline is {d.inputline}")
            # print(f"d.selvalue is {d.selvalue}")
            # print(f"lineonly is {lineonly}")
            # print(f"allowstar is {allowstar}")
            if negate or d.neg:
                neg = "-"
            else:
                neg = ""

            if not vals[0]:
                t = func_gettext()
                n = vals[1]
                # multiple runs of insert_helper are still separated by spaces and in other 
                # situations this makes the search more readable
                # make sure that "-" remains in front of terms like deck
                if len(t[:n]) > 0 and t[:n][-1] == "-":
                    b = t[:n-1] + "  -" + t[n:]
                else:
                    b = t[:n] + "  " + neg + t[n:]  
            else:
                b = neg + func_gettext()[:vals[0]]
            # print(f"b is:  {b}")


            # vals[2] = UseFilterDialogValue: if values tuple with info, if list is False
            # sofar only True for cases where allowstar is always wrong: quick workaround finish here
            if vals[2]:
                if vals[2] == "cfn":
                    mycard = d.selvalue[0]
                    mynote = d.selvalue[1]
                    mysearch = f'''("card:{mycard}" and "note:{mynote}")'''
                    already_in_line = b[:-4]  # substract cfn:
                    func_settext(already_in_line + mysearch)
                    return (True, override_autosearch_default)
                if vals[2] == "ffn":
                    field = d.selvalue[0]
                    mynote = d.selvalue[1]
                    mysearch = f''' "note:{mynote}" "{field}:" '''
                    already_in_line = b[:-4]  # substract ffn:
                    func_settext(already_in_line + mysearch)
                    return (True, override_autosearch_default)
                elif vals[2] == "is_with_explanations":
                    already_in_line = b[:-3]  # substract is:
                    func_settext(already_in_line + d.selvalue)
                    return (True, override_autosearch_default)
                elif vals[2] == "prop":
                    already_in_line = b[:-5]  # substract prop:
                    func_settext(already_in_line + d.selvalue)
                    return (True, override_autosearch_default)
            else:
                sel = d.selkey
            # print(f"sel is {sel}")
            if lineonly and allowstar:
                if xx1 or xx2:
                    # I need to add tag or deck
                    if d.selkey.startswith("tag:"):
                        sel = "tag:" + d.inputline
                    else:
                        sel = "deck:" + d.inputline
                else:
                    sel = d.inputline
            # maybe add '*' to match other deeper nested hierarchical tags
            if sel in ["none", "filtered", "tag:none", "deck:filtered"]:
                pass
            elif arg[-4:] == "tag:":
                if allowstar and (gc("tag insertion - add '*' to matches") == "all" or d.addstar) and not override_add_star:
                    sel = sel + '*'
                elif allowstar and gc("tag insertion - add '*' to matches") == "if_has_subtags" or d.addstar and not override_add_star:
                    other_subtags_matched = []
                    selplus = sel + "::"
                    for e in vals[3]:
                        if e.startswith(selplus):
                            other_subtags_matched.append(e)
                    if other_subtags_matched:
                        sel = sel + '*'
            # in 2.1.24 card: and note: can also use *
            elif arg[-5:] == "card:":
                if allowstar and (gc("tag insertion - add '*' to matches") == "all" or d.addstar) and not override_add_star:
                    sel = sel + '*'
            elif arg[-5:] == "note:":          
                if allowstar and (gc("tag insertion - add '*' to matches") == "all" or d.addstar) and not override_add_star:
                    sel = sel + '*'
            # ugly fix for xx etc.
            elif (c1 and arg[-len(c1):] == c1) or (c2 and arg[-len(c2):] == c2):
                if allowstar and gc("tag insertion - add '*' to matches") == "all" and not override_add_star:
                    sel = sel + '*'
            elif allowstar and arg[-5:] == "deck:" and gc("modify_deck"):
                 if d.addstar and not override_add_star:
                     sel = sel + '*'
            if vals[4]:  # surround with ""
                sel = '"' + sel + '"'
            func_settext(b + sel)
            TriggerSearchAfter = gc("modify: window opened by search strings triggers search by default")
            if override_autosearch_default:
                TriggerSearchAfter ^= True
            return (True, TriggerSearchAfter)  # shiftmod toggle default search trigger setting
