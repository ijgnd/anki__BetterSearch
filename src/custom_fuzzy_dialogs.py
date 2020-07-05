from aqt.utils import tooltip


from .fuzzy_panel import FilterDialog
from .helpers import (
    cardnames,
    fieldnames,
    overrides,
)


# these should work in the browser and dialog__multi_line.SearchBox


def run_filter_dialog(browser, vals, vals_are_dict, value_for_all, windowtitle, infotext, prefix, sort_vals):
    d = FilterDialog(
        parent=browser,
        parent_is_browser=True,
        values=vals,
        windowtitle=windowtitle,
        adjPos=False,
        show_star=True,
        check_star=False,
        infotext=infotext,
        show_prepend_minus_button=True,
        check_prepend_minus_button=False,
        sort_vals=sort_vals
    )
    if not d.exec():
        return None, None, None
    else:
        if d.selkey == value_for_all:
            return d.selkey, ""
        lineonly, _, override_add_star, negate = overrides()
        if d.lineonly:
            lineonly = True
        if override_add_star:
            d.addstar ^= True
        out = d.selvalue if vals_are_dict else d.selkey
        if lineonly or d.addstar:
            out += "*"
        out = prefix + out
        neg = True if (negate or d.neg) else False
        return d.selkey, out, neg


def get_browser_instance(self):
    from .dialog__multi_line import SearchBox
    if isinstance(self, SearchBox):
        return self.browser
    else:
        return self


def note_filter_helper(self, remaining_sentence):
    browser = get_browser_instance(self)
    infotext = (f"""
<span>
In a first step select the note type to search. After this you'll see a dialog to narrow 
by {remaining_sentence}
</span>
""")
    val, fmt, neg = run_filter_dialog(
        browser=browser,
        vals=["--All Note Types--"] + self.col.models.allNames(),
        vals_are_dict=False,
        value_for_all="--All Note Types--",
        windowtitle="Anki: Step 1: Select Note Type to search",
        infotext=infotext,
        prefix="note:",
        sort_vals=True,
    )
    return val, fmt, neg


def note__card(self):
    browser = get_browser_instance(self)
    remaining = "card template name if the note has multiple cards." 
    model, model_search_string, modelneg = note_filter_helper(self, remaining)
    if not model:
        return

    infotext = ("""
<span>
After having selected the note types to search now select the
card template/type/name you want to search.
</span>
""")
    iscloze = False
    show_card_dialog = True
    if not model_search_string:
        # then from all notetypes
        vals = cardnames(self.col)
        vals_are_dict = False
        sort_vals = True
    else:
        # for one note type
        sort_vals = False
        nt = self.col.models.byName(model)
        if nt["type"] == 1:  # it's a cloze and for cloze it doesn't make sense to show a list
                                # of cards
            show_card_dialog = False
            iscloze = True
        else:
            card_name_to_fmt_dict = {}
            for c, tmpl in enumerate(nt["tmpls"]):
                # T: name is a card type name. n it's order in the list of card type.
                name = tmpl["name"]
                n = str(c + 1)
                fmt = f"{n.zfill(2)}: {name}"
                card_name_to_fmt_dict[fmt] = name
            default_fake_dict = {"--All the Card Types--":"--All the Card Types--"}
            vals = {**default_fake_dict, **card_name_to_fmt_dict}
            vals_are_dict = True
            if c == 0:  # only one card type 
                show_card_dialog = False
    if not show_card_dialog:
        card_string = ""
        cardneg = False
    else:
        card, card_string, cardneg = run_filter_dialog(
            browser=browser,
            vals=vals,
            vals_are_dict=vals_are_dict,
            value_for_all="--All the Card Types--",
            windowtitle="Anki: Step 2: Select Card Type to search",
            infotext=infotext,
            prefix="card:",
            sort_vals=sort_vals,
        )
        if not card:
            return


    if " " in model_search_string:
        model_search_string = '"' + model_search_string + '"'
    if model_search_string:
        model_search_string += " "
    if " " in card_string:
        card_string = '"' + card_string + '"'
    out = '(' + model_search_string + card_string + ')'
    if modelneg or cardneg:
        out = "-" + out
    if iscloze:
        msg = ("""
You selected a cloze note type. To match only c2 clozes type you would have to 
add&nbsp;&nbsp;card:2&nbsp;&nbsp;
"""
        )
        tooltip(msg, parent=self)  # default is period=3000
    #self.button_helper(out, False)
    return out


def note__field(self):
    browser = get_browser_instance(self)
    remaining = "field (if the note has more than one field)." 
    model, model_search_string, modelneg = note_filter_helper(self, remaining)
    if not model:
        return

    infotext = ("""
<span>
After having selected the note type to search now select the field name you want 
to search. After closing this dialog the text inserted will be "fieldname:**" 
which doesn't limit your search yet. You must <b>adjust</b> this search and
add some text to limit to a certain term.
<span>
""")
    show_card_dialog = True
    if not model_search_string:
        # then from all notetypes
        fnames = fieldnames()
        value_for_all = False
    else:
        # for one note type
        nt = self.col.models.byName(model)
        fnames = [fld["name"] for fld in nt["flds"]]
        if not len(fnames) > 1:
            show_card_dialog = False
        value_for_all="--All the Card Types--"
        fnames.insert(0, value_for_all)
    if not show_card_dialog:
        field_string = ""
        fieldneg = False
    else:
        field, field_string, fieldneg = run_filter_dialog(
            browser=browser,
            vals=fnames,
            vals_are_dict=False,
            value_for_all=value_for_all,
            windowtitle="Anki: Step 2: Select Field Name to search",
            infotext=infotext,
            prefix="",
            sort_vals=False
        )
        if not field:
            return

    if " " in model_search_string:
        model_search_string = '"' + model_search_string + '"'
    if model_search_string:
        model_search_string += " "
    if field_string:
        field_string += ":**"
    if " " in field_string:
        field_string = '"' + field_string + '"'
    out = '(' + model_search_string + field_string + ')'
    if modelneg or fieldneg:
        out = "-" + out
    #self.button_helper(out, False)
    return out