# Multishot Manager Architecture

Complete technical documentation of how the Multishot Manager implements per-shot version control and shot switching.

---

## 🎯 Overview

The Multishot Manager provides a **per-shot version control system** where:
- Each MultishotRead node can have **different versions for different shots**
- Switching shots automatically updates all nodes to use the correct versions
- Versions are stored **persistently** in the Nuke script
- The system is **farm-compatible** (all data travels with the .nk file)

---

## 📊 Data Storage Architecture

### **1. Shot List Storage**

**Location:** `nuke.root()['multishot_shots']` (hidden String_Knob)

**Format:** JSON array of shot dictionaries
```json
[
  {
    "project": "SWA",
    "ep": "Ep01",
    "seq": "sq0010",
    "shot": "SH0010"
  },
  {
    "project": "SWA",
    "ep": "Ep01",
    "seq": "sq0010",
    "shot": "SH0020"
  }
]
```

**Purpose:** Stores the list of shots managed by the Multishot Manager.

---

### **2. Current Shot Storage**

**Location:** Root knobs (visible in script)
```python
nuke.root()['multishot_project']  # "SWA"
nuke.root()['multishot_ep']       # "Ep01"
nuke.root()['multishot_seq']      # "sq0010"
nuke.root()['multishot_shot']     # "SH0010"
```

**Purpose:** Defines the currently active shot context.

**Shot Key Format:** `{project}_{ep}_{seq}_{shot}`
- Example: `"SWA_Ep01_sq0010_SH0010"`

---

### **3. Per-Shot Version Storage**

**Location:** Each MultishotRead node has a hidden `shot_versions` knob (File_Knob)

**Format:** JSON dictionary mapping shot keys to versions
```json
{
  "SWA_Ep01_sq0010_SH0010": "v003",
  "SWA_Ep01_sq0010_SH0020": "v005",
  "SWA_Ep01_sq0010_SH0030": "v002"
}
```

**Purpose:** Each node remembers which version to use for each shot.

**Example Node Structure:**
```python
# MultishotRead_lighting_MASTER_CHAR_A node
node['shot_versions'].value() = '{
  "SWA_Ep01_sq0010_SH0010": "v003",
  "SWA_Ep01_sq0010_SH0020": "v005"
}'

node['shot_version'].value() = "v003"  # Current shot's version
```

---

## 🔄 Shot Switching Workflow

### **Step-by-Step Process:**

#### **1. User Clicks "Set Shot" Button**

```python
# multishot_manager.py line 384
def _set_shot(self, shot_data):
    """Set the current shot by updating root knobs."""
```

#### **2. Create/Update Root Knobs**

```python
# Lines 394-411
knobs_to_create = {
    'multishot_project': shot_data['project'],
    'multishot_ep': shot_data['ep'],
    'multishot_seq': shot_data['seq'],
    'multishot_shot': shot_data['shot']
}

for knob_name, value in knobs_to_create.items():
    if not nuke.root().knob(knob_name):
        # Create the knob if it doesn't exist
        knob = nuke.String_Knob(knob_name, '')
        knob.setVisible(False)
        nuke.root().addKnob(knob)
    
    # Set the value
    nuke.root()[knob_name].setValue(value)
```

**Result:** Root knobs now contain the new shot context.

---

#### **3. Set Frame Range from Shot JSON**

```python
# Lines 414-434
frame_range = self._read_frame_range_from_shot_json(shot_data)

if frame_range:
    first_frame, last_frame = frame_range
    nuke.root()['first_frame'].setValue(first_frame)
    nuke.root()['last_frame'].setValue(last_frame)
else:
    # Fallback to default
    nuke.root()['first_frame'].setValue(1001)
    nuke.root()['last_frame'].setValue(1100)
```

**JSON File Location:**
```
{PROJ_ROOT}/{project}/all/scene/{ep}/{seq}/{shot}/.{ep}_{seq}_{shot}.json
```

**Supported JSON Formats:**
```json
// Format 1
{"frameRange": {"start": 1001, "end": 1150}}

// Format 2
{"first_frame": 1001, "last_frame": 1150}

// Format 3
{"shot_info": {"start_frame": 1001, "end_frame": 1028}}

// Format 4
{"timeline_settings": {"animation_start": 1001.0, "animation_end": 1028.0}}
```

---

#### **4. Update Variable Manager**

```python
# Lines 437-442
self.variable_manager.set_context_variables({
    'project': shot_data['project'],
    'ep': shot_data['ep'],
    'seq': shot_data['seq'],
    'shot': shot_data['shot']
})
```

**Result:** Variable manager cache is updated with new context.

---

#### **5. Update All MultishotRead Nodes**

```python
# Lines 455-456
self._update_nodes_for_shot(shot_data)
```

**What This Does:**

```python
# Lines 484-533
def _update_nodes_for_shot(self, shot_data):
    """Update all MultishotRead nodes to use versions for the new shot."""
    
    shot_key = f"{shot_data['project']}_{shot_data['ep']}_{shot_data['seq']}_{shot_data['shot']}"
    
    # Find all MultishotRead nodes
    for node in nuke.allNodes():
        if node.knob('multishot_sep'):  # Is a MultishotRead node
            # Get node instance
            if node_name in read_node_module._node_instances:
                instance = read_node_module._node_instances[node_name]
                
                # Get version for this shot from shot_versions knob
                version = instance.get_version_for_shot(shot_key)
                
                # Update ONLY the shot_version knob
                node['shot_version'].setValue(version)
                
                # ❌ DO NOT rebuild path - expressions handle it automatically!
```

**Key Point:** Only the `shot_version` knob is updated. The file path uses expressions like `[value root.shot]` which automatically resolve to the new shot.

---

#### **6. Refresh UI**

```python
# Lines 461
self._refresh_table(update_current_shot=False)
```

**Result:** Table is refreshed to show the new active shot highlighted in green.

---

## 🎨 Version Control Implementation

### **Getting Version for a Shot**

```python
# read_node.py lines 323-356
def get_version_for_shot(self, shot_key=None):
    """Get version for a specific shot."""
    
    if shot_key is None:
        shot_key = self.get_shot_key()  # Get current shot from root knobs
    
    # Read shot_versions knob
    shot_versions_str = self.node['shot_versions'].value()
    shot_versions = json.loads(shot_versions_str) if shot_versions_str else {}
    
    # Get version for this shot (default to v001)
    version = shot_versions.get(shot_key, 'v001')
    
    return version
```

**Example:**
```python
# Node has these versions stored:
shot_versions = {
    "SWA_Ep01_sq0010_SH0010": "v003",
    "SWA_Ep01_sq0010_SH0020": "v005"
}

# Get version for SH0010
version = node.get_version_for_shot("SWA_Ep01_sq0010_SH0010")
# Returns: "v003"

# Get version for SH0030 (not in dict)
version = node.get_version_for_shot("SWA_Ep01_sq0010_SH0030")
# Returns: "v001" (default)
```

---

### **Setting Version for a Shot**

```python
# read_node.py lines 358-407
def set_version_for_shot(self, version, shot_key=None):
    """Set version for a specific shot."""
    
    if shot_key is None:
        shot_key = self.get_shot_key()
    
    current_shot_key = self.get_shot_key()
    
    # Read current shot_versions
    shot_versions_str = self.node['shot_versions'].value()
    shot_versions = json.loads(shot_versions_str) if shot_versions_str else {}
    
    # Update version for this shot
    shot_versions[shot_key] = version
    
    # Write back to knob
    self.node['shot_versions'].setValue(json.dumps(shot_versions))
    
    # ✅ ONLY update shot_version knob if we're setting version for the CURRENT shot
    if shot_key == current_shot_key:
        self.node['shot_version'].setValue(version)
```

**Key Behavior:**
- Always updates the `shot_versions` JSON (persistent storage)
- Only updates `shot_version` knob if setting version for the **current** shot
- This prevents changing the active version when setting versions for other shots

---

## 🔧 Set Versions Dialog

### **Purpose**
Allow users to set versions for all MultishotRead nodes for a specific shot.

### **Workflow:**

#### **1. User Clicks "Set Versions..." Button**

```python
# multishot_manager.py lines 669-685
def _set_versions(self, shot_data):
    """Open version setting dialog for a shot."""
    
    shot_key = f"{shot_data['project']}_{shot_data['ep']}_{shot_data['seq']}_{shot_data['shot']}"
    
    # Create and show version dialog
    dialog = VersionSettingDialog(shot_data, shot_key, parent=self)
    if dialog.exec_() == QtWidgets.QDialog.Accepted:
        # Versions were updated
        pass
```

---

#### **2. Dialog Loads All MultishotRead Nodes**

```python
# multishot_manager.py lines 1022-1101
def _load_nodes(self):
    """Load all MultishotRead nodes."""
    
    for node in nuke.allNodes():
        if node.knob('multishot_sep'):  # Is a MultishotRead node
            # Get current version for THIS shot
            if node.name() in read_node_module._node_instances:
                instance = read_node_module._node_instances[node.name()]
                current_version = instance.get_version_for_shot(self.shot_key)
            
            # Scan available versions from directory
            versions = self._scan_versions_for_node(node)
            
            # Create dropdown with versions
            version_combo = QtWidgets.QComboBox()
            version_combo.addItems(versions)
            version_combo.setCurrentText(current_version)
```

**Result:** Table shows all nodes with dropdowns showing available versions.

---

#### **3. User Selects Versions and Clicks "Apply"**

```python
# multishot_manager.py lines 1197-1223
def accept(self):
    """Apply version changes when user clicks Apply."""
    
    import multishot.nodes.read_node as read_node_module
    
    # Update each node's version for this shot
    for row in range(self.nodes_table.rowCount()):
        version_combo = self.nodes_table.cellWidget(row, 3)
        node = version_combo.property('node')
        selected_version = version_combo.currentText()
        
        # Get node instance
        if node.name() in read_node_module._node_instances:
            instance = read_node_module._node_instances[node.name()]
            
            # Set version for this shot
            instance.set_version_for_shot(selected_version, self.shot_key)
```

**Result:** Each node's `shot_versions` knob is updated with the new version for this shot.

---

## 📋 Expression-Based Path System

### **Why Expressions?**

The system uses Nuke expressions in file paths instead of rebuilding paths programmatically.

**Example Path:**
```
[value root.IMG_ROOT]/[value root.project]/all/scene/[value root.ep]/[value root.seq]/[value root.shot]/lighting/publish/[value parent.MultishotRead_lighting_MASTER_CHAR_A.shot_version]/MASTER_CHAR_A.%04d.exr
```

**Benefits:**
1. ✅ **Automatic Updates:** When root knobs change, paths update automatically
2. ✅ **Farm Compatible:** Expressions evaluate on render farm
3. ✅ **No Rebuilding:** Don't need to call `build_path()` when switching shots
4. ✅ **Visible:** Users can see the expression in the file knob

---

### **How Shot Switching Works with Expressions:**

**Before Shot Switch:**
```python
# Root knobs
nuke.root()['multishot_shot'] = "SH0010"

# Node knobs
node['shot_version'] = "v003"

# File path expression
"[value root.IMG_ROOT]/[value root.project]/all/scene/[value root.ep]/[value root.seq]/[value root.shot]/lighting/publish/[value parent.MultishotRead_lighting_MASTER_CHAR_A.shot_version]/MASTER_CHAR_A.%04d.exr"

# Evaluates to:
"W:/SWA/all/scene/Ep01/sq0010/SH0010/lighting/publish/v003/MASTER_CHAR_A.%04d.exr"
```

**After Shot Switch to SH0020:**
```python
# Root knobs (CHANGED)
nuke.root()['multishot_shot'] = "SH0020"

# Node knobs (CHANGED)
node['shot_version'] = "v005"  # Retrieved from shot_versions JSON

# File path expression (SAME)
"[value root.IMG_ROOT]/[value root.project]/all/scene/[value root.ep]/[value root.seq]/[value root.shot]/lighting/publish/[value parent.MultishotRead_lighting_MASTER_CHAR_A.shot_version]/MASTER_CHAR_A.%04d.exr"

# Evaluates to (DIFFERENT):
"W:/SWA/all/scene/Ep01/sq0010/SH0020/lighting/publish/v005/MASTER_CHAR_A.%04d.exr"
```

**Key Point:** The expression stays the same, but evaluates differently because the referenced knobs changed!

---

## 🎯 Summary

### **Per-Shot Version Control:**
1. Each node stores a JSON dictionary mapping shot keys to versions
2. When switching shots, nodes look up the version for that shot
3. Only the `shot_version` knob is updated (not the entire path)
4. Expressions automatically resolve to the correct path

### **Shot Switching:**
1. Update root knobs with new shot context
2. Set frame range from shot JSON file
3. Update variable manager cache
4. Update each node's `shot_version` knob
5. Refresh UI to show new active shot

### **Data Persistence:**
- Shot list: `nuke.root()['multishot_shots']` (JSON)
- Current shot: `nuke.root()['multishot_*']` (individual knobs)
- Per-shot versions: `node['shot_versions']` (JSON per node)

### **Farm Compatibility:**
- All data stored in nuke.root() knobs
- Travels with .nk file
- No external dependencies
- Expressions evaluate correctly on farm

---

**The system is elegant, efficient, and farm-compatible!** 🎉

