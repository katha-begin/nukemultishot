"""
CompPass Dialogs - Qt dialogs for AOV Manager and Mirror functionality.

Provides:
- AOVManagerDialog: Table-based AOV selection with +/- buttons
- MirrorDialog: Mirror settings to other CompPass nodes
"""

try:
    from PySide2.QtWidgets import (
        QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
        QPushButton, QLabel, QHeaderView, QCheckBox, QMessageBox,
        QAbstractItemView, QGroupBox, QComboBox
    )
    from PySide2.QtCore import Qt
except ImportError:
    from PySide6.QtWidgets import (
        QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
        QPushButton, QLabel, QHeaderView, QCheckBox, QMessageBox,
        QAbstractItemView, QGroupBox, QComboBox
    )
    from PySide6.QtCore import Qt

from ..utils.logging import get_logger

logger = get_logger(__name__)


class AOVManagerDialog(QDialog):
    """Dialog for managing AOV layers with table and +/- buttons."""

    def __init__(self, group_node, parent=None):
        super().__init__(parent)
        self.group_node = group_node
        self.setWindowTitle("AOV Manager")
        self.setMinimumSize(500, 400)
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        """Setup the dialog UI."""
        layout = QVBoxLayout(self)

        # Header
        header = QLabel("<b>Manage AOV Layers</b>")
        layout.addWidget(header)

        # Status label
        self.status_label = QLabel("Loading...")
        layout.addWidget(self.status_label)

        # Table for AOV layers
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["AOV Layer", ""])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.table.setColumnWidth(1, 40)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)

        # Add button row
        add_row = QHBoxLayout()
        self.add_btn = QPushButton("+ Add AOV")
        self.add_btn.clicked.connect(self.add_aov)
        add_row.addWidget(self.add_btn)
        add_row.addStretch()
        layout.addLayout(add_row)

        # Bottom buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        apply_btn = QPushButton("Apply")
        apply_btn.clicked.connect(self.apply_changes)
        btn_layout.addWidget(apply_btn)

        layout.addLayout(btn_layout)

    def load_data(self):
        """Load current layers and available layers from input."""
        import nuke

        # Get currently selected layers
        current_layers = []
        if self.group_node.knob('selected_layers'):
            layer_text = self.group_node['selected_layers'].value()
            current_layers = [l.strip() for l in layer_text.split('\n') if l.strip()]

        # Get available layers from input
        self.available_layers = []
        input_node = self.group_node.input(0)
        if input_node:
            prefix_str = self.group_node['layer_prefixes'].value()
            prefixes = [p.strip() for p in prefix_str.split(',') if p.strip()]
            from . import comppass_node
            self.available_layers = comppass_node.get_available_layers(input_node, prefixes)

        # Populate table with current layers
        self.table.setRowCount(len(current_layers))
        for i, layer in enumerate(current_layers):
            self._add_layer_row(i, layer)

        # Update status
        avail_count = len(self.available_layers)
        curr_count = len(current_layers)
        self.status_label.setText(f"Selected: {curr_count} | Available from input: {avail_count}")

    def _add_layer_row(self, row, layer_name):
        """Add a row to the table for a layer."""
        # Layer name
        item = QTableWidgetItem(layer_name)
        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
        self.table.setItem(row, 0, item)

        # Remove button
        remove_btn = QPushButton("-")
        remove_btn.setFixedSize(30, 25)
        remove_btn.clicked.connect(lambda: self.remove_layer(layer_name))
        self.table.setCellWidget(row, 1, remove_btn)

    def add_aov(self):
        """Show dialog to add an AOV from available layers."""
        from .comppass_add_aov_dialog import AddAOVDialog
        dialog = AddAOVDialog(self.available_layers, self._get_current_layers(), self)
        if dialog.exec_() == QDialog.Accepted:
            selected = dialog.get_selected_layers()
            for layer in selected:
                if layer not in self._get_current_layers():
                    row = self.table.rowCount()
                    self.table.insertRow(row)
                    self._add_layer_row(row, layer)
            self._update_status()

    def _get_current_layers(self):
        """Get list of layers currently in the table."""
        layers = []
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item:
                layers.append(item.text())
        return layers

    def remove_layer(self, layer_name):
        """Remove a layer from the table."""
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item and item.text() == layer_name:
                self.table.removeRow(row)
                break
        self._update_status()

    def _update_status(self):
        """Update status label."""
        curr_count = self.table.rowCount()
        avail_count = len(self.available_layers)
        self.status_label.setText(f"Selected: {curr_count} | Available from input: {avail_count}")

    def apply_changes(self):
        """Apply changes to the CompPass node."""
        layers = self._get_current_layers()
        self.group_node['selected_layers'].setValue('\n'.join(layers))
        self.group_node['status'].setValue(f'<font color="green">{len(layers)} layers selected</font>')
        self.accept()


class MirrorDialog(QDialog):
    """Dialog for mirroring CompPass settings to other nodes."""

    def __init__(self, source_node, parent=None):
        super().__init__(parent)
        self.source_node = source_node
        self.setWindowTitle("Mirror CompPass Settings")
        self.setMinimumSize(600, 500)
        self.comppass_nodes = []
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        """Setup the dialog UI."""
        layout = QVBoxLayout(self)

        # Source info
        source_group = QGroupBox("Source Node")
        source_layout = QVBoxLayout(source_group)
        self.source_label = QLabel("Loading...")
        source_layout.addWidget(self.source_label)
        layout.addWidget(source_group)

        # Target nodes table
        target_group = QGroupBox("Target CompPass Nodes")
        target_layout = QVBoxLayout(target_group)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Select", "Node Name", "Namespace", "Layers"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.setColumnWidth(0, 50)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        target_layout.addWidget(self.table)

        # Selection buttons
        sel_row = QHBoxLayout()
        self.select_ns_btn = QPushButton("Select Same Namespace")
        self.select_ns_btn.clicked.connect(self.select_same_namespace)
        sel_row.addWidget(self.select_ns_btn)

        deselect_btn = QPushButton("Deselect All")
        deselect_btn.clicked.connect(self.deselect_all)
        sel_row.addWidget(deselect_btn)
        sel_row.addStretch()
        target_layout.addLayout(sel_row)

        layout.addWidget(target_group)

        # Mirror options
        options_group = QGroupBox("Values to Mirror")
        options_layout = QHBoxLayout(options_group)
        self.mirror_exposure = QCheckBox("Exposure")
        self.mirror_exposure.setChecked(True)
        options_layout.addWidget(self.mirror_exposure)

        self.mirror_gain = QCheckBox("Gain/Color")
        self.mirror_gain.setChecked(True)
        options_layout.addWidget(self.mirror_gain)

        self.mirror_enable = QCheckBox("Enable")
        self.mirror_enable.setChecked(True)
        options_layout.addWidget(self.mirror_enable)
        options_layout.addStretch()
        layout.addWidget(options_group)

        # Bottom buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        apply_btn = QPushButton("Apply Mirror")
        apply_btn.clicked.connect(self.apply_mirror)
        btn_layout.addWidget(apply_btn)

        layout.addLayout(btn_layout)

    def load_data(self):
        """Load source info and find all CompPass nodes."""
        import nuke

        # Source info
        source_name = self.source_node.name()
        source_ns = self.source_node['namespace'].value() if self.source_node.knob('namespace') else 'master'
        source_layers = self._get_layer_count(self.source_node)
        self.source_label.setText(
            f"<b>{source_name}</b> | Namespace: <b>{source_ns}</b> | Layers: {source_layers}"
        )

        # Find all CompPass nodes
        # CompPass nodes are identified by having 'comppass_tab' knob or 'selected_layers' knob
        self.comppass_nodes = []
        for node in nuke.allNodes('Group'):
            if node.name() == source_name:
                continue  # Skip source node
            # Check if it's a CompPass node (has comppass_tab or selected_layers knob)
            if node.knob('comppass_tab') or node.knob('selected_layers'):
                self.comppass_nodes.append(node)

        # Populate table
        self.table.setRowCount(len(self.comppass_nodes))
        for i, node in enumerate(self.comppass_nodes):
            self._add_node_row(i, node, source_ns)

        # Show message if no other CompPass nodes found
        if not self.comppass_nodes:
            self.table.setRowCount(1)
            no_nodes_item = QTableWidgetItem("No other CompPass nodes found in script")
            no_nodes_item.setFlags(no_nodes_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(0, 1, no_nodes_item)
            self.table.setSpan(0, 1, 1, 3)

    def _get_layer_count(self, node):
        """Get number of layers in a CompPass node."""
        if node.knob('selected_layers'):
            layers = node['selected_layers'].value().strip()
            if layers:
                return len(layers.split('\n'))
        return 0

    def _add_node_row(self, row, node, source_namespace):
        """Add a row for a CompPass node."""
        # Checkbox
        checkbox = QCheckBox()
        ns = node['namespace'].value() if node.knob('namespace') else ''
        # Auto-select if same namespace
        checkbox.setChecked(ns == source_namespace)
        self.table.setCellWidget(row, 0, checkbox)

        # Node name
        name_item = QTableWidgetItem(node.name())
        name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
        self.table.setItem(row, 1, name_item)

        # Namespace
        ns_item = QTableWidgetItem(ns)
        ns_item.setFlags(ns_item.flags() & ~Qt.ItemIsEditable)
        self.table.setItem(row, 2, ns_item)

        # Layer count
        layer_count = self._get_layer_count(node)
        layers_item = QTableWidgetItem(f"{layer_count} AOVs")
        layers_item.setFlags(layers_item.flags() & ~Qt.ItemIsEditable)
        self.table.setItem(row, 3, layers_item)

    def select_same_namespace(self):
        """Select all nodes with same namespace as source."""
        source_ns = self.source_node['namespace'].value() if self.source_node.knob('namespace') else 'master'
        for i, node in enumerate(self.comppass_nodes):
            checkbox = self.table.cellWidget(i, 0)
            ns = node['namespace'].value() if node.knob('namespace') else ''
            checkbox.setChecked(ns == source_ns)

    def deselect_all(self):
        """Deselect all nodes."""
        for i in range(self.table.rowCount()):
            checkbox = self.table.cellWidget(i, 0)
            checkbox.setChecked(False)

    def get_selected_nodes(self):
        """Get list of selected target nodes."""
        selected = []
        for i, node in enumerate(self.comppass_nodes):
            checkbox = self.table.cellWidget(i, 0)
            if checkbox.isChecked():
                selected.append(node)
        return selected

    def apply_mirror(self):
        """Apply mirror to selected nodes."""
        selected_nodes = self.get_selected_nodes()
        if not selected_nodes:
            QMessageBox.warning(self, "No Selection", "Please select at least one target node.")
            return

        # Confirm
        msg = f"Mirror settings to {len(selected_nodes)} node(s)?\n\n"
        msg += "Values to mirror:\n"
        if self.mirror_exposure.isChecked():
            msg += "  - Exposure\n"
        if self.mirror_gain.isChecked():
            msg += "  - Gain/Color\n"
        if self.mirror_enable.isChecked():
            msg += "  - Enable\n"

        reply = QMessageBox.question(
            self, "Confirm Mirror",
            msg,
            QMessageBox.Yes | QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        # Perform mirror
        from . import comppass_node
        success_count = comppass_node.mirror_settings(
            self.source_node,
            selected_nodes,
            mirror_exposure=self.mirror_exposure.isChecked(),
            mirror_gain=self.mirror_gain.isChecked(),
            mirror_enable=self.mirror_enable.isChecked()
        )

        QMessageBox.information(
            self, "Mirror Complete",
            f"Successfully mirrored to {success_count} node(s)."
        )
        self.accept()
