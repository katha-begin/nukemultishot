# Deadline Display Error Fix - Lazy Import UI Components

## Problem Summary

When submitting Nuke scripts to Deadline render farm, the render nodes were failing with display/Qt errors:

```
Error: cannot connect to X server
Error: Qt initialization failed
Error: Display not available
```

This prevented the multishot variables from being initialized, causing the same path resolution errors as before.

## Root Cause

The issue was in how UI components were being imported:

### **The Problem Flow:**

```
Deadline Render (batch mode, no display)
  → init.py loads
  → Batch mode detected
  → ensure_variables_for_batch_mode() is called
  → Imports: from multishot.core.variables import VariableManager
  → This triggers multishot/__init__.py to load
  → multishot/__init__.py imports UI components at module level:
      - from .ui.browser import MultishotBrowser
      - from .ui.node_manager import NodeManager
      - from .ui.multishot_manager import MultishotManagerDialog
  → UI components try to import Qt (PySide6/PySide2)
  → Qt requires display/X server
  → ERROR: No display available!
```

### **Why This Happened:**

1. **Module-level imports** in `multishot/__init__.py` (lines 30-32) imported UI classes immediately
2. **Module-level imports** in `multishot/ui/__init__.py` (lines 7-11) also imported UI classes immediately
3. UI classes depend on **Qt (PySide6/PySide2)** which requires a display
4. Deadline render nodes run in **batch mode without display** (no X server)
5. Qt initialization fails → entire import chain fails → variables never initialize

## Solution: Lazy Import Pattern

Implemented lazy imports for all UI components so they're only loaded when actually needed (in GUI mode).

### **Changes Made:**

#### 1. **multishot/__init__.py**

**Before:**
```python
# Import UI components
from .ui.browser import MultishotBrowser
from .ui.node_manager import NodeManager
from .ui.multishot_manager import MultishotManagerDialog
```

**After:**
```python
# UI components are imported lazily to avoid Qt/display errors in batch mode
# They will be imported when needed by get_ui_class() functions

def get_multishot_browser():
    """Get MultishotBrowser class (lazy import)."""
    from .ui.browser import MultishotBrowser
    return MultishotBrowser

def get_node_manager():
    """Get NodeManager class (lazy import)."""
    from .ui.node_manager import NodeManager
    return NodeManager

def get_multishot_manager_dialog():
    """Get MultishotManagerDialog class (lazy import)."""
    from .ui.multishot_manager import MultishotManagerDialog
    return MultishotManagerDialog

# Backward compatibility via __getattr__
def __getattr__(name):
    if name == 'MultishotBrowser':
        return get_multishot_browser()
    elif name == 'NodeManager':
        return get_node_manager()
    elif name == 'MultishotManagerDialog':
        return get_multishot_manager_dialog()
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
```

#### 2. **multishot/ui/__init__.py**

**Before:**
```python
from .browser import MultishotBrowser
from .node_manager import NodeManager, NodeManagerDialog
from .multishot_manager import MultishotManagerDialog
from .qt_utils import get_qt_modules, create_nuke_panel
```

**After:**
```python
# UI components are imported lazily to avoid Qt/display errors in batch mode
# Use the show_*() functions or import directly when needed in GUI mode

def show_browser():
    # Lazy import UI components
    from .browser import MultishotBrowser
    from .qt_utils import create_nuke_panel
    # ... rest of function

# Similar pattern for all show_*() functions
```

#### 3. **setup_ui_integration()**

Added check to skip UI setup in batch mode:

```python
def setup_ui_integration():
    """Setup UI integration with Nuke (only in GUI mode)."""
    try:
        import nuke
        
        # Only setup UI in GUI mode
        if not nuke.GUI:
            print("Multishot: Batch mode detected, skipping UI integration")
            return
        
        # ... rest of UI setup
```

#### 4. **init.py**

Removed remaining emoji characters and f-strings for better compatibility.

## How It Works Now

### **In GUI Mode (Workstation):**
1. User opens Nuke with GUI
2. `init.py` runs → `initialize_multishot()` is called
3. `multishot.initialize()` runs
4. `setup_ui_integration()` checks `nuke.GUI` → True
5. UI menus are created
6. When user clicks menu → UI components are imported on-demand
7. Everything works normally

### **In Batch Mode (Deadline):**
1. Deadline starts Nuke with `-t` flag (batch mode)
2. `init.py` runs → `ensure_variables_for_batch_mode()` is called
3. Imports `VariableManager` from `multishot.core.variables`
4. `multishot/__init__.py` loads but **doesn't import UI components**
5. Variables are initialized successfully
6. No Qt/display errors!
7. Render proceeds normally

## Benefits

1. ✅ **No display errors** on render farm
2. ✅ **Variables initialize correctly** in batch mode
3. ✅ **Backward compatibility** - existing code still works
4. ✅ **GUI mode unaffected** - UI loads normally when needed
5. ✅ **Cleaner separation** - core functionality independent of UI

## Testing

### **Test in GUI Mode:**
```python
# In Nuke GUI
import multishot
multishot.initialize()
# Should work normally, menus appear
```

### **Test in Batch Mode:**
```bash
# On render node
nuke -t script.nk
# Should initialize variables without errors
```

### **Test on Deadline:**
1. Submit a job with multishot nodes
2. Check render logs for:
   ```
   Multishot: Batch mode detected - initializing variables only...
   Multishot: Variables initialized for batch mode
   ```
3. No Qt/display errors should appear
4. Render should complete successfully

## Related Fixes

This fix works together with:
1. **Batch mode variable initialization** (commit 8146990)
2. **onScriptLoad callback** (commit df0d2c7)
3. **Unicode encoding fix** (commit fa4bd7a)
4. **Environment variable setup** (DEADLINE_ENV_SETUP.md)

All these fixes ensure multishot works correctly on Deadline render farm!

