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


def range_dialog(parent, term, old, char_to_del, func_settext):
    d = DateRangeDialog(parent, term)
    if d.exec():
        TriggerSearchAfter = gc("modify: window opened by search strings triggers search by default")
        _, override_autosearch_default, _, _ = overrides()
        if override_autosearch_default:
            TriggerSearchAfter ^= True
        func_settext(old[:-char_to_del] + "  " + d.searchtext)
        return (True, override_autosearch_default)


def onSearchEditTextChange(parent, 
                           move_dialog_in_browser,
                           include_filtered_in_deck, 
                           func_gettext,
                           func_settext,
                           mw,
                           col
                           ):
    old = func_gettext()
    vals = {}

    da = gc("date range dialog for added: string")
    da_match = da and old[-len(da):] == da
    dr = gc("date range dialog for rated: string")
    dr_match = da and old[-len(dr):] == dr
    if da_match:
        term = "added"
    if dr_match:
        term = "rated"
    if da_match or dr_match:
        return range_dialog(parent, term, old, len(da), func_settext)


    c1 = gc("custom tag&deck string 1", "")
    xx1 = c1 and old[-len(c1):] == c1
    c2 = gc("custom tag&deck string 2", "")
    xx2 = c2 and old[-len(c2):] == c2
    if xx1:
        remove_from_end=-len(c1)
    if xx2:
        remove_from_end=-len(c2)
    if xx1 or xx2:

        """
        vals = {
            "remove_from_end_of_old": number of characters to delete from the text before inserting
                                      the selection. E.g. if the user had typed in "xx" and then
                                      "tag:hallo" will be inserted the "xx" part must be removed
                                      beforehand
                                      if nothing to remove you must set it to "0".
            "insert_space_at_pos_in_old": before inserting selected additional search string 
                                          
            "dict_for_dialog": if True use a string that describes it: I use this string for 
                               an if-loop after the dialog closes.
            "vals": tags(col, True) + decknames(col, include_filtered_in_deck, True),
            "surround_with_quotes": ,
            "infotext": text that is shown over the filterbar
            "windowtitle": 
            "show_prepend_minus_button": whether the checkbox left from the ok button is SHOWN
            "check_prepend_minus_button": whether the checkbox left from the ok button is CHECKED
            "show_star": whether the checkbox left from the ok button is SHOWN
            "check_star": whether the checkbox left from the ok button is CHECKED
        }
"""

        vals = {
            "remove_from_end_of_old": remove_from_end,
            "insert_space_at_pos_in_old": 0,
            "dict_for_dialog": False,
            "vals": tags(col, True) + decknames(col, include_filtered_in_deck, True),
            "surround_with_quotes": True,
            "infotext": False,
            "windowtitle": "Anki: Select from decks and tags",
            "show_prepend_minus_button": True,
            "show_star": True,
            "check_star": True,
        }

    if old[-6:] == "field:" and gc("modify_field"):
        vals = {
            "remove_from_end_of_old": -6,
            "insert_space_at_pos_in_old": -6 ,
            "dict_for_dialog": False,
            "vals": fieldnames(),
            "surround_with_quotes": True,
            "infotext": field_infotext,
            "windowtitle": "Anki: Select field to search",
            "show_prepend_minus_button": True,
            "show_star": False if pointVersion() < 24 else True,
            "check_star": False,
        }

    if old[-5:] == "prop:" and gc("modify_props"):
        it = "<b>After closing the dialog you must adjust what's inserted with your numbers</b>"
        vals = {
            "remove_from_end_of_old": 0,
            "insert_space_at_pos_in_old": -5,
            "dict_for_dialog": "prop",
            "vals": props(),
            "surround_with_quotes": False,
            "infotext": it,
            "windowtitle": "Anki: Select properties to search",
            "show_prepend_minus_button": True,
            "show_star": False,
            "check_star": False,
        }

    if old[-3:] == "is:" and gc("modify_is"):
        expl = gc("modify_is__show_explanations")
        vals = {
            "remove_from_end_of_old": 0 if expl else -3,
            "insert_space_at_pos_in_old": -3,
            "dict_for_dialog": "is_with_explanations" if expl else False,
            "vals": is_values_with_explanations() if expl else is_values(),
            "surround_with_quotes": False,
            "infotext": False,
            "windowtitle": "Anki: Search by Card State",
            "show_prepend_minus_button": True,
            "show_star": False,
            "check_star": False,
        }

    if old[-4:] == "tag:" and gc("modify_tag"):
        vals = {
            "remove_from_end_of_old": 0,
            "insert_space_at_pos_in_old": -4,
            "dict_for_dialog": False,
            "vals": tags(col),
            "surround_with_quotes": False,
            "infotext": False,
            "windowtitle": "Anki: Select tag to search",
            "show_prepend_minus_button": True,
            "show_star": True,
            "check_star": gc("tag insertion - add '*' to matches"),
        }

    elif old[-5:] == "note:" and gc("modify_note"):
        vals = {
            "remove_from_end_of_old": 0,
            "insert_space_at_pos_in_old": -5,
            "dict_for_dialog": False,
            "vals": col.models.allNames(),
            "surround_with_quotes": True,
            "infotext": False,
            "windowtitle": "Anki: Select Note Type to search",
            "show_prepend_minus_button": True,
            "show_star": False if pointVersion() < 24 else True,
            "check_star": True,
        }

    elif old[-5:] == "card:" and gc("modify_card"):
        vals = {
            "remove_from_end_of_old": 0,
            "insert_space_at_pos_in_old": -5,
            "dict_for_dialog": False,
            "vals": cardnames(col),
            "surround_with_quotes": True,
            "infotext": False,
            "windowtitle": "Anki: Select Card (Type) Name to search",
            "show_prepend_minus_button": True,
            "show_star": False if pointVersion() < 24 else True,
            "check_star": False,
        }
    
    elif old[-4:] == "cfn:":  # cards from note
        def cardnames_modelname_dict():
            d = {}
            for m in col.models.all():
                modelname = m['name']
                for t in m['tmpls']:
                    d[t['name'] + " (" + modelname + ")"] = (t['name'], modelname)
            return d
        vals = {
            "remove_from_end_of_old": 0,
            "insert_space_at_pos_in_old": -4,
            "dict_for_dialog": "cfn",
            "vals": cardnames_modelname_dict(),
            "surround_with_quotes": True,
            "infotext": False,
            "windowtitle": "Anki: Select Card (Type) Name from selected Note Type",
            "show_prepend_minus_button": False,
            "show_star": False,
            "check_star": False,
        }

    if old[-4:] == "ffn:":
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
            "remove_from_end_of_old": 0,
            "insert_space_at_pos_in_old": -4,
            "dict_for_dialog": "ffn",
            "vals": fieldnames_modelname_dict(),
            "surround_with_quotes": True,
            "infotext": ffn_infotext,
            "windowtitle": "Anki: Select Field to search from selected Note Type",
            "show_prepend_minus_button": False,
            "show_star": False,
            "check_star": False,
        }

    elif old[-5:] == "deck:" and gc("modify_deck"):
        vals = {
            "remove_from_end_of_old": 0,
            "insert_space_at_pos_in_old": -5,
            "dict_for_dialog": False,
            "vals": decknames(col, include_filtered_in_deck),
            "surround_with_quotes": True,
            "infotext": False,
            "windowtitle": "Anki: Select Deck to search",
            "show_prepend_minus_button": True,
            "show_star": True,
            "check_star": False,
        }

    if not vals:
        return False, False

    d = FilterDialog(
        parent=parent,
        parent_is_browser=move_dialog_in_browser,
        values=vals["vals"],
        windowtitle=vals["windowtitle"],
        adjPos=True if gc("autoadjust FilterDialog position", True) else False,
        show_star=vals["show_star"],
        check_star=vals["check_star"],
        infotext=vals["infotext"],
        show_prepend_minus_button=vals["show_prepend_minus_button"],
        check_prepend_minus_button=False,
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


        ####
        ######### maybe modify old (before appending selection)
        neg = "-" if (negate or d.neg) else ""
        if not vals["remove_from_end_of_old"]:
            n = vals["insert_space_at_pos_in_old"]
            # multiple runs of insert_helper are still separated by spaces and in other 
            # situations this makes the search more readable
            # make sure that "-" remains in front of terms like deck
            
            # if at beginning of line in multi-line dialog don't insert space
            if "\n" in old:
                lines = old.split("\n")
                length_to_compare = len(lines[-1])
            else:
                length_to_compare = len(old)
            if length_to_compare - abs(n) == 0:
                spacing = ""
            else:
                spacing = "  "
            if len(old[:n]) > 0 and old[:n][-1] == "-":
                b = old[:n-1] + spacing + "-" + old[n:]
            else:
                b = old[:n] + spacing + neg + old[n:]  
        else:
            b = neg + old[:vals["remove_from_end_of_old"]]
        # print(f"b is:  {b}")



        # vals["dict_for_dialog"]: UseFilterDialogValue: if values tuple with info, if list is False
        if not vals["dict_for_dialog"]:
            sel = d.selkey
            #print(f"sel is {sel}")
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
                mysearch = f''' "note:{mynote}" "{field}:**" '''
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


        if lineonly:
            if xx1 or xx2:
                # I need to add tag or deck
                if d.selkey.startswith("tag:"):
                    sel = "tag:" + d.inputline
                else:
                    sel = "deck:" + d.inputline
            else:
                sel = d.inputline
        # print(f"sel is: {sel}")



        #######
        ############  maybe add '*' to match other deeper nested hierarchical tags
        if sel in ["none", "filtered", "tag:none", "deck:filtered"]:
            pass
        elif old[-4:] == "tag:":
            if not override_add_star:
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
        elif old[-5:] == "card:":
            if d.addstar and not override_add_star:
                sel = sel + '*'

        elif old[-5:] == "note:":          
            if d.addstar and not override_add_star:
                sel = sel + '*'

        elif old[-6:] == "field:":
            sel = sel + '**'

        # ugly fix for xx etc.
        elif (c1 and old[-len(c1):] == c1) or (c2 and old[-len(c2):] == c2):
            if (vals["check_star"] and 
                gc("tag insertion - add '*' to matches") == "all" and 
                not override_add_star
            ):
                sel = sel + '*'

        elif vals["check_star"] and old[-5:] == "deck:" and gc("modify_deck"):
            if d.addstar and not override_add_star:
                sel = sel + '*'







        if vals["surround_with_quotes"]:
            sel = '"' + sel + '"'



        func_settext(b + sel)
        TriggerSearchAfter = gc("modify: window opened by search strings triggers search by default")
        if override_autosearch_default:
            TriggerSearchAfter ^= True
        return (True, TriggerSearchAfter)  # shiftmod toggle default search trigger setting
