"""
Multishot Deadline Submission

Custom Deadline submission that automatically includes required environment variables
for proper multishot functionality on render nodes.

This ensures:
- NUKE_PATH is set so init.py loads on render nodes
- OCIO config path is included
- Individual knobs (ep, seq, shot, PROJ_ROOT, IMG_ROOT) are created
- TCL expressions evaluate correctly
- Viewer nodes are fixed for batch mode compatibility
"""

import os
import sys
import platform
import re


def delete_viewer_nodes_for_batch_mode():
    """
    Delete Viewer nodes before submitting to Deadline.

    Viewer nodes can cause issues in batch mode and are not needed for rendering.
    This is the safest approach - just remove them before submission.
    """
    try:
        import nuke

        print("\n" + "=" * 70)
        print("MULTISHOT: Removing Viewer nodes for batch mode")
        print("=" * 70)

        viewer_nodes = nuke.allNodes('Viewer')
        deleted_count = 0

        for node in viewer_nodes:
            try:
                node_name = node.name()
                nuke.delete(node)
                print("  Deleted Viewer node: {}".format(node_name))
                deleted_count += 1
            except Exception as e:
                print("  Warning: Could not delete Viewer '{}': {}".format(node.name(), e))

        if deleted_count > 0:
            print("Deleted {} Viewer node(s)".format(deleted_count))
            print("=" * 70 + "\n")
            return True
        else:
            print("No Viewer nodes to delete")
            print("=" * 70 + "\n")
            return False

    except Exception as e:
        print("ERROR: Could not delete Viewer nodes: {}".format(e))
        import traceback
        traceback.print_exc()
        return False


def fix_read_node_frame_ranges_for_submission():
    """
    Fix Read node frame ranges before submission.

    Ensures all Read nodes use proper TCL expressions for first/last frames
    instead of hardcoded values that may be incorrect.
    """
    try:
        import nuke

        print("\n" + "=" * 70)
        print("MULTISHOT: Fixing Read node frame ranges")
        print("=" * 70)

        fixed_count = 0

        for node in nuke.allNodes('Read'):
            try:
                node_name = node.name()

                # Reset first/last to use root knobs
                # Note: first/last are Int_Knob, so we use setExpression() not fromUserText()
                if node.knob('first'):
                    node['first'].setExpression('[value root.first_frame]')
                    fixed_count += 1

                if node.knob('last'):
                    node['last'].setExpression('[value root.last_frame]')

                print("  Fixed Read node '{}': frame range now uses root knobs".format(node_name))

            except Exception as e:
                print("  Warning: Could not fix Read node '{}': {}".format(node.name(), e))

        if fixed_count > 0:
            print("Fixed {} Read node(s)".format(fixed_count))
            print("=" * 70 + "\n")
            return True
        else:
            print("No Read nodes to fix")
            print("=" * 70 + "\n")
            return False

    except Exception as e:
        print("ERROR: Could not fix Read node frame ranges: {}".format(e))
        import traceback
        traceback.print_exc()
        return False


def convert_paths_to_linux():
    """
    Convert Windows paths to Linux paths in multishot_custom JSON and individual knobs.

    Returns:
        dict: Backup of original values to restore later
    """
    try:
        import nuke
        import json

        print("\n" + "=" * 70)
        print("MULTISHOT: Converting Windows paths to Linux for submission")
        print("=" * 70)

        root = nuke.root()
        backup = {}

        # Path mappings (case-insensitive)
        path_mappings = {
            'T:/': '/mnt/ppr_dev_t/',
            'T:\\': '/mnt/ppr_dev_t/',
            't:/': '/mnt/ppr_dev_t/',
            't:\\': '/mnt/ppr_dev_t/',
            'V:/': '/mnt/igloo_swa_v/',
            'V:\\': '/mnt/igloo_swa_v/',
            'v:/': '/mnt/igloo_swa_v/',
            'v:\\': '/mnt/igloo_swa_v/',
            'W:/': '/mnt/igloo_swa_w/',
            'W:\\': '/mnt/igloo_swa_w/',
            'w:/': '/mnt/igloo_swa_w/',
            'w:\\': '/mnt/igloo_swa_w/',
            'X:/': '/mnt/igloo_ega_x/',
            'X:\\': '/mnt/igloo_ega_x/',
            'x:/': '/mnt/igloo_ega_x/',
            'x:\\': '/mnt/igloo_ega_x/',
            'Y:/': '/mnt/igloo_ega_y/',
            'Y:\\': '/mnt/igloo_ega_y/',
            'y:/': '/mnt/igloo_ega_y/',
            'y:\\': '/mnt/igloo_ega_y/'
        }

        # 1. Convert multishot_custom JSON
        if root.knob('multishot_custom'):
            custom_json = root['multishot_custom'].value()
            backup['multishot_custom'] = custom_json
            print("  Original multishot_custom: {}".format(custom_json))

            if custom_json:
                try:
                    custom_vars = json.loads(custom_json)
                    modified = False

                    # Convert paths in PROJ_ROOT and IMG_ROOT
                    for key in ['PROJ_ROOT', 'IMG_ROOT']:
                        if key in custom_vars:
                            original_value = custom_vars[key]
                            new_value = original_value

                            # Apply path mappings
                            for win_path, linux_path in path_mappings.items():
                                if win_path in new_value:
                                    new_value = new_value.replace(win_path, linux_path).replace('\\', '/')
                                    print("    {} in JSON: {} -> {}".format(key, original_value, new_value))
                                    modified = True
                                    break

                            custom_vars[key] = new_value

                    if modified:
                        # Update the JSON knob with converted paths
                        new_json = json.dumps(custom_vars, separators=(',', ':'))
                        root['multishot_custom'].setValue(new_json)
                        print("  Updated multishot_custom: {}".format(new_json))

                except Exception as e:
                    print("  ERROR parsing multishot_custom: {}".format(e))
                    import traceback
                    traceback.print_exc()

        # 2. Update individual PROJ_ROOT and IMG_ROOT knobs from the converted JSON
        if root.knob('multishot_custom'):
            custom_json = root['multishot_custom'].value()
            if custom_json:
                try:
                    custom_vars = json.loads(custom_json)
                    for key in ['PROJ_ROOT', 'IMG_ROOT']:
                        if key in custom_vars:
                            value = custom_vars[key]

                            # Backup original value
                            if root.knob(key):
                                backup[key] = root[key].value()

                            # Create knob if it doesn't exist
                            if not root.knob(key):
                                knob = nuke.String_Knob(key, key)
                                root.addKnob(knob)
                                print("  Created knob: {}".format(key))

                            # Set the Linux path
                            root[key].setValue(str(value))
                            print("  Set {} = {}".format(key, value))

                except Exception as e:
                    print("  ERROR updating knobs: {}".format(e))
                    import traceback
                    traceback.print_exc()

        print("=" * 70 + "\n")
        return backup

    except Exception as e:
        print("ERROR: Could not convert paths: {}".format(e))
        import traceback
        traceback.print_exc()
        print("=" * 70 + "\n")
        return {}


def restore_windows_paths(backup):
    """
    Restore Windows paths from backup after submission.

    Args:
        backup (dict): Backup of original values
    """
    try:
        import nuke

        print("\n" + "=" * 70)
        print("MULTISHOT: Restoring Windows paths after submission")
        print("=" * 70)

        root = nuke.root()

        # Restore multishot_custom JSON
        if 'multishot_custom' in backup and root.knob('multishot_custom'):
            root['multishot_custom'].setValue(backup['multishot_custom'])
            print("  Restored multishot_custom: {}".format(backup['multishot_custom']))

        # Restore individual knobs
        for key in ['PROJ_ROOT', 'IMG_ROOT']:
            if key in backup and root.knob(key):
                root[key].setValue(backup[key])
                print("  Restored {} = {}".format(key, backup[key]))

        print("=" * 70 + "\n")

    except Exception as e:
        print("ERROR: Could not restore paths: {}".format(e))
        import traceback
        traceback.print_exc()
        print("=" * 70 + "\n")


def ensure_variables_before_submission():
    """
    Ensure all multishot variables are properly set before submission.

    This creates individual knobs for all variables so they're embedded
    in the script file and available on render nodes.
    """
    try:
        import nuke

        print("\n" + "=" * 70)
        print("MULTISHOT: Ensuring variables are embedded in script")
        print("=" * 70)

        # Add multishot package to Python path
        current_dir = os.path.dirname(os.path.dirname(__file__))
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)

        from multishot.core.variables import VariableManager
        vm = VariableManager()

        # Ensure context variables have individual knobs
        vm._ensure_context_variable_knobs()
        print("  Context variables (ep, seq, shot, project) embedded")

        # Ensure root variables have individual knobs
        custom_vars = vm.get_custom_variables()
        if custom_vars:
            vm._create_individual_root_knobs(custom_vars)
            print("  Root variables (PROJ_ROOT, IMG_ROOT) embedded")

        # Print current values for verification
        root = nuke.root()
        print("\n  Current variable values:")
        for key in ['project', 'ep', 'seq', 'shot', 'PROJ_ROOT', 'IMG_ROOT']:
            if root.knob(key):
                value = root[key].value()
                print("    {} = {}".format(key, value))

        # DEBUG: Print JSON knob values to verify they're embedded
        print("\n  JSON knobs (will be saved to .nk file):")
        for knob_name in ['multishot_context', 'multishot_custom']:
            if root.knob(knob_name):
                value = root[knob_name].value()
                if value:
                    print("    {} = {}".format(knob_name, value))
                else:
                    print("    {} = EMPTY!".format(knob_name))
            else:
                print("    {} = MISSING!".format(knob_name))

        print("=" * 70 + "\n")
        return True

    except Exception as e:
        print("ERROR: Could not ensure variables: {}".format(e))
        import traceback
        traceback.print_exc()
        print("=" * 70 + "\n")
        return False


# Set by prepare_farm_copy() when a bypassed copy was written, and read by the
# CallDeadlineCommand patch so the job renders that file instead of the
# artist's original.
_farm_copy_path = None


def prepare_farm_copy(script_path):
    """Write a farm copy with unavailable OFX nodes bypassed, if any are present.

    Returns the copy's path, or None when the script needs no changes (in which
    case the artist's own file is submitted, untouched, as usual).

    The artist's script is never modified and their open session is never
    touched - the copy is produced from the saved .nk text.
    """
    global _farm_copy_path
    _farm_copy_path = None

    try:
        from .ofx_bypass import bypass_ofx_in_script_text, script_needs_bypass

        with open(script_path, 'r') as handle:
            text = handle.read()

        if not script_needs_bypass(text):
            return None

        new_text, bypassed = bypass_ofx_in_script_text(text)

        farm_dir = os.path.normpath(os.path.join(os.path.dirname(script_path), '..', 'farm'))
        if not os.path.isdir(farm_dir):
            os.makedirs(farm_dir)
        base, ext = os.path.splitext(os.path.basename(script_path))
        copy_path = os.path.join(farm_dir, base + '_farm' + ext).replace('\\', '/')

        with open(copy_path, 'w') as handle:
            handle.write(new_text)

        print("\n" + "=" * 70)
        print("MULTISHOT: Bypassed OFX nodes that are missing on the farm")
        print("=" * 70)
        for name in bypassed:
            print("  bypassed (disable=true): {}".format(name))
        print("  RSMB is not installed on the render nodes, so these would fail")
        print("  the render outright. Bypassed nodes pass input 0 through, which")
        print("  means NO MOTION BLUR from them in this render.")
        print("  Your script is unchanged; submitting this copy instead:")
        print("    {}".format(copy_path))
        print("=" * 70 + "\n")

        _farm_copy_path = copy_path
        return copy_path

    except Exception as e:
        print("Multishot: WARNING - could not build farm copy ({}); "
              "submitting the original script".format(e))
        _farm_copy_path = None
        return None


def merge_job_environment(job_info_content, env_vars, drop_keys=()):
    """Merge env vars into an existing Deadline job info file's environment block.

    Returns (kept_lines, env_lines) where env_lines is a fresh, contiguous
    EnvironmentKeyValue block plus UseJobEnvironmentOnly.

    Deadline stops reading EnvironmentKeyValue entries at the first missing
    index, so the block must be renumbered from 0 with no gaps - appending or
    restarting at 0 both silently discard variables.
    """
    existing = {}
    kept_lines = []
    for line in job_info_content.splitlines():
        stripped = line.strip()
        if stripped.startswith('EnvironmentKeyValue'):
            _, _, assignment = stripped.partition('=')
            key, _, value = assignment.partition('=')
            if key:
                existing[key] = value
        elif stripped.lower().startswith('usejobenvironmentonly'):
            continue
        else:
            kept_lines.append(line)

    merged = dict(existing)
    merged.update(env_vars)
    for key in drop_keys:
        merged.pop(key, None)

    env_lines = ["EnvironmentKeyValue{}={}={}".format(index, key, merged[key])
                 for index, key in enumerate(sorted(merged))]
    env_lines.append("UseJobEnvironmentOnly=false")

    while kept_lines and not kept_lines[-1].strip():
        kept_lines.pop()

    return kept_lines, env_lines


def repoint_scene_file_in_plugin_info(plugin_info_file, scene_file):
    """Point the job's SceneFile at our farm copy instead of the artist's script."""
    try:
        with open(plugin_info_file, 'r') as handle:
            lines = handle.read().splitlines()
    except Exception as e:
        print("  Warning: could not read plugin info file: {}".format(e))
        return False

    updated = []
    changed = False
    for line in lines:
        if line.strip().lower().startswith('scenefile='):
            updated.append('SceneFile=' + scene_file)
            changed = True
        else:
            updated.append(line)

    if changed:
        try:
            with open(plugin_info_file, 'w') as handle:
                handle.write('\n'.join(updated))
                handle.write('\n')
            print("  SceneFile -> {}".format(scene_file))
        except Exception as e:
            print("  Warning: could not update plugin info file: {}".format(e))
            return False
    return changed


def disable_batch_mode_in_plugin_info(plugin_info_file):
    """Force BatchMode=False in a Deadline plugin info file.

    With BatchMode=True this Deadline version's Nuke plugin omits both
    ``-X <WriteNode>`` and ``-F <range>`` from the command line (Nuke.py, the
    ``if not self.BatchMode`` guards around the render arguments). Nuke then
    renders EVERY Write node over the WHOLE script range, ignoring the task's
    frame chunk entirely:

        Plugin rendering frame(s): 1001-1005
        INFO: Argument: -V 2 -x "<scene>"      <- no -X, no -F
        STDOUT: Frame 1001 (1 of 100)          <- 100 frames, not 5

    which also writes output for unrelated Write nodes in the script. Returns
    True if the file was changed.
    """
    try:
        with open(plugin_info_file, 'r') as handle:
            lines = handle.read().splitlines()
    except Exception as e:
        print("  Warning: could not read plugin info file: {}".format(e))
        return False

    changed = False
    updated = []
    for line in lines:
        if line.strip().lower().startswith('batchmode='):
            if line.strip().lower() != 'batchmode=false':
                updated.append('BatchMode=False')
                changed = True
                continue
        updated.append(line)

    if not any(l.strip().lower().startswith('batchmode=') for l in updated):
        updated.append('BatchMode=False')
        changed = True

    if changed:
        try:
            with open(plugin_info_file, 'w') as handle:
                handle.write('\n'.join(updated))
                handle.write('\n')
            print("  Set BatchMode=False so Deadline passes -X <WriteNode> and "
                  "-F <frame range> (otherwise every Write renders the full range)")
        except Exception as e:
            print("  Warning: could not update plugin info file: {}".format(e))
            return False
    return changed


def script_declares_ocio_config():
    """True when the .nk names its own OCIO config via customOCIOConfigPath.

    When it does not, the script is relying on whatever colour management it was
    authored with (for this studio: Nuke's default OCIO config), and nothing
    should override that on the render node.
    """
    try:
        import nuke
        knob = nuke.root().knob('customOCIOConfigPath')
        return bool(knob and knob.value().strip())
    except Exception:
        return False


def get_environment_variables():
    """
    Get environment variables that should be passed to Deadline render nodes.

    IMPORTANT: Deadline render nodes are Linux, so we must use Linux paths!
    Deadline's path mapping does NOT apply to environment variables.

    Returns:
        dict: Dictionary of environment variable names and values
    """
    env_vars = {}

    # CRITICAL: Render nodes are Linux, so use Linux paths for environment variables
    # Deadline path mapping only applies to file paths in .nk scripts, NOT to env vars!

    # NUKE_PATH - critical. Without it init.py never loads on the render node,
    # which means no filenameFilter, which means every Windows path in the
    # script reaches the farm untranslated.
    #
    # Derived from where this package actually lives rather than hardcoded, so a
    # move (or a release/ vs development/ switch) does not silently keep pointing
    # the farm at the old checkout.
    from ..core.pathmap import to_linux, unmapped_drive

    # Known-good location on the farm, used if the drive cannot be translated.
    FARM_NUKE_PATH = '/mnt/ppr_dev_t/pipeline/development/nuke/nukemultishot'

    package_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    nuke_path = to_linux(package_root.replace('\\', '/'))

    # Never ship a Windows path: the render node would search a drive that does
    # not exist there, init.py would not load, and nothing would be path-mapped
    # - which fails silently, with no error in the log, only missing files
    # later. Verified in the wild: a job went out with
    # NUKE_PATH=T:/pipeline/development/nuke/nukemultishot and no mapping ran.
    if unmapped_drive(nuke_path) or (len(nuke_path) > 1 and nuke_path[1] == ':'):
        print("Multishot: WARNING - could not translate {} to a farm path; "
              "falling back to {}".format(nuke_path, FARM_NUKE_PATH))
        nuke_path = FARM_NUKE_PATH

    env_vars['NUKE_PATH'] = nuke_path
    print("Multishot: NUKE_PATH for the farm = {}".format(nuke_path))

    # OCIO - only when the script actually asks for a specific config.
    #
    # We deliberately do NOT force a studio default onto scripts that do not set
    # customOCIOConfigPath. A Write node's display/view and a Viewer's
    # viewerProcess are enums validated against whatever OCIO config is live at
    # script-parse time. Forcing the ACES studio config onto a script authored
    # under Nuke's built-in config makes those values illegal and Nuke aborts
    # during the parse with:
    #
    #     ERROR: Bad value for display : default
    #     ERROR: Bad value for viewerProcess : sRGB (default)
    #
    # which is unfixable from Python because the parse dies first. Verified on
    # the farm: the same shot that failed this way rendered cleanly once OCIO was
    # left unset and the script's own colour management was respected.
    try:
        import nuke
        ocio_knob = nuke.root().knob('customOCIOConfigPath')
        if ocio_knob and ocio_knob.value():
            ocio_path = to_linux(ocio_knob.value())
            env_vars['OCIO'] = ocio_path
            print("Multishot: OCIO from script -> {}".format(ocio_path))
        else:
            print("Multishot: script sets no customOCIOConfigPath; leaving OCIO "
                  "unset so the script's own colour management is used")
    except Exception as e:
        print("Multishot: could not read OCIO from script ({}); leaving OCIO unset".format(e))

    return env_vars


def _patch_deadline_submission():
    """
    Monkey-patch the Deadline submission to inject environment variables into the job info file.

    This patches the CallDeadlineCommand function to intercept job submission and add
    environment variables to the job info file before submission.

    Reference: https://docs.thinkboxsoftware.com/products/deadline/10.4/1_User%20Manual/manual/environment.html
    """
    try:
        import SubmitNukeToDeadline

        # Store original CallDeadlineCommand function
        if not hasattr(SubmitNukeToDeadline, '_multishot_original_call_deadline_command'):
            SubmitNukeToDeadline._multishot_original_call_deadline_command = SubmitNukeToDeadline.CallDeadlineCommand

        def patched_call_deadline_command(args, hideWindow=True):
            """
            Patched CallDeadlineCommand that adds environment variables to job info files.

            This intercepts the deadlinecommand call and modifies the job info file
            to include required environment variables.

            Note: CallDeadlineCommand signature is (args, hideWindow=True)
            The parameter uses camelCase, not snake_case!
            """
            # Check if this is a job submission command
            # Format: deadlinecommand <job_info_file> <plugin_info_file> [aux_files...]
            if args and len(args) >= 2:
                job_info_file = args[0]

                # Check if this is a job info file (not a query command)
                if isinstance(job_info_file, str) and job_info_file.endswith('.job') and os.path.exists(job_info_file):
                    print("\n" + "=" * 70)
                    print("MULTISHOT: Modifying Deadline job info file")
                    print("=" * 70)
                    print("Job info file: {}".format(job_info_file))

                    try:
                        # Read existing job info
                        with open(job_info_file, 'r') as f:
                            job_info_content = f.read()

                        # Get environment variables to add
                        env_vars = get_environment_variables()

                        # The job info file usually already carries environment
                        # entries written by the studio submitter (OCIO,
                        # NUKE_DISABLE_GPU_ACCELERATION, DISPLAY, ...). We must
                        # merge with them rather than append:
                        #
                        #   * Deadline stops reading EnvironmentKeyValue entries
                        #     at the first missing index, so a gap silently
                        #     discards every remaining variable - verified on the
                        #     farm, where a gap at index 0 dropped OCIO entirely.
                        #   * Blindly restarting at 0 overwrote the submitter's
                        #     own entries, which is how NUKE_DISABLE_GPU_ACCELERATION
                        #     was being lost on every job.
                        #
                        # So: parse what is there, merge ours over the top, and
                        # rewrite the whole block contiguously from 0.
                        #
                        # The render must also follow the script's own colour
                        # management. The studio submitter writes an
                        # unconditional EnvironmentKeyValue0=OCIO=<ACES config>
                        # onto every Nuke job; when the script never asked for
                        # that config, the override makes its Write display/view
                        # and Viewer viewerProcess values illegal and Nuke aborts
                        # while parsing:
                        #
                        #     ERROR: Bad value for display : default
                        #
                        # Verified on the farm - the same shot fails with the
                        # override and renders without it. Drop the override so
                        # the .nk decides.
                        drop_keys = []
                        if not script_declares_ocio_config():
                            drop_keys.append('OCIO')

                        kept_lines, env_lines = merge_job_environment(
                            job_info_content, env_vars, drop_keys=drop_keys)

                        for env_line in env_lines:
                            print("  {}".format(env_line))
                        if drop_keys:
                            print("  Dropped {} - script declares no customOCIOConfigPath, "
                                  "so its own colour management is used".format(
                                      ", ".join(drop_keys)))

                        with open(job_info_file, 'w') as f:
                            f.write('\n'.join(kept_lines + env_lines))
                            f.write('\n')

                        # args[1] is the plugin info file for this submission.
                        plugin_info_file = args[1] if len(args) > 1 else None
                        if (isinstance(plugin_info_file, str)
                                and plugin_info_file.endswith('.job')
                                and os.path.exists(plugin_info_file)):
                            disable_batch_mode_in_plugin_info(plugin_info_file)
                            if _farm_copy_path:
                                repoint_scene_file_in_plugin_info(
                                    plugin_info_file, _farm_copy_path)

                        print("=" * 70 + "\n")

                    except Exception as e:
                        print("ERROR: Could not modify job info file: {}".format(e))
                        import traceback
                        traceback.print_exc()

            # Call original function
            return SubmitNukeToDeadline._multishot_original_call_deadline_command(args, hideWindow)

        # Replace with patched version
        SubmitNukeToDeadline.CallDeadlineCommand = patched_call_deadline_command

        return True

    except Exception as e:
        print("Warning: Could not patch Deadline submission: {}".format(e))
        import traceback
        traceback.print_exc()
        return False


def submit_to_deadline_vanilla():
    """
    Submit to Deadline with ALL callbacks disabled (vanilla submission).

    This is for testing - removes all multishot callbacks to isolate issues.
    """
    try:
        import nuke
        from ..deadline.farm_script import FarmScriptManager
        from ..core.variables import VariableManager

        # Check if script is saved
        script_path = nuke.root().name()
        if script_path == 'Root' or not script_path:
            nuke.message("Please save your script before submitting to Deadline.")
            return

        print("\n" + "=" * 70)
        print("VANILLA DEADLINE SUBMISSION (NO CALLBACKS)")
        print("=" * 70)
        print("\nScript: {}".format(script_path))

        # Get shot data
        var_manager = VariableManager()
        shot_data = {
            'project': var_manager.get_variable('multishot_project'),
            'ep': var_manager.get_variable('multishot_ep'),
            'seq': var_manager.get_variable('multishot_seq'),
            'shot': var_manager.get_variable('multishot_shot'),
            'PROJ_ROOT': var_manager.get_variable('PROJ_ROOT'),
            'IMG_ROOT': var_manager.get_variable('IMG_ROOT')
        }

        # Create farm script with callbacks disabled
        farm_manager = FarmScriptManager()
        farm_script = farm_manager.create_farm_script(shot_data, script_path, disable_callbacks=True)

        print("\nVanilla farm script created: {}".format(farm_script))
        print("All callbacks have been removed from this script.")
        print("\nNow submit this farm script to Deadline using standard submission.")
        print("=" * 70 + "\n")

        nuke.message(
            "Vanilla farm script created:\n\n{}\n\n"
            "All callbacks removed.\n\n"
            "Now submit this script to Deadline.".format(farm_script)
        )

    except Exception as e:
        import traceback
        print("\nERROR in vanilla submission:")
        traceback.print_exc()
        nuke.message("Error creating vanilla farm script:\n\n{}".format(str(e)))


def submit_to_deadline():
    """
    Submit current Nuke script to Deadline with multishot environment variables.

    This wraps the standard Deadline submission and automatically adds required
    environment variables.
    """
    try:
        import nuke

        # Check if script is saved
        script_path = nuke.root().name()
        if script_path == 'Root' or not script_path:
            nuke.message("Please save your script before submitting to Deadline.")
            return

        print("=" * 70)
        print("MULTISHOT DEADLINE SUBMISSION")
        print("=" * 70)
        print("\nScript: {}".format(script_path))

        # Get environment variables
        env_vars = get_environment_variables()

        print("\nEnvironment variables that will be added:")
        for key, value in env_vars.items():
            print("  {} = {}".format(key, value))
        print("")

        # Try to import Deadline submission
        try:
            # Get Deadline path
            deadline_path = os.environ.get('DEADLINE_PATH', '')
            print("DEADLINE_PATH: {}".format(deadline_path))

            if not deadline_path:
                nuke.message(
                    "DEADLINE_PATH environment variable is not set.\n\n"
                    "Please install Deadline Client and set DEADLINE_PATH."
                )
                return

            # Get Deadline submission path
            # This handles both local and remote repositories
            submission_path = _get_deadline_submission_path()
            if not submission_path:
                nuke.message(
                    "Could not get Deadline submission path.\n\n"
                    "Please make sure Deadline Client is configured correctly."
                )
                return

            # Check if path exists (it should, since deadlinecommand returned it)
            if not os.path.exists(submission_path):
                nuke.message(
                    "Deadline submission path not found:\n\n{}\n\n"
                    "Please make sure Deadline repository is accessible.".format(submission_path)
                )
                return

            # Add to sys.path
            if submission_path not in sys.path:
                sys.path.insert(0, submission_path)
                print("Added to sys.path: {}".format(submission_path))

            # Import Deadline submission module
            print("Importing SubmitNukeToDeadline...")
            import SubmitNukeToDeadline
            print("Successfully imported SubmitNukeToDeadline")

            # STEP 1: Ensure all variables are embedded in the script
            ensure_variables_before_submission()

            # NOTE: The script is submitted exactly as the artist saved it.
            #
            # We used to rewrite PROJ_ROOT/IMG_ROOT to Linux paths, delete every
            # Viewer node, and then nuke.scriptSave() over the artist's own file.
            # That was destructive - the restore afterwards only put the knob
            # values back in memory and never re-saved, so the file left on disk
            # kept Linux roots and had lost its Viewers, which then broke the
            # shot for the next person to open it on Windows.
            #
            # Path translation now happens on the render node instead, via the
            # filenameFilter installed by init.py (see multishot.core.pathmap).
            # That runs before the .nk is parsed, so it also covers nodes like
            # Camera3/ReadGeo that load their file during parsing - which no
            # callback or post-load fixup could ever reach.
            #
            # For this to work the farm job must carry NUKE_PATH; that is what
            # _patch_deadline_submission() below injects.

            # STEP 2: If the comp uses OFX plugins the farm does not have
            # (RSMB), write a copy with them bypassed and submit that instead.
            # The artist's script is left exactly as they saved it.
            prepare_farm_copy(script_path)

            # STEP 3: Patch the submission to add our environment variables
            _patch_deadline_submission()

            # STEP 3: Open submission dialog
            print("Opening Deadline submission dialog...")
            SubmitNukeToDeadline.SubmitToDeadline()

        except ImportError as e:
            error_msg = (
                "Could not import Deadline submission module.\n\n"
                "Error: {}\n\n"
                "DEADLINE_PATH: {}\n"
                "Submission path: {}\n\n"
                "Please make sure Deadline Client is installed and configured."
            ).format(
                str(e),
                os.environ.get('DEADLINE_PATH', 'NOT SET'),
                submission_path if 'submission_path' in locals() else 'NOT FOUND'
            )
            print(error_msg)
            nuke.message(error_msg)
        except Exception as e:
            nuke.message(
                "Error submitting to Deadline:\n\n{}".format(str(e))
            )
            import traceback
            traceback.print_exc()

    except Exception as e:
        print("Error in multishot Deadline submission: {}".format(e))
        import traceback
        traceback.print_exc()


def _get_deadline_submission_path():
    """
    Get the Deadline submission path for Nuke.

    This uses deadlinecommand to get the submission/Nuke/Main path,
    which handles both local and remote repositories.

    Returns:
        str: Path to Deadline submission scripts, or None if not found
    """
    try:
        import subprocess
        import errno

        deadline_path = os.environ.get('DEADLINE_PATH', '')
        if not deadline_path:
            print("DEADLINE_PATH not set")
            return None

        # Get deadline command
        if platform.system() == 'Windows':
            deadline_command = os.path.join(deadline_path, 'deadlinecommand.exe')
        else:
            deadline_command = os.path.join(deadline_path, 'deadlinecommand')

        if not os.path.exists(deadline_command):
            print("Deadline command not found: {}".format(deadline_command))
            return None

        # Setup startupinfo for Windows
        startupinfo = None
        if platform.system() == 'Windows':
            if hasattr(subprocess, '_subprocess') and hasattr(subprocess._subprocess, 'STARTF_USESHOWWINDOW'):
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess._subprocess.STARTF_USESHOWWINDOW
            elif hasattr(subprocess, 'STARTF_USESHOWWINDOW'):
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        # Get repository path with subdirectory
        # This handles both local and remote repositories
        args = [deadline_command, '-GetRepositoryPath', 'submission/Nuke/Main']

        attempts = 0
        path = ""
        while attempts < 10 and path == "":
            try:
                proc = subprocess.Popen(
                    args,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    startupinfo=startupinfo
                )
                path, errors = proc.communicate()

                if sys.version_info[0] > 2:
                    path = path.decode()

                path = path.replace('\n', '').replace('\r', '').replace('\\', '/')

            except (OSError, IOError) as e:
                if e.errno == errno.EINTR:
                    attempts += 1
                    if attempts == 10:
                        print("Failed to get Deadline repository path after 10 attempts")
                        return None
                    continue
                raise

        if path:
            print("Deadline submission path: {}".format(path))
            return path
        else:
            print("Could not get Deadline submission path")
            return None

    except Exception as e:
        print("Error getting Deadline submission path: {}".format(e))
        import traceback
        traceback.print_exc()
        return None

