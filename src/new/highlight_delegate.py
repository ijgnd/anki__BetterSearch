from aqt.qt import (
    pyqtSlot,
    QApplication,
    QColor,
    QPen,
    QStyle,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    Qt,
)


class HighlightDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.filters = []
        self._highlightColor = QColor(Qt.GlobalColor.red)

    def paint(self, painter, option, index):
        painter.save()

        # Initialize the style option
        viewOption = QStyleOptionViewItem(option)
        self.initStyleOption(viewOption, index)

        text = viewOption.text
        viewOption.text = ""  # otherwise chars are shown twice as if I had double vision

        # Draw the background, selection, etc. as usual
        style = viewOption.widget.style() if viewOption.widget else QApplication.style()
        style.drawControl(QStyle.ControlElement.CE_ItemViewItem, viewOption, painter)

        # manually draw text
        textRect = style.subElementRect(QStyle.SubElement.SE_ItemViewItemText, viewOption)
        painter.setClipRect(textRect)
        painter.translate(textRect.topLeft())

        if option.state & QStyle.StateFlag.State_Selected:
            normalPen = QPen(viewOption.palette.highlightedText().color())
        else:
            normalPen = QPen(viewOption.palette.text().color())

        segments = self.segment_text(text, self.filters)

        # font metrics to measure text widths
        fm = viewOption.fontMetrics
        x = 0
        baseline = fm.ascent()  # so drawText can align on baseline

        for segment, isHighlighted in segments:
            width = fm.horizontalAdvance(segment)
            if isHighlighted:
                painter.setPen(self._highlightColor)
            else:
                painter.setPen(normalPen)
            painter.drawText(x, baseline, segment)
            x += width

        painter.restore()

    def segment_text(self, text, filters):
        # Return a list of (substring, isHighlighted)
        #  - find all matches for each filter
        #  - merge them into intervals
        #  - then cut the original string into normal vs. highlight chunks
        if not filters or not text:
            return [(text, False)]

        intervals = []
        lower_text = text.lower()

        for flt in filters:
            flt_lower = flt.lower()
            start = 0
            while True:
                idx = lower_text.find(flt_lower, start)
                if idx == -1:
                    break
                intervals.append((idx, idx + len(flt)))
                start = idx + len(flt)

        if not intervals:
            return [(text, False)]

        # Merge overlapping intervals
        intervals.sort(key=lambda x: x[0])
        merged = []
        current_start, current_end = intervals[0]
        for i in range(1, len(intervals)):
            st, en = intervals[i]
            if st <= current_end:  # overlap
                current_end = max(current_end, en)
            else:
                merged.append((current_start, current_end))
                current_start, current_end = st, en
        merged.append((current_start, current_end))

        # slice up text based on merged intervals
        segments = []
        last_end = 0
        for (start_i, end_i) in merged:
            # normal text before highlight
            if start_i > last_end:
                segments.append((text[last_end:start_i], False))
            # highlight text
            segments.append((text[start_i:end_i], True))
            last_end = end_i

        # normal text after final highlight
        if last_end < len(text):
            segments.append((text[last_end:], False))

        return segments

    @pyqtSlot(list)
    def setFilters(self, filters):
        # Update the list of substrings to highlight.
        if self.filters != filters:
            self.filters = filters

    def filters(self):
        return self.filters
