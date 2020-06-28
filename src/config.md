<h1>Before you change the config make sure to read the descriptions below</h1>

<h2>Shortcuts in the browser to open certain filter dialogs that you set with the config
keys "shortcut - focus search box and ..." are deprecated since 2020-05. The existing
shortcuts still work but new functions like "field:", "ffn/field from note", date range dialog for added/rated do not have dedicated browser shortcuts.</h2>

This readme is incomplete and will be finished in a future update. But most of the missing
keys should have self-explanatory names.

&nbsp;

- `Multiline Dialog: shortcut: open window` (default is "Ctrl+t,s"): This shortcut is active in 
the browser and opens a new multi-line window where you can edit the current search term.
- `Multiline Dialog: Filter Button overwrites by default` (default is "false"): Depending on the
Anki version you use there's a button "Filter" in the lower left of the multi-line window. This
button is similar to the "Filter" button in the browser. The "Filter" button in the browser
overwrites your search with what you selected. I don't like this so I made this option and set 
it to "false".
- `Multiline Dialog: Shortcut inside: Open History` (default is "Ctrl+H, h"): Inside the multi-line
edit dialog you can insert a prior search which overwrites what's currently in the field.

&nbsp;

- `also use in create filtered deck dialog` (default is "true"): whether to show this dialog in the 
filtered deck dialog. The shortcuts set in this config won't work in the create filtered deck 
dialog. 
The deck list won't include existing filtered decks because cards that are already in a filtered 
deck can't be added to another filtered deck.

&nbsp;

- `autoadjust FilterDialog position` (default is "True"): refers to the positioning of the filter
dialog in the browser.

&nbsp;

- `custom tag&deck string 1` (default is "xx"), `custom tag&deck string 2` (default is "all:"): when 
you type into the browser search box if the last characters match the ones set in these settings 
a dialog with a list of your tags and decks is opened. The selected entry is inserted into the 
search box.

&nbsp;

- `date range dialog for added: string` (default is "dadded:") and 
`date range dialog for rated: string` (default is "drated:") open a dialog with a calender-widget
if you type "dadded"/"drated" into the browser search bar.

&nbsp;

- `ignore upper and lower case (case insensitive search)` (default is "false"): if this setting 
is "true" the search will be case insensitive. If "false" (the default) typing only in lower case 
means case insensitive search while one upper case character makes the search case sensitive.

&nbsp;

- `modify_card` (default is true): when you type into the browser search box if the last 
characters in the search box are "card:" a dialog with a list of your card types is opened. 
The selected entry is inserted into the search box.
- `modify_deck` (default is true): when you type into the browser search box if the last 
characters in the search box are "deck:" a dialog with a list of your decks is opened.
The selected entry is inserted into the search box.
- `modify_note` (default is true): when you type into the browser search box if the last 
characters in the search box are "note:" a dialog with a list of your note types is opened.
The selected entry is inserted into the search box.
- `modify_tag` (default is true): when you type into the browser search box if the last 
characters in the search box are "tag:" a dialog with a list of your tags is opened.
The selected entry is inserted into the search box.

&nbsp;

The config options 

-  `modifier for override autosearch default`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(default is "Shift"), 
-  `modifier for override add * default`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(default is "Meta"), 
-  `modifier for negate`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(default is "Alt"),
-  `modifier for insert current text only`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(default is "Ctrl")

only accept the values "Shift", "Meta", "Alt", "Ctrl" as input. On a Mac "Ctrl" means "Cmd". 
**You may not use "Cmd" for these four config values.**.

&nbsp;

&nbsp;

- `shortcut - focus search box and card selector dialog` (default is "Ctrl+H, c"): shortcut to open 
a dialog with a list of your card types. The selected entry is inserted into the search box.
- `shortcut - focus search box and deck selector dialog` (default is "Ctrl+H, d"): shortcut to open 
a dialog with a list of your decks. The selected entry is inserted into the search box.
- `shortcut - focus search box and note selector dialog` (default is "Ctrl+H, n"): shortcut to open 
a dialog with a list of your note types. The selected entry is inserted into the search box.
- `shortcut - focus search box and tag selector dialog` (default is "Ctrl+H, t"): shortcut to open 
a dialog with a list of your tags. The selected entry is inserted into the search box.
- `shortcut - focus search box and tag/deck selector dialog` (default is "Ctrl+H, m"): shortcut to 
open a dialog with a list of your tags and decks. The selected entry is inserted into the search 
box.

&nbsp;

- `shortcut - select entry from history in fuzzy dialog` (default is "Ctrl+H, h"): opens the search
history in a fuzzy filter dialog. Search terms are split up into multiple lines so that it's easier
to deal with long searches.

&nbsp;

- `shortcuts trigger search by default` (default is true): 

&nbsp;

- `tag insertion - add '*' to matches` (default is "all"): possible values: "all", "if_has_subtags",
"none"
