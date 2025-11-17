# How MultishotRead Node Remembers Shot Versions

## 🎯 Overview

The MultishotRead node uses a **dual-storage system** to remember which version to use for each shot:

1. **Persistent Storage:** `shot_versions` knob (hidden JSON dictionary)
2. **Active Storage:** `shot_version` knob (visible string for current shot)

This allows the node to:
- Remember different versions for different shots
- Automatically switch versions when you change shots
- Work seamlessly with Nuke's expression system

---

## 📊 Data Storage Architecture

### **1. The `shot_versions` Knob (Persistent Storage)**

**Type:** Hidden File_Knob containing JSON string

**Purpose:** Store versions for ALL shots

**Format:**
```json
{
  "SWA_Ep01_sq0010_SH0010": "v002",
  "SWA_Ep01_sq0010_SH0020": "v005",
  "SWA_Ep01_sq0010_SH0030": "v003"
}
```

**Location:** `node['shot_versions']`

**Characteristics:**
- ✅ Persistent (saved with .nk file)
- ✅ Stores multiple shots
- ✅ Hidden from user
- ✅ Farm-compatible (travels with script)

---

### **2. The `shot_version` Knob (Active Storage)**

**Type:** Visible String_Knob

**Purpose:** Store version for CURRENT shot only

**Format:** Simple string like `"v002"`

**Location:** `node['shot_version']`

**Characteristics:**
- ✅ Visible to user
- ✅ Used in expressions
- ✅ Changes when shot changes
- ✅ Single value only (current shot)

---

## 🔄 How Version Memory Works

### **Step-by-Step Flow:**

```
┌─────────────────────────────────────────────────────────────┐
│ 1. USER SETS VERSION FOR SHOT 0010                         │
└─────────────────────────────────────────────────────────────┘
                           ↓
    User opens "Set Versions" dialog for shot 0010
    User selects "v002" for lighting node
    User clicks "Apply"
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. MULTISHOT MANAGER CALLS set_version_for_shot()          │
└─────────────────────────────────────────────────────────────┘
                           ↓
    instance.set_version_for_shot("v002", "SWA_Ep01_sq0010_SH0010")
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. READ NODE UPDATES PERSISTENT STORAGE                    │
└─────────────────────────────────────────────────────────────┘
                           ↓
    Read shot_versions knob: {"SH0020": "v005"}
    Update dictionary: {"SH0020": "v005", "SH0010": "v002"}
    Write back to shot_versions knob
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. READ NODE UPDATES ACTIVE STORAGE (IF CURRENT SHOT)      │
└─────────────────────────────────────────────────────────────┘
                           ↓
    Check: Is "SH0010" the current shot?
    YES → Update shot_version knob to "v002"
    NO  → Skip (will update when switching to this shot)
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. EXPRESSION PATH AUTOMATICALLY RESOLVES                  │
└─────────────────────────────────────────────────────────────┘
                           ↓
    File path expression:
    [value root.IMG_ROOT][value root.project]/all/scene/
    [value root.ep]/[value root.seq]/[value root.shot]/
    lighting/publish/[value parent.MultishotRead1.shot_version]/
    MASTER_CHAR_A/MASTER_CHAR_A.%04d.exr
                           ↓
    Resolves to:
    W:/SWA/all/scene/Ep01/sq0010/SH0010/lighting/publish/v002/
    MASTER_CHAR_A/MASTER_CHAR_A.%04d.exr
```

---

## 🔀 Shot Switching Flow

### **When User Switches from Shot 0010 to Shot 0020:**

```
┌─────────────────────────────────────────────────────────────┐
│ 1. USER CLICKS "SET SHOT" FOR SHOT 0020                    │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. MULTISHOT MANAGER SAVES CURRENT SHOT VERSIONS           │
└─────────────────────────────────────────────────────────────┘
                           ↓
    For each MultishotRead node:
      - Read current shot_version knob: "v002"
      - Save to shot_versions JSON for SH0010
      - shot_versions = {"SH0010": "v002", "SH0020": "v005"}
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. MULTISHOT MANAGER UPDATES ROOT KNOBS                    │
└─────────────────────────────────────────────────────────────┘
                           ↓
    nuke.root()['multishot_shot'].setValue("SH0020")
    nuke.root()['multishot_ep'].setValue("Ep01")
    nuke.root()['multishot_seq'].setValue("sq0010")
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. MULTISHOT MANAGER UPDATES NODES FOR NEW SHOT            │
└─────────────────────────────────────────────────────────────┘
                           ↓
    For each MultishotRead node:
      - Call get_version_for_shot("SH0020")
      - Read from shot_versions JSON: "v005"
      - Update shot_version knob to "v005"
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. EXPRESSION PATH AUTOMATICALLY UPDATES                   │
└─────────────────────────────────────────────────────────────┘
                           ↓
    Expression reads:
      - [value root.shot] = "SH0020"
      - [value parent.MultishotRead1.shot_version] = "v005"
                           ↓
    Path resolves to:
    W:/SWA/all/scene/Ep01/sq0010/SH0020/lighting/publish/v005/
    MASTER_CHAR_A/MASTER_CHAR_A.%04d.exr
                           ↓
    ✅ Node automatically reads correct version for shot 0020!
```

---

## 💾 Code Implementation

### **1. Storing Version (set_version_for_shot)**

<augment_code_snippet path="multishot/nodes/read_node.py" mode="EXCERPT">
```python
def set_version_for_shot(self, version, shot_key=None):
    """Set version for a specific shot."""
    import json
    
    # Get shot key
    if shot_key is None:
        shot_key = self.get_shot_key()
    
    # Read current shot_versions JSON
    shot_versions_str = self.node['shot_versions'].value()
    shot_versions = json.loads(shot_versions_str) if shot_versions_str else {}
    
    # Update version for this shot
    shot_versions[shot_key] = version
    
    # Write back to knob
    self.node['shot_versions'].setValue(json.dumps(shot_versions))
    
    # Only update shot_version knob if setting for CURRENT shot
    current_shot_key = self.get_shot_key()
    if shot_key == current_shot_key:
        self.node['shot_version'].setValue(version)
        self.build_expression_path()
```
</augment_code_snippet>

---

### **2. Retrieving Version (get_version_for_shot)**

<augment_code_snippet path="multishot/nodes/read_node.py" mode="EXCERPT">
```python
def get_version_for_shot(self, shot_key=None):
    """Get version for a specific shot."""
    import json
    
    # Get shot key
    if shot_key is None:
        shot_key = self.get_shot_key()
    
    # Read shot_versions knob
    shot_versions_str = self.node['shot_versions'].value()
    shot_versions = json.loads(shot_versions_str) if shot_versions_str else {}
    
    # Get version for this shot (default to v001)
    version = shot_versions.get(shot_key, 'v001')
    
    return version
```
</augment_code_snippet>

---

### **3. Building Expression Path**

<augment_code_snippet path="multishot/nodes/read_node.py" mode="EXCERPT">
```python
def build_expression_path(self):
    """Build expression-based file path."""
    department = self.node['department'].value()
    file_pattern = self.node['file_pattern'].value()
    node_name = self.node.name()

    # Build expression path
    file_path = (
        f"[value root.IMG_ROOT][value root.project]/all/scene/"
        f"[value root.ep]/[value root.seq]/[value root.shot]/"
        f"{department}/publish/[value parent.{node_name}.shot_version]/{file_pattern}"
    )

    # Use fromUserText() to ensure expressions are evaluated in batch mode
    self.node['file'].fromUserText(file_path)
```
</augment_code_snippet>

---

## 🎬 Real-World Example

### **Scenario: Lighting Artist Working on Multiple Shots**

**Setup:**
- Project: SWA
- Shots: SH0010, SH0020, SH0030
- Node: MultishotRead (lighting department)

**Workflow:**

```
1. Artist opens script, sets shot to SH0010
   → shot_version knob = "v001" (default)
   → Path: .../SH0010/lighting/publish/v001/...

2. Artist sets version to v003 for SH0010
   → shot_versions JSON = {"SH0010": "v003"}
   → shot_version knob = "v003"
   → Path: .../SH0010/lighting/publish/v003/...

3. Artist switches to SH0020
   → Saves: shot_versions JSON = {"SH0010": "v003"}
   → Loads: shot_version knob = "v001" (default for SH0020)
   → Path: .../SH0020/lighting/publish/v001/...

4. Artist sets version to v005 for SH0020
   → shot_versions JSON = {"SH0010": "v003", "SH0020": "v005"}
   → shot_version knob = "v005"
   → Path: .../SH0020/lighting/publish/v005/...

5. Artist switches back to SH0010
   → Saves: shot_versions JSON = {"SH0010": "v003", "SH0020": "v005"}
   → Loads: shot_version knob = "v003" (remembered!)
   → Path: .../SH0010/lighting/publish/v003/...
   
✅ Version v003 was remembered for SH0010!
```

---

## 🔑 Key Concepts

### **1. Dual Storage System**

| Storage | Purpose | Scope | Visibility |
|---------|---------|-------|------------|
| **shot_versions** | Remember all shots | Multiple shots | Hidden |
| **shot_version** | Active version | Current shot only | Visible |

### **2. Expression-Based Paths**

**Why use expressions?**
- ✅ Automatic updates when shot changes
- ✅ No need to rebuild paths manually
- ✅ Farm-compatible (expressions resolve on render nodes)
- ✅ Clean, maintainable code

**Expression Format:**
```
[value root.shot] → Reads from root knob
[value parent.NodeName.shot_version] → Reads from node knob
```

### **3. Shot Key Format**

**Format:** `{project}_{ep}_{seq}_{shot}`

**Example:** `"SWA_Ep01_sq0010_SH0010"`

**Why this format?**
- ✅ Unique identifier for each shot
- ✅ Human-readable
- ✅ Contains full context
- ✅ Works as dictionary key

---

## 📋 Summary

### **How It Works:**

1. **Storage:** Each node has a hidden `shot_versions` JSON storing versions for all shots
2. **Active Version:** The `shot_version` knob shows the version for the current shot
3. **Switching:** When switching shots, the manager saves current versions and loads new ones
4. **Expressions:** File paths use expressions that automatically resolve to correct values
5. **Memory:** Versions are remembered because they're stored in the persistent JSON

### **Key Methods:**

| Method | Purpose | Called By |
|--------|---------|-----------|
| `set_version_for_shot()` | Save version for a shot | Multishot Manager |
| `get_version_for_shot()` | Load version for a shot | Multishot Manager |
| `build_expression_path()` | Build file path with expressions | Read Node |

### **Data Flow:**

```
User Action → Multishot Manager → Read Node Methods → Knob Storage → Expression Resolution → File Path
```

---

**The system is elegant, efficient, and farm-compatible!** 🎉

