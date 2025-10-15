# Nuke Multishot Workflow System

Production-ready multishot workflow system for Nuke that provides variable-driven asset management, context-aware file operations, and streamlined shot-based compositing workflows.

## Features

- **Dynamic Department Discovery**: Automatically discovers departments from your actual directory structure
- **PRD-Compliant**: Follows the exact directory structure specified in the PRD
- **Context-Aware**: Auto-detects project context from file paths and names
- **Farm Compatible**: Variables embedded in Nuke scripts for render farm compatibility
- **Flexible Path Structure**: Works with your production directory structure

## Installation

### Prerequisites

- Nuke 14.x, 15.x, or 16.x
- Network access to V:/ and W:/ drives

### Simple Installation

1. **Add to NUKE_PATH when launching Nuke:**
   ```bash
   # Windows
   set NUKE_PATH=%NUKE_PATH%;C:\path\to\nukemultishot
   nuke

   # Linux/Mac
   export NUKE_PATH=$NUKE_PATH:/path/to/nukemultishot
   nuke
   ```

2. **Or set NUKE_PATH permanently:**
   - **Windows:** Add `C:\path\to\nukemultishot` to NUKE_PATH environment variable
   - **Linux/Mac:** Add `export NUKE_PATH=$NUKE_PATH:/path/to/nukemultishot` to your shell profile

3. **Launch Nuke** - The Multishot menu will appear automatically

4. **Access via menu:** Multishot > Browser

## Quick Start

1. **Open Multishot Browser**: `Multishot > Browser` or `Ctrl+Shift+M`
2. **Set Project Context**: Select Episode/Sequence/Shot from dropdowns
3. **Create Custom Nodes**: Use `Multishot > Read/Write/Switch` nodes
4. **Manage Nodes**: Use `Multishot > Node Manager` or `Ctrl+Shift+N`

## Directory Structure

The system expects this directory structure:

```
V:/{project}/all/scene/{ep}/{seq}/{shot}/comp/version/{ep}_{seq}_{shot}_comp_v001.nk
W:/{project}/all/scene/{ep}/{seq}/{shot}/lighting/publish/v001/{layer}/{layer}.1001.exr
V:/{project}/all/scene/{ep}/{seq}/{shot}/anim/publish/v001/geometry.abc
```

**Example:**
```
V:/MyProject/all/scene/Ep01/sq0010/SH0010/comp/version/Ep01_sq0010_SH0010_comp_v001.nk
W:/MyProject/all/scene/Ep01/sq0010/SH0010/lighting/publish/v001/beauty/beauty.1001.exr
V:/MyProject/all/scene/Ep01/sq0010/SH0010/anim/publish/v001/geometry.abc
```

## File Naming Convention

- **Nuke Files**: `{ep}_{seq}_{shot}_{department}_{variance}_{version}.nk`
- **Example**: `Ep01_sq0010_SH0010_comp_v001.nk`

## Variables

### Root Variables
- `PROJ_ROOT = V:/` - Project root path
- `IMG_ROOT = W:/` - Image/render root path

### Hierarchical Variables
- `{project}` - Project name (e.g., "PROJECT")
- `{ep}` - Episode (e.g., "Ep01")
- `{seq}` - Sequence (e.g., "sq0010")
- `{shot}` - Shot (e.g., "SH0010")
- `{department}` - Department (auto-detected)
- `{variance}` - Optional variation
- `{version}` - Version number

## Custom Nodes

### MultishotRead
- Variable-driven file paths
- Support for images, geometry, cameras
- Version selection dropdown
- Approval status indication
- Missing frame handling (nearest frame)

### MultishotWrite
- Variable-driven output paths
- Auto-directory creation
- Version management
- Render farm compatible

### MultishotSwitch
- Variable-based input switching
- Shot/sequence context switching
- Dynamic input management

## Compatibility

- **Nuke Versions**: 14.x, 15.x, 16.x
- **Python**: 3.7+
- **UI**: PySide2/PySide6 auto-detection
- **Platforms**: Windows, Linux, macOS

## Troubleshooting

### Empty Dropdowns
- Verify your project root path exists and is accessible
- Check network drive permissions
- Ensure directory structure follows PRD specification

### Import Errors
- Verify NUKE_PATH includes the nukemultishot directory
- Check that multishot directory exists in the path
- Restart Nuke after changing NUKE_PATH

### Path Resolution Issues
- Check that PROJ_ROOT and IMG_ROOT variables are set
- Verify project configuration files exist
- Ensure directory structure matches PRD

### Quick Test
Open Nuke Script Editor and run:
```python
import multishot
multishot.initialize()
print("✅ Multishot loaded successfully")
```

## Support

For issues and feature requests, please check the documentation or contact the development team.

## Version

Current version: 1.0.0 - Production Ready

## License

Copyright (c) 2024 Multishot Development Team. All rights reserved.
