# Deadline Batch Mode Expression Evaluation Fix

## Problem Summary

When rendering Nuke scripts on Deadline render farm, MultishotRead nodes were failing with the error:

```
ERROR: MultishotRead_lighting_MASTER_CHAR_FACE: [value root.IMG_ROOT][value root.project]/all/scene/[value root.ep]/[value root.seq]/[value root.shot]/lighting/publish/[value parent.MultishotRead_lighting_MASTER_CHAR_FACE.shot_version]/MASTER_CHAR_FACE/MASTER_CHAR_FACE.%04d.exr: Read error: No such file or directory
```

The error shows that **TCL expressions were not being evaluated** - they were being treated as literal strings instead of being evaluated to actual paths.

## Root Cause

There were **TWO issues** causing TCL expressions to fail in batch mode:

### Issue 1: Expression Setting Method

File paths with TCL expressions were being set incorrectly:

**Before (Incorrect):**
```python
file_path = "[value root.IMG_ROOT][value root.project]/all/scene/..."
self.node['file'].setValue(file_path)
```

When using `.setValue()` with TCL expressions, Nuke may not properly mark them for evaluation in batch mode.

**After (Correct):**
```python
file_path = "[value root.IMG_ROOT][value root.project]/all/scene/..."
self.node['file'].fromUserText(file_path)
```

Using `.fromUserText()` ensures that TCL expressions are properly parsed and marked for evaluation.

### Issue 2: Missing Individual Knobs in Batch Mode

The more critical issue was that **individual knobs for context variables didn't exist in batch mode**!

**The Problem:**
- Variables are stored in TWO places:
  1. **JSON knobs** (`multishot_context`, `multishot_custom`) - stores the data
  2. **Individual knobs** (`ep`, `seq`, `shot`, `project`, `PROJ_ROOT`, `IMG_ROOT`) - for `[value root.variable]` access

- In GUI mode: `init.py` runs and creates individual knobs via `VariableManager._ensure_context_variable_knobs()`
- In batch mode: `init.py` had `if nuke.GUI:` check, so it **never ran**, meaning individual knobs were **never created**!
- Result: `[value root.ep]` failed because the `ep` knob didn't exist!

**The Fix:**
Modified `init.py` to run in both GUI and batch mode:
- **GUI mode**: Full initialization with menus and UI
- **Batch mode**: Minimal initialization that ensures individual knobs are created from JSON data

## What Was Fixed

### 1. **multishot/nodes/read_node.py** (Line 268)
Changed from:
```python
self.node['file'].setValue(file_path)
```

To:
```python
self.node['file'].fromUserText(file_path)
```

### 2. **multishot/nodes/write_gizmo.py** (Lines 349-350)
Changed from:
```python
self.write_exr['file'].setValue(exr_template)
self.write_mov['file'].setValue(mov_template)
```

To:
```python
self.write_exr['file'].fromUserText(exr_template)
self.write_mov['file'].fromUserText(mov_template)
```

### 3. **multishot/ui/browser.py** (Lines 1614, 1622)
Changed from:
```python
geo_node['file'].setValue(expr_path)
```

To:
```python
geo_node['file'].fromUserText(expr_path)
```

### 4. **init.py** (Lines 11-106)
**CRITICAL FIX**: Added batch mode support

Changed from:
```python
if nuke.GUI:
    initialize_multishot()
```

To:
```python
if nuke.GUI:
    # GUI mode: Full initialization
    initialize_multishot()
else:
    # Batch mode: Ensure variables are accessible
    ensure_variables_for_batch_mode()
    nuke.addOnScriptLoad(ensure_variables_for_batch_mode)
```

Added new function `ensure_variables_for_batch_mode()` that:
- Reads context variables from JSON knobs (`multishot_context`, `multishot_custom`)
- Creates individual knobs (`ep`, `seq`, `shot`, `project`, `PROJ_ROOT`, `IMG_ROOT`)
- Ensures TCL expressions like `[value root.ep]` can be evaluated

### 5. **Documentation Updates**
- Updated `HOW_MULTISHOT_READ_REMEMBERS_VERSIONS.md` to show correct usage
- Updated `toolset/README.md` examples to use `.fromUserText()`

## Why This Works

### `.setValue()` vs `.fromUserText()`

- **`.setValue()`**: Sets the knob value as a literal string. If the string contains TCL expressions, they may or may not be evaluated depending on context.

- **`.fromUserText()`**: Parses the string as if it were typed by a user in the GUI. This properly handles TCL expressions and ensures they are marked for evaluation.

### Deadline Path Mapping Still Works

The Deadline logs showed that path mapping was working correctly:

```
CheckPathMapping: Swapped " PROJ_ROOT V:/ " with " PROJ_ROOT /mnt/igloo_swa_v/ "
CheckPathMapping: Swapped " IMG_ROOT W:/ " with " IMG_ROOT /mnt/igloo_swa_w/ "
```

The root knob values were being mapped from Windows to Linux paths. The issue was that the expressions referencing these knobs weren't being evaluated.

## Testing

### Local Batch Mode Test
You can test this locally by running Nuke in batch mode:

```bash
# Windows
"C:\Program Files\Nuke16.0v6\Nuke16.0.exe" -t "path\to\your\script.nk"

# Linux
/home/rocky/Nuke16.0v6/Nuke16.0 -t "/path/to/your/script.nk"
```

### Expected Behavior After Fix

1. **On Windows workstation**: Expressions evaluate to Windows paths (V:/, W:/)
2. **On Linux render nodes**: Deadline maps root knobs to Linux paths, expressions evaluate correctly
3. **Batch mode**: Expressions are evaluated at render time, not treated as literal strings

## Technical Details

### How Nuke Stores Expressions in .nk Files

In .nk files, TCL expressions are stored with escaped brackets:

```tcl
Read {
 file "\[value root.IMG_ROOT]/\[value root.project]/plate.%04d.exr"
 name Read1
}
```

When using `.fromUserText()`, Nuke properly handles the conversion from Python string to .nk file format.

### Why Expressions Are Better Than Resolved Paths

The multishot system uses expressions (not resolved paths) for Read nodes because:

1. **Dynamic Updates**: When switching shots, expressions automatically update
2. **Farm Compatible**: Deadline can map the root knob values, expressions evaluate on render nodes
3. **No Rebuilding**: Don't need to rebuild paths when context changes

## Conclusion

The fix ensures that TCL expressions in file knobs are properly evaluated in all contexts:
- ✅ GUI mode (interactive)
- ✅ Batch mode (local `-t` flag)
- ✅ Render farm (Deadline with path mapping)

All values are still stored in the script (PRD 4.1 compliant), and Deadline path mapping continues to work as expected.

