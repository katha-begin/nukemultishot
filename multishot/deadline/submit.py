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
    Monkey-patch the Deadline submission to inject environment variables.
    """
    try:
        import SubmitNukeToDeadline

        # Store original function
        if not hasattr(SubmitNukeToDeadline, '_multishot_original_submit'):
            SubmitNukeToDeadline._multishot_original_submit = SubmitNukeToDeadline.SubmitToDeadline

        def patched_submit():
            """Patched submission that adds environment variables."""
            # Set environment variables before submission
            env_vars = get_environment_variables()

            print("\n" + "=" * 70)
            print("MULTISHOT: Adding environment variables to Deadline job")
            print("=" * 70)

            for key, value in env_vars.items():
                os.environ[key] = value
                print("  {} = {}".format(key, value))

            print("=" * 70 + "\n")

            # Call original submission
            return SubmitNukeToDeadline._multishot_original_submit()

        # Replace with patched version
        SubmitNukeToDeadline.SubmitToDeadline = patched_submit

        return True

    except Exception as e:
        print("Warning: Could not patch Deadline submission: {}".format(e))
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

            # Get Deadline repository path
            repo_path = _get_deadline_repository_path()
            if not repo_path:
                nuke.message(
                    "Could not get Deadline repository path.\n\n"
                    "Please make sure Deadline Client is configured correctly."
                )
                return

            # Add Deadline submission path to sys.path
            submission_path = os.path.join(repo_path, 'submission', 'Nuke', 'Main')
            print("Deadline submission path: {}".format(submission_path))

            if not os.path.exists(submission_path):
                nuke.message(
                    "Deadline submission path not found:\n\n{}\n\n"
                    "Please make sure Deadline repository is accessible.".format(submission_path)
                )
                return

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
                "Repository path: {}\n"
                "Submission path: {}\n\n"
                "Please make sure Deadline Client is installed and configured."
            ).format(
                str(e),
                os.environ.get('DEADLINE_PATH', 'NOT SET'),
                repo_path if 'repo_path' in locals() else 'NOT FOUND',
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


def _get_deadline_repository_path():
    """Get the Deadline repository path."""
    try:
        import subprocess

        deadline_path = os.environ.get('DEADLINE_PATH', '')
        if not deadline_path:
            return None

        # Try different command names
        if platform.system() == 'Windows':
            deadline_command = os.path.join(deadline_path, 'deadlinecommand.exe')
        else:
            deadline_command = os.path.join(deadline_path, 'deadlinecommand')

        if not os.path.exists(deadline_command):
            print("Deadline command not found: {}".format(deadline_command))
            return None

        # Run deadlinecommand to get repository path
        startupinfo = None
        if platform.system() == 'Windows':
            # Hide console window on Windows
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        result = subprocess.check_output(
            [deadline_command, '-GetRepositoryPath'],
            startupinfo=startupinfo,
            stderr=subprocess.STDOUT
        )

        if sys.version_info[0] > 2:
            result = result.decode()

        repo_path = result.strip().replace('\n', '').replace('\r', '')
        print("Deadline repository path: {}".format(repo_path))
        return repo_path

    except Exception as e:
        print("Could not get Deadline repository path: {}".format(e))
        import traceback
        traceback.print_exc()
        return None

