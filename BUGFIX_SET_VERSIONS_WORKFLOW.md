# Bug Fix: Set Versions Workflow and Node Filtering

## 🐛 Bug Description

**Issue 1:** When clicking "Set Versions" button, the shot was not being set until after setting versions in the dialog.

**Problem:**
1. User clicks "Set Versions" for shot 0010
2. Dialog opens but shot context is still on previous shot (e.g., 0020)
3. Version scanning uses wrong shot context
4. User sets versions
5. Shot is never actually set to 0010

**Issue 2:** Multishot Manager was showing ALL nodes with `multishot_sep` knob, including MultishotWrite and MultishotSwitch nodes, which don't have version control.

---

## 🔍 Analysis

### **Issue 1: Set Versions Workflow**

**Original Flow:**
```
User clicks "Set Versions" for shot 0010
    ↓
Open VersionSettingDialog
    ↓
Dialog scans for versions using CURRENT shot context (wrong shot!)
    ↓
User sets versions
    ↓
Dialog closes
    ↓
Shot is NEVER set to 0010!
```

**Problem:** The `_set_versions()` method only opened the dialog without setting the shot first.

---

### **Issue 2: Node Filtering**

**Original Behavior:**
- Multishot Manager showed ALL nodes with `multishot_sep` knob
- This included MultishotWrite and MultishotSwitch nodes
- These nodes don't have per-shot version control
- Caused confusion and potential errors

**What Should Happen:**
- Only show MultishotRead nodes (images, geometry, cameras)
- Filter out MultishotWrite nodes (render outputs)
- Filter out MultishotSwitch nodes (shot switching)

---

## 🔧 Solution

### **Fix 1: Set Shot Before Opening Version Dialog**

Modified `_set_versions()` to call `_set_shot()` BEFORE opening the dialog:

```python
def _set_versions(self, shot_data):
    """Open version setting dialog for a shot."""
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
```

**New Flow:**
```
User clicks "Set Versions" for shot 0010
    ↓
Call _set_shot(shot_0010)
    ├─ Save current shot's versions
    ├─ Update root knobs to shot 0010
    ├─ Set frame range from JSON
    ├─ Update variable manager
    └─ Update all nodes for shot 0010
    ↓
Open VersionSettingDialog
    ├─ Scan versions using CORRECT shot context (0010)
    └─ Show available versions
    ↓
User sets versions
    ↓
Dialog closes
    ↓
✅ Shot is already set to 0010!
```

---

### **Fix 2: Filter to Only Show MultishotRead Nodes**

Updated `_update_all_to_latest()` to use proper node filtering:

**Before:**
```python
all_nodes = nuke.allNodes()
multishot_nodes = [n for n in all_nodes if n.knob('multishot_sep')]
```

**After:**
```python
all_nodes = nuke.allNodes()
multishot_nodes = [n for n in all_nodes if self._is_multishot_read_node(n)]
```

**Node Detection Function:**
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

---

## 📊 Updated Workflows

### **Workflow 1: Set Shot Button**

```
User clicks "Set Shot" for shot 0010
    ↓
1. Save current shot's versions (if any)
2. Update root knobs to shot 0010
3. Set frame range from JSON
4. Update variable manager
5. Update all MultishotRead nodes
6. Refresh UI
    ↓
✅ Shot is set to 0010
✅ All nodes show correct versions for 0010
```

---

### **Workflow 2: Set Versions Button**

```
User clicks "Set Versions" for shot 0010
    ↓
1. Call _set_shot(shot_0010)
   ├─ Save current shot's versions
   ├─ Update root knobs to shot 0010
   ├─ Set frame range from JSON
   ├─ Update variable manager
   └─ Update all nodes for shot 0010
    ↓
2. Open VersionSettingDialog
   ├─ Load all MultishotRead nodes (filtered!)
   ├─ Scan versions for each node
   └─ Show version dropdowns
    ↓
3. User selects versions
    ↓
4. User clicks "Apply"
   ├─ Update shot_version knobs
   └─ Save to shot_versions JSON
    ↓
✅ Shot is set to 0010
✅ Versions are updated
```

---

## 🎯 Node Filtering Summary

### **What Gets Shown in Multishot Manager:**

| Node Type | Shown in Manager | Has Version Control | Reason |
|-----------|------------------|---------------------|--------|
| **MultishotRead** | ✅ YES | ✅ YES | Main use case - read plates/renders |
| **MultishotWrite** | ❌ NO | ❌ NO | Output node - no version selection |
| **MultishotSwitch** | ❌ NO | ❌ NO | Switching node - no version selection |
| **Regular Read** | ❌ NO | ❌ NO | Not a multishot node |
| **Regular Write** | ❌ NO | ❌ NO | Not a multishot node |

### **MultishotRead Node Types:**

The MultishotRead node supports different asset types:
- **Images:** Rendered plates, comp elements (EXR, JPEG, etc.)
- **Geometry:** Alembic caches, FBX, OBJ files
- **Cameras:** Camera data, tracking info

All of these use the same MultishotRead node class and have per-shot version control.

---

## ✅ Testing

### **Test Case 1: Set Versions Workflow**

1. Create MultishotRead node
2. Add shots: SH0010, SH0020
3. Set shot to SH0010 (using "Set Shot" button)
4. Switch to SH0020 (using "Set Shot" button)
5. Click "Set Versions" for SH0010
6. **Expected:** 
   - Shot is set to SH0010 BEFORE dialog opens ✅
   - Version scanning uses SH0010 context ✅
   - Available versions are correct for SH0010 ✅
7. **Before Fix:**
   - Shot was still SH0020 ❌
   - Version scanning used wrong context ❌

---

### **Test Case 2: Node Filtering**

1. Create 3 nodes:
   - MultishotRead (lighting)
   - MultishotWrite (comp_render)
   - MultishotSwitch (shot switcher)
2. Open Multishot Manager
3. Click "Set Versions" for any shot
4. **Expected:**
   - Only MultishotRead node appears in dialog ✅
   - MultishotWrite is filtered out ✅
   - MultishotSwitch is filtered out ✅
5. **Before Fix:**
   - All 3 nodes appeared ❌
   - Errors trying to set versions on Write/Switch ❌

---

### **Test Case 3: Multiple Read Nodes**

1. Create 3 MultishotRead nodes:
   - lighting (images)
   - fx (images)
   - anim (geometry)
2. Add shots: SH0010, SH0020
3. Click "Set Versions" for SH0010
4. **Expected:**
   - Shot is set to SH0010 first ✅
   - All 3 Read nodes appear in dialog ✅
   - Version scanning works for all nodes ✅
   - Can set different versions for each node ✅

---

## 📝 Files Modified

### **multishot/ui/multishot_manager.py**

**Changes:**

1. **Modified `_set_versions()` method (line 748-770)**
   - Added call to `_set_shot()` before opening dialog
   - Ensures shot context is set correctly

2. **Modified `_update_all_to_latest()` method (line 870-883)**
   - Changed node filtering to use `_is_multishot_read_node()`
   - Only processes MultishotRead nodes

**Lines Modified:** ~15 lines

---

## 🎯 Summary

### **What Was Fixed:**

1. ✅ **Set Versions Workflow:** Shot is now set BEFORE opening version dialog
2. ✅ **Node Filtering:** Only MultishotRead nodes shown in Multishot Manager
3. ✅ **Version Scanning:** Uses correct shot context for version detection
4. ✅ **Error Prevention:** No more errors from Write/Switch nodes

### **How It Works Now:**

**Set Shot Button:**
- Sets shot immediately
- Updates all nodes
- Refreshes UI

**Set Versions Button:**
- Sets shot FIRST (same as "Set Shot" button)
- THEN opens version dialog
- Version scanning uses correct context
- Only shows MultishotRead nodes

### **Key Benefits:**

1. **Predictable Behavior:** Shot is always set when you click either button
2. **Correct Context:** Version scanning always uses the right shot
3. **Clean UI:** Only relevant nodes (Read nodes) shown in dialogs
4. **No Errors:** Write/Switch nodes properly filtered out

---

## 🚀 Impact

**Before Fix:**
- ❌ Shot not set when clicking "Set Versions"
- ❌ Version scanning used wrong shot context
- ❌ Write/Switch nodes shown in dialogs
- ❌ Confusing workflow

**After Fix:**
- ✅ Shot always set correctly
- ✅ Version scanning uses correct context
- ✅ Only Read nodes shown
- ✅ Clear, predictable workflow

---

**Bugs fixed and workflow improved!** 🎉

