"""
Variables dialog for the Multishot Workflow System.

Provides a UI for viewing and editing variables.
"""

from .qt_utils import BaseDialog, get_qt_modules
from ..core.variables import VariableManager
from ..core.context import ContextDetector

# Get Qt modules
QtCore, QtWidgets, QtGui, Signal, Slot = get_qt_modules()

class VariablesDialog(BaseDialog):
    """Dialog for managing variables."""

    # Signal emitted when variables change
    variables_changed = Signal()

    def __init__(self, parent=None, variable_manager=None, scanner=None, initial_context=None):
        super().__init__(parent, "Multishot Variables")

        # Use provided variable_manager or create new one (for standalone use)
        if variable_manager is not None:
            self.variable_manager = variable_manager
            self.logger.info("VariablesDialog using shared VariableManager instance")
        else:
            self.variable_manager = VariableManager()
            self.logger.info("VariablesDialog created new VariableManager instance")

        # Use provided scanner or create new one (for standalone use)
        if scanner is not None:
            self.scanner = scanner
            self.logger.info("VariablesDialog using shared DirectoryScanner instance")
        else:
            from ..core.scanner import DirectoryScanner
            self.scanner = DirectoryScanner()
            self.logger.info("VariablesDialog created new DirectoryScanner instance")

        # Store initial context from browser (if provided)
        self.initial_context = initial_context or {}
        if self.initial_context:
            self.logger.info(f"VariablesDialog initialized with context: {self.initial_context}")

        self.context_detector = ContextDetector()

        self.setup_ui()
        self.load_variables()
        self.resize(700, 600)
        self.center_on_parent()
    
    def setup_ui(self):
        """Setup the user interface."""
        layout = QtWidgets.QVBoxLayout(self)
        
        # Title
        title = QtWidgets.QLabel("Multishot Variables")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        # Tab widget for different variable types
        self.tab_widget = QtWidgets.QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Context variables tab
        self.context_tab = self.create_context_tab()
        self.tab_widget.addTab(self.context_tab, "Context")
        
        # Custom variables tab
        self.custom_tab = self.create_custom_tab()
        self.tab_widget.addTab(self.custom_tab, "Custom")
        
        # Root variables tab (read-only)
        self.root_tab = self.create_root_tab()
        self.tab_widget.addTab(self.root_tab, "Root Paths")
        
        # Info tab
        self.info_tab = self.create_info_tab()
        self.tab_widget.addTab(self.info_tab, "Info")
        
        # Buttons
        button_layout = QtWidgets.QHBoxLayout()

        self.refresh_btn = QtWidgets.QPushButton("Refresh Context")
        self.refresh_btn.clicked.connect(self.refresh_context)
        button_layout.addWidget(self.refresh_btn)

        self.echo_btn = QtWidgets.QPushButton("Echo Variables")
        self.echo_btn.setToolTip("Print all variables to Nuke Script Editor")
        self.echo_btn.clicked.connect(self.echo_variables_to_script_editor)
        button_layout.addWidget(self.echo_btn)

        button_layout.addStretch()

        self.apply_btn = QtWidgets.QPushButton("Apply")
        self.apply_btn.clicked.connect(self.apply_changes)
        button_layout.addWidget(self.apply_btn)

        self.close_btn = QtWidgets.QPushButton("Close")
        self.close_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.close_btn)
        
        layout.addLayout(button_layout)
    
    def create_context_tab(self):
        """Create context variables tab with dropdowns."""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)

        # Description
        desc = QtWidgets.QLabel("Context variables define the current project, episode, sequence, and shot.")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Form layout for context variables
        form_layout = QtWidgets.QFormLayout()

        # Project dropdown
        self.project_combo = QtWidgets.QComboBox()
        self.project_combo.setEditable(True)
        self.project_combo.currentTextChanged.connect(self._on_project_changed)
        form_layout.addRow("Project:", self.project_combo)

        # Episode dropdown
        self.episode_combo = QtWidgets.QComboBox()
        self.episode_combo.setEditable(True)
        self.episode_combo.currentTextChanged.connect(self._on_episode_changed)
        form_layout.addRow("Episode:", self.episode_combo)

        # Sequence dropdown
        self.sequence_combo = QtWidgets.QComboBox()
        self.sequence_combo.setEditable(True)
        self.sequence_combo.currentTextChanged.connect(self._on_sequence_changed)
        form_layout.addRow("Sequence:", self.sequence_combo)

        # Shot dropdown
        self.shot_combo = QtWidgets.QComboBox()
        self.shot_combo.setEditable(True)
        self.shot_combo.currentTextChanged.connect(self._on_shot_changed)
        form_layout.addRow("Shot:", self.shot_combo)

        layout.addLayout(form_layout)

        # Spacer
        layout.addStretch()

        # Info label
        info_label = QtWidgets.QLabel("These variables are accessible in Nuke expressions as [value root.project], [value root.ep], etc.")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #666; font-style: italic; margin-top: 10px;")
        layout.addWidget(info_label)

        return widget
    
    def create_custom_tab(self):
        """Create custom variables tab."""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)
        
        # Description
        desc = QtWidgets.QLabel("Custom variables are user-defined key-value pairs.")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Custom variables table
        self.custom_table = QtWidgets.QTableWidget(0, 3)
        self.custom_table.setHorizontalHeaderLabels(["Variable", "Value", "Template Expression"])
        self.custom_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.custom_table)
        
        # Add/Remove buttons
        button_layout = QtWidgets.QHBoxLayout()
        
        add_btn = QtWidgets.QPushButton("Add Variable")
        add_btn.clicked.connect(self.add_custom_variable)
        button_layout.addWidget(add_btn)
        
        remove_btn = QtWidgets.QPushButton("Remove Selected")
        remove_btn.clicked.connect(self.remove_custom_variable)
        button_layout.addWidget(remove_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        return widget
    
    def create_root_tab(self):
        """Create root variables tab (read-only)."""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)
        
        # Description
        desc = QtWidgets.QLabel("Root path variables are defined in the project configuration.")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Root variables table
        self.root_table = QtWidgets.QTableWidget(0, 3)
        self.root_table.setHorizontalHeaderLabels(["Variable", "Value", "Template Expression"])
        self.root_table.horizontalHeader().setStretchLastSection(True)
        self.root_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        layout.addWidget(self.root_table)
        
        return widget
    
    def create_info_tab(self):
        """Create info tab."""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)
        
        # Info text
        self.info_text = QtWidgets.QTextEdit()
        self.info_text.setReadOnly(True)
        layout.addWidget(self.info_text)
        
        return widget
    
    def load_variables(self):
        """Load variables into the UI."""
        try:
            # Load context variables into dropdowns
            self._load_context_dropdowns()

            # Load custom variables
            custom_vars = self.variable_manager.get_custom_variables()
            self.populate_table(self.custom_table, custom_vars)

            # Load root variables from script knobs only (PRD 4.1 compliance)
            custom_vars = self.variable_manager.get_custom_variables()
            root_vars = {k: v for k, v in custom_vars.items() if k in ['PROJ_ROOT', 'IMG_ROOT']}
            self.populate_table(self.root_table, root_vars)

            # Update info
            self.update_info()

        except Exception as e:
            self.logger.error(f"Error loading variables: {e}")
            self.show_error("Error", f"Failed to load variables: {e}")

    def _load_context_dropdowns(self):
        """Load context variables into dropdowns and populate options from directory structure."""
        try:
            # Block signals during initial population to prevent cascading updates
            self.project_combo.blockSignals(True)
            self.episode_combo.blockSignals(True)
            self.sequence_combo.blockSignals(True)
            self.shot_combo.blockSignals(True)

            # Get current context variables - prioritize initial_context from browser
            if self.initial_context:
                context_vars = self.initial_context.copy()
                self.logger.info(f"Using initial_context from browser: {context_vars}")
            else:
                context_vars = self.variable_manager.get_context_variables()
                self.logger.info(f"Using context_vars from VariableManager: {context_vars}")

            # Get root paths - try script-embedded first, fallback to config for initial population
            all_vars = self.variable_manager.get_all_variables()
            proj_root = all_vars.get("PROJ_ROOT", "")
            self.logger.debug(f"PROJ_ROOT: {proj_root}")

            # If no PROJ_ROOT in script (not in Nuke or not yet populated), use config for initial population
            if not proj_root:
                config_roots = self.variable_manager.config_manager.get("roots", {})
                proj_root = config_roots.get("PROJ_ROOT", "")
                self.logger.debug(f"Using config PROJ_ROOT for initial population: {proj_root}")

            if not proj_root:
                self.logger.warning("No PROJ_ROOT found for directory scanning")
                return

            # Load projects
            self.logger.info(f"Scanning projects from PROJ_ROOT: {proj_root}")
            projects = self.scanner.scan_projects(proj_root)
            self.logger.info(f"Found projects: {projects}")

            self.project_combo.clear()
            self.project_combo.addItems(projects)

            # Set current project
            current_project = context_vars.get('project', '')
            self.logger.info(f"Setting project dropdown to: {current_project}")

            if current_project:
                index = self.project_combo.findText(current_project)
                if index >= 0:
                    self.project_combo.setCurrentIndex(index)
                    self.logger.info(f"Project set to index {index}: {current_project}")
                else:
                    self.project_combo.setCurrentText(current_project)
                    self.logger.info(f"Project set as editable text: {current_project}")

            # Load episodes, sequences, shots based on current project
            self._update_episode_dropdown()

            # Set current values
            current_ep = context_vars.get('ep', '')
            self.logger.info(f"Setting episode dropdown to: {current_ep}")
            if current_ep:
                index = self.episode_combo.findText(current_ep)
                if index >= 0:
                    self.episode_combo.setCurrentIndex(index)
                else:
                    self.episode_combo.setCurrentText(current_ep)

            self._update_sequence_dropdown()

            current_seq = context_vars.get('seq', '')
            self.logger.info(f"Setting sequence dropdown to: {current_seq}")
            if current_seq:
                index = self.sequence_combo.findText(current_seq)
                if index >= 0:
                    self.sequence_combo.setCurrentIndex(index)
                else:
                    self.sequence_combo.setCurrentText(current_seq)

            self._update_shot_dropdown()

            current_shot = context_vars.get('shot', '')
            self.logger.info(f"Setting shot dropdown to: {current_shot}")
            if current_shot:
                index = self.shot_combo.findText(current_shot)
                if index >= 0:
                    self.shot_combo.setCurrentIndex(index)
                else:
                    self.shot_combo.setCurrentText(current_shot)

        except Exception as e:
            self.logger.error(f"Error loading context dropdowns: {e}")
        finally:
            # Unblock signals after population is complete
            self.project_combo.blockSignals(False)
            self.episode_combo.blockSignals(False)
            self.sequence_combo.blockSignals(False)
            self.shot_combo.blockSignals(False)

    def populate_table(self, table, variables):
        """Populate a table with variables."""
        table.setRowCount(len(variables))

        for row, (key, value) in enumerate(variables.items()):
            # Variable name
            name_item = QtWidgets.QTableWidgetItem(str(key))
            table.setItem(row, 0, name_item)

            # Variable value
            value_item = QtWidgets.QTableWidgetItem(str(value))
            table.setItem(row, 1, value_item)

            # Template expression (how to reference this variable)
            template_expr = f"{{{key}}}"
            template_item = QtWidgets.QTableWidgetItem(template_expr)
            template_item.setForeground(QtGui.QColor(100, 100, 100))  # Gray color
            template_item.setFont(QtGui.QFont("Courier", 9))  # Monospace font
            table.setItem(row, 2, template_item)
    
    def get_table_variables(self, table):
        """Get variables from a table."""
        variables = {}

        for row in range(table.rowCount()):
            name_item = table.item(row, 0)
            value_item = table.item(row, 1)
            # Skip template expression column (column 2) - it's read-only

            if name_item and value_item:
                name = name_item.text().strip()
                value = value_item.text().strip()

                if name:  # Only add non-empty names
                    variables[name] = value

        return variables
    
    def add_custom_variable(self):
        """Add a new custom variable row."""
        row = self.custom_table.rowCount()
        self.custom_table.insertRow(row)
        
        # Add empty items
        self.custom_table.setItem(row, 0, QtWidgets.QTableWidgetItem(""))
        self.custom_table.setItem(row, 1, QtWidgets.QTableWidgetItem(""))
        
        # Focus on the new row
        self.custom_table.setCurrentCell(row, 0)
    
    def remove_custom_variable(self):
        """Remove selected custom variable."""
        current_row = self.custom_table.currentRow()
        if current_row >= 0:
            self.custom_table.removeRow(current_row)

    def _update_episode_dropdown(self):
        """Update episode dropdown based on current project."""
        try:
            project = self.project_combo.currentText()
            if not project:
                return

            # Get root paths - try script-embedded first, fallback to config for initial population
            all_vars = self.variable_manager.get_all_variables()
            proj_root = all_vars.get("PROJ_ROOT", "")

            if not proj_root:
                config_roots = self.variable_manager.config_manager.get("roots", {})
                proj_root = config_roots.get("PROJ_ROOT", "")

            episodes = self.scanner.scan_episodes(proj_root, project)
            self.episode_combo.clear()
            self.episode_combo.addItems(episodes)

        except Exception as e:
            self.logger.error(f"Error updating episode dropdown: {e}")

    def _update_sequence_dropdown(self):
        """Update sequence dropdown based on current project and episode."""
        try:
            project = self.project_combo.currentText()
            episode = self.episode_combo.currentText()
            if not project or not episode:
                return

            # Get root paths - try script-embedded first, fallback to config for initial population
            all_vars = self.variable_manager.get_all_variables()
            proj_root = all_vars.get("PROJ_ROOT", "")

            if not proj_root:
                config_roots = self.variable_manager.config_manager.get("roots", {})
                proj_root = config_roots.get("PROJ_ROOT", "")

            sequences = self.scanner.scan_sequences(proj_root, project, episode)
            self.sequence_combo.clear()
            self.sequence_combo.addItems(sequences)

        except Exception as e:
            self.logger.error(f"Error updating sequence dropdown: {e}")

    def _update_shot_dropdown(self):
        """Update shot dropdown based on current project, episode, and sequence."""
        try:
            project = self.project_combo.currentText()
            episode = self.episode_combo.currentText()
            sequence = self.sequence_combo.currentText()
            if not project or not episode or not sequence:
                return

            # Get root paths - try script-embedded first, fallback to config for initial population
            all_vars = self.variable_manager.get_all_variables()
            proj_root = all_vars.get("PROJ_ROOT", "")

            if not proj_root:
                config_roots = self.variable_manager.config_manager.get("roots", {})
                proj_root = config_roots.get("PROJ_ROOT", "")

            shots = self.scanner.scan_shots(proj_root, project, episode, sequence)
            self.shot_combo.clear()
            self.shot_combo.addItems(shots)

        except Exception as e:
            self.logger.error(f"Error updating shot dropdown: {e}")

    def _on_project_changed(self):
        """Handle project dropdown change."""
        self._update_episode_dropdown()
        self._save_context_variables()

    def _on_episode_changed(self):
        """Handle episode dropdown change."""
        self._update_sequence_dropdown()
        self._save_context_variables()

    def _on_sequence_changed(self):
        """Handle sequence dropdown change."""
        self._update_shot_dropdown()
        self._save_context_variables()

    def _on_shot_changed(self):
        """Handle shot dropdown change."""
        self._save_context_variables()

    def _save_context_variables(self):
        """Save current context variables from dropdowns."""
        try:
            context_vars = {
                'project': self.project_combo.currentText(),
                'ep': self.episode_combo.currentText(),
                'seq': self.sequence_combo.currentText(),
                'shot': self.shot_combo.currentText()
            }

            # Remove empty values
            context_vars = {k: v for k, v in context_vars.items() if v}

            success = self.variable_manager.set_context_variables(context_vars)
            if success:
                self.update_info()
                self.variables_changed.emit()

        except Exception as e:
            self.logger.error(f"Error saving context variables: {e}")

    def refresh_context(self):
        """Refresh context from current script."""
        try:
            success = self.variable_manager.refresh_context()
            
            if success:
                # Reload context variables into dropdowns
                self._load_context_dropdowns()
                self.update_info()
                self.show_info("Success", "Context refreshed from current script.")
                self.variables_changed.emit()
            else:
                self.show_warning("Warning", "Could not detect context from current script.")
                
        except Exception as e:
            self.logger.error(f"Error refreshing context: {e}")
            self.show_error("Error", f"Failed to refresh context: {e}")
    
    def apply_changes(self):
        """Apply changes to variables."""
        try:
            # Context variables are saved automatically via dropdowns
            # Just save custom variables from table
            custom_vars = self.get_table_variables(self.custom_table)

            # Save custom variables
            if custom_vars:
                self.variable_manager.set_custom_variables(custom_vars)

            self.update_info()
            self.show_info("Success", "Variables saved successfully.")
            self.variables_changed.emit()

        except Exception as e:
            self.logger.error(f"Error applying changes: {e}")
            self.show_error("Error", f"Failed to save variables: {e}")
    
    def update_info(self):
        """Update the info tab."""
        try:
            info = self.variable_manager.get_variable_info()
            
            info_text = f"""Variable Information:

Context Variables: {len(info['context_variables'])}
Custom Variables: {len(info['custom_variables'])}
Root Variables: {len(info['root_variables'])}
Total Variables: {info['total_count']}

Script Embedded: {'Yes' if info['script_embedded'] else 'No'}

All Variables:
"""
            
            all_vars = self.variable_manager.get_all_variables()
            for key, value in sorted(all_vars.items()):
                info_text += f"  {key}: {value}\n"
            
            # Add validation info
            issues = self.variable_manager.validate_variables()
            if issues:
                info_text += f"\nValidation Issues:\n"
                for issue in issues:
                    info_text += f"  • {issue}\n"
            else:
                info_text += f"\nValidation: All variables are valid ✓"
            
            self.info_text.setPlainText(info_text)
            
        except Exception as e:
            self.logger.error(f"Error updating info: {e}")
            self.info_text.setPlainText(f"Error loading info: {e}")

    def echo_variables_to_script_editor(self):
        """Print all variables to Nuke Script Editor in key=value format."""
        try:
            # Get all variables
            all_variables = self.variable_manager.get_all_variables()

            # Check if running in Nuke
            try:
                import nuke

                # Print to Nuke Script Editor
                print("=== Multishot Variables ===")

                # Print by category
                context_vars = self.variable_manager.get_context_variables()
                if context_vars:
                    print("\n# Context Variables:")
                    for key, value in context_vars.items():
                        print(f"{key} = {value}")

                custom_vars = self.variable_manager.get_custom_variables()
                if custom_vars:
                    print("\n# Custom Variables:")
                    for key, value in custom_vars.items():
                        print(f"{key} = {value}")

                # Root variables from script knobs only (PRD 4.1 compliance)
                custom_vars_all = self.variable_manager.get_custom_variables()
                root_vars = {k: v for k, v in custom_vars_all.items() if k in ['PROJ_ROOT', 'IMG_ROOT']}
                if root_vars:
                    print("\n# Root Variables (Script-Embedded):")
                    for key, value in root_vars.items():
                        print(f"{key} = {value}")

                print("\n# All Variables (merged):")
                for key, value in all_variables.items():
                    print(f"{key} = {value}")

                print("===========================")

                # Show success message
                self.show_info("Variables Echoed", f"Printed {len(all_variables)} variables to Script Editor")

            except ImportError:
                # Not in Nuke, show in dialog
                var_text = "=== Multishot Variables ===\n\n"

                context_vars = self.variable_manager.get_context_variables()
                if context_vars:
                    var_text += "# Context Variables:\n"
                    for key, value in context_vars.items():
                        var_text += f"{key} = {value}\n"
                    var_text += "\n"

                custom_vars = self.variable_manager.get_custom_variables()
                if custom_vars:
                    var_text += "# Custom Variables:\n"
                    for key, value in custom_vars.items():
                        var_text += f"{key} = {value}\n"
                    var_text += "\n"

                # Root variables from script knobs only (PRD 4.1 compliance)
                custom_vars_all = self.variable_manager.get_custom_variables()
                root_vars = {k: v for k, v in custom_vars_all.items() if k in ['PROJ_ROOT', 'IMG_ROOT']}
                if root_vars:
                    var_text += "# Root Variables (Script-Embedded):\n"
                    for key, value in root_vars.items():
                        var_text += f"{key} = {value}\n"
                    var_text += "\n"

                var_text += "# All Variables (merged):\n"
                for key, value in all_variables.items():
                    var_text += f"{key} = {value}\n"

                var_text += "==========================="

                # Show in message box
                msg = QtWidgets.QMessageBox()
                msg.setWindowTitle("Variables Echo")
                msg.setText("Variables (not in Nuke environment):")
                msg.setDetailedText(var_text)
                msg.exec_()

        except Exception as e:
            self.logger.error(f"Error echoing variables: {e}")
            self.show_error("Echo Error", f"Failed to echo variables: {e}")

    def show_info(self, title, message):
        """Show info message."""
        QtWidgets.QMessageBox.information(self, title, message)

    def show_error(self, title, message):
        """Show error message."""
        QtWidgets.QMessageBox.critical(self, title, message)
