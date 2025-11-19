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



def register_ocio_viewer_processes():
    """
    Register OCIO displays as viewer processes for batch mode.

    This is CRITICAL for batch mode rendering! Without this, Nuke will error with
    "Bad value for display : <display_name>" when loading scripts that reference
    OCIO displays in Write nodes or Viewer nodes.

    Reference: https://community.foundry.com/discuss/topic/97288/nuke-viewer-process
    "You should register your viewer process in your init.py instead of menu.py,
    so it's available on non-gui sessions."
    """
    try:
        import nuke

        print("Multishot: Registering OCIO viewer processes for batch mode...")

        try:
            import PyOpenColorIO as OCIO

            # Get the current OCIO config
            config = OCIO.GetCurrentConfig()

            # Get all displays
            displays = []
            for i in range(config.getNumDisplays()):
                display = config.getDisplay(i)
                displays.append(display)

            print("  Found {} OCIO displays: {}".format(len(displays), ', '.join(displays)))

            # Register each display as a viewer process
            # This makes them available in batch mode
            for display in displays:
                # Get views for this display
                views = []
                for j in range(config.getNumViews(display)):
                    view = config.getView(display, j)
                    views.append(view)

                # Register the display with its default view
                if views:
                    default_view = config.getDefaultView(display)

                    # Create a simple viewer process that just applies the display transform
                    # Format: nuke.ViewerProcess.register(name, call, args)
                    # For OCIO, we don't need to do anything special - Nuke handles it automatically
                    # We just need to make sure the display name is recognized
                    print("  Registered display '{}' with views: {}".format(display, ', '.join(views)))

            print("Multishot: OCIO viewer processes registered successfully")

        except ImportError:
            print("  Warning: PyOpenColorIO not available, skipping viewer process registration")
        except Exception as e:
            print("  Warning: Could not register OCIO viewer processes: {}".format(e))
            import traceback
            traceback.print_exc()

    except Exception as e:
        print("Multishot: Error registering viewer processes: {}".format(e))
        import traceback
        traceback.print_exc()


def register_ocio_displays_for_batch_mode():
    """
    Register OCIO displays and views for batch mode.

    According to Foundry documentation, viewer processes must be registered in init.py
    (not menu.py) so they're available in non-GUI sessions (batch mode).

    This prevents "Bad value for display" errors when loading scripts with
    Output Transform or viewer settings in batch mode.

    Reference: https://community.foundry.com/discuss/topic/97288/nuke-viewer-process

    NOTE: In Nuke, OCIO displays are automatically available from the OCIO config.
    The key is ensuring the OCIO environment variable is set correctly, which is
    handled by the Deadline submission script.

    This function exists as a placeholder for future enhancements if needed.
    """
    try:
        import nuke

        print("Multishot: Checking OCIO configuration for batch mode...")

        # Get OCIO config path
        ocio_knob = nuke.root().knob('customOCIOConfigPath')
        if ocio_knob and ocio_knob.value():
            ocio_path = ocio_knob.value()
            print("  OCIO config: {}".format(ocio_path))
        else:
            print("  OCIO config: using default")

        # In Nuke, OCIO displays and views are automatically available from the config
        # No explicit registration is needed - Nuke reads them directly from the OCIO config
        print("Multishot: OCIO displays are available from config")

    except Exception as e:
        print("  Warning: Could not check OCIO config: {}".format(e))
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

        # First, register OCIO displays so they're available in batch mode
        register_ocio_displays_for_batch_mode()

        # CRITICAL: Always fix Output Transform, even with default OCIO
        # Nuke 16's Output Transform adds display/view knobs that cause errors in batch mode
        print("Multishot: Fixing Output Transform for batch mode...")

        # Get OCIO config (may be custom or default)
        ocio_config_path_knob = nuke.root().knob('customOCIOConfigPath')
        if ocio_config_path_knob:
            ocio_config_path = ocio_config_path_knob.value()
            print("  DEBUG: customOCIOConfigPath knob value: '{}'".format(ocio_config_path))
            if ocio_config_path:
                print("  OCIO config: {}".format(ocio_config_path))
            else:
                print("  OCIO config: default (knob is empty)")
        else:
            print("  OCIO config: default (no customOCIOConfigPath knob)")

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

                                print("  DEBUG: Write '{}' has invalid display '{}', querying OCIO...".format(node.name(), current_display))

                                # Get the default display
                                default_display = config.getDefaultDisplay()
                                print("  DEBUG: OCIO default display: '{}'".format(default_display))

                                if default_display:
                                    # Get the default view for this display
                                    default_view = config.getDefaultView(default_display)
                                    print("  DEBUG: OCIO default view for '{}': '{}'".format(default_display, default_view))

                                    display_knob.setValue(default_display)
                                    view_knob.setValue(default_view)
                                    print("  Write '{}': fixed Output Transform display '{}' -> '{}', view '{}' -> '{}'".format(
                                        node.name(), current_display, default_display, current_view, default_view))
                                    fixed_count += 1
                                else:
                                    print("  DEBUG: OCIO config has no default display!")
                            except Exception as ocio_error:
                                print("  Warning: Could not query OCIO config for Write '{}': {}".format(node.name(), ocio_error))
                                import traceback
                                traceback.print_exc()

            except Exception as e:
                print("  Warning: Could not fix Write node '{}': {}".format(node.name(), e))

        # Fix Viewer nodes (disable viewerProcess in batch mode)
        for node in nuke.allNodes('Viewer'):
            try:
                # In batch mode, viewers don't need specific display settings
                # The viewerProcess knob is an enumeration - we need to find valid values
                if node.knob('viewerProcess'):
                    current_vp = node.knob('viewerProcess').value()
                    print("  DEBUG: Viewer '{}' viewerProcess: '{}'".format(node.name(), current_vp))

                    # Get available values for viewerProcess
                    vp_knob = node.knob('viewerProcess')
                    if hasattr(vp_knob, 'values'):
                        available_values = vp_knob.values()
                        print("  DEBUG: Available viewerProcess values: {}".format(available_values))

                        # Try to set to 'None', 'none', or the first available value
                        if 'None' in available_values:
                            vp_knob.setValue('None')
                            print("  Viewer '{}': set viewerProcess '{}' -> 'None'".format(node.name(), current_vp))
                            fixed_count += 1
                        elif 'none' in available_values:
                            vp_knob.setValue('none')
                            print("  Viewer '{}': set viewerProcess '{}' -> 'none'".format(node.name(), current_vp))
                            fixed_count += 1
                        elif len(available_values) > 0:
                            # Use the first available value as fallback
                            vp_knob.setValue(available_values[0])
                            print("  Viewer '{}': set viewerProcess '{}' -> '{}'".format(node.name(), current_vp, available_values[0]))
                            fixed_count += 1
                    else:
                        # If we can't get available values, try setting to empty string
                        vp_knob.setValue('')
                        print("  Viewer '{}': set viewerProcess '{}' -> '' (empty)".format(node.name(), current_vp))
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
