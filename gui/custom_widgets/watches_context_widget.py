import logging
from typing import TYPE_CHECKING, Dict, Tuple

from PySide6.QtCore import Qt, Signal, Slot, QParallelAnimationGroup, QPropertyAnimation, QAbstractAnimation
from PySide6.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QWidget, \
    QPushButton, QFrame, QScrollArea, QToolButton, QGridLayout, QSizePolicy, QBoxLayout, QSpinBox

from gui.custom_widgets.context_text_edit import ContextTextEdit
from gui.parser import ContextParser

# Prevent circular import error
if TYPE_CHECKING:
    from gui.pwndbg_gui import PwnDbgGui

logger = logging.getLogger(__file__)


class Spoiler(QWidget):
    def __init__(self, content_layout: QBoxLayout, parent=None, title='', animationDuration=300):
        """
        References:
            # Adapted from c++ version
            http://stackoverflow.com/questions/32476006/how-to-make-an-expandable-collapsable-section-widget-in-qt
        """
        super(Spoiler, self).__init__(parent=parent)

        self.animationDuration = animationDuration
        self.toggleAnimation = QParallelAnimationGroup()
        self.contentArea = QScrollArea()
        self.headerLine = QFrame()
        self.toggleButton = QToolButton()
        self.mainLayout = QGridLayout()

        toggle_button = self.toggleButton
        toggle_button.setStyleSheet("QToolButton { border: none; }")
        toggle_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        toggle_button.setArrowType(Qt.RightArrow)
        toggle_button.setText(str(title))
        toggle_button.setCheckable(True)
        toggle_button.setChecked(False)

        header_line = self.headerLine
        header_line.setFrameShape(QFrame.HLine)
        header_line.setFrameShadow(QFrame.Sunken)
        header_line.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)

        self.contentArea.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        # start out collapsed
        self.contentArea.setMaximumHeight(0)
        self.contentArea.setMinimumHeight(0)

        # let the entire widget grow and shrink with its content
        toggle_animation = self.toggleAnimation
        toggle_animation.addAnimation(QPropertyAnimation(self, b"minimumHeight"))
        toggle_animation.addAnimation(QPropertyAnimation(self, b"maximumHeight"))
        toggle_animation.addAnimation(QPropertyAnimation(self.contentArea, b"maximumHeight"))
        # don't waste space
        main_layout = self.mainLayout
        main_layout.setVerticalSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        row = 0
        main_layout.addWidget(self.toggleButton, row, 0, 1, 1, Qt.AlignLeft)
        main_layout.addWidget(self.headerLine, row, 2, 1, 1)
        row += 1
        main_layout.addWidget(self.contentArea, row, 0, 1, 3)
        self.setLayout(self.mainLayout)
        self.setContentLayout(content_layout)

        def start_animation(checked):
            arrow_type = Qt.DownArrow if checked else Qt.RightArrow
            direction = QAbstractAnimation.Forward if checked else QAbstractAnimation.Backward
            toggle_button.setArrowType(arrow_type)
            self.toggleAnimation.setDirection(direction)
            self.toggleAnimation.start()

        self.toggleButton.clicked.connect(start_animation)
        self.toggleButton.click()

    def setContentLayout(self, content_layout):
        self.contentArea.destroy()
        self.contentArea.setLayout(content_layout)
        collapsed_height = self.sizeHint().height() - self.contentArea.maximumHeight()
        content_height = content_layout.sizeHint().height()
        for i in range(self.toggleAnimation.animationCount() - 1):
            spoiler_animation = self.toggleAnimation.animationAt(i)
            spoiler_animation.setDuration(self.animationDuration)
            spoiler_animation.setStartValue(collapsed_height)
            spoiler_animation.setEndValue(collapsed_height + content_height)
        content_animation = self.toggleAnimation.animationAt(self.toggleAnimation.animationCount() - 1)
        content_animation.setDuration(self.animationDuration)
        content_animation.setStartValue(0)
        content_animation.setEndValue(content_height)


class HDumpContextWidget(QGroupBox):
    # Execute "hexdump" in pwndbg and add watch in controller
    add_watch = Signal(str)
    # Delete watch in controller
    del_watch = Signal(str)

    def __init__(self, parent: 'PwnDbgGui'):
        super().__init__(parent)
        self.parser = ContextParser()
        # Currently watched addresses to ContextTextWidgets
        self.watches: Dict[str, Tuple[Spoiler, ContextTextEdit]] = {}
        # UI init
        self.watches_output: [ContextTextEdit] | None = None
        self.new_watch_input: QLineEdit | None = None
        # The watch context
        self.context_layout = QVBoxLayout()
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFlat(True)
        self.setTitle("Watches")
        self.add_watch.connect(parent.gdb_handler.add_watch)
        self.del_watch.connect(parent.gdb_handler.del_watch)
        # Set up the interior layout of this widget
        self.setup_widget_layout()
        # Insert this widget into the UI
        parent.ui.splitter.replaceWidget(2, self)

    def setup_widget_layout(self):
        # The layout for the input mask (label and line edit) of the New Watch functionality
        new_watch_input_layout = QHBoxLayout()
        new_watch_input_label = QLabel("New Watch:")
        new_watch_input_label.setToolTip("Add an address to be watched every context update via 'hexdump'")
        new_watch_input_layout.addWidget(new_watch_input_label)
        self.new_watch_input = QLineEdit()
        self.new_watch_input.setToolTip("New address to watch")
        self.new_watch_input.returnPressed.connect(self.new_watch_submit)
        new_watch_input_layout.addWidget(self.new_watch_input)
        # Package the new_watch layout in a widget so that we can add it to the overall widget
        new_watch_widget = QWidget(self)
        new_watch_widget.setLayout(new_watch_input_layout)
        self.context_layout.addWidget(new_watch_widget)
        # Active Watches test alignment
        #self.setup_new_watch_widget("0x4011c2")
        #self.setup_new_watch_widget("0x4011d2")
        '''
        self.watches_output = []
        for i in range(5):
            new_watch_spoiler_layout = QHBoxLayout()
            new_watch_label = QLabel("I am a Test")
            new_watch_spoiler_layout.addWidget(new_watch_label)
            new_watch_button = QPushButton("Test button")
            new_watch_spoiler_layout.addWidget(new_watch_button)
            self.watches_output.append(Spoiler(new_watch_spoiler_layout, parent=self, title="test"))
            self.context_layout.addWidget(self.watches_output[i])
        '''
        self.setLayout(self.context_layout)

    def setup_new_watch_widget(self, address: str):
        # Setup inter Spoiler layout
        inter_spoiler_layout = QVBoxLayout()
        # First setup HBoxLayout for delete and lines
        watch_interact_layout = QHBoxLayout()
        watch_interact_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # bytes Spinbox
        watch_lines_label = QLabel("Bytes:")
        watch_interact_layout.addWidget(watch_lines_label)
        watch_lines_incrementor = QSpinBox()
        watch_lines_incrementor.setRange(1, 999)
        watch_lines_incrementor.setValue(32)
        watch_interact_layout.addWidget(watch_lines_incrementor)

        # Delete button
        delete_watch_button = QPushButton("Delete Watch")
        delete_watch_button.clicked.connect(lambda: self.delete_watch_submit(address))
        watch_interact_layout.addWidget(delete_watch_button)

        spoiler_interact_widget = QWidget(self)
        spoiler_interact_widget.setLayout(watch_interact_layout)
        inter_spoiler_layout.addWidget(spoiler_interact_widget)
        # Second setup hexdump output
        hexdump_output = ContextTextEdit(self)
        inter_spoiler_layout.addWidget(hexdump_output)
        # Setup Spoiler
        spoiler = Spoiler(inter_spoiler_layout, parent=self, title=address)
        # Add watch to outer context
        self.watches[address] = (spoiler, hexdump_output)
        self.context_layout.addWidget(spoiler)

    @Slot()
    def new_watch_submit(self):
        """Callback for when the user presses Enter in the new_watch input mask"""
        param = self.new_watch_input.text()
        self.setup_new_watch_widget(param)
        self.add_watch.emit(param)
        self.new_watch_input.clear()

    @Slot(str)
    def delete_watch_submit(self, address: str):
        """Callback for when the user presses Delete in one of the watch spoilers"""
        self.context_layout.removeWidget(self.watches[address][0])
        self.watches[address][0].deleteLater()
        del self.watches[address]
        self.del_watch.emit(address)

    @Slot(bytes)
    def receive_hexdump_result(self, result: bytes):
        """Callback for receiving the result of the 'hexdump' command from the GDB reader"""
        #self.watches_output[0].add_content(self.parser.to_html(result))
        pass
