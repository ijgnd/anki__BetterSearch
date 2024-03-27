"""
    Elypson/qt-collapsible-section
    (c) 2016 Michael A. Voelkel - michael.alexander.voelkel@gmail.com
    This file is part of Elypson/qt-collapsible section.

    Elypson/qt-collapsible-section is free software: you can redistribute it and/or modify
    it under the terms of the GNU Lesser General Public License as published by
    the Free Software Foundation, version 3 of the License, or
    (at your option) any later version.

    Elypson/qt-collapsible-section is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Lesser General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Elypson/qt-collapsible-section. If not, see <http:#www.gnu.org/licenses/>.

    
    copied from https://github.com/MichaelVoelkel/qt-collapsible-section/blob/master/Section.py
    in 2024-03

    MODIFIED ijgnd 2024+    
"""


from aqt.qt import (
    QAbstractAnimation,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QParallelAnimationGroup,
    QPropertyAnimation,
    QSizePolicy,
    QScrollArea,
    QSpacerItem,
    Qt,
    QToolButton,
    QWidget,
)


class CollapsibleSection(QWidget):
    def __init__(self, title="", animationDuration=100, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.animationDuration = animationDuration
        self.toggleButton = QToolButton(self)
        self.headerLine = QFrame(self)
        self.toggleAnimation = QParallelAnimationGroup(self)
        self.contentArea = QScrollArea(self)
        self.mainLayout = QGridLayout(self)

        self.toggleButton.setStyleSheet("QToolButton {border: none;}")
        self.toggleButton.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.toggleButton.setArrowType(Qt.ArrowType.RightArrow)
        self.toggleButton.setText(title)
        self.toggleButton.setCheckable(True)
        self.toggleButton.setChecked(False)

        self.headerLine.setFrameShape(QFrame.Shape.HLine)
        self.headerLine.setFrameShadow(QFrame.Shadow.Sunken)
        self.headerLine.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)  # horizontal, vertical

        # self.contentArea.setLayout(QHBoxLayout())
        self.contentArea.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)  # horizontal, vertical

        # start out collapsed
        self.contentArea.setMaximumHeight(0)
        self.contentArea.setMinimumHeight(0)

        # let the entire widget grow and shrink with its content
        self.toggleAnimation.addAnimation(QPropertyAnimation(self, b"minimumHeight"))
        self.toggleAnimation.addAnimation(QPropertyAnimation(self, b"maximumHeight"))
        self.toggleAnimation.addAnimation(QPropertyAnimation(self.contentArea, b"maximumHeight"))

        self.mainLayout.setVerticalSpacing(0)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)

        row = 0
        self.mainLayout.addWidget(self.toggleButton, row, 0, 1, 1, Qt.AlignmentFlag.AlignLeft)
        self.mainLayout.addWidget(self.headerLine, row, 2, 1, 1)
        self.mainLayout.addWidget(self.contentArea, row + 1, 0, 1, 3)
        self.setLayout(self.mainLayout)

        self.toggleButton.toggled.connect(self.toggle)

        self.contentArea.setFrameStyle(QFrame.Shape.NoFrame)  # no border

    def setContentLayout(self, contentLayout):
        layout = self.contentArea.layout()
        del layout

        left_padding_layout = QHBoxLayout()
        spacer = QSpacerItem(35, 35, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        left_padding_layout.addItem(spacer)
        left_padding_layout.addLayout(contentLayout)
        self.contentArea.setLayout(left_padding_layout)

        # self.contentArea.setLayout(contentLayout)
        collapsedHeight = self.sizeHint().height() - self.contentArea.maximumHeight()
        contentHeight = contentLayout.sizeHint().height()
        for i in range(0, self.toggleAnimation.animationCount() - 1):
            SectionAnimation = self.toggleAnimation.animationAt(i)
            SectionAnimation.setDuration(self.animationDuration)
            SectionAnimation.setStartValue(collapsedHeight)
            SectionAnimation.setEndValue(collapsedHeight + contentHeight)
        contentAnimation = self.toggleAnimation.animationAt(self.toggleAnimation.animationCount() - 1)
        contentAnimation.setDuration(self.animationDuration)
        contentAnimation.setStartValue(0)
        contentAnimation.setEndValue(contentHeight)

    def toggle(self, collapsed):
        if collapsed:
            self.toggleButton.setArrowType(Qt.ArrowType.DownArrow)
            self.toggleAnimation.setDirection(QAbstractAnimation.Direction.Forward)
            self.last_resize_action_was_collapsing = False
        else:
            self.toggleButton.setArrowType(Qt.ArrowType.RightArrow)
            self.toggleAnimation.setDirection(QAbstractAnimation.Direction.Backward)
            self.last_resize_action_was_collapsing = True
        self.toggleAnimation.start()
        self.toggleAnimation.finished.connect(self.on_finish)

    def on_finish(self):
        if self.parent and self.last_resize_action_was_collapsing:
            # this solves the problem that the collapsed window is too big
            # BUT resizing so fast that it flickers
            # BUT also the width is reset but this should be remembered -> TODO store width
            # self.parent.adjustSize()
            pass
