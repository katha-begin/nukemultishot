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

        print("Multishot: Variables initialized for batch mode")

        # Fix OCIO display settings for batch mode
        fix_ocio_display_for_batch_mode()

    except Exception as e:
        print("Multishot: Error initializing variables in batch mode: {}".format(e))
        import traceback
        traceback.print_exc()



def fix_ocio_display_for_batch_mode():
    """
    Fix OCIO display/colorspace settings for batch mode rendering.

    Common issues:
    1. Display device names (e.g., "sRGB - Display") used as colorspaces in Read/Write nodes
    2. Invalid viewer settings in batch mode

    This function fixes these issues by:
    - Replacing display device names with proper colorspaces
    - Setting safe defaults for viewer nodes
    """
    try:
        import nuke

        # CRITICAL: Always fix Output Transform, even with default OCIO
        # Nuke 16's Output Transform adds display/view knobs that cause errors in batch mode
        print("Multishot: Fixing Output Transform for batch mode...")

        # Get OCIO config (may be custom or default)
        ocio_config_path = nuke.root().knob('customOCIOConfigPath')
        if ocio_config_path and ocio_config_path.value():
            print("  OCIO config: {}".format(ocio_config_path.value()))
        else:
            print("  OCIO config: default")

        # Map of display device names to proper colorspaces
        display_to_colorspace_map = {
            'sRGB - Display': 'sRGB - Texture',
            'Rec.1886 Rec.709 - Display': 'Rec.709 - Display',
            'Rec.1886 Rec.2020 - Display': 'Rec.2020 - Display',
        }

        fixed_count = 0

        # Fix Read nodes
        for node in nuke.allNodes('Read'):
            try:
                if node.knob('colorspace'):
                    current_cs = node.knob('colorspace').value()
                    if current_cs in display_to_colorspace_map:
                        new_cs = display_to_colorspace_map[current_cs]
                        node.knob('colorspace').setValue(new_cs)
                        print("  Read '{}': changed colorspace '{}' -> '{}'".format(
                            node.name(), current_cs, new_cs))
                        fixed_count += 1
            except Exception as e:
                print("  Warning: Could not fix Read node '{}': {}".format(node.name(), e))

        # Fix Write nodes
        for node in nuke.allNodes('Write'):
            try:
                # Fix colorspace if needed
                if node.knob('colorspace'):
                    current_cs = node.knob('colorspace').value()
                    if current_cs in display_to_colorspace_map:
                        new_cs = display_to_colorspace_map[current_cs]
                        node.knob('colorspace').setValue(new_cs)
                        print("  Write '{}': changed colorspace '{}' -> '{}'".format(
                            node.name(), current_cs, new_cs))
                        fixed_count += 1

                # CRITICAL: Fix invalid display/view values in Output Transform
                # If display="default", it's not a valid display name in any OCIO config
                # We need to query the OCIO config for valid display/view values
                if node.knob('useOCIODisplayView') and node.knob('useOCIODisplayView').value():
                    display_knob = node.knob('display')
                    view_knob = node.knob('view')

                    if display_knob and view_knob:
                        current_display = display_knob.value()
                        current_view = view_knob.value()

                        # If display is "default" or empty, query OCIO for valid values
                        if current_display == "default" or current_display == "":
                            try:
                                # Get available displays from OCIO config
                                import PyOpenColorIO as OCIO
                                config = OCIO.GetCurrentConfig()

                                # Get the default display
                                default_display = config.getDefaultDisplay()
                                if default_display:
                                    # Get the default view for this display
                                    default_view = config.getDefaultView(default_display)

                                    display_knob.setValue(default_display)
                                    view_knob.setValue(default_view)
                                    print("  Write '{}': fixed Output Transform display '{}' -> '{}', view '{}' -> '{}'".format(
                                        node.name(), current_display, default_display, current_view, default_view))
                                    fixed_count += 1
                            except Exception as ocio_error:
                                print("  Warning: Could not query OCIO config for Write '{}': {}".format(node.name(), ocio_error))

            except Exception as e:
                print("  Warning: Could not fix Write node '{}': {}".format(node.name(), e))

        # Fix Viewer nodes (set to default/none in batch mode)
        for node in nuke.allNodes('Viewer'):
            try:
                # In batch mode, viewers don't need specific display settings
                # Set to 'None' or 'default' to avoid errors
                if node.knob('viewerProcess'):
                    node.knob('viewerProcess').setValue('None')
                    print("  Viewer '{}': set viewerProcess to 'None'".format(node.name()))
                    fixed_count += 1
            except Exception as e:
                print("  Warning: Could not fix Viewer '{}': {}".format(node.name(), e))

        if fixed_count > 0:
            print("Multishot: Fixed {} OCIO settings for batch mode".format(fixed_count))
        else:
            print("Multishot: No OCIO settings needed fixing")

    except Exception as e:
        print("Multishot: Warning - Could not fix OCIO settings: {}".format(e))
        # Don't raise - this is not critical

def initialize_multishot():
    """Initialize the Multishot Workflow System."""
    try:
        print("Multishot: Starting initialization...")

        # Add multishot package to Python path if not already there
        current_dir = os.path.dirname(__file__)
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
            print("Multishot: Added {} to Python path".format(current_dir))

        # Import and initialize multishot
        import multishot
        print("Multishot: Imported multishot v{}".format(multishot.__version__))

        success = multishot.initialize()

        if success:
            print("Multishot Workflow System v{} loaded successfully".format(multishot.__version__))
            print("   - Menu: Multishot > Browser")
            print("   - Toolbar: Look for 'Multishot' in the toolbar")
            print("   - Shortcuts: Ctrl+Shift+M (Browser), F5 (Refresh Context)")

            # Load gizmos and toolsets
            try:
                from multishot.utils.gizmo_loader import load_gizmos_and_toolsets
                from multishot.core.variables import VariableManager

                variable_manager = VariableManager()
                loader = load_gizmos_and_toolsets(variable_manager)
                print("   - Loaded: {}".format(loader.get_loaded_summary()))
            except Exception as e:
                print("   Warning: Could not load gizmos/toolsets: {}".format(e))
        else:
            print("Failed to initialize Multishot Workflow System")

    except Exception as e:
        print("Error loading Multishot Workflow System: {}".format(e))
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

        # Also add as callbacks for when new scripts are loaded
        nuke.addOnScriptLoad(ensure_variables_for_batch_mode)
        nuke.addOnCreate(ensure_variables_for_batch_mode, nodeClass='Root')

except ImportError:
    # Not in Nuke environment
    pass
