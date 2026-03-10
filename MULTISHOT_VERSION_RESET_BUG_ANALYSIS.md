# 🔍 INVESTIGATION COMPLETE: Multishot Manager Version Reset Bug

## 📋 EXECUTIVE SUMMARY

**✅ GOOD NEWS:** The Multishot Manager UI initialization is **READ-ONLY** and does NOT reset root knobs to "v001".

The VariableManager initialization is also **SAFE** - it only auto-detects context from script filename if context is NOT already stored.

**❌ ROOT CAUSE NOT FOUND** in initialization code. The version reset must be happening elsewhere.

---

## 🔎 DETAILED FINDINGS

### **1. MultishotManagerDialog Initialization (READ-ONLY)**

**Location:** `multishot/ui/multishot_manager.py` lines 27-57

```python
def __init__(self, variable_manager=None, parent=None):
    # Get shared VariableManager instance (does NOT create new one)
    self.variable_manager = get_shared_variable_manager()
    
    # Load shots from root knobs (READ-ONLY)
    self._load_shots()
    
    # Refresh table display (READ-ONLY)
    self._refresh_table(update_current_shot=False)
```

**Verdict:** ✅ **READ-ONLY** - Does NOT modify root knobs

---

### **2. VariableManager Initialization (SAFE)**

**Location:** `multishot/core/variables.py` lines 27-54

```python
def __init__(self):
    if is_batch_mode:
        # BATCH MODE: Do NOT modify variables!
        self.logger.info("VariableManager initialized in batch mode (read-only)")
    else:
        # GUI MODE: Normal initialization
        self._ensure_knobs_exist()
        self._ensure_root_variables_in_script()
        self._auto_detect_context_from_script()  # ← SAFE!
```

**Verdict:** ✅ **SAFE** - Only creates knobs if missing, does NOT reset values

---

### **3. _auto_detect_context_from_script() Method (SAFE)**

**Location:** `multishot/core/variables.py` lines 796-857

**Key Logic:**
```python
# CRITICAL: Check if context already exists in script
existing_context = self.get_context_variables()

# Check if we have a complete context (project, ep, seq, shot)
has_complete_context = all(
    existing_context.get(key)
    for key in ['project', 'ep', 'seq', 'shot']
)

if has_complete_context:
    # Context already exists - DO NOT overwrite with filename!
    # Only update version if it's missing
    if not existing_context.get('version'):
        # Update version from filename
        existing_context['version'] = detected['version']
        self.set_context_variables(existing_context)
    else:
        # Preserve existing context
        return
```

**Verdict:** ✅ **SAFE** - Preserves existing context, only updates missing version

---

## 🤔 WHERE IS THE BUG?

The initialization code is **READ-ONLY and SAFE**. The version reset must be happening:

1. **When user clicks "Set Shot" button** - `_set_shot()` method updates root knobs
2. **When user opens Version Setting dialog** - Dialog loads nodes and may reset versions
3. **In MultishotRead node initialization** - `knobChanged()` callback may reset versions
4. **In some other UI interaction** - Need to trace user actions

---

## 🎯 NEXT STEPS

**Please provide:**
1. **Exact reproduction steps** - What actions trigger the "v001" reset?
2. **Debug output** - Enable logging and capture console output when bug occurs
3. **Script state** - What are the root knob values BEFORE and AFTER the reset?

This will help pinpoint the exact location of the bug.

