# Example init.py for user's .nuke directory
# Place this file at: C:\Users\[username]\.nuke\init.py

import nuke
import sys
import os

# Add multishot to Nuke's plugin path
multishot_path = r'T:\pipeline\development\nuke\nukemultishot'

# Check if path exists
if os.path.exists(multishot_path):
    # Add to plugin path
    nuke.pluginAddPath(multishot_path)
    print(f"Added multishot path: {multishot_path}")
else:
    print(f"Warning: Multishot path not found: {multishot_path}")
    # Try alternative paths
    alternative_paths = [
        r'C:\Users\Admin\Documents\augment-projects\nukemultishot',
        r'C:\nukemultishot',
        r'D:\nukemultishot'
    ]
    
    for alt_path in alternative_paths:
        if os.path.exists(alt_path):
            nuke.pluginAddPath(alt_path)
            print(f"Added alternative multishot path: {alt_path}")
            break
    else:
        print("Could not find multishot in any expected location")

# Optional: Auto-initialize multishot when Nuke starts
def auto_init_multishot():
    """Auto-initialize multishot when a script is loaded."""
    try:
        import multishot
        multishot.initialize()
        print("Multishot auto-initialized")
    except Exception as e:
        print(f"Could not auto-initialize multishot: {e}")

# Add callback to initialize when root node is created
nuke.addOnCreate(auto_init_multishot, nodeClass='Root')
