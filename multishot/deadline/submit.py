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


def convert_paths_to_linux_for_submission():
    """
    Convert Windows paths to Linux paths in multishot_custom and root knobs.

    This must be called BEFORE saving the script for Deadline submission.
    """
    try:
        import nuke
        import json

        print("\n" + "=" * 70)
        print("MULTISHOT: Converting Windows paths to Linux for farm")
        print("=" * 70)

        root = nuke.root()

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
            'w:\\': '/mnt/igloo_swa_w/'
        }

        # FIRST PRIORITY: Fix multishot_custom JSON
        if root.knob('multishot_custom'):
            custom_json = root['multishot_custom'].value()
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
                    else:
                        print("  No path conversion needed in multishot_custom")

                except Exception as e:
                    print("  ERROR parsing multishot_custom: {}".format(e))
                    import traceback
                    traceback.print_exc()

        # SECOND: Update individual PROJ_ROOT and IMG_ROOT knobs
        for key in ['PROJ_ROOT', 'IMG_ROOT']:
            if root.knob(key):
                current_value = root[key].value()
                new_value = current_value

                # Apply path mappings
                for win_path, linux_path in path_mappings.items():
                    if win_path in new_value:
                        new_value = new_value.replace(win_path, linux_path).replace('\\', '/')
                        print("  {} knob: {} -> {}".format(key, current_value, new_value))
                        break

                root[key].setValue(new_value)

        print("=" * 70 + "\n")
        return True

    except Exception as e:
        print("ERROR: Could not convert paths: {}".format(e))
        import traceback
        traceback.print_exc()
        print("=" * 70 + "\n")
        return False


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

    # NUKE_PATH - critical for loading init.py
    # Use Linux path for render nodes
    multishot_path_linux = '/mnt/ppr_dev_t/pipeline/development/nuke/nukemultishot'
    env_vars['NUKE_PATH'] = multishot_path_linux

    # OCIO - color management config
    try:
        import nuke
        # Try to get OCIO from script first
        ocio_knob = nuke.root().knob('customOCIOConfigPath')
        if ocio_knob and ocio_knob.value():
            # Convert Windows path to Linux path for render nodes
            ocio_path = ocio_knob.value()
            print("DEBUG: Original OCIO path from script: {}".format(ocio_path))

            # Apply path mapping for all drive letters (case-insensitive)
            # Check both uppercase and lowercase drive letters
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
                'w:\\': '/mnt/igloo_swa_w/'
            }

            for win_path, linux_path in path_mappings.items():
                if ocio_path.startswith(win_path):
                    ocio_path = ocio_path.replace(win_path, linux_path).replace('\\', '/')
                    print("DEBUG: Converted OCIO path to Linux: {}".format(ocio_path))
                    break

            env_vars['OCIO'] = ocio_path
            print("DEBUG: Setting OCIO environment variable to: {}".format(ocio_path))
        else:
            # Use default OCIO path (Linux path for render nodes)
            ocio_path_linux = '/mnt/ppr_dev_t/pipeline/ocio/aces_2.0/studio-config-v1.0.0_aces-v1.3_ocio-v2.0.ocio'
            env_vars['OCIO'] = ocio_path_linux
            print("DEBUG: No customOCIOConfigPath in script, using default: {}".format(ocio_path_linux))
    except Exception as e:
        # Fallback to default OCIO path
        ocio_path_linux = '/mnt/ppr_dev_t/pipeline/ocio/aces_2.0/studio-config-v1.0.0_aces-v1.3_ocio-v2.0.ocio'
        env_vars['OCIO'] = ocio_path_linux
        print("DEBUG: Error getting OCIO from script: {}".format(e))
        print("DEBUG: Using default OCIO: {}".format(ocio_path_linux))

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

                        # Append environment variables to job info
                        env_lines = []
                        env_index = 0
                        for key, value in env_vars.items():
                            env_line = "EnvironmentKeyValue{}={}={}".format(env_index, key, value)
                            env_lines.append(env_line)
                            print("  Adding: {} = {}".format(key, value))
                            env_index += 1

                        # Add UseJobEnvironmentOnly=false to merge with worker environment
                        env_lines.append("UseJobEnvironmentOnly=false")
                        print("  Set: UseJobEnvironmentOnly = false (merge with worker env)")

                        # Write back to file
                        with open(job_info_file, 'a') as f:
                            f.write('\n')
                            f.write('\n'.join(env_lines))
                            f.write('\n')

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

            # STEP 2: Convert Windows paths to Linux paths (FIRST PRIORITY!)
            convert_paths_to_linux_for_submission()

            # STEP 3: Fix Read node frame ranges
            # ❌ DISABLED: This was forcing expressions even when user wants static values!
            # If Read nodes have static frame ranges, we should NOT overwrite them.
            # fix_read_node_frame_ranges_for_submission()

            # STEP 4: Delete Viewer nodes (they cause issues in batch mode)
            delete_viewer_nodes_for_batch_mode()

            # STEP 5: SAVE THE SCRIPT to write variables to .nk file!
            print("\n" + "=" * 70)
            print("MULTISHOT: Saving script with Linux paths for farm")
            print("=" * 70)
            nuke.scriptSave()
            print("Script saved: {}".format(nuke.root().name()))
            print("=" * 70 + "\n")

            # STEP 5: Patch the submission to add our environment variables
            _patch_deadline_submission()

            # STEP 6: Open submission dialog
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

