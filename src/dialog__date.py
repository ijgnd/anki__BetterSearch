import datetime

from .config import gc, wcs
from . import in_full_anki_with_gui

if in_full_anki_with_gui:
    from aqt import mw
    from aqt.qt import (
        QDate,
        QDialog,
        Qt,
        qtmajor,
    )
    from aqt.utils import (
        restoreGeom,
        saveGeom,
        tooltip,
    )

    if qtmajor == 5:
        from .forms5 import date_dialog_ui  # type: ignore  # noqa
    else:
        from .forms6 import date_dialog_ui  # type: ignore  # noqa
    size_string = "Addon Browser Quick Insert Date Picker"


def date_range_string_from_upper_and_lower(lower, upper, search_word, is_minus):
    # search word is either "rated" or "added" or "edited" or "introduced"
    if is_minus:
        if upper > 1:
            stext = f"(-{search_word}:{lower} OR {search_word}:{upper - 1})"
        else:
            stext = f"-{search_word}:{lower}"
    else:
        stext = f"{search_word}:{lower}"
        if upper > 1:
            stext += f" -{search_word}:{upper - 1}"
    return stext


def get_date_range_string(
    parent, col, search_operator, prefixed_with_minus, test_lower=None, test_upper=None, test_custom_datetime=None
):
    if test_custom_datetime:
        today = test_custom_datetime
    else:
        today = datetime.datetime.today()  # returns the current local date, same as date.fromtimestamp(time.time())
    today_as_dt = today_as_datetime_adjusted_for_next_day_starts_at(col, today)
    if in_full_anki_with_gui:
        d = DatesDialog(parent, search_operator, today_as_dt, prefixed_with_minus)
        if d.exec():
            return (
                True,
                date_range_string_from_upper_and_lower(d.lower, d.upper, search_operator, prefixed_with_minus),
                d.run_search_on_exit,
            )
        else:
            return None, None, None
    else:
        return True, date_range_string_from_upper_and_lower(
            test_lower, test_upper, search_operator, prefixed_with_minus
        ), None


# TODO: simplify this
def today_as_datetime_adjusted_for_next_day_starts_at(col, today):
    # dayOffset - next day starts at
    # in 2.1.14 values can be between 0 and 23, no negative values
    if col.schedVer() == 2:
        day_offset = col.conf.get("rollover", 4)
    else:
        # https://github.com/ankidroid/Anki-Android/wiki/Database-Structure
        #   crt = timestamp of the creation date. It's correct up to the day. For V1 scheduler,
        #   the hour corresponds to starting a new day. By default, new day is 4.
        day_offset = datetime.datetime.fromtimestamp(col.crt).hour
    if today.hour < day_offset:
        today = today - datetime.timedelta(days=1)
    return today


toptext = """
<div>
In Anki you cannot search by date. Instead you can only limit your search to "rated:1"(=rated today)
or "rated:2" (=rated today or yesterday) and so on. This add-on dialog allows you select two dates
and transforms them to a search term Anki understands.
</div>
<br>
<div>
e.g. if today is 2020-06-28 and you select 2020-06-15 in the left calendar widget and 2020-06-19 
this add-on will generate the following search text:  rated:14 -rated:9  which means "show all 
notes/cards that were rated in the last 14 days (i.e. on or after 2020-06-15) but not those that  
were rated after 9 days (i.e. those rated on or after 2020-06-20).
</div>
<br>
<br>
<br>
"""

if in_full_anki_with_gui:

    class DatesDialog(QDialog):
        silentlyClose = True

        def __init__(self, parent, search_word, today_as_dt, is_minus=False):
            self.search_word = search_word
            self.parent = parent
            self.is_minus = is_minus
            QDialog.__init__(self, self.parent, Qt.WindowType.Window)
            mw.garbage_collect_on_dialog_finish(self)
            self.form = date_dialog_ui.Ui_Dialog()
            self.form.setupUi(self)
            self.today_in_dt = today_as_dt
            self.setupUI()
            self.setupConnections()
            check = gc(["filter dialog automatically search on close", "Date Dialogs"])
            self.form.cb_run_search_after.setChecked(check)
            self.run_search_on_exit = False

        def setupUI(self):
            self.form.qlabel_top.setText(toptext)
            self.setWindowTitle("Anki: Pick Dates")
            self.resize(800, 650)
            restoreGeom(self, size_string)
            self.form.pb_accepted.clicked.connect(self.accept)
            self.form.pb_accepted.setShortcut("Ctrl+Return")
            self.form.pb_accepted.setToolTip("Ctrl+Return")
            self.form.pb_rejected.clicked.connect(self.reject)
            self.form.pb_rejected.setShortcut("Esc")
            self.form.pb_rejected.setToolTip("Esc")

            d = self.today_in_dt
            today_as_qdate = QDate(d.year, d.month, d.day)
            self.form.cw_before.setMaximumDate(today_as_qdate)
            # if self.is_minus:
            #     self.form.cw_before.hide()
            #     self.form.label_before.hide()
            #     self.form.label_before_days.hide()
            #     self.form.qsp_before.hide()
            self.form.cw_after.setMaximumDate(today_as_qdate)

            self.form.qsp_before.setValue(1)
            self.form.qsp_before.setMinimum(1)
            self.form.qsp_before.setMaximum(6000)  # default is 99

            self.form.qsp_after.setValue(1)
            self.form.qsp_after.setMinimum(1)
            self.form.qsp_after.setMaximum(6000)

        def setupConnections(self):
            # calendar widget changed
            self.form.cw_before.selectionChanged.connect(
                lambda cw=self.form.cw_before, sb=self.form.qsp_before: self.adjust_spinbox_on_other_date_clicked(
                    cw, sb
                )
            )
            self.form.cw_after.selectionChanged.connect(
                lambda cw=self.form.cw_after, sb=self.form.qsp_after: self.adjust_spinbox_on_other_date_clicked(cw, sb)
            )

            # spinbox changed
            self.form.qsp_before.valueChanged.connect(
                lambda cw=self.form.cw_before, sb=self.form.qsp_before: self.adjust_calendar_based_on_spinbox_change(
                    cw, sb
                )
            )
            self.form.qsp_after.valueChanged.connect(
                lambda cw=self.form.cw_after, sb=self.form.qsp_after: self.adjust_calendar_based_on_spinbox_change(
                    cw, sb
                )
            )

        def adjust_spinbox_on_other_date_clicked(self, cal_widget, spinbox):
            sel = cal_widget.selectedDate()  # QDate
            sd = datetime.datetime(sel.year(), sel.month(), sel.day())
            diff = self.today_in_dt - sd
            # https://stackoverflow.com/questions/26358945/qt-find-out-if-qspinbox-was-changed-by-user
            spinbox.blockSignals(True)
            spinbox.setValue(diff.days + 1)
            spinbox.blockSignals(False)

        def adjust_calendar_based_on_spinbox_change(self, cal_widget, spinbox):
            sbval = spinbox.value()
            newday = self.today_in_dt - datetime.timedelta(days=sbval - 1)
            # https://stackoverflow.com/questions/26358945/qt-find-out-if-qspinbox-was-changed-by-user
            cal_widget.blockSignals(True)
            cal_widget.setSelectedDate(QDate(newday.year, newday.month, newday.day))
            cal_widget.blockSignals(False)

        def reject(self):
            saveGeom(self, size_string)
            QDialog.reject(self)

        def accept(self):
            self.lower = self.form.qsp_after.value()
            self.upper = self.form.qsp_before.value()
            checked = self.form.cb_run_search_after.isChecked()
            self.run_search_on_exit = checked
            wcs(["filter dialog automatically search on close", "Date Dialogs"], checked)
            if self.upper > self.lower:  # upper/before may not be more in the past than lower/after
                tooltip("the before date(right) may not be earlier than the after date(left)")
                return
            saveGeom(self, size_string)
            QDialog.accept(self)
