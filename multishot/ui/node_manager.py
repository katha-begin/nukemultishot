"""
Node management UI for the Multishot Workflow System.

Provides interface to list, control, and batch-update all custom nodes.
"""

import os
from typing import Dict, List, Optional, Any

from .qt_utils import QtCore, QtWidgets, QtGui, BaseWidget
from ..core.variables import VariableManager

class NodeManagerDialog(QtWidgets.QDialog):
    """
    Dialog for managing custom Multishot nodes.

    Features:
    - List all custom nodes in the script
    - Batch update node paths
    - Version management
    - Node status monitoring
    - Bulk operations
    """

    def __init__(self, variable_manager=None, parent=None):
        super().__init__(parent)
        self.logger = self._get_logger()

        # Use provided variable_manager or create new one
        if variable_manager is not None:
            self.variable_manager = variable_manager
            self.logger.info("NodeManager using shared VariableManager instance")
        else:
            self.variable_manager = VariableManager()
            self.logger.info("NodeManager created new VariableManager instance")

        # Dialog state
        self.nodes_data = []

        self.setWindowTitle("Multishot Node Manager")
        self.setModal(False)
        self.resize(800, 600)

        self._setup_ui()
        self._connect_signals()
        self._refresh_nodes()

        self.logger.info("NodeManagerDialog initialized")

    def _get_logger(self):
        """Get logger instance."""
        from ..utils.logging import get_logger
        return get_logger(__name__)

    def _setup_ui(self):
        """Setup the user interface."""
        layout = QtWidgets.QVBoxLayout(self)

        # Header
        header_layout = QtWidgets.QHBoxLayout()

        title_label = QtWidgets.QLabel("Multishot Node Manager")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # Refresh button
        self.refresh_btn = QtWidgets.QPushButton("Refresh")
        self.refresh_btn.setToolTip("Refresh node list")
        header_layout.addWidget(self.refresh_btn)

        layout.addLayout(header_layout)

        # Node list
        self.nodes_table = QtWidgets.QTableWidget()
        self.nodes_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.nodes_table.setAlternatingRowColors(True)

        # Setup columns
        columns = ['Node Name', 'Type', 'Status', 'Path/Value', 'Version', 'Department']
        self.nodes_table.setColumnCount(len(columns))
        self.nodes_table.setHorizontalHeaderLabels(columns)

        # Set column widths
        header = self.nodes_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.resizeSection(0, 150)  # Node Name
        header.resizeSection(1, 100)  # Type
        header.resizeSection(2, 80)   # Status
        header.resizeSection(3, 300)  # Path/Value
        header.resizeSection(4, 80)   # Version

        layout.addWidget(self.nodes_table)

        # Batch operations
        batch_group = QtWidgets.QGroupBox("Batch Operations")
        batch_layout = QtWidgets.QVBoxLayout(batch_group)

        # Variable update section
        var_layout = QtWidgets.QHBoxLayout()
        var_layout.addWidget(QtWidgets.QLabel("Update Variable:"))

        self.variable_combo = QtWidgets.QComboBox()
        self.variable_combo.setEditable(True)
        var_layout.addWidget(self.variable_combo)

        var_layout.addWidget(QtWidgets.QLabel("Value:"))

        self.variable_value = QtWidgets.QLineEdit()
        var_layout.addWidget(self.variable_value)

        self.update_variable_btn = QtWidgets.QPushButton("Update Selected")
        self.update_variable_btn.setToolTip("Update variable for selected nodes")
        var_layout.addWidget(self.update_variable_btn)

        batch_layout.addLayout(var_layout)

        # Batch buttons
        batch_buttons_layout = QtWidgets.QHBoxLayout()

        self.refresh_paths_btn = QtWidgets.QPushButton("Refresh Paths")
        self.refresh_paths_btn.setToolTip("Refresh file paths for selected nodes")
        batch_buttons_layout.addWidget(self.refresh_paths_btn)

        self.update_versions_btn = QtWidgets.QPushButton("Update Versions")
        self.update_versions_btn.setToolTip("Update to latest versions for selected nodes")
        batch_buttons_layout.addWidget(self.update_versions_btn)

        self.validate_paths_btn = QtWidgets.QPushButton("Validate Paths")
        self.validate_paths_btn.setToolTip("Validate file paths for selected nodes")
        batch_buttons_layout.addWidget(self.validate_paths_btn)

        batch_buttons_layout.addStretch()

        batch_layout.addLayout(batch_buttons_layout)
        layout.addWidget(batch_group)

        # Status bar
        self.status_label = QtWidgets.QLabel("Ready")
        layout.addWidget(self.status_label)

        # Dialog buttons
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()

        self.close_btn = QtWidgets.QPushButton("Close")
        button_layout.addWidget(self.close_btn)

        layout.addLayout(button_layout)

    def _connect_signals(self):
        """Connect UI signals."""
        self.refresh_btn.clicked.connect(self._refresh_nodes)
        self.update_variable_btn.clicked.connect(self._update_variable)
        self.refresh_paths_btn.clicked.connect(self._refresh_paths)
        self.update_versions_btn.clicked.connect(self._update_versions)
        self.validate_paths_btn.clicked.connect(self._validate_paths)
        self.close_btn.clicked.connect(self.close)

        # Double-click to select node in Nuke
        self.nodes_table.itemDoubleClicked.connect(self._select_node_in_nuke)

    def _refresh_nodes(self):
        """Refresh the list of custom nodes."""
        try:
            self.status_label.setText("Refreshing nodes...")

            # Get all custom nodes from Nuke
            self.nodes_data = self._get_custom_nodes()

            # Update variable combo
            self._update_variable_combo()

            # Update table
            self._update_nodes_table()

            self.status_label.setText(f"Found {len(self.nodes_data)} custom nodes")

        except Exception as e:
            self.logger.error(f"Error refreshing nodes: {e}")
            self.status_label.setText(f"Error: {e}")

    def _get_custom_nodes(self) -> List[Dict[str, Any]]:
        """Get all custom Multishot nodes from the current script."""
        try:
            import nuke

            nodes_data = []

            # Get all nodes
            all_nodes = nuke.allNodes()
            self.logger.info(f"Found {len(all_nodes)} total nodes in script")

            # Find all nodes in the script
            for node in all_nodes:
                node_class = node.Class()
                node_name = node.name()

                # Debug: Check for multishot_sep knob
                has_sep = node.knob('multishot_sep') is not None
                self.logger.debug(f"Node {node_name} ({node_class}): has_multishot_sep={has_sep}")

                # Check if it's a custom Multishot node
                if self._is_multishot_node(node):
                    self.logger.info(f"Found Multishot node: {node_name} ({node_class})")
                    node_info = self._extract_node_info(node)
                    if node_info:
                        nodes_data.append(node_info)

            self.logger.info(f"Found {len(nodes_data)} Multishot nodes")
            return nodes_data

        except ImportError:
            self.logger.warning("Nuke not available - cannot get nodes")
            return []
        except Exception as e:
            self.logger.error(f"Error getting custom nodes: {e}")
            import traceback
            traceback.print_exc()
            return []

    def _is_multishot_node(self, node) -> bool:
        """Check if a node is a custom Multishot node."""
        try:
            # Check for multishot separator knob
            if node.knob('multishot_sep'):
                return True

            # Check node name patterns
            node_name = node.name()
            if any(prefix in node_name for prefix in ['MultishotRead', 'MultishotWrite', 'MultishotSwitch']):
                return True

            return False

        except Exception as e:
            self.logger.error(f"Error checking if node is Multishot node: {e}")
            return False

    def _extract_node_info(self, node) -> Optional[Dict[str, Any]]:
        """Extract information from a Multishot node."""
        try:
            node_class = node.Class()
            node_name = node.name()

            # Base info
            info = {
                'node': node,
                'name': node_name,
                'class': node_class,
                'type': self._get_node_type(node),
                'status': 'Unknown',
                'path': '',
                'version': '',
                'department': ''
            }

            # Extract specific info based on node type
            if node_class == 'Read' and 'MultishotRead' in node_name:
                info.update(self._extract_read_node_info(node))
            elif node_class == 'Write' and 'MultishotWrite' in node_name:
                info.update(self._extract_write_node_info(node))
            elif node_class == 'Switch' and 'MultishotSwitch' in node_name:
                info.update(self._extract_switch_node_info(node))

            return info

        except Exception as e:
            self.logger.error(f"Error extracting node info: {e}")
            return None

    def _get_node_type(self, node) -> str:
        """Get the Multishot node type."""
        node_name = node.name()
        if 'MultishotRead' in node_name:
            return 'Read'
        elif 'MultishotWrite' in node_name:
            return 'Write'
        elif 'MultishotSwitch' in node_name:
            return 'Switch'
        else:
            return 'Unknown'

    def _extract_read_node_info(self, node) -> Dict[str, Any]:
        """Extract info from MultishotRead node."""
        try:
            info = {}

            # Get file path
            file_knob = node.knob('file')
            if file_knob:
                info['path'] = file_knob.value()
                info['status'] = 'OK' if os.path.exists(info['path'].split('%')[0] if '%' in info['path'] else info['path']) else 'Missing'

            # Get version
            version_knob = node.knob('version')
            if version_knob:
                info['version'] = version_knob.value()

            # Get department
            dept_knob = node.knob('department')
            if dept_knob:
                info['department'] = dept_knob.value()

            return info

        except Exception as e:
            self.logger.error(f"Error extracting read node info: {e}")
            return {}

    def _extract_write_node_info(self, node) -> Dict[str, Any]:
        """Extract info from MultishotWrite node."""
        try:
            info = {}

            # Get file path
            file_knob = node.knob('file')
            if file_knob:
                info['path'] = file_knob.value()
                # Check if output directory exists
                output_dir = os.path.dirname(info['path']) if info['path'] else ''
                info['status'] = 'Ready' if os.path.exists(output_dir) else 'Dir Missing'

            # Get version
            version_knob = node.knob('version')
            if version_knob:
                info['version'] = version_knob.value()

            # Get department
            dept_knob = node.knob('department')
            if dept_knob:
                info['department'] = dept_knob.value()

            return info

        except Exception as e:
            self.logger.error(f"Error extracting write node info: {e}")
            return {}

    def _extract_switch_node_info(self, node) -> Dict[str, Any]:
        """Extract info from MultishotSwitch node."""
        try:
            info = {}

            # Get current switch value
            which_knob = node.knob('which')
            if which_knob:
                info['path'] = f"Input {which_knob.value()}"

            # Get switch mode
            mode_knob = node.knob('switch_mode')
            if mode_knob:
                info['version'] = mode_knob.value()

            # Get variable name
            var_knob = node.knob('variable_name')
            if var_knob:
                info['department'] = var_knob.value()

            info['status'] = 'Active'

            return info

        except Exception as e:
            self.logger.error(f"Error extracting switch node info: {e}")
            return {}

    def _update_variable_combo(self):
        """Update the variable combo box with available variables."""
        try:
            variables = self.variable_manager.get_all_variables()

            self.variable_combo.clear()

            # Add common variables
            common_vars = ['project', 'ep', 'seq', 'shot', 'department', 'version', 'layer']
            for var in common_vars:
                self.variable_combo.addItem(var)

            # Add other variables from current context
            for var_name in variables.keys():
                if var_name not in common_vars:
                    self.variable_combo.addItem(var_name)

        except Exception as e:
            self.logger.error(f"Error updating variable combo: {e}")

    def _update_nodes_table(self):
        """Update the nodes table with current data."""
        try:
            self.nodes_table.setRowCount(len(self.nodes_data))

            for row, node_info in enumerate(self.nodes_data):
                # Node Name
                name_item = QtWidgets.QTableWidgetItem(node_info.get('name', ''))
                self.nodes_table.setItem(row, 0, name_item)

                # Type
                type_item = QtWidgets.QTableWidgetItem(node_info.get('type', ''))
                self.nodes_table.setItem(row, 1, type_item)

                # Status
                status_item = QtWidgets.QTableWidgetItem(node_info.get('status', ''))
                # Color code status
                if node_info.get('status') == 'OK' or node_info.get('status') == 'Ready':
                    status_item.setBackground(QtGui.QColor(144, 238, 144))  # Light green
                elif node_info.get('status') == 'Missing' or 'Missing' in node_info.get('status', ''):
                    status_item.setBackground(QtGui.QColor(255, 182, 193))  # Light red
                elif node_info.get('status') == 'Active':
                    status_item.setBackground(QtGui.QColor(173, 216, 230))  # Light blue

                self.nodes_table.setItem(row, 2, status_item)

                # Path/Value
                path_item = QtWidgets.QTableWidgetItem(node_info.get('path', ''))
                path_item.setToolTip(node_info.get('path', ''))
                self.nodes_table.setItem(row, 3, path_item)

                # Version
                version_item = QtWidgets.QTableWidgetItem(node_info.get('version', ''))
                self.nodes_table.setItem(row, 4, version_item)

                # Department
                dept_item = QtWidgets.QTableWidgetItem(node_info.get('department', ''))
                self.nodes_table.setItem(row, 5, dept_item)

        except Exception as e:
            self.logger.error(f"Error updating nodes table: {e}")

    def _select_node_in_nuke(self, item):
        """Select the corresponding node in Nuke."""
        try:
            import nuke

            row = item.row()
            if row < len(self.nodes_data):
                node_info = self.nodes_data[row]
                node = node_info.get('node')

                if node:
                    # Clear current selection
                    for n in nuke.selectedNodes():
                        n.setSelected(False)

                    # Select the node
                    node.setSelected(True)

                    # Show the node in the node graph
                    nuke.show(node)

                    self.status_label.setText(f"Selected node: {node.name()}")

        except ImportError:
            self.status_label.setText("Nuke not available")
        except Exception as e:
            self.logger.error(f"Error selecting node in Nuke: {e}")
            self.status_label.setText(f"Error selecting node: {e}")

    def _get_selected_nodes(self) -> List[Dict[str, Any]]:
        """Get selected nodes from the table."""
        selected_rows = set()
        for item in self.nodes_table.selectedItems():
            selected_rows.add(item.row())

        return [self.nodes_data[row] for row in selected_rows if row < len(self.nodes_data)]

    def _update_variable(self):
        """Update variable for selected nodes."""
        try:
            selected_nodes = self._get_selected_nodes()
            if not selected_nodes:
                self.status_label.setText("No nodes selected")
                return

            variable_name = self.variable_combo.currentText()
            variable_value = self.variable_value.text()

            if not variable_name or not variable_value:
                self.status_label.setText("Please specify variable name and value")
                return

            updated_count = 0

            for node_info in selected_nodes:
                node = node_info.get('node')
                if not node:
                    continue

                # Try to update the variable in the node
                if self._update_node_variable(node, variable_name, variable_value):
                    updated_count += 1

            self.status_label.setText(f"Updated {variable_name}={variable_value} for {updated_count} nodes")

            # Refresh the display
            self._refresh_nodes()

        except Exception as e:
            self.logger.error(f"Error updating variable: {e}")
            self.status_label.setText(f"Error updating variable: {e}")

    def _update_node_variable(self, node, variable_name: str, variable_value: str) -> bool:
        """Update a variable in a specific node."""
        try:
            # Try to find the knob for this variable
            knob = node.knob(variable_name)
            if knob:
                knob.setValue(variable_value)
                return True

            # For some variables, we might need to trigger a refresh
            if variable_name in ['department', 'version', 'layer']:
                # Trigger node refresh if it has an update method
                update_knob = node.knob('update') or node.knob('refresh') or node.knob('update_path')
                if update_knob:
                    update_knob.execute()

            return False

        except Exception as e:
            self.logger.error(f"Error updating node variable: {e}")
            return False

    def _refresh_paths(self):
        """Refresh file paths for selected nodes."""
        try:
            selected_nodes = self._get_selected_nodes()
            if not selected_nodes:
                self.status_label.setText("No nodes selected")
                return

            refreshed_count = 0

            for node_info in selected_nodes:
                node = node_info.get('node')
                if not node:
                    continue

                # Try to refresh the node
                if self._refresh_node_path(node):
                    refreshed_count += 1

            self.status_label.setText(f"Refreshed paths for {refreshed_count} nodes")

            # Refresh the display
            self._refresh_nodes()

        except Exception as e:
            self.logger.error(f"Error refreshing paths: {e}")
            self.status_label.setText(f"Error refreshing paths: {e}")

    def _refresh_node_path(self, node) -> bool:
        """Refresh the path for a specific node."""
        try:
            # Look for refresh/update buttons
            refresh_knobs = ['refresh', 'update', 'update_path']

            for knob_name in refresh_knobs:
                knob = node.knob(knob_name)
                if knob:
                    knob.execute()
                    return True

            return False

        except Exception as e:
            self.logger.error(f"Error refreshing node path: {e}")
            return False

    def _update_versions(self):
        """Update to latest versions for selected nodes."""
        try:
            selected_nodes = self._get_selected_nodes()
            if not selected_nodes:
                self.status_label.setText("No nodes selected")
                return

            updated_count = 0

            for node_info in selected_nodes:
                node = node_info.get('node')
                if not node:
                    continue

                # Try to update to latest version
                if self._update_node_to_latest_version(node):
                    updated_count += 1

            self.status_label.setText(f"Updated {updated_count} nodes to latest versions")

            # Refresh the display
            self._refresh_nodes()

        except Exception as e:
            self.logger.error(f"Error updating versions: {e}")
            self.status_label.setText(f"Error updating versions: {e}")

    def _update_node_to_latest_version(self, node) -> bool:
        """Update a node to the latest version."""
        try:
            # This is a simplified implementation
            # In a real scenario, you'd scan for available versions and select the latest

            version_knob = node.knob('version')
            if not version_knob:
                return False

            current_version = version_knob.value()

            # Simple increment for demo (v001 -> v002)
            if current_version.startswith('v') and current_version[1:].isdigit():
                version_num = int(current_version[1:])
                new_version = f"v{version_num + 1:03d}"
                version_knob.setValue(new_version)

                # Trigger refresh
                self._refresh_node_path(node)
                return True

            return False

        except Exception as e:
            self.logger.error(f"Error updating node to latest version: {e}")
            return False

    def _validate_paths(self):
        """Validate file paths for selected nodes."""
        try:
            selected_nodes = self._get_selected_nodes()
            if not selected_nodes:
                self.status_label.setText("No nodes selected")
                return

            valid_count = 0
            invalid_count = 0

            for node_info in selected_nodes:
                node = node_info.get('node')
                if not node:
                    continue

                # Validate the node's path
                if self._validate_node_path(node):
                    valid_count += 1
                else:
                    invalid_count += 1

            self.status_label.setText(f"Validation: {valid_count} valid, {invalid_count} invalid paths")

            # Refresh the display to show updated status
            self._refresh_nodes()

        except Exception as e:
            self.logger.error(f"Error validating paths: {e}")
            self.status_label.setText(f"Error validating paths: {e}")

    def _validate_node_path(self, node) -> bool:
        """Validate the path for a specific node."""
        try:
            file_knob = node.knob('file')
            if not file_knob:
                return False

            file_path = file_knob.value()
            if not file_path:
                return False

            # For sequences, check if directory exists and has files
            if '%' in file_path:
                base_dir = os.path.dirname(file_path)
                return os.path.exists(base_dir) and bool(os.listdir(base_dir))
            else:
                return os.path.exists(file_path)

        except Exception as e:
            self.logger.error(f"Error validating node path: {e}")
            return False


# Keep the original NodeManager class for compatibility
class NodeManager(BaseWidget):
    """Node management interface for multishot workflows."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger.info("NodeManager initialized (stub)")


def show_node_manager():
    """Show the Node Manager dialog."""
    try:
        dialog = NodeManagerDialog()
        dialog.show()
        return dialog

    except Exception as e:
        import nuke
        nuke.message(f"Error showing Node Manager: {e}")
        return None
