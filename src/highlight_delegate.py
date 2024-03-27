# Original work Copyright (c): 2018 eyllanesc (https://stackoverflow.com/a/53357083, CC BY-SA 4.0)
# modified: 2024- ijgnd

# adopted from https://stackoverflow.com/questions/53353450/how-to-highlight-a-words-in-qtablewidget-from-a-searchlist
# the QTextDocument approach is common, see e.g.
#    https://stackoverflow.com/questions/1956542/how-to-make-item-view-render-rich-html-text-in-qt/#66091713
#    https://stackoverflow.com/questions/51613638/highlight-search-results-in-qtablewidgetselect-and-highlight-that-text-or-chara
#
# the approach from https://stackoverflow.com/questions/1956542/how-to-make-item-view-render-rich-html-text-in-qt/#66091713
# can also be reused more or less directly. The downside is that (a) I need to apply the html/rich text styling
# myself, e.g. in FilterDialog.update_listwidget and (b) sometimes the line height is wrong initially (though
# after typing one letter when everything gets repainted the problem disappears.


from aqt.qt import (
    QAbstractTextDocumentLayout,
    QApplication,
    QPalette,
    QStyle,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QTextCharFormat,
    QTextCursor,
    QTextDocument,
    Qt,
    pyqtSlot,
)


class HighlightDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super(HighlightDelegate, self).__init__(parent)
        self.doc = QTextDocument(self)
        self._filters = []

    def paint(self, painter, option, index):
        painter.save()
        options = QStyleOptionViewItem(option)
        self.initStyleOption(options, index)
        self.doc.setPlainText(options.text)
        self.apply_highlight()
        options.text = ""
        style = QApplication.style() if options.widget is None else options.widget.style()
        style.drawControl(QStyle.ControlElement.CE_ItemViewItem, options, painter)

        ctx = QAbstractTextDocumentLayout.PaintContext()
        if option.state & QStyle.StateFlag.State_Selected:
            ctx.palette.setColor(
                QPalette.ColorRole.Text,
                option.palette.color(QPalette.ColorGroup.Active, QPalette.ColorRole.HighlightedText),
            )
        else:
            ctx.palette.setColor(
                QPalette.ColorRole.Text, option.palette.color(QPalette.ColorGroup.Active, QPalette.ColorRole.Text)
            )

        textRect = style.subElementRect(QStyle.SubElement.SE_ItemViewItemText, options)

        if index.column() != 0:
            textRect.adjust(5, 0, 0, 0)

        the_constant = 4
        margin = (option.rect.height() - options.fontMetrics.height()) // 2
        margin = margin - the_constant
        textRect.setTop(textRect.top() + margin)

        painter.translate(textRect.topLeft())
        painter.setClipRect(textRect.translated(-textRect.topLeft()))
        self.doc.documentLayout().draw(painter, ctx)

        painter.restore()

    def apply_highlight(self):
        cursor = QTextCursor(self.doc)
        cursor.beginEditBlock()
        fmt = QTextCharFormat()
        fmt.setForeground(Qt.GlobalColor.red)
        for f in self.filters():
            highlightCursor = QTextCursor(self.doc)
            while not highlightCursor.isNull() and not highlightCursor.atEnd():
                highlightCursor = self.doc.find(f, highlightCursor)
                if not highlightCursor.isNull():
                    highlightCursor.mergeCharFormat(fmt)
        cursor.endEditBlock()

    @pyqtSlot(list)
    def setFilters(self, filters):
        if self._filters == filters:
            return
        self._filters = filters

    def filters(self):
        return self._filters
