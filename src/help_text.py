from anki.utils import pointVersion

from .config import gc


# for multiline add-on
def help_string_for_actions_used():
    lines = []
    if gc("modify_note"):
        s = '"note:" filter by note type (model) name'
        lines.append(s)
    if gc("modify_card"):
        s = '"card:" filter for card (type) names'
        lines.append(s)
    if gc("modify_field"):
        s = '"field:" filter by field name'
        lines.append(s)
    if gc("modify_deck"):
        s = '"deck:" filter by deck name'
        lines.append(s)
    s = '"ffn:" select two filters: field from note'
    lines.append(s)
    s = '"cfn:" select two filters: card from note'
    lines.append(s)
    if gc("modify_tag"):
        s = '"tag:" filter by tag'
        lines.append(s)
    if gc("modify_is"):
        s = '"is:" filter by card state'
        lines.append(s)
    if gc("modify_props"):
        s = '"prop:" filter by card properties (like due date, ease)'
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
    if gc("date range dialog for edited: string") and pointVersion() >= 28:
        s = f'"{gc("date range dialog for edited: string")}": date range dialog for date edited'
        lines.append(s)
    if gc("date range dialog for rated: string"):
        s = f'"{gc("date range dialog for rated: string")}": date range dialog for date rated'
        lines.append(s)

    s = """
<div style="font-size: 120%;">
<b>
BetterSearch Add-on: terms/keywords that open a filter dialog:
</b>
</div>
"""
    s += "<ul>"
    for l in lines:
        s += "<li>" + l + "</li>"
    s += "</ul>"
    return s



helptext = help_string_for_actions_used() + """
<br>
<div>
The following section is copied from the manual in 2020-07-03. So you have the search section with you 
even if you are offline. In the future the rest of this page might get replaced with some shorter
notes.
</div>
<section class="content">
<article id="main" class="markdown-section">
<h1 id="searching"><a class="anchor" href="https://docs.ankiweb.net/#/searching?id=searching" data-id="searching">About Searching in Anki</a></h1>
<p>Anki&rsquo;s Browse screen and the Filtered Deck feature use a common method of searching for specific cards/notes.</p>
<h2 id="simple-searches"><a class="anchor" href="https://docs.ankiweb.net/#/searching?id=simple-searches" data-id="simple-searches">Simple searches</a></h2>
<p>When you type some text into the search box, Anki finds matching notes and displays their cards. Anki searches in all fields of the notes, but does not search for tags (see later in this section for how to search for tags). Some examples:</p>
<p><code>dog</code><br />search for &ldquo;dog&rdquo; - will match words like &ldquo;doggy&rdquo; and &ldquo;underdog&rdquo; too.</p>
<p><code>dog cat</code><br />finds notes that have both &ldquo;dog&rdquo; and &ldquo;cat&rdquo; on them, such as &ldquo;raining cats and dogs&rdquo;&rdquo;.</p>
<p><code>dog or cat</code><br />finds notes with either &ldquo;dog&rdquo; or &ldquo;cat&rdquo;.</p>
<p><code>dog (cat or mouse)</code><br />finds notes with dog and cat, or dog and mouse.</p>
<p><code>-cat</code><br />finds notes without the word &ldquo;cat&rdquo;.</p>
<p><code>-cat -mouse</code><br />finds notes with neither &ldquo;cat&rdquo; nor &ldquo;mouse&rdquo;.</p>
<p><code>-(cat or mouse)</code><br />same as the above.</p>
<p><code>"a dog"</code><br />finds notes with the exact sequence of characters &ldquo;a dog&rdquo; on them, such as &ldquo;atta dog&rdquo;, but not &ldquo;dog a&rdquo; or &ldquo;adog&rdquo;.</p>
<p><code>-"a dog"</code><br />finds notes without the exact phrase &ldquo;a dog&rdquo;</p>
<p><code>d_g</code><br />finds notes with d, &lt;a letter&gt;, g, like dog, dig, dug, and so on.</p>
<p><code>d*g</code><br />finds notes with d, &lt;zero or more letters&gt;, g, like dg, dog, dung, etc.</p>
<p><code>w:dog</code><br />search for &ldquo;dog&rdquo; on a word boundary - will match &ldquo;dog&rdquo;, but not &ldquo;doggy&rdquo; or &ldquo;underdog&rdquo;. Requires Anki 2.1.24+ or AnkiMobile 2.1.61+.</p>
<p><code>w:dog*</code><br />will match &ldquo;dog&rdquo; and &ldquo;doggy&rdquo;, but not &ldquo;underdog&rdquo;.</p>
<p><code>w:*dog</code><br />will match &ldquo;dog&rdquo; and &ldquo;underdog&rdquo;, but not &ldquo;doggy&rdquo;.</p>
<p>Things to note from the above:</p>
<ul>
<li>
<p>Search terms are separated by spaces.</p>
</li>
<li>
<p>When multiple search terms are provided, Anki looks for notes that match all of the terms - an implicit &lsquo;and&rsquo; is inserted between each term. On Anki 2.1.24+ and AnkiMobile 2.0.60+ you can be explicit if you like (&ldquo;dog and cat&rdquo; is the same as &ldquo;dog cat&rdquo;), but older Anki versions will treat &ldquo;and&rdquo; as just another word to search for.</p>
</li>
<li>
<p>You can use &ldquo;or&rdquo; if you only need one of the terms to match.</p>
</li>
<li>
<p>You can prepend a minus sign to a term to find notes that don&rsquo;t match.</p>
</li>
<li>
<p>If you want to search for something including a space or parenthesis, enclose it in double quotes. You can quote either the <code>"entire:term"</code>, or just the <code>part:"after a colon"</code>.</p>
</li>
<li>
<p>You can group search terms by placing them in parentheses, as in the <strong>dog (cat or mouse)</strong> example. This becomes important when combining OR and AND searches&thinsp;&mdash;&thinsp;in the example, with the parentheses, it matches either &lsquo;dog cat&rsquo; or &lsquo;dog mouse&rsquo;, whereas without them it would match either &lsquo;dog and cat&rsquo; or &lsquo;mouse&rsquo;.</p>
</li>
<li>
<p>Anki is only able to search within formatting in the <a href="https://docs.ankiweb.net/#/editing?id=customizing-fields">sort field</a> you&rsquo;ve configured. For example, if you add &ldquo;<strong>exa</strong>mple&rdquo; to one of your fields, this will not be matched when searching for &ldquo;example&rdquo; unless that field is the sort field. If a word is not formatted, or the formatting does not change in the middle of the word, then Anki will be able to find it in any field.</p>
</li>
</ul>
<h2 id="limiting-to-a-field"><a class="anchor" href="https://docs.ankiweb.net/#/searching?id=limiting-to-a-field" data-id="limiting-to-a-field">Limiting to a field</a></h2>
<p>You can also ask Anki to match only if a particular field contains some text. Unlike the searches above, searching on fields requires an &lsquo;exact match&rsquo; by default.</p>
<p><code>front:dog</code><br />find notes with a Front field of exactly &ldquo;dog&rdquo;. A field that says &ldquo;a dog&rdquo; will not match.</p>
<p><code>front:*dog*</code><br />find notes with Front field containing dog somewhere</p>
<p><code>front:</code><br />find notes that have an empty Front field</p>
<p><code>front:_*</code><br />find notes that have a non-empty Front field</p>
<p><code>front:*</code><br />find notes that have a Front field, empty or not</p>
<p><code>fr*:text</code> find notes in a field starting with &ldquo;fr&rdquo;. Requires Anki 2.1.24+ or AnkiMobile 2.1.60+.</p>
<h2 id="tags-decks-cards-and-notes"><a class="anchor" href="https://docs.ankiweb.net/#/searching?id=tags-decks-cards-and-notes" data-id="tags-decks-cards-and-notes">Tags, decks, cards and notes</a></h2>
<p><code>tag:animal</code><br />find notes with the tag &ldquo;animal&rdquo;</p>
<p><code>tag:none</code><br />find notes with no tags</p>
<p><code>tag:ani*</code><br />find notes with tags starting with ani</p>
<p><code>deck:french</code><br />find cards in a French deck, or subdecks like French::Vocab</p>
<p><code>deck:french -deck:french::*</code><br />find cards in French, but not subdecks</p>
<p><code>deck:"french vocab"</code><br />searching when a deck has a space</p>
<p><code>"deck:french vocab"</code><br />also ok</p>
<p><code>deck:filtered</code><br />filtered decks only</p>
<p><code>-deck:filtered</code><br />normal decks only</p>
<p><code>card:forward</code><br />search for Forward cards</p>
<p><code>card:1</code><br />search for cards by template number - eg, to find the second cloze deletion for a note, you&rsquo;d use card:2</p>
<p><code>note:basic</code><br />search for cards with a Basic note type</p>
<h2 id="ignoring-accentscombining-characters"><a class="anchor" href="https://docs.ankiweb.net/#/searching?id=ignoring-accentscombining-characters" data-id="ignoring-accentscombining-characters">Ignoring accents/combining characters</a></h2>
<p>Requires Anki 2.1.24+ or AnkiMobile 2.0.60+.</p>
<p>You can use <code>nc:</code> to remove combining characters (&ldquo;no combining&rdquo;). For example:</p>
<p><code>nc:uber</code><br />matches notes with &ldquo;uber&rdquo;, &ldquo;&uuml;ber&rdquo;, &ldquo;&Uuml;ber&rdquo; and so on.</p>
<p><code>nc:は</code><br />matches &ldquo;は&rdquo;, &ldquo;ば&rdquo;, and &ldquo;ぱ&rdquo;</p>
<p>Searches that ignore combining characters are slower than regular searches.</p>
<h2 id="regular-expressions"><a class="anchor" href="https://docs.ankiweb.net/#/searching?id=regular-expressions" data-id="regular-expressions">Regular expressions</a></h2>
<p>Anki 2.1.24+ and AnkiMobile 2.0.60+ support searching in notes with &ldquo;regular expressions&rdquo;, a standard and powerful way of searching in text.</p>
<p>Start a search with <code>re:</code> to search by regular expression. Some examples:</p>
<p><code>"re:(some|another).*thing"</code><br />find notes that have &ldquo;some&rdquo; or &ldquo;another&rdquo; on them, followed by 0 or more characters, and then &ldquo;thing&rdquo;</p>
<p><code>re:\d{3}</code><br />find notes that have 3 digits in a row</p>
<p>Regular expressions can also be limited to a specific field. Please note that unlike the normal searches in a specific field, regular expressions in fields don&rsquo;t require an exact match. Eg:</p>
<p><code>front:re:[a-c]1</code><br />matches uppercase or lowercase a1, B1 or c1 that occurs anywhere in the &ldquo;Front&rdquo; field</p>
<p><code>front:re:^[a-c]1$</code><br />like the above, but will not match if any other text falls before or after a1/b1/c1.</p>
<p>You can learn more about regular expressions here: <a href="https://regexone.com/lesson/introduction_abcs" target="_blank" rel="noopener">https://regexone.com/lesson/introduction_abcs</a></p>
<p>Some things to be aware of:</p>
<ul>
<li>The search is case-insensitive by default; use (?-i) at the start to turn on case sensitivity.</li>
<li>Some text like spaces and newlines may be represented differently in HTML - you can use the HTML editor in the editing screen to see the underlying HTML contents.</li>
<li>For the specifics of Anki&rsquo;s regex support, please see the regex crate documentation: <a href="https://docs.rs/regex/1.3.9/regex/#syntax" target="_blank" rel="noopener">https://docs.rs/regex/1.3.9/regex/#syntax</a></li>
</ul>
<h2 id="card-state"><a class="anchor" href="https://docs.ankiweb.net/#/searching?id=card-state" data-id="card-state">Card state</a></h2>
<p><code>is:due</code><br />review cards and learning cards waiting to be studied</p>
<p><code>is:new</code><br />new cards</p>
<p><code>is:learn</code><br />cards in learning</p>
<p><code>is:review</code><br />reviews (both due and not due) and lapsed cards</p>
<p><code>is:suspended</code><br />cards that have been manually suspended</p>
<p><code>is:buried</code><br />cards that have been buried, either <a href="https://docs.ankiweb.net/#/studying?id=siblings-and-burying">automatically</a> or manually</p>
<p>Cards that have lapsed fall into several of these categories, so it may be useful to combine them to get more precise results:</p>
<p><code>is:learn is:review</code><br />cards that have lapsed and are awaiting relearning</p>
<p><code>-is:learn is:review</code><br />review cards, not including lapsed cards</p>
<p><code>is:learn -is:review</code><br />cards that are in learning for the first time</p>
<h2 id="card-properties"><a class="anchor" href="https://docs.ankiweb.net/#/searching?id=card-properties" data-id="card-properties">Card properties</a></h2>
<p><code>prop:ivl&gt;=10</code><br />cards with interval of 10 days or more</p>
<p><code>prop:due=1</code><br />cards due tomorrow</p>
<p><code>prop:due=-1</code><br />cards due yesterday that haven&rsquo;t been answered yet</p>
<p><code>prop:due&gt;-1 prop:due&lt;1</code><br />cards due between yesterday and tomorrow</p>
<p><code>prop:reps&lt;10</code><br />cards that have been answered less than 10 times</p>
<p><code>prop:lapses&gt;3</code><br />cards that have moved into relearning more than 3 times</p>
<p><code>prop:ease!=2.5</code><br />cards easier or harder than default</p>
<p>Note that due only matches review cards and learning cards with an interval of a day or more: cards in learning with small intervals like 10 minutes are not included.</p>
<h2 id="recently-added"><a class="anchor" href="https://docs.ankiweb.net/#/searching?id=recently-added" data-id="recently-added">Recently added</a></h2>
<p><code>added:1</code><br />cards added today</p>
<p><code>added:7</code><br />cards added in last week</p>
<p>The check is made against card creation time rather than note creation time, so cards that were generated within the time frame will be included even if their notes were added a long time ago.</p>
<h2 id="recently-answered"><a class="anchor" href="https://docs.ankiweb.net/#/searching?id=recently-answered" data-id="recently-answered">Recently answered</a></h2>
<p><code>rated:1</code><br />cards answered today</p>
<p><code>rated:1:2</code><br />cards answered Hard (2) today</p>
<p><code>rated:7:1</code><br />cards answered Again (1) over the last 7 days</p>
<p><code>rated:31:4</code><br />cards answered Easy (4) in the last month</p>
<p>For speed, rating searches are limited to 31 days.</p>
<h2 id="object-ids"><a class="anchor" href="https://docs.ankiweb.net/#/searching?id=object-ids" data-id="object-ids">Object IDs</a></h2>
<p><code>nid:123</code><br />all cards of the note with note id 123</p>
<p><code>cid:123</code><br />the card with card id 123</p>
<p><code>mid:123</code><br />find note types with note type id 123</p>
<p>Note and card IDs can be found in the <a href="https://docs.ankiweb.net/#/stats">card info</a> dialog in the browser. Note type IDs can be found by clicking on a note type in the Browse screen. These searches may also be helpful when doing add-on development or otherwise working closely with the database.</p>
<p>Object IDs will not work in the mobile clients, and are not intended to be used in filtered decks at the moment.</p>
</article>
</section>
"""