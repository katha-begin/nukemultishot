"""
Nuke initialization script for the Multishot Workflow System.

This file is automatically loaded when Nuke starts up if the multishot
directory is in the NUKE_PATH.
"""

import os
import sys

def ensure_variables_for_batch_mode():
    """
    Ensure variables are accessible in batch mode (render farm).
    This is called when a script is loaded in batch mode to ensure
    individual knobs exist for TCL expression evaluation.
    """
    try:
        # Add multishot package to Python path
        current_dir = os.path.dirname(__file__)
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)

        # Import and ensure variables are accessible
        from multishot.core.variables import VariableManager
        vm = VariableManager()

        # Ensure individual knobs exist for context variables (ep, seq, shot, project)
        vm._ensure_context_variable_knobs()

        # Ensure individual knobs exist for root variables (PROJ_ROOT, IMG_ROOT)
        custom_vars = vm.get_custom_variables()
        if custom_vars:
            vm._create_individual_root_knobs(custom_vars)

        print("✅ Multishot: Variables initialized for batch mode")

    except Exception as e:
        print(f"⚠️  Multishot: Error initializing variables in batch mode: {e}")
        import traceback
        traceback.print_exc()

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

# Initialize in both GUI and batch mode
try:
    import nuke

    if nuke.GUI:
        # GUI mode: Full initialization with menus and UI
        initialize_multishot()
        # Also add as callback for new scripts (backup)
        nuke.addOnCreate(initialize_multishot, nodeClass='Root')
    else:
        # Batch mode (render farm): Minimal initialization
        # Only ensure variables are accessible for expression evaluation
        print("Multishot: Batch mode detected - initializing variables only...")

        # Call immediately for current script
        ensure_variables_for_batch_mode()

        # Also add as callback for when scripts are loaded
        nuke.addOnScriptLoad(ensure_variables_for_batch_mode)
        nuke.addOnCreate(ensure_variables_for_batch_mode, nodeClass='Root')

except ImportError:
    # Not in Nuke environment
    pass
