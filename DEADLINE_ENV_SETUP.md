# Deadline Environment Variable Setup for Multishot

This document explains how to configure Deadline to pass required environment variables (NUKE_PATH and OCIO) to render nodes.

## Problem

When rendering on Deadline, the render nodes don't have `NUKE_PATH` set, which means:
- The multishot `init.py` doesn't load
- Individual knobs for variables (ep, seq, shot, PROJ_ROOT, IMG_ROOT) are not created
- TCL expressions like `[value root.ep]` fail

Additionally, OCIO config path needs to be set for proper color management.

## Solution

Add environment variables to the Deadline job submission so they are available on render nodes.

## Method 1: Modify Deadline Repository SubmitNukeToDeadline.py (Recommended)

### Step 1: Locate the Deadline Submission Script

The script is located in your Deadline Repository:
```
<DeadlineRepository>/submission/Nuke/Main/SubmitNukeToDeadline.py
```

### Step 2: Add Environment Variables

Find the section where the job info file is being written (search for `fileHandle.write`).

Add this code after the plugin line and before closing the file:

```python
# Add multishot environment variables
import platform

env_index = 0

# Determine paths based on platform
if platform.system() == 'Windows':
    nuke_path = 'T:/pipeline/development/nuke/nukemultishot'
    ocio_path = 'T:/pipeline/ocio/aces_2.0/studio-config-v1.0.0_aces-v1.3_ocio-v2.0.ocio'
else:
    # Linux (render farm)
    nuke_path = '/mnt/ppr_dev_t/pipeline/development/nuke/nukemultishot'
    ocio_path = '/mnt/ppr_dev_t/pipeline/ocio/aces_2.0/studio-config-v1.0.0_aces-v1.3_ocio-v2.0.ocio'

# Add NUKE_PATH
if os.path.exists(nuke_path):
    fileHandle.write(
        EncodeAsUTF16String(f"EnvironmentKeyValue{env_index}=NUKE_PATH={nuke_path}\n")
    )
    env_index += 1

# Add OCIO
if os.path.exists(ocio_path):
    fileHandle.write(
        EncodeAsUTF16String(f"EnvironmentKeyValue{env_index}=OCIO={ocio_path}\n")
    )
    env_index += 1
```

### Example Integration

```python
# In SubmitNukeToDeadline.py, find this section:
fileHandle = open(jobInfoFile, "wb")
fileHandle.write(EncodeAsUTF16String("Plugin=Nuke\n"))
fileHandle.write(EncodeAsUTF16String("Name=%s\n" % jobName))
# ... other job info ...

# ADD THIS SECTION HERE:
# ============================================================
# Add multishot environment variables
# ============================================================
import platform

env_index = 0

# Determine paths based on platform
if platform.system() == 'Windows':
    nuke_path = 'T:/pipeline/development/nuke/nukemultishot'
    ocio_path = 'T:/pipeline/ocio/aces_2.0/studio-config-v1.0.0_aces-v1.3_ocio-v2.0.ocio'
else:
    # Linux (render farm)
    nuke_path = '/mnt/ppr_dev_t/pipeline/development/nuke/nukemultishot'
    ocio_path = '/mnt/ppr_dev_t/pipeline/ocio/aces_2.0/studio-config-v1.0.0_aces-v1.3_ocio-v2.0.ocio'

# Add NUKE_PATH
if os.path.exists(nuke_path):
    fileHandle.write(
        EncodeAsUTF16String("EnvironmentKeyValue{0}=NUKE_PATH={1}\n".format(env_index, nuke_path))
    )
    env_index += 1

# Add OCIO
if os.path.exists(ocio_path):
    fileHandle.write(
        EncodeAsUTF16String("EnvironmentKeyValue{0}=OCIO={1}\n".format(env_index, ocio_path))
    )
    env_index += 1
# ============================================================

fileHandle.close()
```

## Method 2: Use the Provided Hook Script

We've provided a helper script `tests/deadline_env_hook.py` that you can integrate:

```python
# In SubmitNukeToDeadline.py
import sys
sys.path.append('/path/to/nukemultishot/tests')
from deadline_env_hook import add_multishot_env_vars

# After opening the job info file:
fileHandle = open(jobInfoFile, "wb")
fileHandle.write(EncodeAsUTF16String("Plugin=Nuke\n"))
# ... other job info ...

# Add multishot environment variables
next_index = add_multishot_env_vars(fileHandle, start_index=0)

fileHandle.close()
```

## Verification

After modifying the submission script:

1. Submit a Nuke job to Deadline
2. In Deadline Monitor, select the job
3. Go to **Job Details** tab
4. Look for **Environment** section
5. You should see:
   ```
   NUKE_PATH=/mnt/ppr_dev_t/pipeline/development/nuke/nukemultishot
   OCIO=/mnt/ppr_dev_t/pipeline/ocio/aces_2.0/studio-config-v1.0.0_aces-v1.3_ocio-v2.0.ocio
   ```

## Testing

1. Submit a render job with multishot nodes
2. Check the render log for:
   ```
   Loading /mnt/ppr_dev_t/pipeline/development/nuke/nukemultishot/init.py
   Multishot: Batch mode detected - initializing variables only...
   ✅ Multishot: Variables initialized for batch mode
   ```

3. The render should complete without errors about missing variables

## Troubleshooting

### Environment variables not showing in Deadline

- Check that the paths exist on both Windows and Linux
- Verify the SubmitNukeToDeadline.py was modified correctly
- Restart Nuke after modifying the submission script

### Still getting "No such file or directory" errors

- Check that path mapping is configured in Deadline Repository Options
- Verify that the multishot init.py is being loaded (check render logs)
- Ensure the onScriptLoad callback is set in the Root node (open script and check)

## Path Mapping

Deadline's path mapping should already be configured at the repository level:
- `V:` → `/mnt/igloo_swa_v/`
- `W:` → `/mnt/igloo_swa_w/`
- `T:` → `/mnt/ppr_dev_t/`

The environment variables use the Linux paths directly, so they work correctly on render nodes.

