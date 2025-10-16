"""
Nuke initialization script for the Multishot Workflow System.

This file is automatically loaded when Nuke starts up if the multishot
directory is in the NUKE_PATH.
"""

import os
import sys

def initialize_multishot():
    """Initialize the Multishot Workflow System."""
    try:
        print("Multishot: Starting initialization...")

        # Add multishot package to Python path if not already there
        current_dir = os.path.dirname(__file__)
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
            print(f"Multishot: Added {current_dir} to Python path")

        # Import and initialize multishot
        import multishot
        print(f"Multishot: Imported multishot v{multishot.__version__}")

        success = multishot.initialize()

        if success:
            print("✅ Multishot Workflow System v{} loaded successfully".format(multishot.__version__))
            print("   - Menu: Multishot > Browser")
            print("   - Toolbar: Look for 'Multishot' in the toolbar")
            print("   - Shortcuts: Ctrl+Shift+M (Browser), F5 (Refresh Context)")

            # Load gizmos and toolsets
            try:
                from multishot.utils.gizmo_loader import load_gizmos_and_toolsets
                from multishot.core.variables import VariableManager

                variable_manager = VariableManager()
                loader = load_gizmos_and_toolsets(variable_manager)
                print(f"   - Loaded: {loader.get_loaded_summary()}")
            except Exception as e:
                print(f"   ⚠️  Warning: Could not load gizmos/toolsets: {e}")
        else:
            print("❌ Failed to initialize Multishot Workflow System")

    except Exception as e:
        print(f"❌ Error loading Multishot Workflow System: {e}")
        import traceback
        traceback.print_exc()

# Only initialize in GUI mode
try:
    import nuke
    if nuke.GUI:
        # Initialize immediately when this file is loaded
        # This happens when Nuke starts and loads files from NUKE_PATH
        initialize_multishot()

        # Also add as callback for new scripts (backup)
        nuke.addOnCreate(initialize_multishot, nodeClass='Root')
except ImportError:
    # Not in Nuke environment
    pass
