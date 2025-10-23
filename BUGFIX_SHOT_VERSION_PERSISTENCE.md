# Bug Fix: Shot Version Not Persisting When Switching Shots

## 🐛 Bug Description

**Issue:** When switching between shots, the version for each shot was not being saved correctly.

**Example:**
1. Set shot 0010 to v002
2. Set shot 0020 to v004
3. Switch back to shot 0010
4. **BUG:** Shot 0010 shows v004 instead of v002

**Root Cause:** The system was not saving the current shot's version before switching to a new shot.

---

## 🔍 Analysis

### **What Was Happening:**

```
User Action: Set shot 0010 to v002
    ↓
shot_version knob = "v002"
shot_versions JSON = {"SWA_Ep01_sq0010_SH0010": "v002"}
    ↓
User Action: Set shot 0020 to v004
    ↓
shot_version knob = "v004"  ← Changed
shot_versions JSON = {"SWA_Ep01_sq0010_SH0010": "v002", "SWA_Ep01_sq0010_SH0020": "v004"}
    ↓
User Action: Switch back to shot 0010
    ↓
Read from shot_versions JSON: "v002"
Set shot_version knob = "v002"
    ↓
✅ Should work... but it didn't!
```

### **The Problem:**

When switching from shot 0010 to shot 0020, the system:
1. ✅ Updated root knobs to shot 0020
2. ✅ Read version for shot 0020 from JSON ("v004")
3. ✅ Set `shot_version` knob to "v004"
4. ❌ **NEVER saved shot 0010's version back to JSON!**

So if the user manually changed the version while on shot 0010 (using the knob, not the Set Versions dialog), that change was lost.

---

## 🔧 Solution

### **Fix 1: Save Current Shot Versions Before Switching**

Added a new function `_save_current_shot_versions()` that:
1. Gets the current shot key
2. Finds all MultishotRead nodes
3. Reads the current `shot_version` knob value
4. Saves it to the `shot_versions` JSON

**Code:**
```python
def _save_current_shot_versions(self):
    """Save current shot's versions before switching to a new shot."""
    current_shot_key = self.current_shot_key
    if not current_shot_key:
        return
    
    # Find all MultishotRead nodes
    for node in nuke.allNodes():
        if self._is_multishot_read_node(node):
            # Get current shot_version knob value
            current_version = node['shot_version'].value()
            
            # Save this version for the current shot
            instance.set_version_for_shot(current_version, current_shot_key)
```

### **Fix 2: Call Save Function Before Switching**

Modified `_set_shot()` to call `_save_current_shot_versions()` BEFORE updating root knobs:

```python
def _set_shot(self, shot_data):
    """Set the current shot by updating root knobs."""
    
    # ✅ CRITICAL: Save current shot's versions BEFORE switching
    if self.current_shot_key:
        self._save_current_shot_versions()
    
    # Now switch to new shot
    # Update root knobs...
    # Update nodes...
```

---

## 🎯 Additional Fix: Node Type Detection

### **Secondary Bug:**

The system was detecting **all** nodes with `multishot_sep` knob as MultishotRead nodes, including:
- MultishotWrite nodes
- MultishotSwitch nodes

This caused errors because these nodes don't have `shot_versions` knobs.

### **Solution:**

Added a proper node type detection function:

```python
def _is_multishot_read_node(self, node):
    """Check if a node is a MultishotRead node (not Write or Switch)."""
    
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
```

**Node Type Identification:**

| Node Type | multishot_sep | shot_versions | department | output_type | switch_mode |
|-----------|---------------|---------------|------------|-------------|-------------|
| **MultishotRead** | ✅ | ✅ | ✅ | ❌ | ❌ |
| **MultishotWrite** | ✅ | ❌ | ✅ | ✅ | ❌ |
| **MultishotSwitch** | ✅ | ❌ | ❌ | ❌ | ✅ |

---

## 📊 Updated Flow

### **New Shot Switching Flow:**

```
User Action: Switch from shot 0010 to shot 0020
    ↓
1. Save Current Shot Versions
   For each MultishotRead node:
     - Read shot_version knob: "v002"
     - Save to shot_versions JSON: {"SWA_Ep01_sq0010_SH0010": "v002"}
    ↓
2. Update Root Knobs
   - multishot_shot = "SH0020"
    ↓
3. Update Nodes for New Shot
   For each MultishotRead node:
     - Read from shot_versions JSON: "v004"
     - Set shot_version knob: "v004"
    ↓
4. Refresh UI
   - Highlight new active shot
```

---

## ✅ Testing

### **Test Case 1: Basic Version Persistence**

1. Create MultishotRead node
2. Add shots: SH0010, SH0020
3. Set shot to SH0010
4. Change version to v002 (using knob)
5. Set shot to SH0020
6. Change version to v004 (using knob)
7. Set shot back to SH0010
8. **Expected:** Version should be v002 ✅
9. **Before Fix:** Version was v004 ❌

### **Test Case 2: Multiple Nodes**

1. Create 3 MultishotRead nodes (lighting, fx, comp)
2. Add shots: SH0010, SH0020
3. Set shot to SH0010
4. Set versions: lighting=v002, fx=v003, comp=v001
5. Set shot to SH0020
6. Set versions: lighting=v005, fx=v004, comp=v002
7. Set shot back to SH0010
8. **Expected:** lighting=v002, fx=v003, comp=v001 ✅

### **Test Case 3: Mixed Node Types**

1. Create MultishotRead, MultishotWrite, MultishotSwitch nodes
2. Add shots: SH0010, SH0020
3. Switch between shots
4. **Expected:** No errors, only MultishotRead nodes updated ✅
5. **Before Fix:** Errors trying to access shot_versions on Write/Switch nodes ❌

---

## 📝 Files Modified

### **multishot/ui/multishot_manager.py**

**Changes:**
1. Added `_is_multishot_read_node()` method (line 491-514)
2. Added `_save_current_shot_versions()` method (line 516-561)
3. Modified `_set_shot()` to call save function before switching (line 391-397)
4. Updated `_update_nodes_for_shot()` to use proper node detection (line 577)
5. Added `_is_multishot_read_node()` to VersionSettingDialog (line 1101-1127)
6. Updated `_load_nodes()` to use proper node detection (line 1148)

**Lines Added:** ~80 lines
**Lines Modified:** ~10 lines

---

## 🎯 Summary

### **What Was Fixed:**

1. ✅ **Version Persistence:** Current shot's versions are now saved before switching
2. ✅ **Node Type Detection:** Properly distinguish between Read/Write/Switch nodes
3. ✅ **Error Prevention:** No more errors when Write/Switch nodes are present

### **How It Works Now:**

1. User switches from shot A to shot B
2. System saves all node versions for shot A
3. System updates root knobs to shot B
4. System loads all node versions for shot B
5. User switches back to shot A
6. System saves all node versions for shot B
7. System loads all node versions for shot A (correctly restored!)

### **Key Insight:**

The `shot_version` knob is **ephemeral** (changes with current shot), while the `shot_versions` JSON is **persistent** (stores all shots). We need to sync the ephemeral value back to persistent storage before switching.

---

## 🚀 Impact

**Before Fix:**
- ❌ Versions lost when switching shots
- ❌ Errors with Write/Switch nodes
- ❌ Confusing behavior for users

**After Fix:**
- ✅ Versions correctly preserved
- ✅ No errors with mixed node types
- ✅ Predictable, reliable behavior

---

**Bug fixed and tested!** 🎉

