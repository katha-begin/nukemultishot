"""
Render Farm Submission Dialog for Multishot Workflow System.

Allows user to select Write nodes and specify render order.
"""

import os
from typing import List, Dict, Optional

try:
    from PySide2 import QtWidgets, QtCore, QtGui
except ImportError:
    from PySide6 import QtWidgets, QtCore, QtGui

from ..utils.logging import get_logger


class RenderFarmDialog(QtWidgets.QDialog):
    """Dialog for selecting Write nodes and configuring render farm submission."""
    
    def __init__(self, shot_data: Dict, parent=None):
        super().__init__(parent)
        self.logger = get_logger(__name__)
        self.shot_data = shot_data
        self.write_nodes = []
        self.selected_writes = []
        
        self.setWindowTitle("Submit to Render Farm")
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)
        
        self._init_ui()
        self._detect_write_nodes()
        self._detect_chain_order()
        
    def _init_ui(self):
        """Initialize the user interface."""
        layout = QtWidgets.QVBoxLayout(self)
        
        # Title
        title = QtWidgets.QLabel("<h2>Submit to Render Farm</h2>")
        layout.addWidget(title)
        
        # Shot info
        shot_key = f"{self.shot_data['project']}_{self.shot_data['ep']}_{self.shot_data['seq']}_{self.shot_data['shot']}"
        info_label = QtWidgets.QLabel(f"<b>Shot:</b> {shot_key}")
        layout.addWidget(info_label)
        
        layout.addSpacing(10)
        
        # "All Write Nodes" checkbox
        self.all_writes_checkbox = QtWidgets.QCheckBox("All Write Nodes")
        self.all_writes_checkbox.stateChanged.connect(self._on_all_writes_changed)
        layout.addWidget(self.all_writes_checkbox)
        
        layout.addSpacing(5)
        
        # Write nodes table
        table_label = QtWidgets.QLabel("<b>Render Order (drag to reorder):</b>")
        layout.addWidget(table_label)
        
        self.writes_table = QtWidgets.QTableWidget()
        self.writes_table.setColumnCount(4)
        self.writes_table.setHorizontalHeaderLabels(['#', 'Write Node', 'Output Path', 'Render'])
        self.writes_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.writes_table.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.writes_table.setDragEnabled(True)
        self.writes_table.setAcceptDrops(True)
        self.writes_table.setDropIndicatorShown(True)
        
        # Set column widths
        header = self.writes_table.horizontalHeader()
        header.setStretchLastSection(False)
        header.resizeSection(0, 40)   # #
        header.resizeSection(1, 150)  # Write Node
        header.resizeSection(2, 300)  # Output Path
        header.resizeSection(3, 80)   # Render checkbox
        
        layout.addWidget(self.writes_table)
        
        # Auto-detect button
        detect_btn = QtWidgets.QPushButton("Auto-Detect Chain Order")
        detect_btn.clicked.connect(self._detect_chain_order)
        layout.addWidget(detect_btn)
        
        layout.addSpacing(10)
        
        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QtWidgets.QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        submit_btn = QtWidgets.QPushButton("Submit to Deadline")
        submit_btn.setDefault(True)
        submit_btn.clicked.connect(self._on_submit)
        button_layout.addWidget(submit_btn)
        
        layout.addLayout(button_layout)
        
    def _detect_write_nodes(self):
        """Detect all Write nodes in the script."""
        try:
            import nuke
            
            self.write_nodes = []
            for node in nuke.allNodes('Write'):
                node_info = {
                    'node': node,
                    'name': node.name(),
                    'file': node['file'].value() if node.knob('file') else '',
                    'enabled': True
                }
                self.write_nodes.append(node_info)
            
            self.logger.info(f"Detected {len(self.write_nodes)} Write nodes")
            self._populate_table()
            
        except Exception as e:
            self.logger.error(f"Error detecting Write nodes: {e}")
            
    def _detect_chain_order(self):
        """Detect render order based on node chain dependencies."""
        try:
            import nuke
            
            # TODO: Implement dependency detection
            # For now, just use the order they appear in the script
            self.logger.info("Auto-detecting chain order...")
            
            # Refresh table with current order
            self._populate_table()
            
        except Exception as e:
            self.logger.error(f"Error detecting chain order: {e}")

    def _populate_table(self):
        """Populate the table with Write nodes."""
        try:
            self.writes_table.setRowCount(len(self.write_nodes))

            for row, write_info in enumerate(self.write_nodes):
                # Column 0: Row number
                num_item = QtWidgets.QTableWidgetItem(str(row + 1))
                num_item.setTextAlignment(QtCore.Qt.AlignCenter)
                num_item.setFlags(num_item.flags() & ~QtCore.Qt.ItemIsEditable)
                self.writes_table.setItem(row, 0, num_item)

                # Column 1: Write node name
                name_item = QtWidgets.QTableWidgetItem(write_info['name'])
                name_item.setFlags(name_item.flags() & ~QtCore.Qt.ItemIsEditable)
                self.writes_table.setItem(row, 1, name_item)

                # Column 2: Output path
                path_item = QtWidgets.QTableWidgetItem(write_info['file'])
                path_item.setFlags(path_item.flags() & ~QtCore.Qt.ItemIsEditable)
                path_item.setToolTip(write_info['file'])
                self.writes_table.setItem(row, 2, path_item)

                # Column 3: Render checkbox
                checkbox = QtWidgets.QCheckBox()
                checkbox.setChecked(write_info['enabled'])
                checkbox_widget = QtWidgets.QWidget()
                checkbox_layout = QtWidgets.QHBoxLayout(checkbox_widget)
                checkbox_layout.addWidget(checkbox)
                checkbox_layout.setAlignment(QtCore.Qt.AlignCenter)
                checkbox_layout.setContentsMargins(0, 0, 0, 0)
                self.writes_table.setCellWidget(row, 3, checkbox_widget)

        except Exception as e:
            self.logger.error(f"Error populating table: {e}")

    def _on_all_writes_changed(self, state):
        """Handle 'All Write Nodes' checkbox change."""
        try:
            checked = (state == QtCore.Qt.Checked)

            # Update all checkboxes
            for row in range(self.writes_table.rowCount()):
                checkbox_widget = self.writes_table.cellWidget(row, 3)
                if checkbox_widget:
                    checkbox = checkbox_widget.findChild(QtWidgets.QCheckBox)
                    if checkbox:
                        checkbox.setChecked(checked)

        except Exception as e:
            self.logger.error(f"Error updating checkboxes: {e}")

    def _on_submit(self):
        """Handle submit button click."""
        try:
            # Collect selected Write nodes
            self.selected_writes = []

            for row in range(self.writes_table.rowCount()):
                checkbox_widget = self.writes_table.cellWidget(row, 3)
                if checkbox_widget:
                    checkbox = checkbox_widget.findChild(QtWidgets.QCheckBox)
                    if checkbox and checkbox.isChecked():
                        if row < len(self.write_nodes):
                            self.selected_writes.append({
                                'node': self.write_nodes[row]['node'],
                                'name': self.write_nodes[row]['name'],
                                'order': row + 1
                            })

            if not self.selected_writes:
                QtWidgets.QMessageBox.warning(
                    self,
                    "No Write Nodes Selected",
                    "Please select at least one Write node to render."
                )
                return

            self.logger.info(f"Selected {len(self.selected_writes)} Write nodes for rendering")
            self.accept()

        except Exception as e:
            self.logger.error(f"Error collecting selected writes: {e}")
            QtWidgets.QMessageBox.critical(
                self,
                "Error",
                f"Failed to collect selected Write nodes:\n{e}"
            )

    def get_selected_writes(self) -> List[Dict]:
        """Get the list of selected Write nodes in render order."""
        return self.selected_writes

