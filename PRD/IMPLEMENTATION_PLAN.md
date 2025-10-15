# Nuke Multishot Workflow System - Implementation Plan

## Project Structure

```
nukemultishot/
├── multishot/                    # Main package
│   ├── __init__.py              # Package initialization
│   ├── core/                    # Core functionality
│   │   ├── __init__.py
│   │   ├── variables.py         # Variable management system
│   │   ├── scanner.py           # Directory walker and path scanner
│   │   ├── paths.py             # Path resolution and templates
│   │   └── context.py           # Context detection from filenames
│   ├── nodes/                   # Custom Nuke nodes
│   │   ├── __init__.py
│   │   ├── base_node.py         # Base class for custom nodes
│   │   ├── read_node.py         # Custom read node
│   │   ├── write_node.py        # Custom write node
│   │   └── switch_node.py       # Custom switch node
│   ├── ui/                      # User interface components
│   │   ├── __init__.py
│   │   ├── qt_utils.py          # Qt compatibility layer
│   │   ├── browser.py           # Main browser UI
│   │   ├── node_manager.py      # Node management UI
│   │   └── widgets.py           # Custom UI widgets
│   └── utils/                   # Utility modules
│       ├── __init__.py
│       ├── version.py           # Version handling and parsing
│       ├── approval.py          # Approval system (.approved files)
│       ├── config.py            # Configuration management
│       └── logging.py           # Logging utilities
├── menu.py                      # Nuke menu integration
├── init.py                      # Nuke initialization script
├── toolbar.py                   # Toolbar integration
├── README.md                    # Installation and usage guide
├── CHANGELOG.md                 # Version history
└── tests/                       # Test suite
    ├── __init__.py
    ├── test_variables.py
    ├── test_scanner.py
    ├── test_paths.py
    └── sample_data/             # Test data structure
```

## Implementation Tasks Breakdown

### Task 1: Project Setup & Core Structure
**Duration**: 1 day
**Dependencies**: None

#### Deliverables:
1. **Directory Structure Creation**
   - Create all package directories
   - Set up `__init__.py` files with proper imports
   - Create basic module stubs

2. **Nuke Integration Setup**
   - `init.py` - Nuke startup integration
   - `menu.py` - Menu system integration
   - `toolbar.py` - Toolbar button setup
   - Qt compatibility detection (PySide2/PySide6)

3. **Configuration System**
   - `utils/config.py` - JSON config management
   - Default configuration templates
   - Project-specific config handling

4. **Logging System**
   - `utils/logging.py` - Centralized logging
   - Debug/info/error level handling
   - File and console output

#### Technical Details:
```python
# init.py structure
import nuke
import nukescripts
from multishot import register_nodes, create_toolbar, setup_menu

def initialize():
    register_nodes()
    create_toolbar()
    setup_menu()

# Auto-initialize when Nuke starts
if nuke.GUI:
    initialize()
```

### Task 2: Variable Management System
**Duration**: 2 days
**Dependencies**: Task 1

#### Deliverables:
1. **Script-Embedded Variables** (`core/variables.py`)
   - Nuke knob creation and management
   - Variable serialization/deserialization
   - Hierarchical variable resolution
   - Context inheritance system

2. **Project Configuration** (`utils/config.py`)
   - JSON-based project defaults
   - Root path management (PROJ_ROOT, IMG_ROOT)
   - Department and naming convention storage

3. **Context Detection** (`core/context.py`)
   - Filename parsing for episode/sequence/shot
   - Auto-population of variables from current file
   - Context change detection and propagation

#### Technical Details:
```python
# Variable storage in Nuke script
class VariableManager:
    def __init__(self):
        self.ensure_knobs_exist()
    
    def ensure_knobs_exist(self):
        root = nuke.root()
        if 'multishot_variables' not in root.knobs():
            root.addKnob(nuke.String_Knob('multishot_variables', 'Variables'))
    
    def set_variable(self, key, value):
        variables = self.get_all_variables()
        variables[key] = value
        self.save_variables(variables)
    
    def get_variable(self, key, default=None):
        variables = self.get_all_variables()
        return variables.get(key, default)
```

### Task 3: Directory Walker & Path Scanner
**Duration**: 2 days
**Dependencies**: Task 2

#### Deliverables:
1. **Directory Scanner** (`core/scanner.py`)
   - Recursive directory traversal
   - Episode/Sequence/Shot detection
   - Department discovery
   - Caching for performance

2. **Path Templates** (`core/paths.py`)
   - Template-based path generation
   - Variable substitution engine
   - Path validation and existence checking
   - Cross-platform path handling

3. **Version Detection** (`utils/version.py`)
   - Version pattern matching (v### and v###_###)
   - Latest version detection
   - Version comparison and sorting

#### Technical Details:
```python
# Directory scanning with caching
class DirectoryScanner:
    def __init__(self, cache_timeout=300):  # 5 minute cache
        self.cache = {}
        self.cache_timeout = cache_timeout
    
    def scan_episodes(self, project_root):
        cache_key = f"episodes_{project_root}"
        if self.is_cache_valid(cache_key):
            return self.cache[cache_key]['data']
        
        episodes = self._scan_directory_pattern(
            project_root, 
            pattern=r'^Ep\d+$'
        )
        self.cache[cache_key] = {
            'data': episodes,
            'timestamp': time.time()
        }
        return episodes
```

### Task 4: Main Browser UI
**Duration**: 3 days
**Dependencies**: Task 2, Task 3

#### Deliverables:
1. **Qt Compatibility Layer** (`ui/qt_utils.py`)
   - PySide2/PySide6 detection and imports
   - Common widget abstractions
   - Nuke panel integration helpers

2. **Main Browser Interface** (`ui/browser.py`)
   - File browser with project navigation
   - Episode/Sequence/Shot dropdown controls
   - Variable management panel
   - Save/Open with context awareness
   - Recent projects list

3. **Custom Widgets** (`ui/widgets.py`)
   - Variable editor widget
   - Path template widget
   - Version selector widget
   - Approval status indicator

#### Technical Details:
```python
# Main browser UI structure
class MultishotBrowser(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.variable_manager = VariableManager()
        self.scanner = DirectoryScanner()
        self.setup_ui()
        self.connect_signals()
    
    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout()
        
        # Context controls
        self.context_widget = self.create_context_controls()
        layout.addWidget(self.context_widget)
        
        # File browser
        self.file_browser = self.create_file_browser()
        layout.addWidget(self.file_browser)
        
        # Variable management
        self.variable_panel = self.create_variable_panel()
        layout.addWidget(self.variable_panel)
```

### Task 5: Custom Read Node
**Duration**: 3 days
**Dependencies**: Task 2, Task 3

#### Deliverables:
1. **Base Node Class** (`nodes/base_node.py`)
   - Common functionality for all custom nodes
   - Variable resolution integration
   - Path template handling
   - Error handling and validation

2. **Custom Read Node** (`nodes/read_node.py`)
   - Inherit from Nuke's Read node
   - Variable-driven file path resolution
   - Version selection dropdown
   - Asset type detection (images, geometry, cameras)
   - Missing frame handling configuration
   - Approval status visualization

3. **Node Registration**
   - Register custom nodes with Nuke
   - Custom node icons and UI
   - Help documentation integration

#### Technical Details:
```python
# Custom Read Node implementation
class MultishotRead(nuke.Node):
    def __init__(self):
        super().__init__()
        self.variable_manager = VariableManager()
        self.setup_knobs()
        self.setup_callbacks()
    
    def setup_knobs(self):
        # Path template knob
        self.addKnob(nuke.String_Knob('path_template', 'Path Template'))
        
        # Version selection
        self.addKnob(nuke.Enumeration_Knob('version', 'Version', []))
        
        # Asset type
        self.addKnob(nuke.Enumeration_Knob('asset_type', 'Type', 
                                          ['image', 'geometry', 'camera']))
    
    def knobChanged(self, knob):
        if knob.name() == 'path_template':
            self.update_resolved_path()
        elif knob.name() == 'version':
            self.update_file_path()
```

### Task 6: Custom Write Node
**Duration**: 2 days
**Dependencies**: Task 5

#### Deliverables:
1. **Custom Write Node** (`nodes/write_node.py`)
   - Inherit from Nuke's Write node
   - Variable-driven output paths
   - Automatic directory creation
   - Version management (auto-increment/manual)
   - Render farm compatibility validation

2. **Output Path Management**
   - Template-based output path generation
   - Directory structure creation
   - Path conflict detection and resolution
   - Network path validation

#### Technical Details:
```python
# Custom Write Node with auto-directory creation
class MultishotWrite(nuke.Node):
    def beforeRender(self):
        # Resolve output path using current variables
        output_path = self.resolve_output_path()
        
        # Create directories if they don't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Update the file knob with resolved path
        self['file'].setValue(output_path)
    
    def resolve_output_path(self):
        template = self['path_template'].value()
        variables = self.variable_manager.get_all_variables()
        return self.substitute_variables(template, variables)
```

### Task 7: Custom Switch Node
**Duration**: 2 days
**Dependencies**: Task 5

#### Deliverables:
1. **Custom Switch Node** (`nodes/switch_node.py`)
   - Variable-based input switching
   - Dynamic input management
   - Context-aware switching rules
   - Visual feedback for active input

2. **Switching Logic**
   - Shot-based switching
   - Sequence-based switching
   - Custom variable switching
   - Manual override capability

### Task 8: Node Management UI
**Duration**: 2 days
**Dependencies**: Task 4, Task 5, Task 6, Task 7

#### Deliverables:
1. **Node Manager Interface** (`ui/node_manager.py`)
   - List all custom nodes in current script
   - Batch operation controls
   - Version management for multiple nodes
   - Path override capabilities
   - Node status indicators

2. **Batch Operations**
   - Update multiple node versions
   - Change shot context for all nodes
   - Batch approval management
   - Export/import node configurations

### Task 9: Version Control System
**Duration**: 2 days
**Dependencies**: Task 3, Task 8

#### Deliverables:
1. **Approval System** (`utils/approval.py`)
   - `.approved` file creation and detection
   - Approval status tracking
   - Batch approval operations
   - UI integration for approval indicators

2. **Version Management**
   - Version comparison utilities
   - Latest version detection
   - Version history tracking
   - Rollback capabilities

### Task 10: Integration & Testing
**Duration**: 2 days
**Dependencies**: All previous tasks

#### Deliverables:
1. **Integration Testing**
   - End-to-end workflow testing
   - Cross-platform compatibility testing
   - Nuke version compatibility testing
   - Performance benchmarking

2. **Documentation**
   - User manual and tutorials
   - API documentation
   - Installation guide
   - Troubleshooting guide

3. **Sample Data**
   - Test project structure
   - Sample Nuke scripts
   - Example configurations

## Timeline Summary

- **Week 1**: Tasks 1-3 (Core Infrastructure)
- **Week 2**: Tasks 4-5 (UI and Read Node)
- **Week 3**: Tasks 6-8 (Write/Switch Nodes and Management UI)
- **Week 4**: Tasks 9-10 (Version Control and Integration)

**Total Estimated Duration**: 4 weeks

## Success Metrics

1. **Functionality**: All core features working as specified
2. **Performance**: Directory scanning < 5 seconds, UI responsive
3. **Compatibility**: Works on Nuke 14-16, Windows/Linux/macOS
4. **Usability**: Reduces manual path entry by 90%
5. **Reliability**: Farm compatibility validated with test renders
