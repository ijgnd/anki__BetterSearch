from aqt.utils import (
    tr,
)


def browser_searchEdit_hint_shown(searchstring, browser=None):
    return searchstring == tr.browsing_search_bar_hint()
