"""
Multishot Deadline Submission

Custom Deadline submission that automatically includes required environment variables
for proper multishot functionality on render nodes.

This ensures:
- NUKE_PATH is set so init.py loads on render nodes
- OCIO config path is included
- Individual knobs (ep, seq, shot, PROJ_ROOT, IMG_ROOT) are created
- TCL expressions evaluate correctly
"""

import os
import sys
import platform


def get_environment_variables():
    """
    Get environment variables that should be passed to Deadline render nodes.
    
    Returns:
        dict: Dictionary of environment variable names and values
    """
    env_vars = {}
    
    # Determine platform-specific paths
    is_windows = platform.system() == 'Windows'
    
    # NUKE_PATH - critical for loading init.py
    if is_windows:
        multishot_path = 'T:/pipeline/development/nuke/nukemultishot'
    else:
        multishot_path = '/mnt/ppr_dev_t/pipeline/development/nuke/nukemultishot'
    
    # Check if path exists
    if os.path.exists(multishot_path):
        # Get existing NUKE_PATH and append if needed
        existing_nuke_path = os.environ.get('NUKE_PATH', '')
        if existing_nuke_path:
            if multishot_path not in existing_nuke_path:
                env_vars['NUKE_PATH'] = multishot_path + os.pathsep + existing_nuke_path
            else:
                env_vars['NUKE_PATH'] = existing_nuke_path
        else:
            env_vars['NUKE_PATH'] = multishot_path
    
    # OCIO - color management config
    try:
        import nuke
        # Try to get OCIO from script first
        ocio_knob = nuke.root().knob('customOCIOConfigPath')
        if ocio_knob and ocio_knob.value():
            env_vars['OCIO'] = ocio_knob.value()
        else:
            # Use default OCIO path
            if is_windows:
                ocio_path = 'T:/pipeline/ocio/aces_2.0/studio-config-v1.0.0_aces-v1.3_ocio-v2.0.ocio'
            else:
                ocio_path = '/mnt/ppr_dev_t/pipeline/ocio/aces_2.0/studio-config-v1.0.0_aces-v1.3_ocio-v2.0.ocio'
            
            if os.path.exists(ocio_path):
                env_vars['OCIO'] = ocio_path
    except:
        pass
    
    return env_vars


def _patch_deadline_submission():
    """
    Monkey-patch the Deadline submission to inject environment variables into the job.

    This patches the SubmitJob function to add environment variables to the job info
    before submission, so they get passed to the render nodes.
    """
    try:
        import SubmitNukeToDeadline

        # Store original SubmitJob function
        if not hasattr(SubmitNukeToDeadline, '_multishot_original_submit_job'):
            SubmitNukeToDeadline._multishot_original_submit_job = SubmitNukeToDeadline.SubmitJob

        def patched_submit_job(dialog, root):
            """Patched SubmitJob that adds environment variables to job info."""
            # Get environment variables to add
            env_vars = get_environment_variables()

            print("\n" + "=" * 70)
            print("MULTISHOT: Adding environment variables to Deadline job")
            print("=" * 70)

            # Add environment variables to the dialog's environment list
            # The dialog has an environmentList that stores env vars for the job
            if hasattr(dialog, 'environmentList'):
                for key, value in env_vars.items():
                    # Add to environment list
                    env_entry = "{}={}".format(key, value)
                    if env_entry not in dialog.environmentList:
                        dialog.environmentList.append(env_entry)
                        print("  Added: {} = {}".format(key, value))
                    else:
                        print("  Already exists: {} = {}".format(key, value))
            else:
                print("  Warning: Dialog has no environmentList attribute")
                for key, value in env_vars.items():
                    print("  Would add: {} = {}".format(key, value))

            print("=" * 70 + "\n")

            # Call original SubmitJob
            return SubmitNukeToDeadline._multishot_original_submit_job(dialog, root)

        # Replace with patched version
        SubmitNukeToDeadline.SubmitJob = patched_submit_job

        return True

    except Exception as e:
        print("Warning: Could not patch Deadline submission: {}".format(e))
        import traceback
        traceback.print_exc()
        return False


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

            # Patch the submission to add our environment variables
            _patch_deadline_submission()

            # Open submission dialog
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

