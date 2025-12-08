"""
Add AOV Dialog - Select AOV layers to add from available layers.
"""

try:
    from PySide2.QtWidgets import (
        QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
        QPushButton, QLabel, QAbstractItemView
    )
    from PySide2.QtCore import Qt
except ImportError:
    from PySide6.QtWidgets import (
        QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
        QPushButton, QLabel, QAbstractItemView
    )
    from PySide6.QtCore import Qt

from ..utils.logging import get_logger

logger = get_logger(__name__)


class AddAOVDialog(QDialog):
    """Dialog for selecting AOV layers to add."""

    def __init__(self, available_layers, current_layers, parent=None):
        super().__init__(parent)
        self.available_layers = available_layers
        self.current_layers = current_layers
        self.setWindowTitle("Add AOV Layer")
        self.setMinimumSize(400, 350)
        self.setup_ui()

    def setup_ui(self):
        """Setup the dialog UI."""
        layout = QVBoxLayout(self)

        # Header
        header = QLabel("<b>Select AOV layers to add:</b>")
        layout.addWidget(header)

        # Info label
        info = QLabel("Layers detected from input stream (already added layers are disabled)")
        info.setStyleSheet("color: gray; font-size: 11px;")
        layout.addWidget(info)

        # List widget with checkboxes
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QAbstractItemView.MultiSelection)

        # Populate list
        for layer in self.available_layers:
            item = QListWidgetItem(layer)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)

            # Disable if already added
            if layer in self.current_layers:
                item.setCheckState(Qt.Unchecked)
                item.setFlags(item.flags() & ~Qt.ItemIsEnabled)
                item.setForeground(Qt.gray)
            else:
                item.setCheckState(Qt.Unchecked)

            self.list_widget.addItem(item)

        layout.addWidget(self.list_widget)

        # Select all / Deselect all buttons
        select_row = QHBoxLayout()
        select_all_btn = QPushButton("Select All")
        select_all_btn.clicked.connect(self.select_all)
        select_row.addWidget(select_all_btn)

        deselect_all_btn = QPushButton("Deselect All")
        deselect_all_btn.clicked.connect(self.deselect_all)
        select_row.addWidget(deselect_all_btn)

        select_row.addStretch()
        layout.addLayout(select_row)

        # Bottom buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        add_btn = QPushButton("Add Selected")
        add_btn.clicked.connect(self.accept)
        btn_layout.addWidget(add_btn)

        layout.addLayout(btn_layout)

    def select_all(self):
        """Select all enabled items."""
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.flags() & Qt.ItemIsEnabled:
                item.setCheckState(Qt.Checked)

    def deselect_all(self):
        """Deselect all items."""
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            item.setCheckState(Qt.Unchecked)

    def get_selected_layers(self):
        """Get list of selected layer names."""
        selected = []
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.checkState() == Qt.Checked:
                selected.append(item.text())
        return selected

