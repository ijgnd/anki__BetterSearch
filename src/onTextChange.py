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


def range_dialog(parent, term, arg, char_to_del, func_settext):
    d = DateRangeDialog(parent, term)
    if d.exec():
        TriggerSearchAfter = gc("modify: window opened by search strings triggers search by default")
        _, override_autosearch_default, _, _ = overrides()
        if override_autosearch_default:
            TriggerSearchAfter ^= True
        func_settext(arg[:-char_to_del] + "  " + d.searchtext)
        return (True, override_autosearch_default)


def onSearchEditTextChange(parent, 
                           move_dialog_in_browser,
                           include_filtered_in_deck, 
                           func_gettext,
                           func_settext,
                           mw,
                           col
                           ):
    arg = func_gettext()
    vals = {}

    da = gc("date range dialog for added: string")
    da_match = da and arg[-len(da):] == da
    dr = gc("date range dialog for rated: string")
    dr_match = da and arg[-len(dr):] == dr
    if da_match:
        term = "added"
    if dr_match:
        term = "rated"
    if da_match or dr_match:
        return range_dialog(parent, term, arg, len(da), func_settext)


    c1 = gc("custom tag&deck string 1", "")
    xx1 = c1 and arg[-len(c1):] == c1
    c2 = gc("custom tag&deck string 2", "")
    xx2 = c2 and arg[-len(c2):] == c2
    if xx1:
        remove_from_end=-len(c1)
    if xx2:
        remove_from_end=-len(c2)
    if xx1 or xx2:
        vals = {
            "remove_from_end_of_string": remove_from_end,
            "insert_space_at_pos": 0,
            "dict_for_dialog": False,  # if True (use a string that describes it)
            "vals": tags(col, True) + decknames(col, include_filtered_in_deck, True),
            "surround_with_quotes": True,
            "infotext": False,
            "windowtitle": "Anki: Select from decks and tags",
            "show_prepend_minus_button": True,
            "allowstar": True
        }

    if arg[-6:] == "field:" and gc("modify_field"):
        vals = {
            "remove_from_end_of_string": -6,
            "insert_space_at_pos": -6 ,
            "dict_for_dialog": False,
            "vals": fieldnames(),
            "surround_with_quotes": True,
            "infotext": field_infotext,
            "windowtitle": "Anki: Select field to search",
            "show_prepend_minus_button": True,
            "allowstar": False, 
        }

    if arg[-5:] == "prop:" and gc("modify_props"):
        it = "<b>After closing the dialog you must adjust what's inserted with your numbers</b>"
        vals = {
            "remove_from_end_of_string": False,
            "insert_space_at_pos": -5,
            "dict_for_dialog": "prop",
            "vals": props(),
            "surround_with_quotes": False,
            "infotext": it,
            "windowtitle": "Anki: Select properties to search",
            "show_prepend_minus_button": True,
            "allowstar": False 
        }

    if arg[-3:] == "is:" and gc("modify_is"):
        expl = gc("modify_is__show_explanations")
        vals = {
            "remove_from_end_of_string": False if expl else -3,
            "insert_space_at_pos": -3,
            "dict_for_dialog": "is_with_explanations" if expl else False,
            "vals": is_values_with_explanations() if expl else is_values(),
            "surround_with_quotes": False,
            "infotext": False,
            "windowtitle": "Anki: Search by Card State",
            "show_prepend_minus_button": True,
            "allowstar": False,
        }

    if arg[-4:] == "tag:" and gc("modify_tag"):
        vals = {
            "remove_from_end_of_string": False,
            "insert_space_at_pos": -4,
            "dict_for_dialog": False,
            "vals": tags(col),
            "surround_with_quotes": False,
            "infotext": False,
            "windowtitle": "Anki: Select tag to search",
            "show_prepend_minus_button": True,
            "allowstar": True,
        }

    elif arg[-5:] == "note:" and gc("modify_note"):
        vals = {
            "remove_from_end_of_string": False,
            "insert_space_at_pos": -5,
            "dict_for_dialog": False,
            "vals": col.models.allNames(),
            "surround_with_quotes": True,
            "infotext": False,
            "windowtitle": "Anki: Select Note Type to search",
            "show_prepend_minus_button": True,
            "allowstar": False,
        }

    elif arg[-5:] == "card:" and gc("modify_card"):
        vals = {
            "remove_from_end_of_string": False,
            "insert_space_at_pos": -5,
            "dict_for_dialog": False,
            "vals": cardnames(col),
            "surround_with_quotes": True,
            "infotext": False,
            "windowtitle": "Anki: Select Card (Type) Name to search",
            "show_prepend_minus_button": True,
            "allowstar": False if pointVersion() < 24 else True,
        }
    
    elif arg[-4:] == "cfn:":  # cards from note
        def cardnames_modelname_dict():
            d = {}
            for m in col.models.all():
                modelname = m['name']
                for t in m['tmpls']:
                    d[t['name'] + " (" + modelname + ")"] = (t['name'], modelname)
            return d
        vals = {
            "remove_from_end_of_string": False,
            "insert_space_at_pos": -4,
            "dict_for_dialog": "cfn",
            "vals": cardnames_modelname_dict(),
            "surround_with_quotes": True,
            "infotext": False,
            "windowtitle": "Anki: Select Card (Type) Name from selected Note Type",
            "show_prepend_minus_button": False,
            "allowstar": False, 
        }

    if arg[-4:] == "ffn:":
        ffn_infotext = (
"<b>"
"Besides the note type name this dialog only inserts the field name to search. After closing <br>"
"the dialog you must enter the actual search term for the field.<br>"
"</b>"
        )
        def fieldnames_modelname_dict():
            d = {}
            for m in col.models.all():
                modelname = m['name']
                for f in m['flds']:
                    d[f['name'] + " (" + modelname + ")"] = (f['name'], modelname)
            return d
        vals = {
            "remove_from_end_of_string": False,
            "insert_space_at_pos": -4,
            "dict_for_dialog": "ffn",
            "vals": fieldnames_modelname_dict(),
            "surround_with_quotes": True,
            "infotext": ffn_infotext,
            "windowtitle": "Anki: Select Field to search from selected Note Type",
            "show_prepend_minus_button": False,
            "allowstar": False,
        }

    elif arg[-5:] == "deck:" and gc("modify_deck"):
        vals = {
            "remove_from_end_of_string": False,
            "insert_space_at_pos": -5,
            "dict_for_dialog": False,
            "vals": decknames(col, include_filtered_in_deck),
            "surround_with_quotes": True,
            "infotext": False,
            "windowtitle": "Anki: Select Deck to search",
            "show_prepend_minus_button": True,
            "allowstar": True,
        }

    if not vals:
        return False, False

    d = FilterDialog(
        parent=parent,
        parent_is_browser=move_dialog_in_browser,
        values=vals["vals"],
        windowtitle=vals["windowtitle"],
        adjPos=True if gc("autoadjust FilterDialog position", True) else False,
        allowstar=vals["allowstar"],
        infotext=vals["infotext"],
        show_prepend_minus_button=vals["show_prepend_minus_button"]
    )
    if not d.exec():
        return False, False
    else:
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


        if not vals["remove_from_end_of_string"]:
            t = arg
            n = vals["insert_space_at_pos"]
            # multiple runs of insert_helper are still separated by spaces and in other 
            # situations this makes the search more readable
            # make sure that "-" remains in front of terms like deck
            if len(t[:n]) > 0 and t[:n][-1] == "-":
                b = t[:n-1] + "  -" + t[n:]
            else:
                b = t[:n] + "  " + neg + t[n:]  
        else:
            b = neg + arg[:vals["remove_from_end_of_string"]]
        # print(f"b is:  {b}")



        # vals["dict_for_dialog"]: UseFilterDialogValue: if values tuple with info, if list is False
        if not vals["dict_for_dialog"]:
            sel = d.selkey
            # print(f"sel is {sel}")
        else:
            # workaround: return from function here
            if vals["dict_for_dialog"] == "cfn":
                mycard = d.selvalue[0]
                mynote = d.selvalue[1]
                mysearch = f'''("card:{mycard}" and "note:{mynote}")'''
                already_in_line = b[:-4]  # substract cfn:
                func_settext(already_in_line + mysearch)
                return (True, override_autosearch_default)
            if vals["dict_for_dialog"] == "ffn":
                field = d.selvalue[0]
                mynote = d.selvalue[1]
                mysearch = f''' "note:{mynote}" "{field}:" '''
                already_in_line = b[:-4]  # substract ffn:
                func_settext(already_in_line + mysearch)
                return (True, override_autosearch_default)
            elif vals["dict_for_dialog"] == "is_with_explanations":
                already_in_line = b[:-3]  # substract is:
                func_settext(already_in_line + d.selvalue)
                return (True, override_autosearch_default)
            elif vals["dict_for_dialog"] == "prop":
                already_in_line = b[:-5]  # substract prop:
                func_settext(already_in_line + d.selvalue)
                return (True, override_autosearch_default)


        if lineonly and vals["allowstar"]:
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
            if vals["allowstar"] and not override_add_star:
                if gc("tag insertion - add '*' to matches") == "all" or d.addstar:
                    sel = sel + '*'
                elif gc("tag insertion - add '*' to matches") == "if_has_subtags" or d.addstar:
                    other_subtags_matched = []
                    selplus = sel + "::"
                    for e in vals[3]:
                        if e.startswith(selplus):
                            other_subtags_matched.append(e)
                    if other_subtags_matched:
                        sel = sel + '*'

        # in 2.1.24 card: and note: can also use *
        elif arg[-5:] == "card:":
            if (vals["allowstar"] and 
                (gc("tag insertion - add '*' to matches") == "all" or d.addstar) and 
                not override_add_star
            ):
                sel = sel + '*'

        elif arg[-5:] == "note:":          
            if (vals["allowstar"] and
                (gc("tag insertion - add '*' to matches") == "all" or d.addstar) and
                not override_add_star
            ):
                sel = sel + '*'

        # ugly fix for xx etc.
        elif (c1 and arg[-len(c1):] == c1) or (c2 and arg[-len(c2):] == c2):
            if (vals["allowstar"] and 
                gc("tag insertion - add '*' to matches") == "all" and 
                not override_add_star
            ):
                sel = sel + '*'
        elif vals["allowstar"] and arg[-5:] == "deck:" and gc("modify_deck"):
            if d.addstar and not override_add_star:
                sel = sel + '*'
        if vals["surround_with_quotes"]:
            sel = '"' + sel + '"'
        func_settext(b + sel)
        TriggerSearchAfter = gc("modify: window opened by search strings triggers search by default")
        if override_autosearch_default:
            TriggerSearchAfter ^= True
        return (True, TriggerSearchAfter)  # shiftmod toggle default search trigger setting
