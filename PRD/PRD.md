# Nuke Multishot Workflow System - Product Requirements Document

## 1. Project Overview

### 1.1 Purpose
Create a comprehensive multishot workflow system for Nuke that provides variable-driven asset management, context-aware file operations, and streamlined shot-based compositing workflows.

### 1.2 Goals
- Eliminate manual path management in multishot projects
- Provide context-aware file operations based on current shot
- Enable render farm compatibility through script-embedded variables
- Streamline version management and approval workflows
- Support hierarchical project structure (Project > Episode > Sequence > Shot)

## 2. Technical Specifications

### 2.1 Compatibility
- **Nuke Versions**: 14.x, 15.x, 16.x
- **Python**: 3.7+ compatibility
- **UI Framework**: PySide2 (Nuke 14-15), PySide6 detection (Nuke 16)
- **Installation**: NUKE_PATH environment variable
- **Platform**: Cross-platform (Windows, Linux, macOS)

### 2.2 Directory Structure
```
Project Structure:
V:/SWA/all/scene/Ep01/sq0110/SH0520/comp/version/Ep01_sq0110_SH0520_comp_v001.nk
W:/SWA/all/scene/Ep01/sq0090/SH0450/lighting/publish/v005/MASTER_ATMOS_A/MASTER_ATMOS_A.1001.exr
V:/SWA/all/scene/Ep01/sq0090/SH0450/anim/publish/v004/geometry.abc
```

### 2.3 File Naming Convention
- **Pattern**: `{ep}_{seq}_{shot}_{department}_{variance}_{version}.nk`
- **Example**: `Ep01_sq0110_SH0520_comp_v001.nk`
- **Variance**: Optional field for variations
- **Version Formats**: `v###` or `v###_###`

### 2.4 Variable System
#### Root Variables
- `PROJ_ROOT = V:/`
- `IMG_ROOT = W:/`

#### Hierarchical Variables
- `{project}` - Project name (e.g., "SWA")
- `{ep}` - Episode (e.g., "Ep01")
- `{seq}` - Sequence (e.g., "sq0110")
- `{shot}` - Shot (e.g., "SH0520")
- `{department}` - Department (auto-detected from directories)
- `{variance}` - Optional variation
- `{version}` - Version number

#### Custom Variables
- User-defined key-value pairs
- Global across all scripts
- Hierarchical inheritance

## 3. Core Features

### 3.1 Variable Management System
- **Script-Embedded Storage**: Variables stored in nuke.root() knobs for farm compatibility
- **Project Configuration**: Default settings in `{PROJ_ROOT}{project}/.multishot/config.json`
- **Context Detection**: Auto-populate from current file name
- **Hierarchical Resolution**: Project > Episode > Sequence > Shot inheritance

### 3.2 Directory Walker & Path Scanner
- **Automatic Discovery**: Scan filesystem to populate dropdowns
- **Real-time Updates**: Refresh when directories change
- **Department Detection**: Auto-detect available departments
- **Version Scanning**: Find all available versions for assets

### 3.3 Custom Nodes

#### 3.3.1 Custom Read Node
- **Variable-Driven Paths**: Use template variables for file paths
- **Asset Types**: Images (EXR, PNG, JPG, TIFF), Geometry (ABC), Cameras
- **Version Selection**: Dropdown for available versions
- **Missing Frame Handling**: Use Nuke's "nearest frame" attribute
- **Approval System**: Visual indication of approved versions
- **Auto-Detection**: Scan for available files matching pattern

#### 3.3.2 Custom Write Node
- **Variable-Driven Output**: Template-based output paths
- **Auto-Directory Creation**: Create output directories if missing
- **Version Management**: Auto-increment or manual version selection
- **Render Farm Compatible**: All paths resolved at render time

#### 3.3.3 Custom Switch Node
- **Variable-Based Switching**: Switch inputs based on shot/sequence/custom variables
- **Dynamic Input Management**: Add/remove inputs based on available shots
- **Context Awareness**: Auto-switch when shot context changes

### 3.4 User Interface Components

#### 3.4.1 Main Browser UI
- **File Browser**: Navigate and open/save Nuke scripts
- **Context Controls**: Episode/Sequence/Shot selection dropdowns (no department in context)
- **Variable Management**: Set and edit custom variables with echo button
- **Recent Projects**: Quick access to recent work
- **Save Templates**: Save current variable set as template
- **Nuke Files Tab**: List nuke scripts with save increment functionality
- **Renders Tab**: Tree view of all department renders with multi-selection
- **Geometry Tab**: Tree view of geometry/camera files with multi-selection
- **Asset Status**: Visual indicators for assets already in script (green/red/white)
- **Read Node Creation**: Create read nodes from selected assets with context variables

#### 3.4.2 Node Management UI
- **Node List**: Display all custom read/write/switch nodes in current script
- **Batch Operations**: Update multiple nodes simultaneously
- **Version Control**: Change versions for multiple nodes
- **Path Override**: Manually override paths when needed
- **Approval Management**: Mark/unmark versions as approved

### 3.5 Version Control & Approval System
- **Version Detection**: Auto-detect available versions in directories
- **Approval Marking**: Create `.approved` marker files
- **UI Highlighting**: Different colors for approved vs unapproved versions
- **Version Comparison**: Basic version information display
- **Batch Approval**: Approve multiple versions at once

## 4. Data Storage Strategy

### 4.1 Script-Embedded Variables (Primary)
- **Location**: Nuke script knobs (`nuke.root()`)
- **Purpose**: Farm-compatible variable storage
- **Content**: All critical variables for rendering
- **Persistence**: Travels with .nk file automatically

### 4.2 Project Configuration (Secondary)
- **Location**: `{PROJ_ROOT}{project}/.multishot/config.json`
- **Purpose**: Default settings and templates
- **Content**: Root paths, department lists, naming conventions
- **Scope**: Project-wide defaults

### 4.3 User Preferences (Tertiary)
- **Location**: `{PROJ_ROOT}{project}/.multishot/user_prefs.json`
- **Purpose**: UI state and user preferences
- **Content**: Window positions, recent files, UI settings
- **Scope**: User-specific, non-critical

## 5. Workflow Integration

### 5.1 Context Detection
1. **File Open**: Detect context from filename
2. **Variable Population**: Auto-populate episode/sequence/shot
3. **Path Resolution**: Resolve all template paths
4. **Node Updates**: Update all custom nodes with new context

### 5.2 Render Farm Compatibility
1. **Variable Embedding**: All variables stored in script
2. **Path Resolution**: Resolved at render time on farm
3. **No External Dependencies**: No need for config files on farm
4. **Asset Validation**: Check asset availability before submission

### 5.3 Version Management Workflow
1. **Version Scanning**: Auto-detect available versions
2. **Approval Checking**: Check for `.approved` markers
3. **UI Updates**: Highlight approved versions
4. **Batch Operations**: Update multiple nodes efficiently

## 6. Success Criteria

### 6.1 Functional Requirements
- [ ] Variables persist with Nuke scripts for farm compatibility
- [ ] Context auto-detection from filenames works reliably
- [ ] Custom nodes resolve paths correctly using variables
- [ ] UI provides efficient multishot navigation and management
- [ ] Version management system works with approval workflow
- [ ] All asset types (images, geometry, cameras) supported

### 6.2 Performance Requirements
- [ ] Directory scanning completes within 5 seconds for typical projects
- [ ] UI remains responsive during large project navigation
- [ ] Node path resolution has minimal impact on script performance
- [ ] Version detection works efficiently with hundreds of versions

### 6.3 Usability Requirements
- [ ] Intuitive UI that reduces manual path entry by 90%
- [ ] Context switching between shots takes less than 10 seconds
- [ ] New users can understand the system within 30 minutes
- [ ] Existing Nuke workflows remain unaffected

## 7. Implementation Phases

### Phase 1: Core Infrastructure
- Project setup and basic structure
- Variable management system
- Directory walker and path scanner

### Phase 2: Custom Nodes
- Custom read node implementation
- Custom write node implementation
- Custom switch node implementation

### Phase 3: User Interface
- Main browser UI with tabbed asset browsing
- Asset tree views for renders, geometry, and camera files
- Multi-selection asset management with visual status indicators
- Read node creation from browser selections
- Node management UI
- Integration and testing

### Phase 4: Advanced Features
- Version control system
- Approval workflow
- Performance optimization

## 8. Risk Assessment

### 8.1 Technical Risks
- **Nuke Version Compatibility**: Different API changes across versions
- **Network Path Performance**: Slow network drives affecting UI responsiveness
- **Farm Integration**: Ensuring variables resolve correctly on different farm systems

### 8.2 Mitigation Strategies
- **Version Testing**: Test on all supported Nuke versions
- **Caching Strategy**: Cache directory scans and version information
- **Fallback Mechanisms**: Graceful degradation when network paths unavailable