# Multishot Deadline Submission

## Overview

The Multishot system now includes a custom Deadline submission that **automatically** adds required environment variables to render jobs. No manual setup needed!

## Usage

### Method 1: Use Multishot Menu (Recommended)

1. Open your Nuke script
2. Go to **Multishot > Submit to Deadline**
3. The standard Deadline submission dialog will open
4. Environment variables are automatically added!

### Method 2: Python Script

```python
import multishot.deadline
multishot.deadline.submit_to_deadline()
```

## What It Does

The custom submission automatically adds these environment variables to your Deadline job:

### NUKE_PATH
- **Windows**: `T:/pipeline/development/nuke/nukemultishot`
- **Linux**: `/mnt/ppr_dev_t/pipeline/development/nuke/nukemultishot`

This ensures `init.py` loads on render nodes, which creates the individual knobs needed for TCL expressions.

### OCIO
- Uses the OCIO config path from your script's Root node (`customOCIOConfigPath`)
- Falls back to: `T:/pipeline/ocio/aces_2.0/studio-config-v1.0.0_aces-v1.3_ocio-v2.0.ocio` (Windows)
- Or: `/mnt/ppr_dev_t/pipeline/ocio/aces_2.0/studio-config-v1.0.0_aces-v1.3_ocio-v2.0.ocio` (Linux)

## Why This Is Important

Without these environment variables:

❌ **Problem**: TCL expressions show literal text instead of evaluated paths
```
[value root.IMG_ROOT][value root.project]/all/scene/[value root.ep]/...
```

✅ **Solution**: With environment variables, expressions evaluate correctly
```
/mnt/igloo_swa_w/SWA/all/scene/Ep03/sq0060/SH0180/...
```

## How It Works

1. **Monkey-patching**: The custom submission wraps the standard Deadline submission
2. **Environment Injection**: Before opening the dialog, it sets environment variables
3. **Platform Detection**: Automatically uses correct paths for Windows/Linux
4. **Transparent**: Works exactly like standard Deadline submission

## Verification

After submitting, check the Deadline log for these lines:

```
MULTISHOT: Adding environment variables to Deadline job
======================================================================
  NUKE_PATH = /mnt/ppr_dev_t/pipeline/development/nuke/nukemultishot
  OCIO = /mnt/ppr_dev_t/pipeline/ocio/aces_2.0/studio-config-v1.0.0_aces-v1.3_ocio-v2.0.ocio
======================================================================
```

And during rendering:

```
Multishot: Batch mode detected - initializing variables only...
Multishot: Variables initialized for batch mode
```

## Troubleshooting

### "DEADLINE_PATH environment variable is not set"

**Solution**: Install Deadline Client and set `DEADLINE_PATH` environment variable to point to Deadline bin folder.

### "Could not import Deadline submission module"

**Solution**: Make sure Deadline Client is installed and `DEADLINE_PATH` is set correctly.

### Environment variables not showing in Deadline log

**Solution**: 
1. Check that you're using **Multishot > Submit to Deadline** (not standard Deadline submission)
2. Verify paths exist on your system
3. Check console output for error messages

## Manual Method (If Needed)

If you need to use the standard Deadline submission for some reason, you can manually add environment variables:

1. Submit job normally
2. In Deadline Monitor, right-click job
3. Select "Modify Job Properties"
4. Go to "Environment" tab
5. Add:
   - `NUKE_PATH = T:/pipeline/development/nuke/nukemultishot`
   - `OCIO = T:/pipeline/ocio/aces_2.0/studio-config-v1.0.0_aces-v1.3_ocio-v2.0.ocio`

## Technical Details

### Files

- `multishot/deadline/submit.py` - Custom submission implementation
- `multishot/deadline/__init__.py` - Module initialization
- `menu.py` - Menu integration

### Functions

- `get_environment_variables()` - Returns dict of env vars to add
- `submit_to_deadline()` - Main submission function
- `_patch_deadline_submission()` - Monkey-patches standard submission
- `_get_deadline_repository_path()` - Gets Deadline repo path

### Platform Detection

Uses `platform.system()` to determine OS:
- `'Windows'` → Use T:/ paths
- Other (Linux) → Use /mnt/ paths

## Benefits

✅ **Automatic**: No manual environment variable setup
✅ **Consistent**: Same setup for all artists
✅ **Platform-aware**: Correct paths for Windows/Linux
✅ **Transparent**: Works like standard submission
✅ **Reliable**: TCL expressions always evaluate correctly

