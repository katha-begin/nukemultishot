# OCIO Display Error Fix - "Bad value for display : sRGB - Display"

## Problem

When submitting Nuke scripts to Deadline, renders fail with:

```
ERROR: Bad value for display : sRGB - Display
```

This error occurs even though:
- The same script works fine in GUI mode
- The OCIO config file exists and is valid
- The display device "sRGB - Display" is defined in the OCIO config

## Root Cause

The error happens because **display device names are being used as colorspaces** in Read/Write nodes.

### Understanding OCIO Terminology

In OCIO configs, there are two different concepts:

1. **Display Devices** - For viewing (e.g., "sRGB - Display", "Rec.1886 Rec.709 - Display")
2. **Colorspaces** - For file I/O (e.g., "sRGB - Texture", "Rec.709 - Display", "ACES - ACEScg")

The OCIO config lists display device names in `inactive_colorspaces`, meaning they **should NOT be used as colorspaces** in Read/Write nodes.

### Why It Works in GUI But Fails in Batch Mode

- **GUI mode**: Nuke is more forgiving and may auto-correct invalid colorspace settings
- **Batch mode**: Nuke strictly validates OCIO settings and fails immediately

### When The Error Occurs

The error happens during **script loading** when Nuke parses the `.nk` file and encounters:

```python
Read {
    colorspace "sRGB - Display"  # ❌ WRONG - This is a display device, not a colorspace
    ...
}
```

This happens **before** any Python callbacks (like `init.py`) can run, so we can't fix it programmatically after the fact.

## Solution

### Option 1: Fix Scripts Before Submission (RECOMMENDED)

**Before submitting to Deadline**, run this function in the Nuke Script Editor:

```python
# Run this in Nuke Script Editor BEFORE submitting to Deadline
import sys
sys.path.insert(0, 'T:/pipeline/development/nuke/nukemultishot/tests')  # Windows
# sys.path.insert(0, '/mnt/ppr_dev_t/pipeline/development/nuke/nukemultishot/tests')  # Linux

from deadline_env_hook import fix_ocio_in_current_script
fix_ocio_in_current_script()

# Save the script
import nuke
nuke.scriptSave()
```

This will:
1. Scan all Read/Write nodes
2. Replace display device names with proper colorspaces:
   - `"sRGB - Display"` → `"sRGB - Texture"`
   - `"Rec.1886 Rec.709 - Display"` → `"Rec.709 - Display"`
   - `"Rec.1886 Rec.2020 - Display"` → `"Rec.2020 - Display"`
3. Save the script with fixes

### Option 2: Don't Set OCIO Environment Variable in Deadline

If you're setting the `OCIO` environment variable in Deadline job submission, **remove it**.

The Nuke script already has the OCIO config path embedded in the Root node:

```python
Root {
    customOCIOConfigPath "/mnt/ppr_dev_t/pipeline/ocio/aces_2.0/studio-config-v1.0.0_aces-v1.3_ocio-v2.0.ocio"
}
```

Nuke will use this embedded path automatically. Setting the `OCIO` environment variable can cause conflicts.

**In your Deadline submission script**, comment out or remove the OCIO environment variable:

```python
# DON'T DO THIS:
# job_info_file_handle.write(EncodeAsUTF16String("EnvironmentKeyValue0=OCIO=/path/to/config.ocio\n"))

# The script already has customOCIOConfigPath set in the Root node
```

### Option 3: Use Correct Colorspaces From The Start

When setting colorspaces in Nuke GUI:

✅ **Correct colorspaces for Read/Write nodes:**
- `sRGB - Texture`
- `Rec.709 - Display`
- `Rec.2020 - Display`
- `ACES - ACEScg`
- `ACES - ACES2065-1`
- `Linear - sRGB`
- `Raw`

❌ **AVOID these (they're display devices, not colorspaces):**
- `sRGB - Display`
- `Rec.1886 Rec.709 - Display`
- `Rec.1886 Rec.2020 - Display`
- `Rec.2100-HLG - Display`
- `Rec.2100-PQ - Display`

**Tip**: Display device names usually have " - Display" suffix and appear in the OCIO dropdown, but they're meant for Viewer nodes, not Read/Write nodes.

## How To Check Your Script

Run this in Nuke Script Editor to check for problematic colorspaces:

```python
import nuke

# Check Read nodes
for node in nuke.allNodes('Read'):
    if node.knob('colorspace'):
        cs = node.knob('colorspace').value()
        if '- Display' in cs:
            print("❌ Read '{}': colorspace = '{}'".format(node.name(), cs))

# Check Write nodes
for node in nuke.allNodes('Write'):
    if node.knob('colorspace'):
        cs = node.knob('colorspace').value()
        if '- Display' in cs:
            print("❌ Write '{}': colorspace = '{}'".format(node.name(), cs))
```

If you see any output, those nodes need to be fixed.

## Testing

After applying the fix:

1. **Save the script** with the corrected colorspaces
2. **Submit to Deadline**
3. **Check render logs** - should see no OCIO errors
4. **Render should complete successfully**

## Prevention

To prevent this issue in the future:

1. **Train artists** to use proper colorspaces (not display device names)
2. **Add a pre-submission check** that runs `fix_ocio_in_current_script()` automatically
3. **Don't set OCIO environment variable** in Deadline - let scripts use embedded config path
4. **Use the automatic fix** in `tests/deadline_env_hook.py` before submission

## Related Files

- `tests/deadline_env_hook.py` - Contains `fix_ocio_in_current_script()` function
- `init.py` - Contains `fix_ocio_display_for_batch_mode()` (runs after script loads)
- `DEADLINE_ENV_SETUP.md` - Environment variable setup documentation

## Summary

The key insight: **Display device names ≠ Colorspaces**

- Display devices are for **viewing** (Viewer nodes)
- Colorspaces are for **file I/O** (Read/Write nodes)

Always use proper colorspaces in Read/Write nodes, and the error will go away!

