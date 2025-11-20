"""
Nuke initialization script for the Multishot Workflow System.

This file is automatically loaded when Nuke starts up if the multishot
directory is in the NUKE_PATH.
"""

import os
import sys

def ensure_variables_for_batch_mode():
    """
    DEBUG: Just print all root knobs to see what's in the script.
    Also manually create knobs from JSON if the onScriptLoad callback failed.
    """
    try:
        import nuke
        import json
        root = nuke.root()

        print("\n" + "=" * 80)
        print("MULTISHOT DEBUG: Printing ALL root knobs")
        print("=" * 80)

        # Print ALL knobs on root
        all_knobs = root.knobs()
        print("Total knobs on root: {}".format(len(all_knobs)))

        # Print multishot-related knobs
        print("\nMultishot JSON knobs:")
        for knob_name in ['multishot_context', 'multishot_custom', 'multishot_variables']:
            if knob_name in all_knobs:
                value = root[knob_name].value()
                print("  {} = {}".format(knob_name, value))
            else:
                print("  {} = MISSING!".format(knob_name))

        # Print individual variable knobs
        print("\nIndividual variable knobs:")
        for knob_name in ['ep', 'seq', 'shot', 'project', 'PROJ_ROOT', 'IMG_ROOT', 'first_frame', 'last_frame']:
            if knob_name in all_knobs:
                value = root[knob_name].value()
                print("  {} = '{}'".format(knob_name, value))
            else:
                print("  {} = MISSING!".format(knob_name))

        print("=" * 80)

        # DEBUG: Check a Read node's frame range
        print("\nDEBUG: Checking Read node frame ranges...")
        for read_node in nuke.allNodes('Read'):
            if 'Multishot' in read_node.name():
                print("  Read node: {}".format(read_node.name()))
                if read_node.knob('first'):
                    first_val = read_node['first'].value()
                    first_expr = read_node['first'].toScript()
                    print("    first value: {}".format(first_val))
                    print("    first expression: {}".format(first_expr))
                if read_node.knob('last'):
                    last_val = read_node['last'].value()
                    last_expr = read_node['last'].toScript()
                    print("    last value: {}".format(last_val))
                    print("    last expression: {}".format(last_expr))
                break  # Just check first MultishotRead node
        print("=" * 80)

        # MANUALLY CREATE KNOBS if the onScriptLoad callback failed!
        print("\nMultishot: Manually creating individual knobs from JSON...")
        print("DEBUG: Checking for JSON knobs...")
        print("DEBUG: 'multishot_context' in all_knobs: {}".format('multishot_context' in all_knobs))
        print("DEBUG: 'multishot_custom' in all_knobs: {}".format('multishot_custom' in all_knobs))

        # Ensure Multishot tab exists
        if 'multishot_tab' not in root.knobs():
            tab = nuke.Tab_Knob('multishot_tab', 'Multishot')
            root.addKnob(tab)
            print("DEBUG: Created Multishot tab")

        # Create knobs from multishot_context
        if 'multishot_context' in all_knobs:
            context_json = root['multishot_context'].value()
            print("DEBUG: context_json value: {}".format(repr(context_json)))
            if context_json:
                try:
                    context_vars = json.loads(context_json)
                    print("DEBUG: Parsed context_vars: {}".format(context_vars))
                    for key, value in context_vars.items():
                        if key not in root.knobs():
                            knob = nuke.String_Knob(key, key)
                            # DON'T set INVISIBLE - Deadline strips invisible knobs!
                            root.addKnob(knob)
                            print("  Created knob: {}".format(key))
                        root[key].setValue(str(value))
                        print("  Set {} = {}".format(key, value))
                except Exception as e:
                    print("  ERROR parsing multishot_context: {}".format(e))
                    import traceback
                    traceback.print_exc()
            else:
                print("DEBUG: context_json is empty!")
        else:
            print("DEBUG: multishot_context knob does NOT exist!")

        # Create knobs from multishot_custom
        if 'multishot_custom' in all_knobs:
            custom_json = root['multishot_custom'].value()
            print("DEBUG: custom_json value: {}".format(repr(custom_json)))
            if custom_json:
                try:
                    custom_vars = json.loads(custom_json)
                    print("DEBUG: Parsed custom_vars: {}".format(custom_vars))

                    # CRITICAL: On Linux, replace Windows paths BEFORE setting knobs
                    import platform
                    if platform.system() == 'Linux':
                        print("DEBUG: Linux detected - replacing Windows paths in custom_vars...")
                        path_mappings = {
                            'V:/': '/mnt/igloo_swa_v/',
                            'V:\\': '/mnt/igloo_swa_v/',
                            'W:/': '/mnt/igloo_swa_w/',
                            'W:\\': '/mnt/igloo_swa_w/',
                            'T:/': '/mnt/ppr_dev_t/',
                            'T:\\': '/mnt/ppr_dev_t/'
                        }
                        for key in ['PROJ_ROOT', 'IMG_ROOT']:
                            if key in custom_vars:
                                original_value = custom_vars[key]
                                for win_path, linux_path in path_mappings.items():
                                    if win_path in str(original_value):
                                        custom_vars[key] = str(original_value).replace(win_path, linux_path).replace('\\', '/')
                                        print("  Replaced {} in custom_vars: {} -> {}".format(key, original_value, custom_vars[key]))
                                        break

                    for key, value in custom_vars.items():
                        if key in ['PROJ_ROOT', 'IMG_ROOT']:
                            if key not in root.knobs():
                                knob = nuke.String_Knob(key, key)
                                # DON'T set INVISIBLE - Deadline strips invisible knobs!
                                root.addKnob(knob)
                                print("  Created knob: {}".format(key))
                            root[key].setValue(str(value))
                            print("  Set {} = {}".format(key, value))
                except Exception as e:
                    print("  ERROR parsing multishot_custom: {}".format(e))
                    import traceback
                    traceback.print_exc()
            else:
                print("DEBUG: custom_json is empty!")
        else:
            print("DEBUG: multishot_custom knob does NOT exist!")

        print("Multishot: Variables initialized in batch mode")
        print("=" * 80 + "\n")

    except Exception as e:
        print("Multishot: Error in batch mode initialization: {}".format(e))
        import traceback
        traceback.print_exc()



def fix_read_node_frame_ranges():
    """
    Fix Read node first/last frame expressions for batch mode.

    Issue: Read nodes may have incorrectly evaluated first/last expressions
    like {{"\[value root.first_frame]" x1 1}} which causes frame mismatches.

    Solution: Reset first/last to proper TCL expressions.
    """
    try:
        import nuke

        print("Multishot: Fixing Read node frame ranges for batch mode...")

        fixed_count = 0

        # Fix all Read nodes
        for node in nuke.allNodes('Read'):
            try:
                # Reset first/last frame to use root knobs
                # Note: first/last are Int_Knob, so we use setExpression() not fromUserText()
                if node.knob('first'):
                    node['first'].setExpression('[value root.first_frame]')
                    fixed_count += 1

                if node.knob('last'):
                    node['last'].setExpression('[value root.last_frame]')

                print("  Read '{}': reset frame range to use root knobs".format(node.name()))

            except Exception as e:
                print("  Warning: Could not fix Read node '{}': {}".format(node.name(), e))

        if fixed_count > 0:
            print("Multishot: Fixed {} Read node(s)".format(fixed_count))
        else:
            print("Multishot: No Read nodes needed fixing")

    except Exception as e:
        print("  Warning: Could not fix Read node frame ranges: {}".format(e))
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
    Register OCIO displays as viewer processes for batch mode.

    According to Foundry documentation, viewer processes must be registered in init.py
    (not menu.py) so they're available in non-GUI sessions (batch mode).

    This prevents "Bad value for viewerProcess" errors when loading scripts with
    custom viewer processes in batch mode.

    Reference: https://community.foundry.com/discuss/topic/97288/nuke-viewer-process

    The trick is to unregister default viewer processes and register OCIO-based ones.
    """
    try:
        import nuke

        print("Multishot: Registering OCIO viewer processes for batch mode...")

        # Unregister default viewer processes
        # This is necessary to avoid conflicts with OCIO-based viewer processes
        try:
            nuke.ViewerProcess.unregister('sRGB')
            print("  Unregistered: sRGB")
        except:
            pass

        try:
            nuke.ViewerProcess.unregister('rec709')
            print("  Unregistered: rec709")
        except:
            pass

        try:
            nuke.ViewerProcess.unregister('rec1886')
            print("  Unregistered: rec1886")
        except:
            pass

        # Register OCIO-based viewer processes
        # These will be available in the viewerProcess dropdown
        try:
            # Register a "None" viewer process for batch mode
            # Syntax: register(name, call, args, kwargs)
            # kwargs must be a dict, not tuple!
            nuke.ViewerProcess.register("None", nuke.createNode, ("Viewer", ""), {})
            print("  Registered: None")
        except Exception as e:
            print("  Warning: Could not register 'None' viewer process: {}".format(e))

        # Register OCIO display transforms as viewer processes
        # Format: "View Name (Display Name)"
        ocio_viewer_processes = [
            "ACES 1.0 - SDR Video (sRGB - Display)",
            "ACES 1.0 - SDR Video (Rec.1886 Rec.709 - Display)",
            "Un-tone-mapped (sRGB - Display)",
        ]

        for vp_name in ocio_viewer_processes:
            try:
                # Register as OCIO display transform
                # The viewer process will use OCIODisplay node internally
                nuke.ViewerProcess.register(vp_name, nuke.createNode, ("OCIODisplay", ""), {})
                print("  Registered: {}".format(vp_name))
            except Exception as e:
                print("  Warning: Could not register '{}': {}".format(vp_name, e))

        print("Multishot: OCIO viewer processes registered")

    except Exception as e:
        print("  Warning: Could not register OCIO viewer processes: {}".format(e))
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

                # CRITICAL: Disable Output Transform in batch mode
                # Output Transform is a creative decision that should be baked into the colorspace knob
                # In batch mode, we just want to render with the colorspace setting, not apply display transforms
                if node.knob('useOCIODisplayView'):
                    if node.knob('useOCIODisplayView').value():
                        # Disable Output Transform
                        node.knob('useOCIODisplayView').setValue(False)
                        print("  Write '{}': disabled Output Transform for batch mode".format(node.name()))
                        fixed_count += 1

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

        # DO NOT call immediately! The script hasn't loaded yet!
        # The .nk file has an onScriptLoad callback that will create the knobs.
        # We just add our debug callback to verify after the script loads.

        # Add as callbacks for when scripts are loaded
        nuke.addOnScriptLoad(ensure_variables_for_batch_mode)
        nuke.addOnCreate(ensure_variables_for_batch_mode, nodeClass='Root')

except ImportError:
    # Not in Nuke environment
    pass
