"""
Main browser UI for the Multishot Workflow System.

Provides a comprehensive interface for browsing, saving, and opening files
with context-aware controls and variable management integration.
"""

import os
import re
from typing import Dict, List, Optional, Any

from .qt_utils import BaseWidget, get_qt_modules
from ..core.variables import VariableManager
from ..core.scanner import DirectoryScanner
from ..core.paths import PathResolver
from ..core.context import ContextDetector
from ..core.version_control import VersionControl

# Get Qt modules
QtCore, QtWidgets, QtGui, Signal, Slot = get_qt_modules()

class MultishotBrowser(BaseWidget):
    """
    Main browser interface for multishot workflows.

    Provides context-aware file browsing, variable management,
    and integration with the complete multishot workflow system.
    """

    # Signals
    context_changed = Signal(dict)
    file_selected = Signal(str)
    variables_updated = Signal(dict)

    def __init__(self, variable_manager=None, parent=None):
        super().__init__(parent)

        # Initialize core components
        # Use provided variable_manager or create new one
        if variable_manager is not None:
            self.variable_manager = variable_manager
            self.logger.info("Browser using shared VariableManager instance")
        else:
            self.variable_manager = VariableManager()
            self.logger.info("Browser created new VariableManager instance")

        self.scanner = DirectoryScanner()
        self.path_resolver = PathResolver()
        self.context_detector = ContextDetector()
        self.version_control = VersionControl()

        # UI state
        self._current_context = {}
        self._current_files = []
        self._updating_ui = False

        # Setup UI
        self.setup_ui()
        self.connect_signals()
        self.load_initial_data()

        self.logger.info("MultishotBrowser initialized")

    def setup_ui(self):
        """Setup the user interface."""
        # Main layout
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Title bar
        title_layout = QtWidgets.QHBoxLayout()
        title_label = QtWidgets.QLabel("Multishot Browser")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2E86AB;")
        title_layout.addWidget(title_label)

        # Refresh button
        self.refresh_btn = QtWidgets.QPushButton("Refresh")
        self.refresh_btn.setMaximumWidth(80)
        self.refresh_btn.setToolTip("Refresh directory structure and context")
        title_layout.addWidget(self.refresh_btn)

        main_layout.addLayout(title_layout)

        # Create main content area with splitter
        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        main_layout.addWidget(splitter)

        # Left panel - Context controls and navigation
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)

        # Right panel - File browser and details
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)

        # Set splitter proportions (30% left, 70% right)
        splitter.setSizes([300, 700])

        # Bottom panel - Actions and status
        bottom_panel = self.create_bottom_panel()
        main_layout.addWidget(bottom_panel)

        # Set minimum size
        self.setMinimumSize(1000, 700)

    def create_left_panel(self):
        """Create the left panel with context controls."""
        panel = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(panel)
        layout.setContentsMargins(5, 5, 5, 5)

        # Context section
        context_group = QtWidgets.QGroupBox("Context")
        context_layout = QtWidgets.QFormLayout(context_group)

        # Project selection
        self.project_combo = QtWidgets.QComboBox()
        self.project_combo.setEditable(True)
        context_layout.addRow("Project:", self.project_combo)

        # Episode selection
        self.episode_combo = QtWidgets.QComboBox()
        context_layout.addRow("Episode:", self.episode_combo)

        # Sequence selection
        self.sequence_combo = QtWidgets.QComboBox()
        context_layout.addRow("Sequence:", self.sequence_combo)

        # Shot selection
        self.shot_combo = QtWidgets.QComboBox()
        context_layout.addRow("Shot:", self.shot_combo)

        layout.addWidget(context_group)

        # Path templates section
        paths_group = QtWidgets.QGroupBox("Path Templates")
        paths_layout = QtWidgets.QVBoxLayout(paths_group)

        # Nuke files path
        self.nuke_path_label = QtWidgets.QLabel("Nuke Files: Not set")
        self.nuke_path_label.setWordWrap(True)
        self.nuke_path_label.setStyleSheet("font-family: monospace; font-size: 10px;")
        paths_layout.addWidget(self.nuke_path_label)

        # Renders path
        self.renders_path_label = QtWidgets.QLabel("Renders: Not set")
        self.renders_path_label.setWordWrap(True)
        self.renders_path_label.setStyleSheet("font-family: monospace; font-size: 10px;")
        paths_layout.addWidget(self.renders_path_label)

        layout.addWidget(paths_group)

        # Variables section
        variables_group = QtWidgets.QGroupBox("Variables")
        variables_layout = QtWidgets.QVBoxLayout(variables_group)

        # Variables button
        self.variables_btn = QtWidgets.QPushButton("Manage Variables")
        variables_layout.addWidget(self.variables_btn)

        # Current variables display
        self.variables_text = QtWidgets.QTextEdit()
        self.variables_text.setMaximumHeight(100)
        self.variables_text.setReadOnly(True)
        self.variables_text.setStyleSheet("font-family: monospace; font-size: 10px;")
        variables_layout.addWidget(self.variables_text)

        layout.addWidget(variables_group)

        # Add stretch to push everything to top
        layout.addStretch()

        return panel

    def create_right_panel(self):
        """Create the right panel with file browser."""
        panel = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(panel)
        layout.setContentsMargins(5, 5, 5, 5)

        # File browser section
        browser_group = QtWidgets.QGroupBox("Files")
        browser_layout = QtWidgets.QVBoxLayout(browser_group)

        # File type tabs
        self.file_tabs = QtWidgets.QTabWidget()
        browser_layout.addWidget(self.file_tabs)

        # Nuke files tab (simple list)
        self.nuke_files_widget = self.create_nuke_files_widget()
        self.file_tabs.addTab(self.nuke_files_widget, "Nuke Files")

        # Renders tab (tree view with departments)
        self.renders_widget = self.create_renders_tree_widget()
        self.file_tabs.addTab(self.renders_widget, "Renders")

        # Geometry tab (tree view with departments - includes cameras)
        self.geometry_widget = self.create_geometry_tree_widget()
        self.file_tabs.addTab(self.geometry_widget, "Geometry")

        layout.addWidget(browser_group)

        # File details section
        details_group = QtWidgets.QGroupBox("File Details")
        details_layout = QtWidgets.QVBoxLayout(details_group)

        # Multishot Context section
        context_label = QtWidgets.QLabel("<b>Multishot Context:</b>")
        details_layout.addWidget(context_label)

        self.context_details_text = QtWidgets.QTextEdit()
        self.context_details_text.setMaximumHeight(80)
        self.context_details_text.setReadOnly(True)
        self.context_details_text.setStyleSheet("font-family: monospace; font-size: 10px; background-color: #f0f0f0;")
        details_layout.addWidget(self.context_details_text)

        # File info section
        file_label = QtWidgets.QLabel("<b>Selected File:</b>")
        details_layout.addWidget(file_label)

        self.file_details_text = QtWidgets.QTextEdit()
        self.file_details_text.setMaximumHeight(70)
        self.file_details_text.setReadOnly(True)
        self.file_details_text.setStyleSheet("font-family: monospace; font-size: 10px;")
        details_layout.addWidget(self.file_details_text)

        layout.addWidget(details_group)

        return panel



    def create_nuke_files_widget(self):
        """Create Nuke files widget - simple file list only."""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # File list
        file_list = QtWidgets.QListWidget()
        file_list.setAlternatingRowColors(True)
        file_list.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        layout.addWidget(file_list)

        # Store references for easy access
        widget.file_list = file_list

        return widget

    def create_renders_tree_widget(self):
        """Create renders tree widget with department hierarchy."""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # Tree view
        tree_view = QtWidgets.QTreeWidget()
        tree_view.setHeaderLabels(["Asset", "Status"])
        tree_view.setAlternatingRowColors(True)
        tree_view.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        tree_view.setRootIsDecorated(True)
        tree_view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        tree_view.customContextMenuRequested.connect(lambda pos: self._show_context_menu(tree_view, pos))
        layout.addWidget(tree_view)

        # Action buttons
        button_layout = QtWidgets.QHBoxLayout()

        create_read_btn = QtWidgets.QPushButton("Create Read Nodes")
        create_read_btn.setEnabled(False)
        button_layout.addWidget(create_read_btn)

        button_layout.addStretch()

        refresh_btn = QtWidgets.QPushButton("Refresh")
        refresh_btn.setMaximumWidth(80)
        button_layout.addWidget(refresh_btn)

        layout.addLayout(button_layout)

        # Store references
        widget.tree_view = tree_view
        widget.create_read_btn = create_read_btn
        widget.refresh_btn = refresh_btn

        # Connect signals
        tree_view.itemSelectionChanged.connect(lambda: self.on_tree_selection_changed(widget))
        create_read_btn.clicked.connect(lambda: self.create_read_nodes_from_selection(widget))
        refresh_btn.clicked.connect(self.update_file_lists)

        return widget

    def create_geometry_tree_widget(self):
        """Create geometry tree widget with department hierarchy."""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # Tree view
        tree_view = QtWidgets.QTreeWidget()
        tree_view.setHeaderLabels(["Asset", "Status"])
        tree_view.setAlternatingRowColors(True)
        tree_view.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        tree_view.setRootIsDecorated(True)
        tree_view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        tree_view.customContextMenuRequested.connect(lambda pos: self._show_context_menu(tree_view, pos))
        layout.addWidget(tree_view)

        # Action buttons
        button_layout = QtWidgets.QHBoxLayout()

        create_readgeo_btn = QtWidgets.QPushButton("Create ReadGeo Nodes")
        create_readgeo_btn.setEnabled(False)
        button_layout.addWidget(create_readgeo_btn)

        button_layout.addStretch()

        refresh_btn = QtWidgets.QPushButton("Refresh")
        refresh_btn.setMaximumWidth(80)
        button_layout.addWidget(refresh_btn)

        layout.addLayout(button_layout)

        # Store references
        widget.tree_view = tree_view
        widget.create_readgeo_btn = create_readgeo_btn
        widget.refresh_btn = refresh_btn

        # Connect signals
        tree_view.itemSelectionChanged.connect(lambda: self.on_tree_selection_changed(widget))
        create_readgeo_btn.clicked.connect(lambda: self.create_readgeo_nodes_from_selection(widget))
        refresh_btn.clicked.connect(self.update_file_lists)

        return widget

    def create_bottom_panel(self):
        """Create the bottom panel with actions and status."""
        panel = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(panel)
        layout.setContentsMargins(5, 5, 5, 5)

        # Status label
        self.status_label = QtWidgets.QLabel("Ready")
        self.status_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(self.status_label)

        layout.addStretch()

        # Action buttons
        self.open_btn = QtWidgets.QPushButton("Open")
        self.open_btn.setMinimumWidth(80)
        self.open_btn.setEnabled(False)
        layout.addWidget(self.open_btn)

        self.save_as_btn = QtWidgets.QPushButton("Save As...")
        self.save_as_btn.setMinimumWidth(80)
        layout.addWidget(self.save_as_btn)

        self.new_version_btn = QtWidgets.QPushButton("New Version")
        self.new_version_btn.setMinimumWidth(100)
        layout.addWidget(self.new_version_btn)

        self.save_increment_btn = QtWidgets.QPushButton("Save Increment")
        self.save_increment_btn.setMinimumWidth(120)
        self.save_increment_btn.setToolTip("Save as next version increment")
        self.save_increment_btn.clicked.connect(lambda: self.save_increment_version('major'))
        layout.addWidget(self.save_increment_btn)

        return panel

    def connect_signals(self):
        """Connect UI signals to handlers."""
        # Context controls
        self.project_combo.currentTextChanged.connect(self.on_project_changed)
        self.episode_combo.currentTextChanged.connect(self.on_episode_changed)
        self.sequence_combo.currentTextChanged.connect(self.on_sequence_changed)
        self.shot_combo.currentTextChanged.connect(self.on_shot_changed)

        # Buttons
        self.refresh_btn.clicked.connect(self.refresh_all)
        self.variables_btn.clicked.connect(self.show_variables_dialog)
        self.open_btn.clicked.connect(self.open_selected_file)
        self.save_as_btn.clicked.connect(self.save_as_dialog)
        self.new_version_btn.clicked.connect(self.create_new_version)

        # File lists - connect signals based on widget type
        for tab_index in range(self.file_tabs.count()):
            widget = self.file_tabs.widget(tab_index)

            # Nuke Files tab (has file_list only now)
            if hasattr(widget, 'file_list'):
                widget.file_list.itemSelectionChanged.connect(self.on_file_selection_changed)

            # Tree widgets (renders, geometry, camera) already have their signals connected

        # Tab changes
        self.file_tabs.currentChanged.connect(self.on_tab_changed)

    def load_initial_data(self):
        """Load initial data and setup default state."""
        try:
            # ✅ PHASE 3: Try to detect current script path first
            script_path = self._get_current_script_path()
            if script_path:
                self.logger.info(f"Detected current script: {script_path}")
                # Try to extract context from script path
                detected_context = self._detect_context_from_path(script_path)
                if detected_context:
                    self._current_context = detected_context
                    self.logger.info(f"Detected context from script path: {self._current_context}")

            # If no script path or detection failed, read from root knobs
            if not self._current_context or not self._current_context.get('project'):
                self._current_context = self._read_context_from_root_knobs()
                self.logger.info(f"Read context from root knobs: {self._current_context}")

            # Fill in defaults only for missing values
            if not self._current_context.get('project'):
                self._current_context['project'] = 'SWA'
            if not self._current_context.get('ep'):
                self._current_context['ep'] = ''
            if not self._current_context.get('seq'):
                self._current_context['seq'] = ''
            if not self._current_context.get('shot'):
                self._current_context['shot'] = ''

            # Load project config to get root variables
            try:
                # Try to load SWA config
                config = self.variable_manager.config_manager.load_project_config("", "SWA")
                self.logger.debug(f"Loaded config with roots: {config.get('roots', {})}")
            except Exception as e:
                self.logger.warning(f"Could not load project config: {e}")

            # Set up root variables if not already set
            roots = self.variable_manager.config_manager.get("roots", {})
            if not roots.get("PROJ_ROOT"):
                self.logger.warning("PROJ_ROOT not found in config, using default V:/")
                self.variable_manager.set_variable("PROJ_ROOT", "V:/")
                self.variable_manager.set_variable("IMG_ROOT", "W:/")

            # Load current context from variable manager
            self.refresh_context_from_variables()

            # Load project list
            self.load_projects()

            # Update UI
            self.update_ui_from_context()

            # ✅ PHASE 3: Update context details display
            self._update_context_details()

            # Force initial project selection if none selected
            if not self.project_combo.currentText() and self.project_combo.count() > 0:
                self.project_combo.setCurrentIndex(0)
                self.on_project_changed(self.project_combo.currentText())

        except Exception as e:
            self.logger.error(f"Error loading initial data: {e}")
            self.show_error("Initialization Error", f"Failed to load initial data: {e}")

    def _read_context_from_root_knobs(self):
        """Read current context from Nuke root knobs.

        Returns:
            Dictionary with context values from root knobs
        """
        try:
            import nuke

            context = {}
            knob_mapping = {
                'project': 'multishot_project',
                'ep': 'multishot_ep',
                'seq': 'multishot_seq',
                'shot': 'multishot_shot'
            }

            for context_key, knob_name in knob_mapping.items():
                if nuke.root().knob(knob_name):
                    value = str(nuke.root()[knob_name].value()).strip()
                    context[context_key] = value
                else:
                    context[context_key] = ''

            self.logger.debug(f"Read context from root knobs: {context}")
            return context

        except ImportError:
            self.logger.warning("Nuke not available, cannot read context from root knobs")
            return {'project': '', 'ep': '', 'seq': '', 'shot': ''}
        except Exception as e:
            self.logger.error(f"Error reading context from root knobs: {e}")
            return {'project': '', 'ep': '', 'seq': '', 'shot': ''}

    def refresh_context_from_variables(self):
        """Refresh context from current variables."""
        try:
            # Get current variables
            variables = self.variable_manager.get_all_variables()

            # Extract context (no department in core context)
            context = {}
            context_keys = ['project', 'ep', 'seq', 'shot', 'version']
            for key in context_keys:
                if key in variables:
                    context[key] = variables[key]

            self._current_context = context
            self.logger.debug(f"Refreshed context: {context}")

        except Exception as e:
            self.logger.error(f"Error refreshing context: {e}")

    def load_projects(self):
        """Load available projects."""
        try:
            # Get root paths
            roots = self.variable_manager.config_manager.get("roots", {})
            proj_root = roots.get("PROJ_ROOT", "")

            if not proj_root or not os.path.exists(proj_root):
                self.logger.warning(f"Project root not found: {proj_root}")
                return

            # Use known projects from config files or hardcoded list
            projects = ["SWA", "TestProject"]

            # Also try to scan for projects (directories in project root)
            try:
                for item in os.listdir(proj_root):
                    item_path = os.path.join(proj_root, item)
                    if os.path.isdir(item_path) and item not in projects:
                        projects.append(item)
            except (OSError, PermissionError) as e:
                self.logger.warning(f"Error scanning project root: {e}")

            # Update project combo
            self._updating_ui = True
            self.project_combo.clear()
            self.project_combo.addItems(sorted(projects))

            # Set current project if available
            current_project = self._current_context.get('project', '')
            if current_project and current_project in projects:
                self.project_combo.setCurrentText(current_project)
                self._current_context['project'] = current_project
            elif projects:
                self.project_combo.setCurrentText(projects[0])
                self._current_context['project'] = projects[0]

            self._updating_ui = False

            # Trigger episode loading for the selected project
            if self._current_context.get('project'):
                self.load_episodes()

        except Exception as e:
            self.logger.error(f"Error loading projects: {e}")

    def update_ui_from_context(self):
        """Update UI controls from current context."""
        if self._updating_ui:
            return

        try:
            self._updating_ui = True

            # Update combo boxes
            context = self._current_context

            if 'project' in context:
                self.project_combo.setCurrentText(context['project'])

            if 'ep' in context:
                self.episode_combo.setCurrentText(context['ep'])

            if 'seq' in context:
                self.sequence_combo.setCurrentText(context['seq'])

            if 'shot' in context:
                self.shot_combo.setCurrentText(context['shot'])

            # Update path labels
            self.update_path_labels()

            # Update variables display
            self.update_variables_display()

            # ✅ PHASE 3: Update context details display
            self._update_context_details()

            # Update file lists
            self.update_file_lists()

        except Exception as e:
            self.logger.error(f"Error updating UI from context: {e}")
        finally:
            self._updating_ui = False

    def on_project_changed(self, project):
        """Handle project selection change."""
        if self._updating_ui or not project:
            return

        try:
            self._current_context['project'] = project

            # Clear dependent combos
            self.episode_combo.clear()
            self.sequence_combo.clear()
            self.shot_combo.clear()

            # Load episodes for this project
            self.load_episodes()

            # Update context
            self.update_context()

        except Exception as e:
            self.logger.error(f"Error handling project change: {e}")

    def on_episode_changed(self, episode):
        """Handle episode selection change."""
        if self._updating_ui or not episode:
            return

        try:
            self._current_context['ep'] = episode

            # Clear dependent combos
            self.sequence_combo.clear()
            self.shot_combo.clear()

            # Load sequences for this episode
            self.load_sequences()

            # Update context
            self.update_context()

        except Exception as e:
            self.logger.error(f"Error handling episode change: {e}")

    def on_sequence_changed(self, sequence):
        """Handle sequence selection change."""
        if self._updating_ui or not sequence:
            return

        try:
            self._current_context['seq'] = sequence

            # Clear dependent combos
            self.shot_combo.clear()

            # Load shots for this sequence
            self.load_shots()

            # Update context
            self.update_context()

        except Exception as e:
            self.logger.error(f"Error handling sequence change: {e}")

    def on_shot_changed(self, shot):
        """Handle shot selection change."""
        if self._updating_ui or not shot:
            return

        try:
            self._current_context['shot'] = shot

            # Update context and file lists
            self.update_context()
            self.update_file_lists()

        except Exception as e:
            self.logger.error(f"Error handling shot change: {e}")



    def load_episodes(self):
        """Load episodes for current project."""
        try:
            project = self._current_context.get('project')
            if not project:
                self.logger.debug("No project selected, skipping episode loading")
                return

            roots = self.variable_manager.config_manager.get("roots", {})
            proj_root = roots.get("PROJ_ROOT", "")

            self.logger.debug(f"Loading episodes for project: {project}, proj_root: {proj_root}")

            # Check if project directory exists (PRD structure: V:/SWA/all/scene/)
            scene_dir = os.path.join(proj_root, project, "all", "scene")
            self.logger.debug(f"Checking scene directory: {scene_dir}")

            if not os.path.exists(scene_dir):
                self.logger.warning(f"Scene directory not found: {scene_dir}")
                self._updating_ui = True
                self.episode_combo.clear()
                self.episode_combo.addItem(f"No episodes found (missing: {scene_dir})")
                self.episode_combo.setEnabled(False)
                self._updating_ui = False
                self.status_label.setText(f"Directory not found: {scene_dir}")
                return

            episodes = self.scanner.scan_episodes(proj_root, project)
            self.logger.debug(f"Found episodes: {episodes}")

            self._updating_ui = True
            if episodes:
                self.episode_combo.addItems(episodes)
                self.episode_combo.setCurrentText(episodes[0])
                self._current_context['ep'] = episodes[0]
                self.episode_combo.setEnabled(True)
            else:
                self.episode_combo.addItem("No episodes found")
                self.episode_combo.setEnabled(False)
                self.status_label.setText(f"No episodes found in {scene_dir}")
            self._updating_ui = False

        except Exception as e:
            self.logger.error(f"Error loading episodes: {e}")
            self._updating_ui = True
            self.episode_combo.addItem(f"Error: {str(e)}")
            self.episode_combo.setEnabled(False)
            self._updating_ui = False

    def load_sequences(self):
        """Load sequences for current episode."""
        try:
            project = self._current_context.get('project')
            episode = self._current_context.get('ep')
            if not project or not episode:
                return

            roots = self.variable_manager.config_manager.get("roots", {})
            proj_root = roots.get("PROJ_ROOT", "")

            sequences = self.scanner.scan_sequences(proj_root, project, episode)

            self._updating_ui = True
            if sequences:
                self.sequence_combo.addItems(sequences)
                self.sequence_combo.setCurrentText(sequences[0])
                self._current_context['seq'] = sequences[0]
                self.sequence_combo.setEnabled(True)
            else:
                self.sequence_combo.addItem(f"No sequences found in {episode}")
                self.sequence_combo.setEnabled(False)
            self._updating_ui = False

        except Exception as e:
            self.logger.error(f"Error loading sequences: {e}")
            self._updating_ui = True
            self.sequence_combo.addItem(f"Error: {str(e)}")
            self.sequence_combo.setEnabled(False)
            self._updating_ui = False

    def load_shots(self):
        """Load shots for current sequence."""
        try:
            project = self._current_context.get('project')
            episode = self._current_context.get('ep')
            sequence = self._current_context.get('seq')
            if not project or not episode or not sequence:
                return

            roots = self.variable_manager.config_manager.get("roots", {})
            proj_root = roots.get("PROJ_ROOT", "")

            shots = self.scanner.scan_shots(proj_root, project, episode, sequence)

            self._updating_ui = True
            self.shot_combo.addItems(shots)
            if shots:
                self.shot_combo.setCurrentText(shots[0])
                self._current_context['shot'] = shots[0]
            self._updating_ui = False

        except Exception as e:
            self.logger.error(f"Error loading shots: {e}")



    def update_context(self):
        """Update context and refresh dependent UI elements."""
        try:
            # ❌ REMOVED: Browser should NOT write to root knobs!
            # Only Multishot Manager should set context variables
            # Browser is for browsing only, not for setting shot context
            # context_vars = {k: v for k, v in self._current_context.items() if v}
            # self.variable_manager.set_context_variables(context_vars)

            # Update path labels
            self.update_path_labels()

            # Update variables display
            self.update_variables_display()

            # Update file lists
            self.update_file_lists()

            # Emit signal
            self.context_changed.emit(self._current_context.copy())

            # Update status
            context_str = " / ".join([v for v in self._current_context.values() if v])
            self.status_label.setText(f"Context: {context_str}" if context_str else "Ready")

        except Exception as e:
            self.logger.error(f"Error updating context: {e}")

    def update_path_labels(self):
        """Update path template labels."""
        try:
            # Get all variables
            variables = self.variable_manager.get_all_variables()

            # Update Nuke files path
            nuke_path = self.path_resolver.get_nuke_file_path(variables)
            self.nuke_path_label.setText(f"Nuke Files: {nuke_path}")

            # Update renders path
            renders_path = self.path_resolver.get_render_path(variables)
            self.renders_path_label.setText(f"Renders: {renders_path}")

        except Exception as e:
            self.logger.error(f"Error updating path labels: {e}")

    def update_variables_display(self):
        """Update variables display text."""
        try:
            variables = self.variable_manager.get_all_variables()

            # Format variables for display
            var_text = ""
            for key, value in sorted(variables.items()):
                var_text += f"{key}: {value}\n"

            self.variables_text.setPlainText(var_text)

        except Exception as e:
            self.logger.error(f"Error updating variables display: {e}")

    def update_file_lists(self):
        """Update all file lists based on current context."""
        try:
            # Check if we have enough context (project, ep, seq, shot)
            required_context = ['project', 'ep', 'seq', 'shot']
            if not all(self._current_context.get(key) for key in required_context):
                # Clear all lists if context incomplete
                for tab_index in range(self.file_tabs.count()):
                    widget = self.file_tabs.widget(tab_index)
                    # Clear file list widgets (Nuke Files tab)
                    if hasattr(widget, 'file_list'):
                        widget.file_list.clear()
                    # Clear tree widgets (Renders, Geometry tabs)
                    if hasattr(widget, 'tree_view'):
                        widget.tree_view.clear()
                return

            # Get variables for path resolution
            variables = self.variable_manager.get_all_variables()

            # Update each tab
            self.update_nuke_files_tab(variables)
            self.update_renders_tab(variables)
            self.update_geometry_tab(variables)

        except Exception as e:
            self.logger.error(f"Error updating file lists: {e}")

    def update_nuke_files_tab(self, variables):
        """Update Nuke files tab with all nuke files."""
        try:
            widget = self.nuke_files_widget
            widget.file_list.clear()

            # Get current context
            context = self._current_context
            if not all(k in context for k in ['project', 'ep', 'seq', 'shot']):
                self.logger.debug("Incomplete context for nuke files tab")
                return

            # Get project root from script-embedded variables only (PRD 4.1 compliance)
            all_vars = self.variable_manager.get_all_variables()
            proj_root = all_vars.get("PROJ_ROOT", "")

            if not proj_root:
                self.logger.debug("No PROJ_ROOT found for nuke files tab")
                return

            # Hardcode nuke path - always comp department
            nuke_path = os.path.join(proj_root, context['project'], "all", "scene",
                                   context['ep'], context['seq'], context['shot'],
                                   "comp", "version")

            self.logger.debug(f"Hardcoded nuke path: {nuke_path}")

            if os.path.exists(nuke_path):
                # Scan for .nk files directly in the /version/ directory (no version subdirectories)
                all_nuke_files = []
                for filename in os.listdir(nuke_path):
                    if filename.lower().endswith('.nk'):
                        filepath = os.path.join(nuke_path, filename)
                        if os.path.isfile(filepath):
                            # Extract version from filename like "Ep01_sq0010_SH0020_comp_v001.nk"
                            parts = filename.replace('.nk', '').split('_')
                            version = parts[-1] if len(parts) >= 5 and parts[-1].startswith('v') else 'unknown'

                            file_info = {
                                'filename': filename,
                                'filepath': filepath,
                                'version': version,
                                'size': os.path.getsize(filepath),
                                'modified': os.path.getmtime(filepath)
                            }
                            all_nuke_files.append(file_info)

                # Sort by version (newest first) then by filename
                all_nuke_files.sort(key=lambda x: (x['version'], x['filename']), reverse=True)

                # Add files to list
                for nuke_file in all_nuke_files:
                    display_name = f"{nuke_file['version']} - {nuke_file['filename']}"
                    item = QtWidgets.QListWidgetItem(display_name)
                    item.setData(QtCore.Qt.UserRole, nuke_file)
                    widget.file_list.addItem(item)

                self.logger.debug(f"Found {len(all_nuke_files)} nuke files in {nuke_path}")
            else:
                self.logger.debug(f"Nuke path does not exist: {nuke_path}")
                # Add a helpful message to the user
                item = QtWidgets.QListWidgetItem(f"No nuke files found")
                item.setData(QtCore.Qt.UserRole, {'info': f'Expected path: {nuke_path}'})
                widget.file_list.addItem(item)

                item2 = QtWidgets.QListWidgetItem(f"Expected path: {nuke_path}")
                item2.setData(QtCore.Qt.UserRole, {'info': 'Create directory structure or check configuration'})
                widget.file_list.addItem(item2)

        except Exception as e:
            self.logger.error(f"Error updating Nuke files tab: {e}")

    def update_renders_tab(self, variables):
        """Update renders tab with department > version > render layer > files structure."""
        try:
            widget = self.renders_widget
            tree_view = widget.tree_view
            tree_view.clear()

            # Get current context
            context = self._current_context
            if not all(k in context for k in ['project', 'ep', 'seq', 'shot']):
                self.logger.debug("Incomplete context for renders tab")
                return

            # Get project root for scanning
            roots = self.variable_manager.config_manager.get("roots", {})
            proj_root = roots.get("PROJ_ROOT", "")
            img_root = roots.get("IMG_ROOT", "")

            if not proj_root or not img_root:
                self.logger.debug(f"Missing roots - PROJ_ROOT: {proj_root}, IMG_ROOT: {img_root}")
                return

            self.logger.debug(f"Scanning renders for {context['project']}/{context['ep']}/{context['seq']}/{context['shot']}")

            # Try to scan all department assets
            try:
                all_assets = self.scanner.scan_all_department_assets(
                    proj_root, context['project'], context['ep'], context['seq'], context['shot']
                )
                self.logger.debug(f"Found department assets: {list(all_assets.keys())}")
            except Exception as e:
                self.logger.error(f"Error scanning department assets: {e}")
                all_assets = {}

            # Try to scan comp renders
            try:
                comp_renders = self.scanner.scan_comp_renders(
                    proj_root, context['project'], context['ep'], context['seq'], context['shot']
                )
                self.logger.debug(f"Found comp renders: {len(comp_renders) if comp_renders else 0}")
            except Exception as e:
                self.logger.error(f"Error scanning comp renders: {e}")
                comp_renders = []

            # Fallback: If no assets found, try basic directory scanning
            if not all_assets and not comp_renders:
                self.logger.debug("No assets found via scanner methods, trying basic directory scan")

                # Try to find any render directories manually
                base_path = os.path.join(img_root, context['project'], "all", "scene",
                                       context['ep'], context['seq'], context['shot'])

                if os.path.exists(base_path):
                    self.logger.debug(f"Base path exists: {base_path}")

                    # Look for department directories
                    for item in os.listdir(base_path):
                        dept_path = os.path.join(base_path, item)
                        if os.path.isdir(dept_path):
                            self.logger.debug(f"Found department: {item}")

                            # Add as simple department item
                            dept_item = QtWidgets.QTreeWidgetItem(tree_view, [item])
                            dept_item.setExpanded(True)

                            # Look for publish directory
                            publish_path = os.path.join(dept_path, "publish")
                            if os.path.exists(publish_path):
                                # Add a placeholder item
                                placeholder_item = QtWidgets.QTreeWidgetItem(dept_item, ["(scanning...)"])
                else:
                    self.logger.debug(f"Base path does not exist: {base_path}")
                    # Add a debug item to show the expected path
                    debug_item = QtWidgets.QTreeWidgetItem(tree_view, [f"Expected path: {base_path}"])
                    debug_item.setExpanded(True)

            # Add comp renders first
            if comp_renders:
                comp_item = QtWidgets.QTreeWidgetItem(tree_view, ["comp"])
                comp_item.setExpanded(True)

                # Group comp renders by version (they don't have render layers)
                comp_versions = self._group_assets_by_version(comp_renders)
                for version, files in comp_versions.items():
                    version_item = QtWidgets.QTreeWidgetItem(comp_item, [version])
                    version_item.setExpanded(True)

                    for file_path in files:
                        file_item = QtWidgets.QTreeWidgetItem(version_item, [os.path.basename(file_path)])
                        file_item.setData(0, QtCore.Qt.UserRole, {
                            'department': 'comp',
                            'asset_path': file_path,
                            'asset_type': 'render'
                        })

                        # Apply version control status
                        self._apply_version_status_to_item(file_item, file_path)

            # Add department renders
            for department, dept_assets in all_assets.items():
                if dept_assets.get('renders'):
                    dept_item = QtWidgets.QTreeWidgetItem(tree_view, [department])
                    dept_item.setExpanded(True)

                    # Group by version > render layer > files
                    grouped_renders = self._group_renders_hierarchically(dept_assets['renders'])

                    for version, layers in grouped_renders.items():
                        version_item = QtWidgets.QTreeWidgetItem(dept_item, [version])
                        version_item.setExpanded(True)

                        for layer, files in layers.items():
                            layer_item = QtWidgets.QTreeWidgetItem(version_item, [layer])
                            layer_item.setExpanded(True)

                            for file_path in files:
                                file_item = QtWidgets.QTreeWidgetItem(layer_item, [os.path.basename(file_path)])
                                file_item.setData(0, QtCore.Qt.UserRole, {
                                    'department': department,
                                    'asset_path': file_path,
                                    'asset_type': 'render'
                                })

                                # Apply version control status
                                self._apply_version_status_to_item(file_item, file_path)

            if not comp_renders and not all_assets:
                self.logger.debug("No renders found")
                # Add a helpful message to the user
                info_item = QtWidgets.QTreeWidgetItem(tree_view, ["No renders found"])
                info_item.setExpanded(True)
                help_item = QtWidgets.QTreeWidgetItem(info_item, [f"Expected path: {img_root}/{context['project']}/all/scene/{context['ep']}/{context['seq']}/{context['shot']}/[department]/publish/"])
                help_item2 = QtWidgets.QTreeWidgetItem(info_item, ["Create directory structure or check configuration"])

        except Exception as e:
            self.logger.error(f"Error updating renders tab: {e}")
            import traceback
            traceback.print_exc()

    def _group_assets_by_version(self, assets):
        """Group assets by version (for comp renders without layers)."""
        grouped = {}
        for asset_path in assets:
            # Extract version from path like 'v001/file.1001-1240.exr'
            parts = asset_path.split('/')
            if len(parts) >= 2:
                version = parts[0]  # v001, v002, etc.
                if version not in grouped:
                    grouped[version] = []
                grouped[version].append(asset_path)
            else:
                # No version structure, put in 'unknown'
                if 'unknown' not in grouped:
                    grouped['unknown'] = []
                grouped['unknown'].append(asset_path)
        return grouped

    def _group_renders_hierarchically(self, renders):
        """Group renders by version > render layer > files."""
        grouped = {}
        for render_path in renders:
            # Parse path like 'v001/MASTER_ATMOS_A/MASTER_ATMOS_A.1001-1240.exr'
            parts = render_path.split('/')
            if len(parts) >= 3:
                version = parts[0]  # v001, v002, etc.
                layer = parts[1]    # MASTER_ATMOS_A, etc.

                if version not in grouped:
                    grouped[version] = {}
                if layer not in grouped[version]:
                    grouped[version][layer] = []
                grouped[version][layer].append(render_path)
            elif len(parts) == 2:
                # No layer, just version/file
                version = parts[0]
                if version not in grouped:
                    grouped[version] = {}
                if 'default' not in grouped[version]:
                    grouped[version]['default'] = []
                grouped[version]['default'].append(render_path)
            else:
                # No structure, put in unknown
                if 'unknown' not in grouped:
                    grouped['unknown'] = {}
                if 'default' not in grouped['unknown']:
                    grouped['unknown']['default'] = []
                grouped['unknown']['default'].append(render_path)
        return grouped

    def update_geometry_tab(self, variables):
        """Update geometry tab with department > version > files structure (includes cameras)."""
        try:
            widget = self.geometry_widget
            tree_view = widget.tree_view
            tree_view.clear()

            # Get current context
            context = self._current_context
            if not all(k in context for k in ['project', 'ep', 'seq', 'shot']):
                self.logger.debug("Incomplete context for geometry tab")
                return

            # Get project root for scanning
            roots = self.variable_manager.config_manager.get("roots", {})
            proj_root = roots.get("PROJ_ROOT", "")

            if not proj_root:
                self.logger.debug("No PROJ_ROOT found for geometry tab")
                return

            self.logger.debug(f"Scanning geometry for {context['project']}/{context['ep']}/{context['seq']}/{context['shot']}")

            # Scan all department assets
            try:
                all_assets = self.scanner.scan_all_department_assets(
                    proj_root, context['project'], context['ep'], context['seq'], context['shot']
                )
                self.logger.debug(f"Geometry scan found departments: {list(all_assets.keys())}")
            except Exception as e:
                self.logger.error(f"Error scanning geometry assets: {e}")
                all_assets = {}

            # Add department geometry and cameras
            for department, dept_assets in all_assets.items():
                # Combine geometry and camera assets
                all_geo_assets = dept_assets.get('geometry', []) + dept_assets.get('camera', [])

                if all_geo_assets:
                    dept_item = QtWidgets.QTreeWidgetItem(tree_view, [department])
                    dept_item.setExpanded(True)

                    # Group by version
                    grouped_assets = self._group_assets_by_version(all_geo_assets)

                    for version, files in grouped_assets.items():
                        version_item = QtWidgets.QTreeWidgetItem(dept_item, [version])
                        version_item.setExpanded(True)

                        for file_path in files:
                            file_item = QtWidgets.QTreeWidgetItem(version_item, [os.path.basename(file_path)])
                            # Determine asset type based on extension
                            asset_type = 'camera' if any(file_path.lower().endswith(ext) for ext in ['.ma', '.mb']) else 'geometry'
                            file_item.setData(0, QtCore.Qt.UserRole, {
                                'department': department,
                                'asset_path': file_path,
                                'asset_type': asset_type
                            })

                            # Apply version control status
                            self._apply_version_status_to_item(file_item, file_path)

            # Add helpful message if no geometry found
            if not any(all_geo_assets for dept_assets in all_assets.values()
                      for all_geo_assets in [dept_assets.get('geometry', []) + dept_assets.get('camera', [])]):
                info_item = QtWidgets.QTreeWidgetItem(tree_view, ["No geometry/camera files found"])
                info_item.setExpanded(True)
                help_item = QtWidgets.QTreeWidgetItem(info_item, [f"Expected path: {proj_root}/{context['project']}/all/scene/{context['ep']}/{context['seq']}/{context['shot']}/[department]/publish/"])
                help_item2 = QtWidgets.QTreeWidgetItem(info_item, ["Create directory structure or check configuration"])

        except Exception as e:
            self.logger.error(f"Error updating geometry tab: {e}")
            import traceback
            traceback.print_exc()





    def on_tab_changed(self, index):
        """Handle tab change."""
        try:
            # Update file details when tab changes
            self.update_file_details()

        except Exception as e:
            self.logger.error(f"Error handling tab change: {e}")

    def on_file_selection_changed(self):
        """Handle file selection change."""
        try:
            # Update file details
            self.update_file_details()

            # Enable/disable open button
            current_widget = self.file_tabs.currentWidget()
            if current_widget and current_widget.file_list.currentItem():
                self.open_btn.setEnabled(True)
            else:
                self.open_btn.setEnabled(False)

        except Exception as e:
            self.logger.error(f"Error handling file selection change: {e}")

    def update_file_details(self):
        """Update file details display."""
        try:
            current_widget = self.file_tabs.currentWidget()
            if not current_widget:
                self.file_details_text.clear()
                return

            current_item = current_widget.file_list.currentItem()
            if not current_item:
                self.file_details_text.clear()
                return

            file_info = current_item.data(QtCore.Qt.UserRole)
            if not file_info:
                self.file_details_text.clear()
                return

            # Format file details
            details = f"File: {file_info['filename']}\n"
            details += f"Path: {file_info['filepath']}\n"

            if 'size' in file_info:
                size_mb = file_info['size'] / (1024 * 1024)
                details += f"Size: {size_mb:.2f} MB\n"

            if 'modified' in file_info:
                import time
                mod_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(file_info['modified']))
                details += f"Modified: {mod_time}\n"

            if 'context' in file_info and file_info['context']:
                details += f"\nContext:\n"
                for key, value in file_info['context'].items():
                    details += f"  {key}: {value}\n"

            self.file_details_text.setPlainText(details)

        except Exception as e:
            self.logger.error(f"Error updating file details: {e}")

    def refresh_all(self):
        """Refresh all data and UI."""
        try:
            self.status_label.setText("Refreshing...")

            # Clear scanner cache
            self.scanner.clear_cache()

            # Check if current script has context that should update our variables
            context_updated = self._check_current_script_context()

            # Refresh context from variables (if not already updated from script)
            if not context_updated:
                self.refresh_context_from_variables()

            # Refresh root variables to ensure they're in script knobs
            self.variable_manager.refresh_root_variables()

            # Reload projects
            self.load_projects()

            # Update UI
            self.update_ui_from_context()

        except Exception as e:
            self.logger.error(f"Error refreshing all: {e}")
            self.show_error("Refresh Error", f"Failed to refresh: {e}")

    def save_increment_version(self, version_type='major'):
        """Save current script as next version increment.

        Args:
            version_type: 'major' for v001->v002, 'sub' for v001->v001_001
        """
        try:
            # Get current context
            context = self._current_context
            if not all(k in context for k in ['project', 'ep', 'seq', 'shot']):
                nuke.message("Error: Incomplete context. Please set project, episode, sequence, and shot.")
                return

            # Get project root from script-embedded variables only (PRD 4.1 compliance)
            all_vars = self.variable_manager.get_all_variables()
            proj_root = all_vars.get("PROJ_ROOT", "")

            if not proj_root:
                nuke.message("Error: No PROJ_ROOT found in configuration.")
                return

            # Hardcode nuke path - always comp department
            nuke_path = os.path.join(proj_root, context['project'], "all", "scene",
                                   context['ep'], context['seq'], context['shot'],
                                   "comp", "version")

            if not os.path.exists(nuke_path):
                os.makedirs(nuke_path, exist_ok=True)

            # Get next version based on type - scan existing .nk files directly in version directory
            existing_files = []
            if os.path.exists(nuke_path):
                for filename in os.listdir(nuke_path):
                    if filename.lower().endswith('.nk'):
                        existing_files.append(filename)

            # Extract version numbers from existing files
            versions = []
            for filename in existing_files:
                # Extract version from filename like "Ep01_sq0010_SH0020_comp_v001.nk"
                parts = filename.replace('.nk', '').split('_')
                if len(parts) >= 5 and parts[-1].startswith('v'):
                    versions.append(parts[-1])  # v001, v002, etc.

            # Get next version
            if versions:
                latest = self.scanner.get_latest_version(versions)
                if latest:
                    if version_type == 'sub':
                        next_version = self.context_detector.create_sub_version(latest)
                    else:
                        next_version = self.context_detector.increment_version(latest)
                else:
                    next_version = "v001"
            else:
                next_version = "v001"

            # Generate filename and save directly in /version/ directory (no version subdirectory)
            context = self._current_context
            if all(k in context for k in ['ep', 'seq', 'shot']):
                filename = f"{context['ep']}_{context['seq']}_{context['shot']}_comp_{next_version}.nk"
                filepath = os.path.join(nuke_path, filename)  # Save directly in /version/ directory

                # Try to save in Nuke if available
                try:
                    import nuke
                    nuke.scriptSaveAs(filepath)
                    self.show_info("Version Saved", f"Saved as {next_version}: {filename}")

                    # Refresh file lists
                    self.update_file_lists()

                except ImportError:
                    self.show_error("Nuke Not Available", "Cannot save - not running in Nuke environment")
            else:
                self.show_error("Context Error", "Incomplete context - need episode, sequence, and shot")

        except Exception as e:
            self.logger.error(f"Error saving increment version: {e}")
            self.show_error("Save Error", f"Failed to save increment version: {e}")

    def on_tree_selection_changed(self, widget):
        """Handle tree selection changes."""
        try:
            selected_items = widget.tree_view.selectedItems()

            # Enable/disable action buttons based on selection
            if hasattr(widget, 'create_read_btn'):
                widget.create_read_btn.setEnabled(len(selected_items) > 0)
            if hasattr(widget, 'create_readgeo_btn'):
                widget.create_readgeo_btn.setEnabled(len(selected_items) > 0)

        except Exception as e:
            self.logger.error(f"Error handling tree selection change: {e}")

    def create_read_nodes_from_selection(self, widget):
        """Create MultishotRead nodes from selected render assets."""
        try:
            selected_items = widget.tree_view.selectedItems()
            if not selected_items:
                return

            # Check if running in Nuke
            try:
                import nuke
            except ImportError:
                self.show_error("Nuke Not Available", "Cannot create nodes - not running in Nuke environment")
                return

            created_nodes = []

            for item in selected_items:
                # Skip department parent items
                asset_data = item.data(0, QtCore.Qt.UserRole)
                if not asset_data or asset_data.get('asset_type') != 'render':
                    continue

                department = asset_data['department']
                asset_path = asset_data['asset_path']

                # Create MultishotRead node with custom knobs
                try:
                    # Import MultishotRead class and _node_instances
                    from ..nodes.read_node import MultishotRead
                    import multishot.nodes.read_node as read_node_module

                    # Create MultishotRead instance
                    multishot_read = MultishotRead(variable_manager=self.variable_manager)
                    read_node = multishot_read.create_node()

                    # ✅ Parse asset path to extract layer and component
                    # Format: v005/MASTER_CHAR_A/MASTER_CHAR_A.Cryptomatte_node.1012.exr
                    # Layer: MASTER_CHAR_A (directory name)
                    # Component: Cryptomatte_node (optional sub-component)

                    path_parts = asset_path.split('/')

                    # Extract layer from directory (second-to-last part)
                    if len(path_parts) >= 3:
                        layer_name = path_parts[-2]  # "MASTER_CHAR_A"
                    else:
                        # Fallback: extract from filename
                        asset_filename = os.path.splitext(os.path.basename(asset_path))[0]
                        clean_filename = re.sub(r'\.\d{4}(-\d{4})?$', '', asset_filename)
                        layer_name = clean_filename.split('.')[0]

                    # Extract component from filename (if exists)
                    # Filename format: {layer}.{component}.{frame}.{ext}
                    # Examples:
                    #   MASTER_CHAR_A.1012.exr → component = None
                    #   MASTER_CHAR_A.Cryptomatte_node.1012.exr → component = "Cryptomatte_node"
                    asset_filename = os.path.splitext(os.path.basename(asset_path))[0]  # "MASTER_CHAR_A.Cryptomatte_node.1012"

                    # Remove frame numbers
                    clean_filename = re.sub(r'\.\d{4}(-\d{4})?$', '', asset_filename)  # "MASTER_CHAR_A.Cryptomatte_node"

                    # Split by dot to get parts
                    filename_parts = clean_filename.split('.')

                    # If more than one part, second part onwards is the component
                    if len(filename_parts) > 1:
                        component = '.'.join(filename_parts[1:])  # "Cryptomatte_node"
                    else:
                        component = None

                    self.logger.info(f"Parsed: layer='{layer_name}', component='{component}' from '{asset_path}'")

                    # ✅ Build node name
                    # Format: MultishotRead_{department}_{layer}_{component}
                    safe_layer_name = re.sub(r'[^a-zA-Z0-9_]', '_', layer_name)
                    if component:
                        safe_component = re.sub(r'[^a-zA-Z0-9_]', '_', component)
                        new_node_name = f"MultishotRead_{department}_{safe_layer_name}_{safe_component}"
                    else:
                        new_node_name = f"MultishotRead_{department}_{safe_layer_name}"

                    # Set name on node
                    read_node.setName(new_node_name)
                    self.logger.info(f"Created node: {new_node_name}")

                    # ✅ CRITICAL FIX: Re-register instance with correct name!
                    if 'MultishotRead' in read_node_module._node_instances:
                        del read_node_module._node_instances['MultishotRead']
                    read_node_module._node_instances[new_node_name] = multishot_read
                    self.logger.info(f"Registered node instance: {new_node_name}")

                    # Set department
                    if read_node.knob('department'):
                        read_node['department'].setValue(department)
                        self.logger.info(f"Set department to: {department}")

                    # Set layer (directory name only, not component)
                    if read_node.knob('layer'):
                        read_node['layer'].setValue(layer_name)
                        self.logger.info(f"Set layer to: {layer_name}")

                    # ✅ Build file pattern (relative to version directory)
                    # Format: {layer}/{layer}.{component}.%04d.{ext}
                    # Examples:
                    #   MASTER_CHAR_A/MASTER_CHAR_A.%04d.exr
                    #   MASTER_CHAR_A/MASTER_CHAR_A.Cryptomatte_node.%04d.exr

                    if len(path_parts) >= 3:
                        # Get filename without frame numbers
                        filename_base = clean_filename  # "MASTER_CHAR_A.Cryptomatte_node"
                        file_ext = os.path.splitext(asset_path)[-1]  # ".exr"

                        # Build pattern: {layer}/{filename_base}.%04d.{ext}
                        file_pattern = f"{layer_name}/{filename_base}.%04d{file_ext}"

                        # Store in knob
                        if read_node.knob('file_pattern'):
                            read_node['file_pattern'].setValue(file_pattern)
                            self.logger.info(f"Set file_pattern to: {file_pattern}")
                        else:
                            self.logger.info(f"Calculated file_pattern: {file_pattern}")

                    # ✅ Extract version from asset path
                    version = self._extract_version_from_path(asset_path)
                    if version and read_node.knob('shot_version'):
                        read_node['shot_version'].setValue(version)
                        self.logger.info(f"Set shot_version to: {version}")

                        # Also store in shot_versions for current shot
                        shot_key = f"{self._current_context.get('project', '')}_{self._current_context.get('ep', '')}_{self._current_context.get('seq', '')}_{self._current_context.get('shot', '')}"
                        if shot_key and shot_key != '___':
                            multishot_read.set_version_for_shot(version, shot_key)
                            self.logger.info(f"Stored version {version} for shot {shot_key}")

                    # ✅ Link frame range to root knobs using expressions
                    # This makes the node automatically update when switching shots
                    if read_node.knob('first'):
                        read_node['first'].setExpression('[value root.first_frame]')
                        self.logger.info("Linked first frame to root.first_frame")

                    if read_node.knob('last'):
                        read_node['last'].setExpression('[value root.last_frame]')
                        self.logger.info("Linked last frame to root.last_frame")

                    # Set missing frames to "nearest frame"
                    if read_node.knob('on_error'):
                        read_node['on_error'].setValue('nearest frame')
                        self.logger.info("Set missing frames to 'nearest frame'")

                    # Build expression path AFTER setting all properties
                    multishot_read.build_expression_path()
                    self.logger.info(f"Built expression path with layer: {clean_filename}")

                except Exception as e:
                    self.logger.error(f"Error creating MultishotRead node: {e}")
                    import traceback
                    traceback.print_exc()
                    continue

                created_nodes.append(read_node.name())

            if created_nodes:
                self.show_info("Read Nodes Created", f"Created {len(created_nodes)} Read nodes:\n" + "\n".join(created_nodes))
            else:
                self.show_info("No Nodes Created", "No valid render assets selected")

        except Exception as e:
            self.logger.error(f"Error creating Read nodes: {e}")
            self.show_error("Read Node Error", f"Failed to create Read nodes: {e}")

    def create_readgeo_nodes_from_selection(self, widget):
        """Create ReadGeo nodes from selected geometry assets."""
        try:
            selected_items = widget.tree_view.selectedItems()
            if not selected_items:
                return

            # Check if running in Nuke
            try:
                import nuke
            except ImportError:
                self.show_error("Nuke Not Available", "Cannot create nodes - not running in Nuke environment")
                return

            created_nodes = []

            for item in selected_items:
                # Skip department parent items
                asset_data = item.data(0, QtCore.Qt.UserRole)
                if not asset_data or asset_data.get('asset_type') not in ['geometry', 'camera']:
                    continue

                department = asset_data['department']
                asset_path = asset_data['asset_path']
                asset_type = asset_data['asset_type']

                # Generate node name from asset filename
                asset_filename = os.path.splitext(os.path.basename(asset_path))[0]
                clean_filename = re.sub(r'\.\d{4}-\d{4}$', '', asset_filename)

                # Create appropriate node based on asset type
                if asset_type == 'camera':
                    # Create Camera node for camera files
                    geo_node = nuke.createNode('Camera2')
                    geo_node.setName(f"Camera_{department}_{clean_filename}")

                    # Build expression-based file path using PROJ_ROOT (geometry uses project root)
                    expr_path = self._build_geometry_expression_path(asset_path, department)
                    geo_node['file'].fromUserText(expr_path)
                else:
                    # Create ReadGeo node for geometry files
                    geo_node = nuke.createNode('ReadGeo2')
                    geo_node.setName(f"ReadGeo_{department}_{clean_filename}")

                    # Build expression-based file path using PROJ_ROOT (geometry uses project root)
                    expr_path = self._build_geometry_expression_path(asset_path, department)
                    geo_node['file'].fromUserText(expr_path)

                created_nodes.append(geo_node.name())

            if created_nodes:
                self.show_info("Geometry Nodes Created", f"Created {len(created_nodes)} geometry nodes:\n" + "\n".join(created_nodes))
            else:
                self.show_info("No Nodes Created", "No valid geometry/camera assets selected")

        except Exception as e:
            self.logger.error(f"Error creating ReadGeo nodes: {e}")
            self.show_error("ReadGeo Node Error", f"Failed to create ReadGeo nodes: {e}")

    def _build_asset_file_path(self, department: str, asset_path: str, asset_type: str) -> str:
        """Build full file path for an asset."""
        try:
            # Get current context
            context = self._current_context
            if not all(k in context for k in ['project', 'ep', 'seq', 'shot']):
                return ""

            # Get path resolver
            variables = self.variable_manager.get_all_variables()

            if asset_type == 'render':
                if department == 'comp':
                    # Comp renders
                    base_path = self.path_resolver.get_comp_render_path(variables, versioned=False)
                else:
                    # Department renders
                    base_path = self.path_resolver.get_department_render_path(variables, department, versioned=False)
            else:
                # Geometry/camera assets
                base_path = self.path_resolver.get_geometry_path(variables, department, versioned=False)

            # Combine with asset path
            full_path = os.path.join(base_path, asset_path).replace('\\', '/')
            return full_path

        except Exception as e:
            self.logger.error(f"Error building asset file path: {e}")
            return ""

    def _build_render_expression_path(self, asset_path: str, department: str, use_img_root: bool = True) -> str:
        """
        Build expression-based file path for render assets using script-embedded variables.

        Args:
            asset_path: Relative asset path (e.g., "v001/layer.1001-1240.exr")
            department: Department name (e.g., "comp", "lighting")
            use_img_root: Whether to use IMG_ROOT (True) or PROJ_ROOT (False)

        Returns:
            Expression path using [value root.variable] syntax
        """
        try:
            # Choose root variable
            root_var = "IMG_ROOT" if use_img_root else "PROJ_ROOT"

            # Build expression path using script-embedded variables
            if department == 'comp':
                # Comp renders: {IMG_ROOT}{project}/all/scene/{ep}/{seq}/{shot}/comp/version/{asset_path}
                expr_path = f"[value root.{root_var}][value root.project]/all/scene/[value root.ep]/[value root.seq]/[value root.shot]/comp/version/{asset_path}"
            else:
                # Department renders: {IMG_ROOT}{project}/all/scene/{ep}/{seq}/{shot}/{department}/publish/{asset_path}
                expr_path = f"[value root.{root_var}][value root.project]/all/scene/[value root.ep]/[value root.seq]/[value root.shot]/{department}/publish/{asset_path}"

            # Convert collapsed sequence format to Nuke sequence format if needed
            if self._is_sequence_file(asset_path):
                expr_path = self._convert_expression_to_nuke_sequence(expr_path)

            self.logger.debug(f"Built render expression path: {expr_path}")
            return expr_path

        except Exception as e:
            self.logger.error(f"Error building render expression path: {e}")
            return asset_path

    def _convert_expression_to_nuke_sequence(self, expr_path: str) -> str:
        """Convert expression path with collapsed sequence to Nuke sequence format."""
        try:
            # Convert: path/file.1001-1240.exr -> path/file.%04d.exr
            match = re.search(r'(.+\.)(\d{4})-(\d{4})(\.[^.]+)$', expr_path)
            if match:
                prefix = match.group(1)
                start_frame = match.group(2)
                end_frame = match.group(3)
                suffix = match.group(4)

                # Use the padding from the original frame numbers
                padding = len(start_frame)
                nuke_expr_path = f"{prefix}%0{padding}d{suffix}"
                return nuke_expr_path

            return expr_path

        except Exception as e:
            self.logger.error(f"Error converting expression to Nuke sequence: {e}")
            return expr_path

    def _build_geometry_expression_path(self, asset_path: str, department: str) -> str:
        """
        Build expression-based file path for geometry/camera assets using script-embedded variables.

        Args:
            asset_path: Relative asset path (e.g., "v001/geometry.abc")
            department: Department name (e.g., "anim", "layout")

        Returns:
            Expression path using [value root.variable] syntax with PROJ_ROOT
        """
        try:
            # Geometry/camera assets use PROJ_ROOT
            # Path: {PROJ_ROOT}{project}/all/scene/{ep}/{seq}/{shot}/{department}/publish/{asset_path}
            expr_path = f"[value root.PROJ_ROOT][value root.project]/all/scene/[value root.ep]/[value root.seq]/[value root.shot]/{department}/publish/{asset_path}"

            self.logger.debug(f"Built geometry expression path: {expr_path}")
            return expr_path

        except Exception as e:
            self.logger.error(f"Error building geometry expression path: {e}")
            return asset_path

    def _is_sequence_file(self, asset_path: str) -> bool:
        """Check if asset path represents a sequence (contains frame range or single frame)."""
        # Check for frame range (.1001-1100.) or single frame (.1012.)
        return bool(re.search(r'\.\d{4}(-\d{4})?\.', asset_path))

    def _convert_to_nuke_sequence_path(self, collapsed_path: str) -> str:
        """Convert collapsed sequence path to Nuke sequence format."""
        try:
            # Convert: file.1001-1240.exr -> file.%04d.exr
            match = re.search(r'(.+\.)(\d{4})-(\d{4})(\.[^.]+)$', collapsed_path)
            if match:
                prefix = match.group(1)
                start_frame = match.group(2)
                end_frame = match.group(3)
                suffix = match.group(4)

                # Use the padding from the original frame numbers
                padding = len(start_frame)
                nuke_path = f"{prefix}%0{padding}d{suffix}"
                return nuke_path

            return collapsed_path

        except Exception as e:
            self.logger.error(f"Error converting to Nuke sequence path: {e}")
            return collapsed_path

    def _extract_frame_range_from_path(self, asset_path: str) -> tuple:
        """Extract first and last frame from collapsed sequence path or single frame."""
        try:
            # Try frame range first (.1001-1100.)
            match = re.search(r'\.(\d{4})-(\d{4})\.', asset_path)
            if match:
                first_frame = int(match.group(1))
                last_frame = int(match.group(2))
                self.logger.info(f"Extracted frame range: {first_frame}-{last_frame}")
                return first_frame, last_frame

            # Try single frame (.1012.)
            match = re.search(r'\.(\d{4})\.', asset_path)
            if match:
                frame = int(match.group(1))
                self.logger.info(f"Extracted single frame: {frame} (using as both first and last)")
                return frame, frame

            self.logger.warning(f"No frame number found in path: {asset_path}")
            return None, None

        except Exception as e:
            self.logger.error(f"Error extracting frame range: {e}")
            return None, None

    def _extract_version_from_path(self, asset_path: str) -> Optional[str]:
        """
        Extract version from asset path.

        Expected path format:
        .../lighting/publish/v003/MASTER_ATMOS_A/MASTER_ATMOS_A.1012.exr

        Returns:
            Version string (e.g., 'v003') or None if not found
        """
        try:
            # Normalize path
            asset_path = os.path.normpath(asset_path)
            parts = asset_path.split(os.sep)

            # Look for version pattern (v001, v002, etc.) in path parts
            for part in parts:
                if re.match(r'^v\d{3,4}$', part):
                    self.logger.info(f"Extracted version: {part}")
                    return part

            self.logger.warning(f"No version found in path: {asset_path}")
            return None

        except Exception as e:
            self.logger.error(f"Error extracting version from path: {e}")
            return None

    def show_variables_dialog(self):
        """Show variables management dialog (non-modal)."""
        try:
            from .variables_dialog import VariablesDialog

            # Check if dialog already exists and is visible
            if hasattr(self, '_variables_dialog') and self._variables_dialog.isVisible():
                # Bring existing dialog to front
                self._variables_dialog.raise_()
                self._variables_dialog.activateWindow()
                return

            # ❌ REMOVED: Browser should NOT write to root knobs!
            # The dialog should read from root knobs (set by Multishot Manager)
            # Browser's _current_context is just for UI navigation, not for setting shot context

            self.logger.info(f"Browser's _current_context (UI only): {self._current_context}")
            self.logger.info(f"Root knobs context (actual shot): {self.variable_manager.get_context_variables()}")

            # Verify the sync worked
            verify_context = self.variable_manager.get_context_variables()
            self.logger.info(f"VariableManager context after sync: {verify_context}")

            # Create new dialog with shared instances
            self._variables_dialog = VariablesDialog(
                parent=self,
                variable_manager=self.variable_manager,  # Pass browser's VariableManager
                scanner=self.scanner,  # Pass browser's DirectoryScanner
                initial_context=self._current_context.copy()  # Pass browser's current context
            )

            # Connect signals for when variables change
            self._variables_dialog.variables_changed.connect(self._on_variables_changed)

            # Show non-modal
            self._variables_dialog.show()

        except Exception as e:
            self.logger.error(f"Error showing variables dialog: {e}")
            self.show_error("Variables Error", f"Failed to show variables dialog: {e}")

    def _on_variables_changed(self):
        """Handle variables changed signal from dialog."""
        try:
            # Refresh UI after variables change
            self.refresh_context_from_variables()
            self.update_ui_from_context()
        except Exception as e:
            self.logger.error(f"Error handling variables changed: {e}")

    def open_selected_file(self):
        """Open the selected file."""
        try:
            current_widget = self.file_tabs.currentWidget()
            if not current_widget:
                return

            current_item = current_widget.file_list.currentItem()
            if not current_item:
                return

            file_info = current_item.data(QtCore.Qt.UserRole)
            if not file_info:
                return

            filepath = file_info['filepath']

            # Emit signal
            self.file_selected.emit(filepath)

            # Try to open in Nuke if available
            try:
                import nuke
                if filepath.lower().endswith('.nk'):
                    nuke.scriptOpen(filepath)

                    # Auto-detect context from opened file and update variables
                    self._update_context_from_opened_file(filepath)

                    self.show_info("File Opened", f"Opened: {os.path.basename(filepath)}")
                else:
                    self.show_info("File Selected", f"Selected: {os.path.basename(filepath)}")
            except ImportError:
                # Not in Nuke environment - still detect context for UI
                if filepath.lower().endswith('.nk'):
                    self._update_context_from_opened_file(filepath)
                self.show_info("File Selected", f"Selected: {os.path.basename(filepath)}")

        except Exception as e:
            self.logger.error(f"Error opening file: {e}")
            self.show_error("Open Error", f"Failed to open file: {e}")

    def _update_context_from_opened_file(self, filepath: str):
        """
        Update context variables based on opened file path.

        Args:
            filepath: Path to the opened file
        """
        try:
            # Detect context from file path
            detected_context = self.context_detector.detect_from_filepath(filepath)

            if detected_context:
                self.logger.info(f"Auto-detected context from opened file: {detected_context}")

                # ❌ REMOVED: Browser should NOT write to root knobs!
                # Just update browser's UI context for navigation
                self._current_context.update(detected_context)

                # Update UI to reflect new context
                self.update_ui_from_context()

                # Emit context changed signal
                self.context_changed.emit(detected_context)

                self.logger.info(f"Browser UI context updated from opened file: {detected_context}")
                self.logger.info(f"Note: Root knobs NOT changed - use Multishot Manager to set shot")
            else:
                self.logger.warning(f"Could not detect context from file path: {filepath}")

        except Exception as e:
            self.logger.error(f"Error updating context from opened file: {e}")

    def _check_current_script_context(self):
        """
        Check if current Nuke script has context that should update our variables.
        Called during refresh to detect context changes from scripts opened outside browser.
        """
        try:
            # Try to get current script context
            suggested_context = self.context_detector.suggest_context_from_current_script()

            if suggested_context:
                # Get current context variables
                current_context = self.variable_manager.get_context_variables()

                # Check if detected context is different from current
                context_changed = False
                for key, value in suggested_context.items():
                    if current_context.get(key) != value:
                        context_changed = True
                        break

                if context_changed:
                    self.logger.info(f"Detected context change from current script: {suggested_context}")

                    # ❌ REMOVED: Browser should NOT write to root knobs!
                    # Just update browser's UI context for navigation
                    self._current_context.update(suggested_context)

                    # Update UI to reflect new context
                    self.update_ui_from_context()

                    # Emit context changed signal
                    self.context_changed.emit(suggested_context)

                    self.logger.info(f"Browser UI context updated from current script: {suggested_context}")
                    self.logger.info(f"Note: Root knobs NOT changed - use Multishot Manager to set shot")
                    return True

        except Exception as e:
            self.logger.error(f"Error checking current script context: {e}")

        return False

    def _apply_version_status_to_item(self, item: QtWidgets.QTreeWidgetItem, filepath: str):
        """Apply version control status styling to a tree item."""
        try:
            # Get version info
            version_info = self.version_control.get_version_info(filepath)
            status = version_info.get('status', 'unknown')

            # Get status color
            color_hex = self.version_control.get_status_color(status)
            color = QtGui.QColor(color_hex)

            # Apply background color
            item.setBackground(0, color)

            # Add status indicator to text
            current_text = item.text(0)
            if version_info.get('approved'):
                item.setText(0, f"✅ {current_text}")
                item.setToolTip(0, f"Approved - {current_text}")
            elif status == 'latest':
                item.setText(0, f"🔵 {current_text}")
                item.setToolTip(0, f"Latest version - {current_text}")
            elif status == 'outdated':
                item.setText(0, f"🟡 {current_text}")
                item.setToolTip(0, f"Outdated version - {current_text}")
            elif status == 'missing':
                item.setText(0, f"❌ {current_text}")
                item.setToolTip(0, f"Missing file - {current_text}")
            else:
                item.setToolTip(0, current_text)

            # Store version info in item data
            current_data = item.data(0, QtCore.Qt.UserRole) or {}
            current_data['version_info'] = version_info
            item.setData(0, QtCore.Qt.UserRole, current_data)

        except Exception as e:
            self.logger.error(f"Error applying version status to item: {e}")

    def _show_context_menu(self, tree_view: QtWidgets.QTreeWidget, position):
        """Show context menu for tree view items."""
        try:
            item = tree_view.itemAt(position)
            if not item:
                return

            # Get item data
            item_data = item.data(0, QtCore.Qt.UserRole)
            if not item_data or 'asset_path' not in item_data:
                return

            filepath = item_data['asset_path']
            version_info = item_data.get('version_info', {})

            # Create context menu
            menu = QtWidgets.QMenu(tree_view)

            # Approval actions
            if version_info.get('approved'):
                unapprove_action = menu.addAction("🚫 Unapprove")
                unapprove_action.triggered.connect(lambda: self._unapprove_asset(filepath, tree_view))
            else:
                approve_action = menu.addAction("✅ Approve")
                approve_action.triggered.connect(lambda: self._approve_asset(filepath, tree_view))

            menu.addSeparator()

            # Version info action
            info_action = menu.addAction("ℹ️ Version Info")
            info_action.triggered.connect(lambda: self._show_version_info(filepath))

            # Show approval history
            history_action = menu.addAction("📋 Approval History")
            history_action.triggered.connect(lambda: self._show_approval_history(filepath))

            menu.addSeparator()

            # Batch operations (if multiple items selected)
            selected_items = tree_view.selectedItems()
            if len(selected_items) > 1:
                batch_approve_action = menu.addAction(f"✅ Batch Approve ({len(selected_items)} items)")
                batch_approve_action.triggered.connect(lambda: self._batch_approve_selected(tree_view))

                batch_unapprove_action = menu.addAction(f"🚫 Batch Unapprove ({len(selected_items)} items)")
                batch_unapprove_action.triggered.connect(lambda: self._batch_unapprove_selected(tree_view))

            # Show menu
            menu.exec_(tree_view.mapToGlobal(position))

        except Exception as e:
            self.logger.error(f"Error showing context menu: {e}")

    def _approve_asset(self, filepath: str, tree_view: QtWidgets.QTreeWidget):
        """Approve a single asset."""
        try:
            success = self.version_control.approve(filepath, approver="User", notes="Approved via browser")

            if success:
                self.show_info("Approval", f"Approved: {os.path.basename(filepath)}")
                # Refresh the tree to show updated status
                self._refresh_current_tab()
            else:
                self.show_error("Approval Error", f"Failed to approve: {os.path.basename(filepath)}")

        except Exception as e:
            self.logger.error(f"Error approving asset: {e}")
            self.show_error("Approval Error", f"Error approving asset: {e}")

    def _unapprove_asset(self, filepath: str, tree_view: QtWidgets.QTreeWidget):
        """Unapprove a single asset."""
        try:
            success = self.version_control.unapprove(filepath)

            if success:
                self.show_info("Unapproval", f"Unapproved: {os.path.basename(filepath)}")
                # Refresh the tree to show updated status
                self._refresh_current_tab()
            else:
                self.show_error("Unapproval Error", f"Failed to unapprove: {os.path.basename(filepath)}")

        except Exception as e:
            self.logger.error(f"Error unapproving asset: {e}")
            self.show_error("Unapproval Error", f"Error unapproving asset: {e}")

    def _batch_approve_selected(self, tree_view: QtWidgets.QTreeWidget):
        """Batch approve selected items."""
        try:
            selected_items = tree_view.selectedItems()
            filepaths = []

            for item in selected_items:
                item_data = item.data(0, QtCore.Qt.UserRole)
                if item_data and 'asset_path' in item_data:
                    filepaths.append(item_data['asset_path'])

            if not filepaths:
                return

            results = self.version_control.batch_approve(filepaths, approver="User", notes="Batch approved via browser")

            successful = sum(1 for success in results.values() if success)
            self.show_info("Batch Approval", f"Approved {successful}/{len(filepaths)} assets")

            # Refresh the tree to show updated status
            self._refresh_current_tab()

        except Exception as e:
            self.logger.error(f"Error in batch approve: {e}")
            self.show_error("Batch Approval Error", f"Error in batch approve: {e}")

    def _batch_unapprove_selected(self, tree_view: QtWidgets.QTreeWidget):
        """Batch unapprove selected items."""
        try:
            selected_items = tree_view.selectedItems()
            filepaths = []

            for item in selected_items:
                item_data = item.data(0, QtCore.Qt.UserRole)
                if item_data and 'asset_path' in item_data:
                    filepaths.append(item_data['asset_path'])

            if not filepaths:
                return

            results = self.version_control.batch_unapprove(filepaths)

            successful = sum(1 for success in results.values() if success)
            self.show_info("Batch Unapproval", f"Unapproved {successful}/{len(filepaths)} assets")

            # Refresh the tree to show updated status
            self._refresh_current_tab()

        except Exception as e:
            self.logger.error(f"Error in batch unapprove: {e}")
            self.show_error("Batch Unapproval Error", f"Error in batch unapprove: {e}")

    def _show_version_info(self, filepath: str):
        """Show detailed version information."""
        try:
            version_info = self.version_control.get_version_info(filepath)

            info_text = f"File: {os.path.basename(filepath)}\n"
            info_text += f"Version: {version_info.get('version', 'Unknown')}\n"
            info_text += f"Status: {version_info.get('status', 'Unknown')}\n"
            info_text += f"Approved: {'Yes' if version_info.get('approved') else 'No'}\n"
            info_text += f"Modified: {version_info.get('modified', 'Unknown')}\n"
            info_text += f"Path: {filepath}"

            self.show_info("Version Information", info_text)

        except Exception as e:
            self.logger.error(f"Error showing version info: {e}")
            self.show_error("Version Info Error", f"Error getting version info: {e}")

    def _show_approval_history(self, filepath: str):
        """Show approval history for an asset."""
        try:
            approval_info = self.version_control.get_approval_info(filepath)

            if approval_info:
                history_text = f"Approval History for: {os.path.basename(filepath)}\n\n"
                history_text += f"Approved by: {approval_info.get('approved_by', 'Unknown')}\n"
                history_text += f"Approved at: {approval_info.get('approved_at', 'Unknown')}\n"
                history_text += f"Notes: {approval_info.get('notes', 'None')}\n"
                history_text += f"Version: {approval_info.get('version', 'Unknown')}"
            else:
                history_text = f"No approval history found for: {os.path.basename(filepath)}"

            self.show_info("Approval History", history_text)

        except Exception as e:
            self.logger.error(f"Error showing approval history: {e}")
            self.show_error("Approval History Error", f"Error getting approval history: {e}")

    def _refresh_current_tab(self):
        """Refresh the currently active tab."""
        try:
            current_index = self.tab_widget.currentIndex()
            variables = self.variable_manager.get_all_variables()

            if current_index == 1:  # Renders tab
                self.update_renders_tab(variables)
            elif current_index == 2:  # Geometry tab
                self.update_geometry_tab(variables)

        except Exception as e:
            self.logger.error(f"Error refreshing current tab: {e}")

    def save_as_dialog(self):
        """Show save as dialog."""
        try:
            # Get current context
            context = self._current_context
            if not all(k in context for k in ['project', 'ep', 'seq', 'shot']):
                nuke.message("Error: Incomplete context. Please set project, episode, sequence, and shot.")
                return

            # Get project root from script-embedded variables only (PRD 4.1 compliance)
            all_vars = self.variable_manager.get_all_variables()
            proj_root = all_vars.get("PROJ_ROOT", "")

            if not proj_root:
                nuke.message("Error: No PROJ_ROOT found in configuration.")
                return

            # Hardcode nuke path - always comp department
            nuke_path = os.path.join(proj_root, context['project'], "all", "scene",
                                   context['ep'], context['seq'], context['shot'],
                                   "comp", "version")

            # Generate default filename (nuke files always go to comp department)
            context = self._current_context
            if all(k in context for k in ['ep', 'seq', 'shot']):
                # Get next version - scan existing .nk files directly in version directory
                existing_files = []
                if os.path.exists(nuke_path):
                    for filename in os.listdir(nuke_path):
                        if filename.lower().endswith('.nk'):
                            existing_files.append(filename)

                # Extract version numbers from existing files
                versions = []
                for filename in existing_files:
                    # Extract version from filename like "Ep01_sq0010_SH0020_comp_v001.nk"
                    parts = filename.replace('.nk', '').split('_')
                    if len(parts) >= 5 and parts[-1].startswith('v'):
                        versions.append(parts[-1])  # v001, v002, etc.

                # Get next version
                if versions:
                    latest = self.scanner.get_latest_version(versions)
                    if latest:
                        next_version = self.context_detector.increment_version(latest)
                    else:
                        next_version = "v001"
                else:
                    next_version = "v001"

                # Nuke files always use comp department - save directly in /version/ directory
                default_filename = f"{context['ep']}_{context['seq']}_{context['shot']}_comp_{next_version}.nk"
                default_path = os.path.join(nuke_path, default_filename)  # No version subdirectory
            else:
                default_path = os.path.join(nuke_path, "untitled.nk")

            # Show file dialog
            filepath, _ = QtWidgets.QFileDialog.getSaveFileName(
                self,
                "Save Nuke Script",
                default_path,
                "Nuke Scripts (*.nk);;All Files (*)"
            )

            if filepath:
                # Create directory if needed
                os.makedirs(os.path.dirname(filepath), exist_ok=True)

                # Try to save in Nuke if available
                try:
                    import nuke
                    nuke.scriptSaveAs(filepath)
                    self.show_info("File Saved", f"Saved: {os.path.basename(filepath)}")

                    # Refresh file lists
                    self.update_file_lists()

                except ImportError:
                    # Not in Nuke environment
                    self.show_info("Save Path", f"Save path: {filepath}")

        except Exception as e:
            self.logger.error(f"Error in save as dialog: {e}")
            self.show_error("Save Error", f"Failed to save: {e}")

    def create_new_version(self):
        """Create a new version of the current file."""
        try:
            # This would increment version and save
            self.show_info("New Version", "New version functionality will be implemented with custom nodes.")

        except Exception as e:
            self.logger.error(f"Error creating new version: {e}")
            self.show_error("Version Error", f"Failed to create new version: {e}")

    # ========================================
    # PHASE 3: Auto-detect and Context Display
    # ========================================

    def _get_current_script_path(self) -> Optional[str]:
        """Get the current Nuke script path if available."""
        try:
            import nuke
            script_path = nuke.root().name()

            # Check if it's a real path (not 'Root' or empty)
            if script_path and script_path != 'Root' and os.path.exists(script_path):
                return script_path

            return None
        except ImportError:
            # Not in Nuke environment
            return None
        except Exception as e:
            self.logger.error(f"Error getting current script path: {e}")
            return None

    def _detect_context_from_path(self, filepath: str) -> Optional[Dict[str, str]]:
        """
        Detect multishot context from a file path.

        Expected path format:
        V:/SWA/all/scene/Ep01/sq0010/SH0040/comp/work/comp_v001.nk
        """
        try:
            # Normalize path
            filepath = os.path.normpath(filepath)
            parts = filepath.split(os.sep)

            context = {}

            # Try to find project (usually after drive letter)
            for i, part in enumerate(parts):
                if part in ['SWA', 'PROJECT_A', 'PROJECT_B']:  # Add your project names
                    context['project'] = part

                    # Look for ep/seq/shot pattern after project
                    if i + 4 < len(parts):
                        # Check if we have scene directory
                        if parts[i + 1] == 'all' and parts[i + 2] == 'scene':
                            context['ep'] = parts[i + 3] if i + 3 < len(parts) else ''
                            context['seq'] = parts[i + 4] if i + 4 < len(parts) else ''
                            context['shot'] = parts[i + 5] if i + 5 < len(parts) else ''
                            break

            # Only return if we found at least project
            if context.get('project'):
                self.logger.info(f"Detected context from path: {context}")
                return context

            return None

        except Exception as e:
            self.logger.error(f"Error detecting context from path: {e}")
            return None

    def _update_context_details(self):
        """Update the context details display with current multishot context and shots."""
        try:
            details = []

            # Current context
            details.append("=== Current Context ===")
            details.append(f"Project: {self._current_context.get('project', 'N/A')}")
            details.append(f"Episode: {self._current_context.get('ep', 'N/A')}")
            details.append(f"Sequence: {self._current_context.get('seq', 'N/A')}")
            details.append(f"Shot: {self._current_context.get('shot', 'N/A')}")
            details.append("")

            # Try to get shots from multishot manager
            shots = self._get_shots_from_manager()
            if shots:
                details.append("=== Shots in Manager ===")
                for shot_key in shots:
                    # Check if this is the current shot
                    current_shot_key = f"{self._current_context.get('project', '')}_{self._current_context.get('ep', '')}_{self._current_context.get('seq', '')}_{self._current_context.get('shot', '')}"
                    marker = " ← CURRENT" if shot_key == current_shot_key else ""
                    details.append(f"• {shot_key}{marker}")
            else:
                details.append("=== Shots in Manager ===")
                details.append("(No shots loaded)")

            # Update display
            self.context_details_text.setPlainText("\n".join(details))

        except Exception as e:
            self.logger.error(f"Error updating context details: {e}")
            self.context_details_text.setPlainText(f"Error loading context: {e}")

    def _get_shots_from_manager(self) -> List[str]:
        """Get list of shots from multishot manager if available."""
        try:
            import nuke

            # Try to read shots from root knobs
            if nuke.root().knob('multishot_shots'):
                import json
                shots_json = nuke.root()['multishot_shots'].value()
                if shots_json:
                    shots_data = json.loads(shots_json)
                    # Extract shot keys
                    shot_keys = []
                    for shot in shots_data:
                        shot_key = f"{shot.get('project', '')}_{shot.get('ep', '')}_{shot.get('seq', '')}_{shot.get('shot', '')}"
                        shot_keys.append(shot_key)
                    return shot_keys

            return []

        except ImportError:
            # Not in Nuke environment
            return []
        except Exception as e:
            self.logger.error(f"Error getting shots from manager: {e}")
            return []
