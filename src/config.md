**Before you change the config make sure to read the descriptions below and/or watch the** 
**following [AnKingMed](https://www.ankingmed.com/) video:** 
**[Anki: Better Searching Tools](https://www.youtube.com/watch?v=PlcsNIsYc7k). Also watch**
**the video [Anki: How to Find Cards and Tags in the Browser](https://www.youtube.com/watch?v=NHpl-j9pULU)**

You can also read this help file in the browser [here](https://github.com/ijgnd/anki__BetterSearch/blob/master/src/config.md). 
The description on ankiweb is [here](https://ankiweb.net/shared/info/1052724801).

This add-on used to be named *Browser Search Box: Quick Insert Tag, Deck, Notetype*. The name
was changed because now it offers more than this.

### Important notes
- This add-on offers about 45 different config options. Most of them can be ignored unless
you have really strong opinions or have another add-on that uses conflicting shortcuts, etc.
TheAnking thinks this one is relevant:
    - If you you have mostly cloze notes (e.g. if you use the TheAnKing decks) and often search for 
specific cloze cards with e.g. "card:2" you might want to set the config key 
`"modify_card"` to `false`: By default when you type in "card:" this add-on will show you 
a list of card *names*. In Anki you can also search by card type *number*. For cloze note types you 
can only search by card type numbers. For details see TheAnkigVideo 
[here](https://www.youtube.com/watch?v=PlcsNIsYc7k&feature=youtu.be&t=354).
- General point about add-on config in Anki: When you adjust the config for an add-on in th
add-on config window you actually edit a so-called "json" file. This means you must 
adhere to the json rules or you will get weird error messages. The json format is actually pretty 
simple. Usually all settings must be surrounded with `""` (quote signs). There are some exceptions 
like the boolean values true/false (lowercase) and numbers. For other add-ons you need
more advanced features but these are not relevant here.
- Besides the functions described on ankiweb this add-on has some additional features, e.g. there's
a menu entry and custom shortcut to open your search history in a filter dialog where long searches 
are split up into multiple lines. The setting is 
`"shortcut - select entry from history in fuzzy dialog"` (default is "Ctrl+H, h").
- The add-on automatically opens filter dialogs for "tag:", "note:", etc. if it detects these
keywords right before the cursor. Sometimes this opens a dialog even if you don't want to see it.
**To close such a filter dialog just press "Esc"**.
- typing "xx" opens a custom filter dialog that contains both deck names and tags, see the 
description below for `"custom tag&deck string 1"` as well as 
[this part](https://www.youtube.com/watch?v=NHpl-j9pULU&feature=youtu.be&t=99) from the 
"How to Find Cards" video.
- When closing the multi-line dialog newlines and tabs are replaced by spaces.
- When you open the multi-line dialog the search term from your search bar is split into multiple
lines for better readability.
- The default shortcut to open the multi-line dialog is "Ctrl+t, s". This is a two-step shortcut.
You press "Ctrl+t", then release both keys and then press "s". On MacOS instead of "Ctrl+t" you 
use "Cmd+t". It's also illustrated [here](https://www.youtube.com/watch?v=PlcsNIsYc7k&feature=youtu.be&t=305)
in the AnKingMed explainer video.
- If you don't know the difference between the Anki terms *note* and *card* this add-on might be 
confusing. For details see the [manual](https://docs.ankiweb.net/#/), or see 
[here](https://www.reddit.com/r/Anki/comments/8w2b5e/the_fundamental_principle_of_anki_card_creation/) 
or 
[here](https://www.reddit.com/r/Anki/comments/9nkg7i/how_do_i_create_separate_card_types_in_different/e7n0x5n/) or [this youtube video](https://www.youtube.com/watch?v=fUKPtnx8LC0).
- When searching I regularly want to see just one card per note. In Anki 2.1.45 from 2021-08 or newer
there's a toggle next to the search bar to show cards or notes. For older Anki versions
you needed workarounds: e.g. you could add "card:1" to each search. Or you could use the add-on
[Card browser: List only one card per note](https://ankiweb.net/shared/info/797076357) 
by Arthur Milchior which depends on the add-on [Advanced Browser](https://ankiweb.net/shared/info/874215009).
- BetterSearch contains lots of code. So you might find a bug or problem. If you do let me know
in the [support thread in the anki support forum](https://forums.ankiweb.net/t/browser-search-box-quick-insert-tag-deck-notetype-official-thread/547) or on [github](https://github.com/ijgnd/anki__browser_search__quick_insert_tag_deck_notetype/issues").

&nbsp;

### For older Anki versions (2.1.40 from 2021-02 or older)

- This add-on has an option `"-Modify Search Bar"` (default is `false`) that offers to modify the 
search bar in the browser. For Anki versions 2.1.40 or lower (where the search bar is narrow 
because there are buttons to "Filter", "Search", and "Preview") you can use the setting
`"down"` to move the search bar is down so that it's just
wider. If you set it to `"multiline"` the search bar will also have multiple lines in the
browser. If you use the `"multiline"` option there's no drop down menu for your search history. 
Instead you access it with the history shortcut you can configure below or with the newly 
added "History" button . If you use the `"multiline"` option you can go to the next line with 
Alt+Return.
The function `"-Modify Search Bar"` not just extends Anki but modifies a built-in feature. Add-ons
often do this but such modifications are more brittle in the long run: If other add-ons try to 
overwrite the same part of Anki errors might occur. E.g. Glutanimate's "Sticky Searches" modifies 
the same part of the browser as this add-on. So most likely if you use "Sticky Searches" you
must set `"-Modify Search Bar"` to `false` so that my add-on doesn't modify this part of the 
browser which means there's no add-on conflict anymore. There are over 600 different add-ons. 
I can't test all of these. So maybe there's another add-on that doesn't work with the 
`"multiline"` or  `"down"` setting.
Another problem with add-ons overwriting built-in Anki functions is that each Anki update might 
break the add-on. In this case I'll try to upload an update in time to ankiweb. But maybe I'll be on
holiday then or no longer use Anki or whatever. In this case you'd have to set
 `"-Modify Search Bar"` to `false` to avoid the problem. 
- `"-Multiline bar Auto Search on space (only for Anki versions <=2.1.40)"` (default is `true`): If true whenever you type a space (or
alt+return/return in the multi-line bar/dialog) a search is activated. This search will **not**
be added to the search history. 

&nbsp;

### Details
Most of the options should have telling names. Here are some notes about some options:

- `"Add Button to the Browser Search Bar"` (default is `true`): whether the SearchDialog
button is shown in the browser. In some special cases you might want to hide this button, e.g.
if you also use the add-on
[Browser: Table/Editor side-by-side (horizontal split)](https://ankiweb.net/shared/info/831846358)
so that the left column can be more narrow.
- `"Multiline Dialog: use bigger typewriter font"` (default is `true`): This only affects the font 
size in the text box of the extra dialog.
- `"Multiline Dialog: shortcut: open window"` (default is `"Ctrl+t,s"`): This shortcut is 
active in the browser and opens a new multi-line window where you can edit the current 
search term.
- `"Multiline Dialog: Filter Button overwrites by default"` (default is `false`): This "Filter"
button is similar to the "Filter" button in the browser. By default the "Filter" button in the browser
overwrites your search with what you selected. In the Anki browser to append the selection from
the Filter dialog you need to also press "Ctrl"/"Cmd". I often forget this so that I lose 
my search terms. That's why there's this option for my custom "Filter" button inside the 
multi-line dialog.
- `"Multiline Dialog: Shortcut inside: Open History"` (default is `"Ctrl+H, h"`): Inside the multi-line
edit dialog you can insert a prior search which overwrites what's currently in the field.

- `"also use in create filtered deck dialog"` (default is `true`): whether to show this dialog in the 
filtered deck dialog. The shortcuts set in this config won't work in the create filtered deck 
dialog. 
The deck list won't include existing filtered decks because cards that are already in a filtered 
deck can't be added to another filtered deck.

- `"autoadjust FilterDialog position"` (default is `true`): refers to the positioning of the filter
dialog in the browser.

- `"custom tag&deck string 1"` (default is `"xx"`), `"custom tag&deck string 2"` (default is `"all:"`): 
when you type into the browser search box if the last characters match the ones set in these settings 
a dialog with a list of your tags and decks is opened. The selected entry is inserted into the 
search box.

- `"date range dialog for added: string"` (default is `"dadded:"`), 
`"date range dialog for rated: string"` (default is `"drated:"`), 
`"date range dialog for edited: string"` (default is `"dedited:"`) (2.1.28+ only), 
`"date range dialog for introduced: string"` (default is `"dintroduced:"`) (2.1.45+ only) 
open a dialog with a calender-widget if you type "dadded:"/"drated:"/"dedited:"/"dintroduced:" 
into the browser search bar.

- `"ignore upper and lower case (case insensitive search)"` (default is `false`): if this setting 
is `true` the search will be case insensitive. If `false` (the default) typing only in lower case 
means case insensitive search while one upper case character makes the search case sensitive.

- `"modify_card"` (default is `true`): If true, when you type into the browser search box if and the 
characters before the cursor are "card:" a dialog with a list of your card types is opened. 
The selected entry is inserted into the search box.
- The other `"modify ..."` config keys work the same way: For `"modify_deck"` it's `"deck:"`, for 
`"modify_note"` it's `"note:"`, for `modify_tag` it's `"tag:"`, etc. 

- `"tag insertion - add '*' to matches"` (default is `"all"`): possible values: `"all"`, 
`"if_has_subtags"`, `"none"`

### modifier keys
The settings

-  `"modifier for override autosearch default"`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(default is "Shift"), 
-  `"modifier for override add * default"`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(default is "Meta"), 
-  `"modifier for negate"`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(default is "Alt"),
-  `"modifier for insert current text only"`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(default is "Ctrl")

only accept the values "Shift", "Meta", "Alt", "Ctrl" as input. On a Mac "Ctrl" means "Cmd". 
**You may not use "Cmd" for these four config values.**.



## Credits

This add-on was made by ijgnd. I use some code made by other people:

The filter dialog is made of source code in the files fuzzy_panel.py and split_string.py. Most of
the code inside these files was originally made by Rene Schallner for his 
https://github.com/renerocksai/sublimeless_zk. I made some changes to these files. For details
see the top of the two aforementioned files. These files are licensed as GPLv3.

This add-on uses the files "sakura.css" and "sakura-dark.css" from https://github.com/oxalorg/sakura
(Copyright (c) 2016 Mitesh Shah, MIT License).
