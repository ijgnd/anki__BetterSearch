import re

from aqt.utils import tooltip

from .anki_version_detection import anki_point_version
from .config import gc
from .custom_fuzzy_dialogs import (
    note__card,
    note__field,
)
from .dialog__date import DateRangeDialog
from .fuzzy_panel import FilterDialog
from .helpers import (
    # this is the order in helpers.py
    cardnames,
    decknames,
    emc,
    tags,
    is_values,
    is_values_with_explanations,
    props,
    fieldnames,
    overrides,
    field_infotext,
    maybe_add_spaced_between,
)


def range_dialog(parent, term, before, after, char_to_del, func_settext):
    d = DateRangeDialog(parent, term)
    if d.exec():
        TriggerSearchAfter = gc("modify: window opened by search strings triggers search by default")
        _, override_autosearch_default, _, _ = overrides()
        if override_autosearch_default:
            TriggerSearchAfter ^= True
        spaces = maybe_add_spaced_between(before, char_to_del)
        func_settext(before[:-char_to_del] + spaces + d.searchtext + after)
        newpos = len(before[:-char_to_del] + spaces + d.searchtext)
        return (newpos, override_autosearch_default)


def note__field__card__helper(parent, term, before, after, char_to_del, func_settext):
    if term == "dnf:":
        out, tomove = note__field(parent)
    else:  # "dnc:"
        out, tomove = note__card(parent)
    if out:
        TriggerSearchAfter = gc("modify: window opened by search strings triggers search by default")
        _, override_autosearch_default, _, _ = overrides()
        if override_autosearch_default:
            TriggerSearchAfter ^= True
        spaces = maybe_add_spaced_between(before, char_to_del)
        new = before[:-char_to_del] + spaces + out + after
        func_settext(new)
        newpos = len(before[:-char_to_del] + spaces + out) + tomove
        return (newpos, override_autosearch_default)


def matches_search_operator(before, term):
    if before == term:
        return True
    # in my multiline dialog users can type RETURN or TAB
    if before[-(len(term)+1):] in [f" {term}", f"\n{term}", f"\t{term}"]:
        return True


def onSearchEditTextChange(parent, 
                           move_dialog_in_browser,
                           include_filtered_in_deck, 
                           func_gettext,
                           func_settext,
                           cursorpos,
                           mw,
                           col,
                           from_button=False
                           ):
    all_text = func_gettext()
    if cursorpos is None:
        before = all_text
        after = ""
    else:
        before = all_text[:cursorpos]
        after = all_text[cursorpos:]
    

    # This offers similar functionality to 
    #     - my addon "browser search aliases/abbreviations", https://ankiweb.net/shared/info/546509374
    #       difference: the search aliases replaces only when you execute the search
    #       I'm not sure if this is worse, e.g. maybe I don't know that the orange flag has the number two.
    #       Direct replacements after each character typed means I'll never have an understandable term like "florange"
    #       in a longer search term that I might want to check ...
    #     - Symbols as you type, https://ankiweb.net/shared/info/2040501954
    #       difference: "Symbols as you type" does not offer a regex replacement in 2024-02
    #       Both addons can be used at the same time.

    if gc("--aliases Replace while typing") and not after:
        alias_dict = gc("--aliases dictionary")
        if alias_dict and isinstance(alias_dict, dict):
            """
            the following doesn't make sense here because I replace after each char typed
            so I can never get to longer strings (as in my separate alias addon)
            # sort dict by length of keys, so that "added:1" is replaced before "added:"
            # in python 3.7 keeps insertion order
            # for original in sorted(alias_dict, key=len, reverse=True):
            for abbrev in sorted(alias_dict, key=lambda k: len(alias_dict[k]), reverse=True):
                repl = alias_dict[abbrev]
                if ...
            """
            for abbrev, repl in alias_dict.items():
                if before == abbrev or before.endswith(f" {abbrev}"):
                    before = before.replace(abbrev, repl)
                    func_settext(before + after)
                    newpos = len(before + after)            
                    return (newpos, False)

    """
    e.g.:

        --aliases_regex dictionary": {
            "aa(\\d{1,4})(?= |$)" : "added:\\1",
            "ee(\\d{1,4})(?= |$)" : "edited:\\1",
            "ii(\\d{1,4})(?= |$)" : "introduced:\\1",
            "rr(\\d{1,4})(?= |$|:)" : "rated:\\1",
            "nid(\\d{13})(?= |$)" : "nid:\\1",
            "cid(\\d{13})(?= |$)" : "cid:\\1",
            "due(\\!?=?>?<?-?)(?=\\d{1,4})" : "prop:due\\1",
            "laps(\\!?=?>?<?-?)(?=\\d{1,4})" : "prop:lapses\\1",
            "lapses(\\!?=?>?<?-?)(?=\\d{1,4})" : "prop:lapses\\1",
            "ease(\\!?=?>?<?-?)(?=\\d{1,4})" : "prop:ease\\1",
            "ivl(\\!?=?>?<?-?)(?=\\d{1,4})" : "prop:ivl\\1",
            "isdue(?= |$)": "is:due",
            "isnew(?= |$)": "is:new",
            "islearn(?= |$)" : "is:learn",
            "isreview(?= |$)" : "is:review",
            "issuspended(?= |$)" : "is:suspended",
            "issuspend(?= |$)" : "is:suspended",
            "isburied(?= |$)" : "is:buried",
            "isbury(?= |$)" : "is:buried",
            "flag(\\d{1,2})(?= |$)": "flag:\\1",
            "flred(?= |$)" : "flag:1",
            "florange(?= |$)" : "flag:2",
            "flgreen(?= |$)" : "flag:3",
            "flblue(?= |$)" : "flag:4",
            "flpink(?= |$)" : "flag:5",
            "flturquoise(?= |$)" : "flag:6",
            "fltur(?= |$)" : "flag:6",
            "flpurple(?= |$)" : "flag7",
            "flpurp(?= |$)" : "flag7",
            "flpur(?= |$)" : "flag7",
            "flpu(?= |$)" : "flag7",
            "flp(?= |$)" : "flag7",
            "retag:": "tag:re:"
        },
    """
    if gc("--aliases_regex Replace while typing") and not after:
        regex_alias_dict = gc("--aliases_regex dictionary")
        if regex_alias_dict and isinstance(regex_alias_dict, dict):
            for abbrev, repl in regex_alias_dict.items():
                before, number_replacements = re.subn(abbrev, repl, before)
                if number_replacements:
                    func_settext(before + after)
                    newpos = len(before + after)            
                    return (newpos, False)






    if after and not after.startswith(" "):
        after = " " + after

    vals = {}


    dnfmatch = before[-4:] == "dnf:"
    dncmatch = before[-4:] == "dnc:"
    if dnfmatch:
        term = "dnf:"
    if dncmatch:
        term = "dnc:"
    if dnfmatch or dncmatch:
        return note__field__card__helper(parent, term, before, after, 4, func_settext)


    da = gc("date range dialog for added: string")
    da_match = da and before[-len(da):] == da
    de = gc("date range dialog for edited: string")
    de_match = de and before[-len(de):] == de and anki_point_version >= 28
    dr = gc("date range dialog for rated: string")
    dr_match = dr and before[-len(dr):] == dr
    di = gc("date range dialog for introduced: string")
    di_match = di and before[-len(di):] == di

    if da_match:
        term = "added"
        length = len(da)
    if de_match:
        term = "edited"
        length = len(de)
    if dr_match:
        term = "rated"
        length = len(dr)
    if di_match:
        term = "introduced"
        length = len(di)
    if any([da_match, de_match, dr_match, di_match]):
        return range_dialog(parent, term, before, after, length, func_settext)


    c1 = gc("custom tag&deck string 1", "")
    xx1 = c1 and before[-len(c1):] == c1
    c2 = gc("custom tag&deck string 2", "")
    xx2 = c2 and before[-len(c2):] == c2
    if xx1:
        remove_from_end=-len(c1)
    if xx2:
        remove_from_end=-len(c2)
    if xx1 or xx2:

        """
        vals = {
            "remove_from_end_of_before": number of characters to delete from the text before inserting
                                      the selection. E.g. if the user had typed in "xx" and then
                                      "tag:hallo" will be inserted the "xx" part must be removed
                                      beforehand
                                      if nothing to remove you must set it to "0".
            "insert_space_at_pos_in_before": before inserting selected additional search string 
                                          
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
            "remove_from_end_of_before": remove_from_end,
            "insert_space_at_pos_in_before": 0,
            "dict_for_dialog": False,
            "vals": tags(col, True) + decknames(col, include_filtered_in_deck, True),
            "surround_with_quotes": True,
            "infotext": False,
            "windowtitle": "Anki: Select from decks and tags",
            "show_prepend_minus_button": True,
            "show_star": True,
            "check_star": True,
        }

    if matches_search_operator(before, "field:") and (gc("modify_field") or from_button):
        vals = {
            "remove_from_end_of_before": -6,
            "insert_space_at_pos_in_before": -6 ,
            "dict_for_dialog": False,
            "vals": fieldnames(),
            "surround_with_quotes": True,
            "infotext": field_infotext,
            "windowtitle": "Anki: Select field to search",
            "show_prepend_minus_button": True,
            "show_star": False if anki_point_version < 24 else True,
            "check_star": False,
        }

    if matches_search_operator(before, "prop:") and (gc("modify_props") or from_button):
        it = "<b>After closing the dialog you must adjust what's inserted with your numbers</b>"
        vals = {
            "remove_from_end_of_before": 0,
            "insert_space_at_pos_in_before": -5,
            "dict_for_dialog": "prop",
            "vals": props(),
            "surround_with_quotes": False,
            "infotext": it,
            "windowtitle": "Anki: Select properties to search",
            "show_prepend_minus_button": True,
            "show_star": False,
            "check_star": False,
        }

    if matches_search_operator(before, "is:") and (gc("modify_is") or from_button):
        expl = gc("modify_is__show_explanations")
        vals = {
            "remove_from_end_of_before": 0 if expl else -3,
            "insert_space_at_pos_in_before": -3,
            "dict_for_dialog": "is_with_explanations" if expl else False,
            "vals": is_values_with_explanations() if expl else is_values(),
            "surround_with_quotes": False,
            "infotext": False,
            "windowtitle": "Anki: Search by Card State",
            "show_prepend_minus_button": True,
            "show_star": False,
            "check_star": False,
        }

    if matches_search_operator(before, "flag:") and (gc("modify_flag") or from_button):
        vals = {
            "remove_from_end_of_before": 0,
            "insert_space_at_pos_in_before": -5,
            "dict_for_dialog": "flags",
            "vals": {
                "red": "1",
                "orange": "2",
                "green": "3",
                "blue": "4",
                "pink": "5",
                "turquoise": "6",
                "purple": "7",
            },
            "surround_with_quotes": False,
            "infotext": False,
            "windowtitle": "Anki: Search by Flag",
            "show_prepend_minus_button": True,
            "show_star": False,
            "check_star": False,
        }

    tag_search = matches_search_operator(before, "tag:") and (gc("modify_tag") or from_button)
    if tag_search:
        vals = {
            "remove_from_end_of_before": 0,
            "insert_space_at_pos_in_before": -4,
            "dict_for_dialog": False,
            "vals": tags(col),
            "surround_with_quotes": False,
            "infotext": False,
            "windowtitle": "Anki: Select tag to search",
            "show_prepend_minus_button": True,
            "show_star": True,
            "check_star": gc("tag insertion - add '*' to matches"),
            "context": "tag",
        }

    elif matches_search_operator(before, "note:") and (gc("modify_note") or from_button):
        vals = {
            "remove_from_end_of_before": 0,
            "insert_space_at_pos_in_before": -5,
            "dict_for_dialog": False,
            "vals": col.models.allNames(),
            "surround_with_quotes": True,
            "infotext": False,
            "windowtitle": "Anki: Select Note Type to search",
            "show_prepend_minus_button": True,
            "show_star": False if anki_point_version < 24 else True,
            "check_star": True,
        }

    elif matches_search_operator(before, "card:") and (gc("modify_card") or from_button):
        vals = {
            "remove_from_end_of_before": 0,
            "insert_space_at_pos_in_before": -5,
            "dict_for_dialog": False,
            "vals": cardnames(col),
            "surround_with_quotes": True,
            "infotext": False,
            "windowtitle": "Anki: Select Card (Type) Name to search",
            "show_prepend_minus_button": True,
            "show_star": False if anki_point_version < 24 else True,
            "check_star": False,
        }
    
    elif matches_search_operator(before, "cfn:"):  # cards from note
        def cardnames_modelname_dict():
            d = {}
            for m in col.models.all():
                modelname = m['name']
                for t in m['tmpls']:
                    d[t['name'] + " (" + modelname + ")"] = (t['name'], modelname)
            return d
        vals = {
            "remove_from_end_of_before": 0,
            "insert_space_at_pos_in_before": -4,
            "dict_for_dialog": "cfn",
            "vals": cardnames_modelname_dict(),
            "surround_with_quotes": True,
            "infotext": False,
            "windowtitle": "Anki: Select Card (Type) Name from selected Note Type",
            "show_prepend_minus_button": False,
            "show_star": False,
            "check_star": False,
        }

    if matches_search_operator(before, "ffn:"):
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
            "remove_from_end_of_before": 0,
            "insert_space_at_pos_in_before": -4,
            "dict_for_dialog": "ffn",
            "vals": fieldnames_modelname_dict(),
            "surround_with_quotes": True,
            "infotext": ffn_infotext,
            "windowtitle": "Anki: Select Field to search from selected Note Type",
            "show_prepend_minus_button": False,
            "show_star": False,
            "check_star": False,
        }

    elif matches_search_operator(before, "deck:") and gc("modify_deck"):
        vals = {
            "remove_from_end_of_before": 0,
            "insert_space_at_pos_in_before": -5,
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
        return False

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
        context=vals.get("context")
    )
    if not d.exec():
        return False
    else:
        lineonly, override_autosearch_default, override_add_star, negate = overrides()
        if d.lineonly:
            lineonly = True
        # print(f"d.selkey is {d.selkey}")
        # print(f"d.inputline is {d.inputline}")
        # print(f"d.selvalue is {d.selvalue}")
        # print(f"lineonly is {lineonly}")


        ####
        ######### maybe modify before (before appending selection)
        neg = "-" if (negate or d.neg) else ""
        if not vals["remove_from_end_of_before"]:
            n = vals["insert_space_at_pos_in_before"]
            # multiple runs of insert_helper are still separated by spaces and in other 
            # situations this makes the search more readable
            # make sure that "-" remains in front of terms like deck
            
            spaces = maybe_add_spaced_between(before, n)
            if len(before[:n]) > 0 and before[:n][-1] == "-":
                b = before[:n-1] + spaces + "-" + before[n:]
            else:
                b = before[:n] + spaces + neg + before[n:]  
        else:
            b = neg + before[:vals["remove_from_end_of_before"]]
        # print(f"b is:  {b}")


        if d.tooltip_after_exit_for_parent:
            tooltip(d.tooltip_after_exit_for_parent, period=6000)

        # vals["dict_for_dialog"]: UseFilterDialogValue: if values tuple with info, if list is False
        if not vals["dict_for_dialog"]:
            sel = emc(d.selkey)
            chars_that_needs_quoting = ["(", ")"]
            if tag_search and any(c in sel for c in chars_that_needs_quoting):
                vals["surround_with_quotes"] = True
            #print(f"sel is {sel}")
        else:
            # workaround: return from function here
            if vals["dict_for_dialog"] == "cfn":
                mycard = d.selvalue[0]
                mynote = d.selvalue[1]
                mysearch = f'''("card:{emc(mycard)}" and "note:{emc(mynote)}")'''
                already_in_line = b[:-4]  # substract cfn:
                func_settext(already_in_line + mysearch + after)
                newpos = len(already_in_line + mysearch)
                return (newpos, override_autosearch_default)
            if vals["dict_for_dialog"] == "ffn":
                field = d.selvalue[0]
                mynote = d.selvalue[1]
                mysearch = f''' "note:{emc(mynote)}" "{emc(field)}:**" '''
                already_in_line = b[:-4]  # substract ffn:
                func_settext(already_in_line + mysearch + after)
                newpos = len(already_in_line + mysearch)
                return (newpos, override_autosearch_default)
            elif vals["dict_for_dialog"] == "is_with_explanations":
                already_in_line = b[:-3]  # substract is:
                func_settext(already_in_line + d.selvalue + after)
                newpos = len(already_in_line + d.selvalue)
                return (newpos, override_autosearch_default)
            elif vals["dict_for_dialog"] == "prop":
                already_in_line = b[:-5]  # substract prop:
                func_settext(already_in_line + d.selvalue + after)
                newpos = len(already_in_line + d.selvalue)
                return (newpos, override_autosearch_default)
            elif vals["dict_for_dialog"] == "flags":
                sel = d.selvalue


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
        if sel in ["none", "filtered", "tag:none", "deck:filtered", "re:"]:
            pass
        elif before[-4:] == "tag:":
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
        elif before[-5:] == "card:":
            if d.addstar and not override_add_star:
                sel = sel + '*'

        elif before[-5:] == "note:":          
            if d.addstar and not override_add_star:
                sel = sel + '*'

        elif before[-5:] == "deck:" and gc("modify_deck"):
            if d.addstar and not override_add_star:
                sel = sel + '*'

        elif before[-6:] == "field:":
            sel = sel + '**'

        # ugly fix for xx etc.
        elif (c1 and before[-len(c1):] == c1) or (c2 and before[-len(c2):] == c2):
            if (vals["check_star"] and 
                gc("tag insertion - add '*' to matches") == "all" and 
                not override_add_star
            ):
                sel = sel + '*'







        if vals["surround_with_quotes"]:
            sel = '"' + sel + '"'



        func_settext(b + sel + after)
        TriggerSearchAfter = gc("modify: window opened by search strings triggers search by default")
        if override_autosearch_default:
            TriggerSearchAfter ^= True
        newpos = len(b + sel)
        return (newpos, TriggerSearchAfter)  # shiftmod toggle default search trigger setting
