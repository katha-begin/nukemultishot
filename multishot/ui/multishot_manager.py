"""
Multishot Manager UI for the Multishot Workflow System.

Provides shot-based context management and version control.
"""

import os
import json
from typing import Dict, List, Optional, Any

from .qt_utils import QtCore, QtWidgets, QtGui, BaseWidget
from ..core.variables import VariableManager
from ..core.scanner import DirectoryScanner


class MultishotManagerDialog(BaseWidget):
    """
    Widget for managing shots and versions in a multi-shot workflow.

    Features:
    - Shot list table with context switching
    - Per-shot version management
    - Add/remove shots
    - Update all shots to latest versions
    """

    def __init__(self, variable_manager=None, parent=None):
        super().__init__(parent)

        # CRITICAL: Always use shared variable manager to avoid resetting context
        if variable_manager is not None:
            self.variable_manager = variable_manager
            self.logger.info("MultishotManager using provided VariableManager instance")
        else:
            # Import shared instance to avoid creating new one
            from . import get_shared_variable_manager
            self.variable_manager = get_shared_variable_manager()
            self.logger.info("MultishotManager using shared VariableManager instance")

        self.scanner = DirectoryScanner()

        # Widget state
        self.shots_data = []  # List of shot dictionaries
        self.current_shot_key = None  # Currently active shot key

        self._setup_ui()
        self._connect_signals()
        self._load_shots()  # This restores current_shot_key from root knobs
        self._refresh_table(update_current_shot=False)  # Don't overwrite the restored current_shot_key!

        # Set window properties
        self.setWindowTitle("Multishot Manager")

        # Set default size (bigger than before)
        self._restore_geometry()

        self.logger.info("MultishotManagerDialog initialized")

    def _setup_ui(self):
        """Setup the user interface."""
        layout = QtWidgets.QVBoxLayout(self)

        # Header
        header_layout = QtWidgets.QHBoxLayout()

        title_label = QtWidgets.QLabel("Multishot Manager")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # Refresh button
        self.refresh_btn = QtWidgets.QPushButton("Refresh")
        self.refresh_btn.setToolTip("Refresh shot list")
        header_layout.addWidget(self.refresh_btn)

        layout.addLayout(header_layout)

        # Current shot display
        current_shot_layout = QtWidgets.QHBoxLayout()
        current_shot_layout.addWidget(QtWidgets.QLabel("Current Shot:"))
        
        self.current_shot_label = QtWidgets.QLabel("None")
        self.current_shot_label.setStyleSheet("font-weight: bold; color: green;")
        current_shot_layout.addWidget(self.current_shot_label)
        
        current_shot_layout.addStretch()
        layout.addLayout(current_shot_layout)

        # Shot table
        self.shots_table = QtWidgets.QTableWidget()
        self.shots_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.shots_table.setAlternatingRowColors(True)

        # Setup columns: # | Shot | Set Shot | Version | Remove | Bake | Unbake | Save | Render
        columns = ['#', 'Shot', 'Set Shot', 'Version', 'Remove', 'Bake', 'Unbake', 'Save', 'Render']
        self.shots_table.setColumnCount(len(columns))
        self.shots_table.setHorizontalHeaderLabels(columns)

        # Set column widths
        header = self.shots_table.horizontalHeader()
        header.setStretchLastSection(False)
        header.resizeSection(0, 50)   # #
        header.resizeSection(1, 300)  # Shot
        header.resizeSection(2, 120)  # Set Shot
        header.resizeSection(3, 150)  # Version
        header.resizeSection(4, 80)   # Remove
        header.resizeSection(5, 80)   # Bake
        header.resizeSection(6, 80)   # Unbake
        header.resizeSection(7, 80)   # Save
        header.resizeSection(8, 80)   # Render

        layout.addWidget(self.shots_table)

        # Bottom buttons
        bottom_layout = QtWidgets.QHBoxLayout()

        self.add_shots_btn = QtWidgets.QPushButton("Add Shots")
        self.add_shots_btn.setToolTip("Add shots from directory structure")
        bottom_layout.addWidget(self.add_shots_btn)

        self.update_all_btn = QtWidgets.QPushButton("Update All to Latest Versions")
        self.update_all_btn.setToolTip("Update all shots to their latest versions")
        bottom_layout.addWidget(self.update_all_btn)

        self.contact_sheet_btn = QtWidgets.QPushButton("Render Contact Sheet")
        self.contact_sheet_btn.setToolTip("Render contact sheet (not implemented yet)")
        self.contact_sheet_btn.setEnabled(False)
        bottom_layout.addWidget(self.contact_sheet_btn)

        layout.addLayout(bottom_layout)

    def _connect_signals(self):
        """Connect UI signals."""
        self.refresh_btn.clicked.connect(self._refresh_table)
        self.add_shots_btn.clicked.connect(self._add_shots)
        self.update_all_btn.clicked.connect(self._update_all_to_latest)

    def _load_shots(self):
        """Load shots from script knobs or config."""
        self.logger.info(f"[LOAD_SHOTS] START: current_shot_key = {self.current_shot_key}")

        try:
            import nuke

            # Try to load from script knob
            if nuke.root().knob('multishot_shots'):
                shots_json = nuke.root()['multishot_shots'].value()
                if shots_json:
                    self.shots_data = json.loads(shots_json)
                    self.logger.info(f"Loaded {len(self.shots_data)} shots from script")
                else:
                    # No shots in script, start with empty list
                    self.shots_data = []
                    self.logger.info("No shots found in script, starting with empty list")
            else:
                # No shots in script, start with empty list
                self.shots_data = []
                self.logger.info("No shots found in script, starting with empty list")

            # Restore current shot from root knobs
            self._restore_current_shot_from_root()

        except ImportError:
            self.logger.warning("Nuke not available, cannot load shots")
            self.shots_data = []
        except Exception as e:
            self.logger.error(f"Error loading shots: {e}")
            self.shots_data = []

        self.logger.info(f"[LOAD_SHOTS] END: current_shot_key = {self.current_shot_key}")

    def _restore_current_shot_from_root(self):
        """Restore current shot key from root knobs."""
        self.logger.info(f"[RESTORE_CURRENT_SHOT] START: current_shot_key = {self.current_shot_key}")

        try:
            import nuke

            # Get current context from root knobs
            project = str(nuke.root()['multishot_project'].value()).strip() if nuke.root().knob('multishot_project') else ''
            ep = str(nuke.root()['multishot_ep'].value()).strip() if nuke.root().knob('multishot_ep') else ''
            seq = str(nuke.root()['multishot_seq'].value()).strip() if nuke.root().knob('multishot_seq') else ''
            shot = str(nuke.root()['multishot_shot'].value()).strip() if nuke.root().knob('multishot_shot') else ''

            self.logger.info(f"[RESTORE_CURRENT_SHOT] Read from root: project='{project}', ep='{ep}', seq='{seq}', shot='{shot}'")

            if project and ep and seq and shot:
                self.current_shot_key = f"{project}_{ep}_{seq}_{shot}"
                self.current_shot_label.setText(self.current_shot_key)
                self.logger.info(f"[RESTORE_CURRENT_SHOT] Restored: {self.current_shot_key}")
            else:
                self.current_shot_key = None
                self.current_shot_label.setText("None")
                self.logger.info(f"[RESTORE_CURRENT_SHOT] No current shot (missing values)")

        except Exception as e:
            self.logger.error(f"[RESTORE_CURRENT_SHOT] Exception: {e}")
            self.current_shot_key = None
            self.current_shot_label.setText("None")

        self.logger.info(f"[RESTORE_CURRENT_SHOT] END: current_shot_key = {self.current_shot_key}")

    def _save_shots(self):
        """Save shots to script knobs."""
        try:
            import nuke
            
            # Create knob if it doesn't exist
            if not nuke.root().knob('multishot_shots'):
                knob = nuke.String_Knob('multishot_shots', '')
                knob.setVisible(False)
                nuke.root().addKnob(knob)
            
            # Save shots as JSON
            shots_json = json.dumps(self.shots_data)
            nuke.root()['multishot_shots'].setValue(shots_json)
            
            self.logger.info(f"Saved {len(self.shots_data)} shots to script")
            
        except ImportError:
            self.logger.warning("Nuke not available, cannot save shots")
        except Exception as e:
            self.logger.error(f"Error saving shots: {e}")

    def _refresh_table(self, update_current_shot=True):
        """Refresh the shots table.

        Args:
            update_current_shot: If True, read current shot from root knobs.
                                If False, keep existing current_shot_key.
        """
        self.logger.info(f"[REFRESH_TABLE] START: current_shot_key = {self.current_shot_key}, update_current_shot = {update_current_shot}")

        try:
            print(f"      _refresh_table: current_shot_key BEFORE = {self.current_shot_key}")
            print(f"      _refresh_table: update_current_shot = {update_current_shot}")

            # Only update current shot from root knobs if requested
            if update_current_shot:
                self._update_current_shot_display()
                print(f"      _refresh_table: current_shot_key AFTER update = {self.current_shot_key}")
            else:
                print(f"      _refresh_table: Keeping current_shot_key = {self.current_shot_key}")

            # Clear table
            self.shots_table.setRowCount(0)

            # Populate table
            for idx, shot_data in enumerate(self.shots_data):
                self._add_shot_row(idx, shot_data)

            self.logger.info(f"Refreshed table with {len(self.shots_data)} shots")
            print(f"      _refresh_table: Table refreshed with {len(self.shots_data)} shots")

        except Exception as e:
            self.logger.error(f"Error refreshing table: {e}")
            import traceback
            traceback.print_exc()

        self.logger.info(f"[REFRESH_TABLE] END: current_shot_key = {self.current_shot_key}")

    def _update_current_shot_display(self):
        """Update the current shot display label."""
        self.logger.info(f"[UPDATE_CURRENT_SHOT_DISPLAY] START: current_shot_key = {self.current_shot_key}")

        try:
            import nuke

            # Get current context from root knobs
            project = str(nuke.root()['multishot_project'].value()) if nuke.root().knob('multishot_project') else ''
            ep = str(nuke.root()['multishot_ep'].value()) if nuke.root().knob('multishot_ep') else ''
            seq = str(nuke.root()['multishot_seq'].value()) if nuke.root().knob('multishot_seq') else ''
            shot = str(nuke.root()['multishot_shot'].value()) if nuke.root().knob('multishot_shot') else ''

            # Strip whitespace
            project = project.strip()
            ep = ep.strip()
            seq = seq.strip()
            shot = shot.strip()

            print(f"         _update_current_shot_display: Read from root knobs:")
            print(f"            project='{project}' (len={len(project)})")
            print(f"            ep='{ep}' (len={len(ep)})")
            print(f"            seq='{seq}' (len={len(seq)})")
            print(f"            shot='{shot}' (len={len(shot)})")

            if project and ep and seq and shot:
                self.current_shot_key = f"{project}_{ep}_{seq}_{shot}"
                self.current_shot_label.setText(self.current_shot_key)
                print(f"         _update_current_shot_display: Set current_shot_key = '{self.current_shot_key}'")
            else:
                self.current_shot_key = None
                self.current_shot_label.setText("None")
                print(f"         _update_current_shot_display: Set current_shot_key = None")
                print(f"            Reason: project={bool(project)}, ep={bool(ep)}, seq={bool(seq)}, shot={bool(shot)}")

        except ImportError:
            self.current_shot_key = None
            self.current_shot_label.setText("Nuke not available")
            print(f"         _update_current_shot_display: Nuke not available")
        except Exception as e:
            self.logger.error(f"Error updating current shot display: {e}")
            self.current_shot_key = None
            self.current_shot_label.setText("Error")
            import traceback
            traceback.print_exc()

        self.logger.info(f"[UPDATE_CURRENT_SHOT_DISPLAY] END: current_shot_key = {self.current_shot_key}")

    def _add_shot_row(self, idx, shot_data):
        """Add a row to the shots table."""
        try:
            row = self.shots_table.rowCount()
            self.shots_table.insertRow(row)

            # Build shot key
            shot_key = f"{shot_data['project']}_{shot_data['ep']}_{shot_data['seq']}_{shot_data['shot']}"

            # Check if this is the current shot
            is_current = (shot_key == self.current_shot_key)

            print(f"         _add_shot_row: Row {row}")
            print(f"            shot_key = '{shot_key}'")
            print(f"            current_shot_key = '{self.current_shot_key}'")
            print(f"            is_current = {is_current}")
            print(f"            Match: {shot_key == self.current_shot_key}")

            # ✅ Check if shot JSON exists
            has_json = self._check_shot_json_exists(shot_data)

            # Define colors
            green_color = QtGui.QColor(144, 238, 144)  # Light green for active shot
            yellow_color = QtGui.QColor(255, 255, 153)  # Light yellow for missing JSON

            # Column 0: Row number
            num_item = QtWidgets.QTableWidgetItem(str(idx + 1))
            num_item.setTextAlignment(QtCore.Qt.AlignCenter)
            if is_current:
                num_item.setBackground(green_color)
            elif not has_json:
                num_item.setBackground(yellow_color)
            self.shots_table.setItem(row, 0, num_item)

            # Column 1: Shot name - Store idx in UserRole for removal
            shot_item = QtWidgets.QTableWidgetItem(shot_key)
            shot_item.setData(QtCore.Qt.UserRole, idx)  # Store index for removal
            if is_current:
                shot_item.setBackground(green_color)
                shot_item.setForeground(QtGui.QColor(0, 100, 0))  # Dark green text
                font = shot_item.font()
                font.setBold(True)
                shot_item.setFont(font)
            elif not has_json:
                shot_item.setBackground(yellow_color)
                shot_item.setToolTip("⚠️ Shot JSON file not found - using default frame range (1001-1100)")
            self.shots_table.setItem(row, 1, shot_item)

            # Column 2: Set Shot button
            set_shot_btn = QtWidgets.QPushButton("Active Shot" if is_current else "Set Shot")
            set_shot_btn.setEnabled(not is_current)
            if is_current:
                set_shot_btn.setStyleSheet("background-color: #90EE90; font-weight: bold;")
            set_shot_btn.clicked.connect(lambda checked=False, sd=shot_data: self._set_shot(sd))
            self.shots_table.setCellWidget(row, 2, set_shot_btn)

            # Column 3: Version button
            version_btn = QtWidgets.QPushButton("Set Versions...")
            if is_current:
                version_btn.setStyleSheet("background-color: #90EE90;")
            version_btn.clicked.connect(lambda checked=False, sd=shot_data: self._set_versions(sd))
            self.shots_table.setCellWidget(row, 3, version_btn)

            # Column 4: Remove button
            remove_btn = QtWidgets.QPushButton("X")
            remove_btn.setMaximumWidth(40)
            remove_btn.setToolTip("Remove shot from list")
            if is_current:
                remove_btn.setStyleSheet("background-color: #90EE90;")
            remove_btn.clicked.connect(lambda checked=False, i=idx: self._remove_shot(i))
            self.shots_table.setCellWidget(row, 4, remove_btn)

            # Column 5: Bake button
            bake_btn = QtWidgets.QPushButton("Bake")
            bake_btn.setMaximumWidth(80)
            bake_btn.setToolTip("Bake all expressions to static values")
            if is_current:
                bake_btn.setStyleSheet("background-color: #90EE90;")
            bake_btn.clicked.connect(lambda checked=False, sd=shot_data: self._bake_expressions(sd))
            self.shots_table.setCellWidget(row, 5, bake_btn)

            # Column 6: Unbake button
            unbake_btn = QtWidgets.QPushButton("Unbake")
            unbake_btn.setMaximumWidth(80)
            unbake_btn.setToolTip("Restore expressions from static values")
            if is_current:
                unbake_btn.setStyleSheet("background-color: #90EE90;")
            unbake_btn.clicked.connect(lambda checked=False, sd=shot_data: self._unbake_expressions(sd))
            self.shots_table.setCellWidget(row, 6, unbake_btn)

            # Column 7: Save button
            save_btn = QtWidgets.QPushButton("Save")
            save_btn.setMaximumWidth(80)
            save_btn.setToolTip("Save script to shot directory")
            if is_current:
                save_btn.setStyleSheet("background-color: #90EE90;")
            save_btn.clicked.connect(lambda checked=False, sd=shot_data: self._save_to_shot_directory(sd))
            self.shots_table.setCellWidget(row, 7, save_btn)

            # Column 8: Render button
            render_btn = QtWidgets.QPushButton("Render")
            render_btn.setMaximumWidth(80)
            render_btn.setToolTip("Submit to render farm")
            if is_current:
                render_btn.setStyleSheet("background-color: #90EE90;")
            render_btn.clicked.connect(lambda checked=False, sd=shot_data: self._submit_to_render_farm(sd))
            self.shots_table.setCellWidget(row, 8, render_btn)

        except Exception as e:
            self.logger.error(f"Error adding shot row: {e}")
            import traceback
            traceback.print_exc()

    def _set_shot(self, shot_data):
        """Set the current shot by updating root knobs."""
        self.logger.info(f"[SET_SHOT] START: current_shot_key = {self.current_shot_key}, shot_data = {shot_data}")

        try:
            import nuke

            print(f"\n🔧 _set_shot called with: {shot_data}")

            # ✅ CRITICAL: Save current shot's versions BEFORE switching
            if self.current_shot_key:
                print(f"\n💾 [SET_SHOT] Saving versions for current shot: {self.current_shot_key}")
                self._save_current_shot_versions()
            else:
                print(f"\n⚠️  [SET_SHOT] No current shot to save (first time setup)")

            # ✅ CRITICAL FIX: Create root knobs if they don't exist!
            knobs_to_create = {
                'multishot_project': shot_data['project'],
                'multishot_ep': shot_data['ep'],
                'multishot_seq': shot_data['seq'],
                'multishot_shot': shot_data['shot']
            }

            for knob_name, value in knobs_to_create.items():
                if not nuke.root().knob(knob_name):
                    # Create the knob
                    knob = nuke.String_Knob(knob_name, '')
                    knob.setVisible(False)
                    nuke.root().addKnob(knob)
                    print(f"   Created knob: {knob_name}")

                # Set the value
                nuke.root()[knob_name].setValue(value)
                print(f"   Set {knob_name} = {value}")

            # ✅ NEW: Set frame range from shot JSON file
            print(f"\n📊 [SET SHOT] Reading frame range from JSON...")
            frame_range = self._read_frame_range_from_shot_json(shot_data)

            if frame_range:
                first_frame, last_frame = frame_range
                print(f"✅ [SET SHOT] Setting root frame range: {first_frame}-{last_frame}")
                nuke.root()['first_frame'].setValue(first_frame)
                nuke.root()['last_frame'].setValue(last_frame)
                print(f"✅ [SET SHOT] Root frame range set successfully!")
                print(f"   root.first_frame = {nuke.root()['first_frame'].value()}")
                print(f"   root.last_frame = {nuke.root()['last_frame'].value()}")
                self.logger.info(f"Set frame range from JSON: {first_frame}-{last_frame}")
            else:
                # Fallback to default
                print(f"⚠️ [SET SHOT] No frame range from JSON, using default: 1001-1100")
                nuke.root()['first_frame'].setValue(1001)
                nuke.root()['last_frame'].setValue(1100)
                print(f"✅ [SET SHOT] Default frame range set!")
                print(f"   root.first_frame = {nuke.root()['first_frame'].value()}")
                print(f"   root.last_frame = {nuke.root()['last_frame'].value()}")
                self.logger.warning(f"No frame range found, using default: 1001-1100")

            # Update variable manager
            self.variable_manager.set_context_variables({
                'project': shot_data['project'],
                'ep': shot_data['ep'],
                'seq': shot_data['seq'],
                'shot': shot_data['shot']
            })
            print(f"   Updated variable manager")

            # Update current shot key BEFORE refreshing table
            shot_key = f"{shot_data['project']}_{shot_data['ep']}_{shot_data['seq']}_{shot_data['shot']}"
            self.current_shot_key = shot_key
            print(f"   Set current_shot_key = {shot_key}")

            # Update current shot display
            self.current_shot_label.setText(shot_key)
            print(f"   Updated label to: {shot_key}")

            # Update all MultishotRead nodes to use versions for this shot
            self._update_nodes_for_shot(shot_data)
            print(f"   Updated nodes for shot")

            # Refresh table to update highlighting and button states
            # DON'T update current_shot from root knobs - we just set it!
            print(f"   Refreshing table (keeping current_shot_key)...")
            self._refresh_table(update_current_shot=False)
            print(f"   Table refreshed")

            self.logger.info(f"✅ Set current shot to: {shot_key}")
            print(f"✅ _set_shot completed successfully\n")

        except ImportError:
            self.logger.error("[SET_SHOT] ImportError - Nuke not available")
            QtWidgets.QMessageBox.warning(
                self,
                "Nuke Not Available",
                "Cannot set shot - Nuke not available"
            )
        except Exception as e:
            self.logger.error(f"[SET_SHOT] Exception: {e}")
            QtWidgets.QMessageBox.critical(
                self,
                "Error",
                f"Failed to set shot:\n{e}"
            )

        self.logger.info(f"[SET_SHOT] END: current_shot_key = {self.current_shot_key}")

    def _is_multishot_read_node(self, node):
        """Check if a node is a MultishotRead node (not Write or Switch)."""
        try:
            # Must have multishot_sep knob
            if not node.knob('multishot_sep'):
                return False

            # Must have shot_versions knob (only MultishotRead has this)
            if not node.knob('shot_versions'):
                return False

            # Must have department knob (MultishotRead has this)
            if not node.knob('department'):
                return False

            # Must NOT have output_type knob (MultishotWrite has this)
            if node.knob('output_type'):
                return False

            # Must NOT have switch_mode knob (MultishotSwitch has this)
            if node.knob('switch_mode'):
                return False

            return True

        except Exception as e:
            self.logger.error(f"Error checking if node is MultishotRead: {e}")
            return False

    def _save_current_shot_versions(self):
        """Save current shot's versions before switching to a new shot."""
        try:
            import nuke
            import multishot.nodes.read_node as read_node_module
            import json

            # Get current shot key
            current_shot_key = self.current_shot_key
            if not current_shot_key:
                print(f"⚠️  [SAVE_VERSIONS] No current shot to save")
                return

            print(f"\n💾 [SAVE_VERSIONS] Saving versions for current shot: {current_shot_key}")

            # Find all MultishotRead nodes (not Write or Switch)
            saved_count = 0
            for node in nuke.allNodes():
                if self._is_multishot_read_node(node):  # Is a MultishotRead node
                    node_name = node.name()

                    # Get node instance
                    if node_name in read_node_module._node_instances:
                        instance = read_node_module._node_instances[node_name]

                        # Get current shot_version knob value
                        current_version = node['shot_version'].value() if node.knob('shot_version') else 'v001'
                        print(f"   📦 [SAVE_VERSIONS] Node: {node_name}, Current version: {current_version}")

                        # Save this version for the current shot
                        instance.set_version_for_shot(current_version, current_shot_key)
                        print(f"   ✅ [SAVE_VERSIONS] Saved {current_version} for {current_shot_key}")

                        saved_count += 1

            self.logger.info(f"Saved {saved_count} node versions for shot {current_shot_key}")
            print(f"✅ [SAVE_VERSIONS] Saved {saved_count} node versions\n")

        except Exception as e:
            self.logger.error(f"Error saving current shot versions: {e}")
            import traceback
            traceback.print_exc()

    def _update_nodes_for_shot(self, shot_data):
        """Update all MultishotRead nodes to use versions for the new shot."""
        try:
            import nuke
            import multishot.nodes.read_node as read_node_module
            import json

            shot_key = f"{shot_data['project']}_{shot_data['ep']}_{shot_data['seq']}_{shot_data['shot']}"

            print(f"\n🔄 [UPDATE_NODES] Updating nodes for shot: {shot_key}")

            # Find all MultishotRead nodes (not Write or Switch)
            updated_count = 0
            for node in nuke.allNodes():
                if self._is_multishot_read_node(node):  # Is a MultishotRead node
                    node_name = node.name()
                    print(f"\n📦 [UPDATE_NODES] Processing node: {node_name}")

                    # Get node instance
                    if node_name in read_node_module._node_instances:
                        instance = read_node_module._node_instances[node_name]

                        # Debug: Show shot_versions knob content
                        shot_versions_str = node['shot_versions'].value() if node.knob('shot_versions') else '{}'
                        shot_versions = json.loads(shot_versions_str) if shot_versions_str else {}
                        print(f"   📊 [UPDATE_NODES] shot_versions knob: {shot_versions}")

                        # Get version for this shot
                        version = instance.get_version_for_shot(shot_key)
                        print(f"   🎯 [UPDATE_NODES] Version for {shot_key}: {version}")

                        # ✅ ONLY update shot_version knob
                        # Path will update automatically via expressions like [value root.shot]
                        current_version = node['shot_version'].value() if node.knob('shot_version') else 'v001'
                        print(f"   📝 [UPDATE_NODES] Current shot_version knob: {current_version}")
                        print(f"   ✏️  [UPDATE_NODES] Setting shot_version knob to: {version}")
                        node['shot_version'].setValue(version)
                        print(f"   ✅ [UPDATE_NODES] shot_version knob set to: {node['shot_version'].value()}")

                        # ❌ DO NOT rebuild path - expressions handle it automatically!
                        # instance.build_expression_path()

                        updated_count += 1
                    else:
                        print(f"   ⚠️  [UPDATE_NODES] Node '{node_name}' not in _node_instances!")

            self.logger.info(f"Updated {updated_count} nodes for shot {shot_key} (version knobs only)")

        except Exception as e:
            self.logger.error(f"Error updating nodes for shot: {e}")

    def _check_shot_json_exists(self, shot_data):
        """
        Check if shot JSON file exists.

        Returns:
            bool: True if JSON exists, False otherwise
        """
        try:
            import os

            # Build path to JSON file
            proj_root = self.variable_manager.get_variable('PROJ_ROOT')
            if not proj_root:
                return False

            project = shot_data['project']
            ep = shot_data['ep']
            seq = shot_data['seq']
            shot = shot_data['shot']

            # JSON filename format: .{ep}_{seq}_{shot}.json
            json_filename = f".{ep}_{seq}_{shot}.json"
            json_path = os.path.join(proj_root, project, 'all', 'scene', ep, seq, shot, json_filename)

            return os.path.exists(json_path)

        except Exception as e:
            self.logger.error(f"Error checking shot JSON: {e}")
            return False

    def _read_frame_range_from_shot_json(self, shot_data):
        """
        Read frame range from shot JSON file.

        Expected path: {PROJ_ROOT}/{project}/all/scene/{ep}/{seq}/{shot}/.{ep}_{seq}_{shot}.json

        Supported JSON structures (in order of priority):
        1. {"frameRange": {"start": 1001, "end": 1150}}
        2. {"first_frame": 1001, "last_frame": 1150}
        3. {"shot_info": {"start_frame": 1001, "end_frame": 1028}}
        4. {"timeline_settings": {"animation_start": 1001.0, "animation_end": 1028.0}}

        Returns:
            tuple: (first_frame, last_frame) or None if not found
        """
        try:
            import json
            import os

            # Build path to JSON file
            proj_root = self.variable_manager.get_variable('PROJ_ROOT')
            print(f"\n🔍 [FRAME RANGE] PROJ_ROOT = {proj_root}")

            if not proj_root:
                print("❌ [FRAME RANGE] PROJ_ROOT not set!")
                self.logger.warning("PROJ_ROOT not set, cannot read frame range")
                return None

            project = shot_data['project']
            ep = shot_data['ep']
            seq = shot_data['seq']
            shot = shot_data['shot']

            # JSON filename format: .{ep}_{seq}_{shot}.json
            json_filename = f".{ep}_{seq}_{shot}.json"
            json_path = os.path.join(proj_root, project, 'all', 'scene', ep, seq, shot, json_filename)

            print(f"🔍 [FRAME RANGE] Looking for: {json_path}")
            self.logger.info(f"Looking for shot JSON: {json_path}")

            if not os.path.exists(json_path):
                print(f"❌ [FRAME RANGE] File not found: {json_path}")
                self.logger.warning(f"Shot JSON not found: {json_path}")
                return None

            print(f"✅ [FRAME RANGE] File found! Reading...")

            # Read JSON file
            with open(json_path, 'r') as f:
                data = json.load(f)

            print(f"📄 [FRAME RANGE] JSON content: {data}")

            # Try different JSON structures
            # Format 1: {"frameRange": {"start": 1001, "end": 1150}}
            if 'frameRange' in data:
                frame_range = data['frameRange']
                first_frame = frame_range.get('start')
                last_frame = frame_range.get('end')
                if first_frame is not None and last_frame is not None:
                    print(f"✅ [FRAME RANGE] Found frameRange: {first_frame}-{last_frame}")
                    self.logger.info(f"Read frame range from JSON: {first_frame}-{last_frame}")
                    return (int(first_frame), int(last_frame))

            # Format 2: {"first_frame": 1001, "last_frame": 1150}
            if 'first_frame' in data and 'last_frame' in data:
                first_frame = data['first_frame']
                last_frame = data['last_frame']
                print(f"✅ [FRAME RANGE] Found first_frame/last_frame: {first_frame}-{last_frame}")
                self.logger.info(f"Read frame range from JSON: {first_frame}-{last_frame}")
                return (int(first_frame), int(last_frame))

            # Format 3: {"shot_info": {"start_frame": 1001, "end_frame": 1028}}
            if 'shot_info' in data:
                shot_info = data['shot_info']
                first_frame = shot_info.get('start_frame')
                last_frame = shot_info.get('end_frame')
                if first_frame is not None and last_frame is not None:
                    print(f"✅ [FRAME RANGE] Found shot_info.start_frame/end_frame: {first_frame}-{last_frame}")
                    self.logger.info(f"Read frame range from JSON: {first_frame}-{last_frame}")
                    return (int(first_frame), int(last_frame))

            # Format 4: {"timeline_settings": {"animation_start": 1001.0, "animation_end": 1028.0}}
            if 'timeline_settings' in data:
                timeline = data['timeline_settings']
                first_frame = timeline.get('animation_start')
                last_frame = timeline.get('animation_end')
                if first_frame is not None and last_frame is not None:
                    print(f"✅ [FRAME RANGE] Found timeline_settings.animation_start/end: {first_frame}-{last_frame}")
                    self.logger.info(f"Read frame range from JSON: {first_frame}-{last_frame}")
                    return (int(first_frame), int(last_frame))

            print(f"⚠️ [FRAME RANGE] No frame range fields found in JSON")
            print(f"   Available keys: {list(data.keys())}")
            self.logger.warning(f"No frame range found in JSON: {json_path}")
            return None

        except Exception as e:
            print(f"❌ [FRAME RANGE] Error: {e}")
            import traceback
            traceback.print_exc()
            self.logger.error(f"Error reading frame range from JSON: {e}")
            return None

    def _set_versions(self, shot_data):
        """Open version setting dialog for a shot."""
        try:
            shot_key = f"{shot_data['project']}_{shot_data['ep']}_{shot_data['seq']}_{shot_data['shot']}"

            # ✅ CRITICAL FIX: Set the shot FIRST before opening version dialog
            # This ensures the shot context is set so version scanning works correctly
            print(f"\n🔧 [SET_VERSIONS] Setting shot first: {shot_key}")
            self._set_shot(shot_data)
            print(f"✅ [SET_VERSIONS] Shot set, now opening version dialog...")

            # Create and show version dialog
            dialog = VersionSettingDialog(shot_data, shot_key, parent=self)
            if dialog.exec_() == QtWidgets.QDialog.Accepted:
                self.logger.info(f"Versions updated for shot {shot_key}")

        except Exception as e:
            self.logger.error(f"Error opening version dialog: {e}")
            QtWidgets.QMessageBox.critical(
                self,
                "Error",
                f"Failed to open version dialog:\n{e}"
            )

    def _remove_shot(self, idx):
        """Remove a shot from the list."""
        try:
            if idx < 0 or idx >= len(self.shots_data):
                return

            shot_data = self.shots_data[idx]
            shot_key = f"{shot_data['project']}_{shot_data['ep']}_{shot_data['seq']}_{shot_data['shot']}"

            # Confirm removal
            reply = QtWidgets.QMessageBox.question(
                self,
                "Remove Shot",
                f"Remove shot from list?\n{shot_key}\n\nThis will not delete any nodes.",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
            )

            if reply == QtWidgets.QMessageBox.Yes:
                # Remove from list
                del self.shots_data[idx]

                # Save to script
                self._save_shots()

                # Refresh table
                self._refresh_table()

                self.logger.info(f"Removed shot: {shot_key}")

        except Exception as e:
            self.logger.error(f"Error removing shot: {e}")
            QtWidgets.QMessageBox.critical(
                self,
                "Error",
                f"Failed to remove shot:\n{e}"
            )

    def _bake_expressions(self, shot_data):
        """Bake all expressions to static values for current shot."""
        try:
            import nuke

            # Confirm action
            reply = QtWidgets.QMessageBox.question(
                self,
                "Bake Expressions",
                "This will bake all Read and Write node expressions to static values.\n\n"
                "Are you sure you want to continue?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
            )

            if reply != QtWidgets.QMessageBox.Yes:
                return

            self.logger.info("Baking expressions to static values...")

            baked_count = 0

            # Helper function to check if a knob has TCL or Python expressions
            def has_expression(knob):
                """Check if knob has TCL [value ...] or Python {{...}} expressions."""
                if knob.hasExpression():
                    return True
                # Check for TCL expressions
                value_str = knob.toScript()
                if '[' in value_str and ']' in value_str:
                    return True
                return False

            # Bake Read nodes
            for node in nuke.allNodes('Read'):
                try:
                    # Store original expressions in user knobs for unbaking
                    if node.knob('file'):
                        # Check if it has an expression (TCL or Python)
                        if has_expression(node['file']):
                            original_expr = node['file'].toScript()
                            # Store original expression
                            if not node.knob('multishot_original_file'):
                                knob = nuke.String_Knob('multishot_original_file', 'Original File Expression')
                                knob.setFlag(nuke.INVISIBLE)
                                node.addKnob(knob)
                            node['multishot_original_file'].setValue(original_expr)

                            # Bake to static value
                            evaluated_path = node['file'].evaluate()
                            node['file'].setValue(evaluated_path)
                            self.logger.info(f"Baked Read file: {node.name()} -> {evaluated_path}")

                    # Bake frame range
                    if node.knob('first') and has_expression(node['first']):
                        # Get the expression string (not the full script representation)
                        anim = node['first'].animation(0)
                        if anim:
                            original_expr = anim.expression()
                        else:
                            original_expr = node['first'].toScript()

                        if not node.knob('multishot_original_first'):
                            knob = nuke.String_Knob('multishot_original_first', 'Original First Expression')
                            knob.setFlag(nuke.INVISIBLE)
                            node.addKnob(knob)
                        node['multishot_original_first'].setValue(original_expr)

                        # Get evaluated value BEFORE clearing expression
                        first_frame = int(node['first'].value())
                        # Clear expression and set static value
                        node['first'].clearAnimated()
                        node['first'].setValue(first_frame)
                        self.logger.info(f"Baked Read first: {node.name()} -> {first_frame}")

                    if node.knob('last') and has_expression(node['last']):
                        # Get the expression string (not the full script representation)
                        anim = node['last'].animation(0)
                        if anim:
                            original_expr = anim.expression()
                        else:
                            original_expr = node['last'].toScript()

                        if not node.knob('multishot_original_last'):
                            knob = nuke.String_Knob('multishot_original_last', 'Original Last Expression')
                            knob.setFlag(nuke.INVISIBLE)
                            node.addKnob(knob)
                        node['multishot_original_last'].setValue(original_expr)

                        # Get evaluated value BEFORE clearing expression
                        last_frame = int(node['last'].value())
                        # Clear expression and set static value
                        node['last'].clearAnimated()
                        node['last'].setValue(last_frame)
                        self.logger.info(f"Baked Read last: {node.name()} -> {last_frame}")

                    baked_count += 1

                except Exception as e:
                    self.logger.warning(f"Could not bake Read node {node.name()}: {e}")

            # Bake Write nodes
            for node in nuke.allNodes('Write'):
                try:
                    if node.knob('file'):
                        if has_expression(node['file']):
                            original_expr = node['file'].toScript()
                            # Store original expression
                            if not node.knob('multishot_original_file'):
                                knob = nuke.String_Knob('multishot_original_file', 'Original File Expression')
                                knob.setFlag(nuke.INVISIBLE)
                                node.addKnob(knob)
                            node['multishot_original_file'].setValue(original_expr)

                            # Bake to static value
                            evaluated_path = node['file'].evaluate()
                            node['file'].setValue(evaluated_path)
                            self.logger.info(f"Baked Write file: {node.name()} -> {evaluated_path}")

                    baked_count += 1

                except Exception as e:
                    self.logger.warning(f"Could not bake Write node {node.name()}: {e}")

            self.logger.info(f"Baked {baked_count} nodes")

            QtWidgets.QMessageBox.information(
                self,
                "Bake Complete",
                f"Successfully baked expressions in {baked_count} nodes.\n\n"
                f"Original expressions are stored and can be restored using 'Unbake'."
            )

        except Exception as e:
            self.logger.error(f"Error baking expressions: {e}")
            import traceback
            traceback.print_exc()
            QtWidgets.QMessageBox.critical(
                self,
                "Error",
                f"Failed to bake expressions:\n{e}"
            )

    def _unbake_expressions(self, shot_data):
        """Restore expressions from baked static values."""
        try:
            import nuke

            # Confirm action
            reply = QtWidgets.QMessageBox.question(
                self,
                "Unbake Expressions",
                "This will restore original expressions from baked values.\n\n"
                "Are you sure you want to continue?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
            )

            if reply != QtWidgets.QMessageBox.Yes:
                return

            self.logger.info("Unbaking expressions...")

            unbaked_count = 0

            # Unbake Read nodes
            for node in nuke.allNodes('Read'):
                try:
                    # Restore file expression
                    if node.knob('multishot_original_file'):
                        original_expr = node['multishot_original_file'].value()
                        if original_expr:
                            node['file'].fromScript(original_expr)
                            node.removeKnob(node['multishot_original_file'])
                            self.logger.info(f"Unbaked Read file: {node.name()}")

                    # Restore first frame expression
                    if node.knob('multishot_original_first'):
                        original_expr = node['multishot_original_first'].value()
                        if original_expr:
                            # For Int_Knob, use setExpression() to restore TCL expressions
                            node['first'].setExpression(original_expr)
                            node.removeKnob(node['multishot_original_first'])
                            self.logger.info(f"Unbaked Read first: {node.name()} -> {original_expr}")

                    # Restore last frame expression
                    if node.knob('multishot_original_last'):
                        original_expr = node['multishot_original_last'].value()
                        if original_expr:
                            # For Int_Knob, use setExpression() to restore TCL expressions
                            node['last'].setExpression(original_expr)
                            node.removeKnob(node['multishot_original_last'])
                            self.logger.info(f"Unbaked Read last: {node.name()} -> {original_expr}")

                    unbaked_count += 1

                except Exception as e:
                    self.logger.warning(f"Could not unbake Read node {node.name()}: {e}")

            # Unbake Write nodes
            for node in nuke.allNodes('Write'):
                try:
                    if node.knob('multishot_original_file'):
                        original_expr = node['multishot_original_file'].value()
                        if original_expr:
                            node['file'].fromScript(original_expr)
                            node.removeKnob(node['multishot_original_file'])
                            self.logger.debug(f"Unbaked Write file: {node.name()}")

                    unbaked_count += 1

                except Exception as e:
                    self.logger.warning(f"Could not unbake Write node {node.name()}: {e}")

            self.logger.info(f"Unbaked {unbaked_count} nodes")

            QtWidgets.QMessageBox.information(
                self,
                "Unbake Complete",
                f"Successfully restored expressions in {unbaked_count} nodes."
            )

        except Exception as e:
            self.logger.error(f"Error unbaking expressions: {e}")
            import traceback
            traceback.print_exc()
            QtWidgets.QMessageBox.critical(
                self,
                "Error",
                f"Failed to unbake expressions:\n{e}"
            )

    def _save_to_shot_directory(self, shot_data):
        """Save Nuke script to target shot directory in the background."""
        try:
            import nuke
            import os
            import re

            # Get PROJ_ROOT
            proj_root = self.variable_manager.get_variable('PROJ_ROOT')
            if not proj_root:
                QtWidgets.QMessageBox.warning(
                    self,
                    "Missing PROJ_ROOT",
                    "PROJ_ROOT variable is not set. Cannot determine save path."
                )
                return

            # Remove trailing slash
            if proj_root.endswith('/') or proj_root.endswith('\\'):
                proj_root = proj_root[:-1]

            # Build shot directory path
            # Format: {PROJ_ROOT}/{project}/all/scene/{ep}/{seq}/{shot}/comp/version/
            shot_dir = os.path.join(
                proj_root,
                shot_data['project'],
                'all',
                'scene',
                shot_data['ep'],
                shot_data['seq'],
                shot_data['shot'],
                'comp',
                'version'
            )

            # Create directory if it doesn't exist
            if not os.path.exists(shot_dir):
                try:
                    os.makedirs(shot_dir)
                    self.logger.info(f"Created directory: {shot_dir}")
                except Exception as e:
                    QtWidgets.QMessageBox.critical(
                        self,
                        "Directory Error",
                        f"Failed to create directory:\n{shot_dir}\n\nError: {e}"
                    )
                    return

            # Build shot name for filename
            # Format: {ep}_{seq}_{shot}
            shot_name = f"{shot_data['ep']}_{shot_data['seq']}_{shot_data['shot']}"

            # Scan for existing versions in the directory
            # Look for files matching: {shotName}_v###.nk
            existing_versions = []
            pattern = re.compile(rf"^{re.escape(shot_name)}_v(\d{{3}})\.nk$")

            try:
                for filename in os.listdir(shot_dir):
                    match = pattern.match(filename)
                    if match:
                        version_num = int(match.group(1))
                        existing_versions.append(version_num)
            except Exception as e:
                self.logger.warning(f"Could not scan directory for versions: {e}")

            # Determine next version number
            if existing_versions:
                next_version_num = max(existing_versions) + 1
                self.logger.info(f"Found existing versions: {existing_versions}, next version: {next_version_num}")
            else:
                next_version_num = 1
                self.logger.info("No existing versions found, starting with v001")

            # Format version as v001, v002, etc.
            next_version = f"v{next_version_num:03d}"

            # Build filename: {shotName}_{next_version}.nk
            filename = f"{shot_name}_{next_version}.nk"

            # Build full save path
            save_path = os.path.join(shot_dir, filename)

            # Confirm save
            reply = QtWidgets.QMessageBox.question(
                self,
                "Save Script",
                f"Save script to:\n{save_path}\n\nContinue?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
            )

            if reply != QtWidgets.QMessageBox.Yes:
                return

            # Save script in background (overwrite=1 means no dialog)
            self.logger.info(f"Saving script to: {save_path}")
            nuke.scriptSaveAs(save_path, overwrite=1)

            self.logger.info(f"Script saved successfully: {save_path}")

            QtWidgets.QMessageBox.information(
                self,
                "Save Complete",
                f"Script saved to:\n{save_path}"
            )

        except Exception as e:
            self.logger.error(f"Error saving script: {e}")
            import traceback
            traceback.print_exc()
            QtWidgets.QMessageBox.critical(
                self,
                "Error",
                f"Failed to save script:\n{e}"
            )

    def _submit_to_render_farm(self, shot_data):
        """Submit shot to render farm with baked expressions."""
        try:
            import nuke
            from .render_farm_dialog import RenderFarmDialog
            from ..deadline.farm_script import FarmScriptManager
            from ..deadline.farm_submission import DeadlineFarmSubmitter

            # Check if script is saved
            script_path = nuke.root().name()
            if script_path == 'Root' or not script_path:
                QtWidgets.QMessageBox.warning(
                    self,
                    "Script Not Saved",
                    "Please save your script before submitting to render farm."
                )
                return

            # Add PROJ_ROOT to shot_data if not present
            if 'PROJ_ROOT' not in shot_data:
                proj_root = self.variable_manager.get_variable('PROJ_ROOT')
                if proj_root:
                    shot_data['PROJ_ROOT'] = proj_root

            # Show render farm dialog
            dialog = RenderFarmDialog(shot_data, parent=self)
            if dialog.exec_() == QtWidgets.QDialog.Accepted:
                # Get selected Write nodes and order
                selected_writes = dialog.get_selected_writes()
                if not selected_writes:
                    return

                self.logger.info(f"Submitting {len(selected_writes)} Write nodes to render farm")

                try:
                    # Get frame range BEFORE creating farm script
                    first_frame = int(nuke.root()['first_frame'].value())
                    last_frame = int(nuke.root()['last_frame'].value())
                    frame_range = (first_frame, last_frame)
                    self.logger.info(f"Frame range: {first_frame}-{last_frame}")

                    # Store Write node info BEFORE creating farm script
                    # (because after reload, node objects will be invalid)
                    write_info_list = []
                    for write_info in selected_writes:
                        node = write_info['node']
                        info = {
                            'name': node.name(),
                            'file': node['file'].value() if node.knob('file') else '',
                            'order': write_info['order']
                        }
                        write_info_list.append(info)
                        self.logger.info(f"  Write node: {info['name']} -> {info['file']}")

                    # Create farm script
                    farm_manager = FarmScriptManager()
                    self.logger.info("Creating farm script...")
                    farm_script_path = farm_manager.create_farm_script(shot_data, script_path)
                    self.logger.info(f"Farm script created: {farm_script_path}")

                    # Submit to Deadline (using stored info, not node objects)
                    submitter = DeadlineFarmSubmitter()
                    self.logger.info("Submitting to Deadline...")
                    job_ids = submitter.submit_write_nodes(
                        farm_script_path,
                        write_info_list,
                        shot_data,
                        frame_range
                    )

                    # Show success message
                    if job_ids:
                        QtWidgets.QMessageBox.information(
                            self,
                            "Render Farm Submission",
                            f"Successfully submitted {len(job_ids)} jobs to Deadline!\n\n"
                            f"Farm script: {farm_script_path}\n"
                            f"Frame range: {first_frame}-{last_frame}\n"
                            f"Job IDs: {', '.join(job_ids)}"
                        )
                    else:
                        QtWidgets.QMessageBox.warning(
                            self,
                            "Render Farm Submission",
                            "No jobs were submitted to Deadline.\n\n"
                            "Check the Script Editor for error details."
                        )

                except Exception as submit_error:
                    self.logger.error(f"Submission error: {submit_error}")
                    import traceback
                    traceback.print_exc()
                    QtWidgets.QMessageBox.critical(
                        self,
                        "Submission Error",
                        f"Failed to submit to Deadline:\n\n{submit_error}"
                    )
                    return

        except Exception as e:
            self.logger.error(f"Error submitting to render farm: {e}")
            import traceback
            traceback.print_exc()
            QtWidgets.QMessageBox.critical(
                self,
                "Error",
                f"Failed to submit to render farm:\n{e}"
            )

    def _add_shots(self):
        """Add shots from directory structure."""
        try:
            # Create and show add shots dialog
            dialog = AddShotsDialog(self.variable_manager, self.scanner, parent=self)
            if dialog.exec_() == QtWidgets.QDialog.Accepted:
                # Get selected shots
                selected_shots = dialog.get_selected_shots()

                if selected_shots:
                    # Add to shots list (avoid duplicates)
                    added_count = 0
                    for shot_data in selected_shots:
                        shot_key = f"{shot_data['project']}_{shot_data['ep']}_{shot_data['seq']}_{shot_data['shot']}"

                        # Check if already exists
                        exists = any(
                            f"{s['project']}_{s['ep']}_{s['seq']}_{s['shot']}" == shot_key
                            for s in self.shots_data
                        )

                        if not exists:
                            self.shots_data.append(shot_data)
                            added_count += 1

                    # Save to script
                    self._save_shots()

                    # Refresh table
                    self._refresh_table()

                    self.logger.info(f"Added {added_count} shots")

                    QtWidgets.QMessageBox.information(
                        self,
                        "Shots Added",
                        f"Added {added_count} shots to the list"
                    )

        except Exception as e:
            self.logger.error(f"Error adding shots: {e}")
            QtWidgets.QMessageBox.critical(
                self,
                "Error",
                f"Failed to add shots:\n{e}"
            )

    def _update_all_to_latest(self):
        """Update all shots to latest versions."""
        try:
            # Show confirmation
            reply = QtWidgets.QMessageBox.question(
                self,
                "Update All Versions",
                "Update all shots to their latest versions?\n\nThis will scan directories and update all MultishotRead nodes.",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
            )

            if reply != QtWidgets.QMessageBox.Yes:
                return

            # Get all MultishotRead nodes (not Write or Switch)
            import nuke
            import multishot.nodes.read_node as read_node_module

            all_nodes = nuke.allNodes()
            multishot_nodes = [n for n in all_nodes if self._is_multishot_read_node(n)]

            if not multishot_nodes:
                QtWidgets.QMessageBox.information(
                    self,
                    "No Nodes",
                    "No MultishotRead nodes found in the script."
                )
                return

            # Get root variables
            proj_root = self.variable_manager.get_variable('PROJ_ROOT')
            if not proj_root:
                QtWidgets.QMessageBox.warning(
                    self,
                    "Missing Variable",
                    "PROJ_ROOT not set. Please configure in Variables dialog."
                )
                return

            # Process each shot in the table
            updated_count = 0
            error_count = 0

            for row in range(self.shots_table.rowCount()):
                shot_label = self.shots_table.item(row, 0)
                if not shot_label:
                    continue

                shot_key = shot_label.data(QtCore.Qt.UserRole)
                if not shot_key:
                    continue

                # Parse shot key (format: "project_ep_seq_shot")
                parts = shot_key.split('_')
                if len(parts) < 4:
                    continue

                project = parts[0]
                ep = parts[1]
                seq = parts[2]
                shot = '_'.join(parts[3:])  # Handle shots with underscores

                # For each MultishotRead node, find latest version
                for node in multishot_nodes:
                    try:
                        # Get department from node
                        department = node['department'].value() if node.knob('department') else None
                        if not department:
                            continue

                        # Build path to department directory
                        dept_path = os.path.join(
                            proj_root,
                            project,
                            "all",
                            "scene",
                            ep,
                            seq,
                            shot,
                            department,
                            "publish"
                        )

                        # Scan for versions
                        if os.path.exists(dept_path):
                            versions = self.scanner.scan_versions(dept_path)

                            if versions:
                                # Get latest version
                                latest_version = self.scanner.get_latest_version(versions)

                                # Update node's version for this shot
                                if node.name() in read_node_module._node_instances:
                                    instance = read_node_module._node_instances[node.name()]
                                    instance.set_version_for_shot(latest_version, shot_key)
                                    updated_count += 1
                                    self.logger.info(f"Updated {node.name()} to {latest_version} for shot {shot_key}")

                    except Exception as e:
                        self.logger.error(f"Error updating node {node.name()} for shot {shot_key}: {e}")
                        error_count += 1

            # Show result
            message = f"Updated {updated_count} node versions to latest."
            if error_count > 0:
                message += f"\n\n{error_count} errors occurred (check console for details)."

            QtWidgets.QMessageBox.information(
                self,
                "Update Complete",
                message
            )

            self.logger.info(f"Update all to latest complete: {updated_count} updated, {error_count} errors")

        except Exception as e:
            self.logger.error(f"Error updating all to latest: {e}")
            import traceback
            traceback.print_exc()
            QtWidgets.QMessageBox.critical(
                self,
                "Error",
                f"Failed to update versions:\n{e}"
            )

    def _restore_geometry(self):
        """Restore window geometry from settings or use default."""
        try:
            # Try to restore from QSettings
            from PySide2.QtCore import QSettings
            settings = QSettings("Multishot", "MultishotManager")

            geometry = settings.value("geometry")
            if geometry:
                self.restoreGeometry(geometry)
                self.logger.info("Restored window geometry from settings")
            else:
                # Calculate default size based on table columns
                # Column widths: 50 + 300 + 120 + 150 + 80 = 700
                # Add padding for margins, scrollbar, and frame: ~80px
                table_width = 50 + 300 + 120 + 150 + 80 + 80  # = 780

                # Height: enough for ~10 rows + header + buttons + margins
                # Row height ~30px, header ~30px, buttons ~100px, margins ~100px
                table_height = (30 * 10) + 30 + 100 + 100  # = 530

                self.resize(table_width, table_height)
                # Center on screen
                self._center_on_screen()
                self.logger.info(f"Using calculated window size: {table_width}x{table_height}")

        except Exception as e:
            # Fallback to default size
            self.resize(780, 530)
            self._center_on_screen()
            self.logger.warning(f"Could not restore geometry, using default: {e}")

    def _center_on_screen(self):
        """Center the window on screen."""
        try:
            from PySide2.QtWidgets import QApplication
            screen = QApplication.desktop().screenGeometry()
            size = self.geometry()
            self.move(
                (screen.width() - size.width()) // 2,
                (screen.height() - size.height()) // 2
            )
        except:
            pass

    def closeEvent(self, event):
        """Save window geometry when closing."""
        try:
            from PySide2.QtCore import QSettings
            settings = QSettings("Multishot", "MultishotManager")
            settings.setValue("geometry", self.saveGeometry())
            self.logger.info("Saved window geometry to settings")
        except Exception as e:
            self.logger.warning(f"Could not save geometry: {e}")

        event.accept()


class VersionSettingDialog(QtWidgets.QDialog):
    """Dialog for setting versions for a specific shot."""

    def __init__(self, shot_data, shot_key, parent=None):
        super().__init__(parent)
        self.logger = self._get_logger()
        self.shot_data = shot_data
        self.shot_key = shot_key

        self.setWindowTitle(f"Set Versions for Shot: {shot_key}")
        self.setModal(True)
        self.resize(700, 500)

        self._setup_ui()
        self._load_nodes()

    def _get_logger(self):
        """Get logger instance."""
        from ..utils.logging import get_logger
        return get_logger(__name__)

    def _setup_ui(self):
        """Setup the user interface."""
        layout = QtWidgets.QVBoxLayout(self)

        # Header
        header_label = QtWidgets.QLabel(f"Set Versions for Shot: {self.shot_key}")
        header_label.setStyleSheet("font-size: 14px; font-weight: bold; margin: 10px;")
        layout.addWidget(header_label)

        # Nodes table
        self.nodes_table = QtWidgets.QTableWidget()
        self.nodes_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.nodes_table.setAlternatingRowColors(True)

        # Setup columns: # | Node Name | Department | Version
        columns = ['#', 'Node Name', 'Department', 'Version']
        self.nodes_table.setColumnCount(len(columns))
        self.nodes_table.setHorizontalHeaderLabels(columns)

        # Set column widths
        header = self.nodes_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.resizeSection(0, 50)   # #
        header.resizeSection(1, 250)  # Node Name
        header.resizeSection(2, 120)  # Department

        layout.addWidget(self.nodes_table)

        # Buttons
        button_layout = QtWidgets.QHBoxLayout()

        self.set_all_latest_btn = QtWidgets.QPushButton("Set All to Latest")
        self.set_all_latest_btn.clicked.connect(self._set_all_to_latest)
        button_layout.addWidget(self.set_all_latest_btn)

        button_layout.addStretch()

        self.apply_btn = QtWidgets.QPushButton("Apply")
        self.apply_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.apply_btn)

        self.cancel_btn = QtWidgets.QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)

        layout.addLayout(button_layout)

    def _is_multishot_read_node(self, node):
        """Check if a node is a MultishotRead node (not Write or Switch)."""
        try:
            # Must have multishot_sep knob
            if not node.knob('multishot_sep'):
                return False

            # Must have shot_versions knob (only MultishotRead has this)
            if not node.knob('shot_versions'):
                return False

            # Must have department knob (MultishotRead has this)
            if not node.knob('department'):
                return False

            # Must NOT have output_type knob (MultishotWrite has this)
            if node.knob('output_type'):
                return False

            # Must NOT have switch_mode knob (MultishotSwitch has this)
            if node.knob('switch_mode'):
                return False

            return True

        except Exception as e:
            self.logger.error(f"Error checking if node is MultishotRead: {e}")
            return False

    def _load_nodes(self):
        """Load all MultishotRead nodes."""
        try:
            import nuke
            import multishot.nodes.read_node as read_node_module

            # Clear table
            self.nodes_table.setRowCount(0)

            # Get all nodes
            all_nodes = nuke.allNodes()
            self.logger.info(f"Found {len(all_nodes)} total nodes in script")

            # Find all MultishotRead nodes (not Write or Switch)
            idx = 0

            # Debug: Show all registered instances
            self.logger.info(f"Registered node instances: {list(read_node_module._node_instances.keys())}")

            for node in all_nodes:
                # Check if it's a MultishotRead node (not Write or Switch)
                if self._is_multishot_read_node(node):
                    self.logger.info(f"Found MultishotRead node: {node.name()}")

                    # Debug: Check if node is in instances
                    in_instances = node.name() in read_node_module._node_instances
                    self.logger.info(f"  Node '{node.name()}' in _node_instances: {in_instances}")

                    row = self.nodes_table.rowCount()
                    self.nodes_table.insertRow(row)

                    # Column 0: Row number
                    num_item = QtWidgets.QTableWidgetItem(str(idx + 1))
                    num_item.setTextAlignment(QtCore.Qt.AlignCenter)
                    self.nodes_table.setItem(row, 0, num_item)

                    # Column 1: Node name
                    name_item = QtWidgets.QTableWidgetItem(node.name())
                    self.nodes_table.setItem(row, 1, name_item)

                    # Column 2: Department
                    department = node['department'].value() if node.knob('department') else 'N/A'
                    dept_item = QtWidgets.QTableWidgetItem(department)
                    self.nodes_table.setItem(row, 2, dept_item)

                    # Column 3: Version dropdown
                    version_combo = QtWidgets.QComboBox()

                    # Get current version for this shot
                    if node.name() in read_node_module._node_instances:
                        instance = read_node_module._node_instances[node.name()]
                        current_version = instance.get_version_for_shot(self.shot_key)
                    else:
                        current_version = 'v001'

                    # Scan actual versions from directory
                    versions = self._scan_versions_for_node(node)
                    if not versions:
                        # Fallback to default list if scan fails
                        versions = [f"v{str(i).zfill(3)}" for i in range(1, 21)]
                        self.logger.warning(f"Could not scan versions for {node.name()}, using default list")

                    version_combo.addItems(versions)

                    # Set current version if it exists in the list
                    if current_version in versions:
                        version_combo.setCurrentText(current_version)
                    elif versions:
                        version_combo.setCurrentText(versions[0])

                    # Store node reference in combo box
                    version_combo.setProperty('node', node)

                    self.nodes_table.setCellWidget(row, 3, version_combo)

                    idx += 1

            self.logger.info(f"Loaded {idx} MultishotRead nodes")

        except ImportError:
            self.logger.warning("Nuke not available")
        except Exception as e:
            self.logger.error(f"Error loading nodes: {e}")

    def _scan_versions_for_node(self, node):
        """Scan available versions for a node from the directory.

        Args:
            node: Nuke node to scan versions for

        Returns:
            List of version strings (e.g., ['v001', 'v002', 'v003'])
        """
        try:
            import os
            from ..core.variables import VariableManager

            # Get node properties
            department = node['department'].value() if node.knob('department') else 'lighting'
            layer = node['layer'].value() if node.knob('layer') else 'MASTER_CHAR_A'

            # Get variable manager to resolve paths
            vm = VariableManager()

            # Build directory path
            # Format: IMG_ROOT/project/all/scene/ep/seq/shot/department/publish/
            img_root = vm.get_variable('IMG_ROOT')
            project = self.shot_data.get('project', '')
            ep = self.shot_data.get('ep', '')
            seq = self.shot_data.get('seq', '')
            shot = self.shot_data.get('shot', '')

            if not all([img_root, project, ep, seq, shot]):
                self.logger.warning(f"Missing path components for version scan")
                return []

            # Build publish directory path
            publish_dir = os.path.join(
                img_root,
                project,
                'all',
                'scene',
                ep,
                seq,
                shot,
                department,
                'publish'
            )

            self.logger.info(f"Scanning versions in: {publish_dir}")

            # Check if directory exists
            if not os.path.exists(publish_dir):
                self.logger.warning(f"Publish directory does not exist: {publish_dir}")
                return []

            # Scan for version directories (v001, v002, etc.)
            versions = []
            for item in os.listdir(publish_dir):
                item_path = os.path.join(publish_dir, item)
                # Check if it's a directory and matches version pattern (v###)
                if os.path.isdir(item_path) and item.startswith('v') and len(item) == 4:
                    try:
                        # Verify it's a valid version number
                        int(item[1:])
                        versions.append(item)
                    except ValueError:
                        continue

            # Sort versions
            versions.sort()

            self.logger.info(f"Found {len(versions)} versions: {versions}")
            return versions

        except Exception as e:
            self.logger.error(f"Error scanning versions: {e}")
            import traceback
            traceback.print_exc()
            return []

    def _set_all_to_latest(self):
        """Set all nodes to latest version."""
        try:
            # Set each node to its latest available version
            for row in range(self.nodes_table.rowCount()):
                version_combo = self.nodes_table.cellWidget(row, 3)
                if version_combo and version_combo.count() > 0:
                    # Set to last item (latest version)
                    version_combo.setCurrentIndex(version_combo.count() - 1)

            self.logger.info("Set all nodes to latest version")

        except Exception as e:
            self.logger.error(f"Error setting all to latest: {e}")

    def accept(self):
        """Apply version changes and close dialog."""
        try:
            import multishot.nodes.read_node as read_node_module

            # Apply version changes to all nodes
            for row in range(self.nodes_table.rowCount()):
                version_combo = self.nodes_table.cellWidget(row, 3)
                if version_combo:
                    node = version_combo.property('node')
                    version = version_combo.currentText()

                    # Get node instance and set version for this shot
                    if node.name() in read_node_module._node_instances:
                        instance = read_node_module._node_instances[node.name()]
                        instance.set_version_for_shot(version, self.shot_key)

            self.logger.info(f"Applied version changes for shot {self.shot_key}")

            super().accept()

        except Exception as e:
            self.logger.error(f"Error applying version changes: {e}")
            QtWidgets.QMessageBox.critical(
                self,
                "Error",
                f"Failed to apply version changes:\n{e}"
            )


class AddShotsDialog(QtWidgets.QDialog):
    """Dialog for adding shots from directory structure."""

    def __init__(self, variable_manager, scanner, parent=None):
        super().__init__(parent)
        self.logger = self._get_logger()
        self.variable_manager = variable_manager
        self.scanner = scanner
        self.selected_shots = []

        self.setWindowTitle("Add Shots")
        self.setModal(True)
        self.resize(600, 700)

        self._setup_ui()
        self._load_directory_tree()

    def _get_logger(self):
        """Get logger instance."""
        from ..utils.logging import get_logger
        return get_logger(__name__)

    def _setup_ui(self):
        """Setup the user interface."""
        layout = QtWidgets.QVBoxLayout(self)

        # Header
        header_label = QtWidgets.QLabel("Select Shots to Add")
        header_label.setStyleSheet("font-size: 14px; font-weight: bold; margin: 10px;")
        layout.addWidget(header_label)

        # Tree view
        self.tree_view = QtWidgets.QTreeWidget()
        self.tree_view.setHeaderLabels(['Shot Structure'])
        self.tree_view.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        layout.addWidget(self.tree_view)

        # Buttons
        button_layout = QtWidgets.QHBoxLayout()

        self.select_all_btn = QtWidgets.QPushButton("Select All")
        self.select_all_btn.clicked.connect(self._select_all)
        button_layout.addWidget(self.select_all_btn)

        self.deselect_all_btn = QtWidgets.QPushButton("Deselect All")
        self.deselect_all_btn.clicked.connect(self._deselect_all)
        button_layout.addWidget(self.deselect_all_btn)

        button_layout.addStretch()

        self.add_btn = QtWidgets.QPushButton("Add Selected")
        self.add_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.add_btn)

        self.cancel_btn = QtWidgets.QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)

        layout.addLayout(button_layout)

    def _load_directory_tree(self):
        """Load directory tree with shots."""
        try:
            # Get root variables
            proj_root = self.variable_manager.get_variable('PROJ_ROOT')
            if not proj_root:
                self.logger.warning("PROJ_ROOT not set")
                placeholder = QtWidgets.QTreeWidgetItem(self.tree_view)
                placeholder.setText(0, "PROJ_ROOT not set - please configure in Variables dialog")
                return

            # Scan for projects
            projects = self.scanner.scan_projects(proj_root)

            if not projects:
                placeholder = QtWidgets.QTreeWidgetItem(self.tree_view)
                placeholder.setText(0, f"No projects found in {proj_root}")
                return

            # Build tree for each project
            for project in projects:
                project_item = QtWidgets.QTreeWidgetItem(self.tree_view)
                project_item.setText(0, f"📁 {project}")
                project_item.setExpanded(False)

                # Scan episodes
                episodes = self.scanner.scan_episodes(proj_root, project)

                for episode in episodes:
                    ep_item = QtWidgets.QTreeWidgetItem(project_item)
                    ep_item.setText(0, f"📁 {episode}")
                    ep_item.setExpanded(False)

                    # Scan sequences
                    sequences = self.scanner.scan_sequences(proj_root, project, episode)

                    for sequence in sequences:
                        seq_item = QtWidgets.QTreeWidgetItem(ep_item)
                        seq_item.setText(0, f"📁 {sequence}")
                        seq_item.setExpanded(False)

                        # Scan shots
                        shots = self.scanner.scan_shots(proj_root, project, episode, sequence)

                        for shot in shots:
                            shot_item = QtWidgets.QTreeWidgetItem(seq_item)
                            shot_item.setText(0, f"🎬 {shot}")

                            # Store shot data
                            shot_data = {
                                'project': project,
                                'ep': episode,
                                'seq': sequence,
                                'shot': shot
                            }
                            shot_item.setData(0, QtCore.Qt.UserRole, shot_data)

            self.logger.info(f"Loaded directory tree with {len(projects)} projects")

        except Exception as e:
            self.logger.error(f"Error loading directory tree: {e}")
            import traceback
            traceback.print_exc()
            placeholder = QtWidgets.QTreeWidgetItem(self.tree_view)
            placeholder.setText(0, f"Error loading directory tree: {e}")

    def _select_all(self):
        """Select all items in tree."""
        self.tree_view.selectAll()

    def _deselect_all(self):
        """Deselect all items in tree."""
        self.tree_view.clearSelection()

    def get_selected_shots(self):
        """Get list of selected shots."""
        return self.selected_shots

    def accept(self):
        """Collect selected shots and close dialog."""
        try:
            # Collect selected shots from tree
            self.selected_shots = []
            selected_items = self.tree_view.selectedItems()

            for item in selected_items:
                # Get shot data from item
                shot_data = item.data(0, QtCore.Qt.UserRole)

                # Only add if it's a shot item (has shot_data)
                if shot_data and isinstance(shot_data, dict):
                    if all(k in shot_data for k in ['project', 'ep', 'seq', 'shot']):
                        self.selected_shots.append(shot_data)

            if not self.selected_shots:
                QtWidgets.QMessageBox.warning(
                    self,
                    "No Shots Selected",
                    "Please select at least one shot (🎬 icon) to add."
                )
                return

            self.logger.info(f"Selected {len(self.selected_shots)} shots")
            super().accept()

        except Exception as e:
            self.logger.error(f"Error collecting selected shots: {e}")
            import traceback
            traceback.print_exc()
            QtWidgets.QMessageBox.critical(
                self,
                "Error",
                f"Failed to collect selected shots:\n{e}"
            )


def show_multishot_manager():
    """Show the multishot manager interface."""
    try:
        from ..core.variables import VariableManager

        # Get or create shared variable manager
        variable_manager = VariableManager()

        # Create and show dialog (use exec_() to keep it open)
        dialog = MultishotManagerDialog(variable_manager=variable_manager)
        dialog.exec_()

    except Exception as e:
        print(f"Error showing multishot manager: {e}")
        import traceback
        traceback.print_exc()

