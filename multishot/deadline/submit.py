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
            # Apply path mapping: T:/ -> /mnt/ppr_dev_t/
            if ocio_path.startswith('T:/') or ocio_path.startswith('T:\\'):
                ocio_path = ocio_path.replace('T:/', '/mnt/ppr_dev_t/').replace('T:\\', '/mnt/ppr_dev_t/')
                ocio_path = ocio_path.replace('\\', '/')
            env_vars['OCIO'] = ocio_path
        else:
            # Use default OCIO path (Linux path for render nodes)
            ocio_path_linux = '/mnt/ppr_dev_t/pipeline/ocio/aces_2.0/studio-config-v1.0.0_aces-v1.3_ocio-v2.0.ocio'
            env_vars['OCIO'] = ocio_path_linux
    except:
        # Fallback to default OCIO path
        ocio_path_linux = '/mnt/ppr_dev_t/pipeline/ocio/aces_2.0/studio-config-v1.0.0_aces-v1.3_ocio-v2.0.ocio'
        env_vars['OCIO'] = ocio_path_linux

    return env_vars


def _patch_deadline_submission():
    """
    Monkey-patch the Deadline submission to inject environment variables into the job info file.

    This patches the built-in open() function temporarily during SubmitJob execution
    to intercept job info file writes and add environment variables.

    Reference: https://docs.thinkboxsoftware.com/products/deadline/10.4/1_User%20Manual/manual/environment.html
    """
    try:
        import SubmitNukeToDeadline
        import builtins

        # Store original SubmitJob function
        if not hasattr(SubmitNukeToDeadline, '_multishot_original_submit_job'):
            SubmitNukeToDeadline._multishot_original_submit_job = SubmitNukeToDeadline.SubmitJob

        # Store original open function
        original_open = builtins.open

        def patched_submit_job(*args, **kwargs):
            """Patched SubmitJob that intercepts file writes to add environment variables."""

            # Track if we've added env vars
            env_vars_added = [False]  # Use list to allow modification in nested function

            # Get environment variables to add
            env_vars = get_environment_variables()

            class FileHandleWrapper:
                """Wrapper for file handle that intercepts writes to job info files."""
                def __init__(self, file_handle, is_job_info):
                    self._handle = file_handle
                    self._is_job_info = is_job_info
                    self._closed = False

                def write(self, data):
                    return self._handle.write(data)

                def close(self):
                    # Before closing job info file, add environment variables
                    if self._is_job_info and not self._closed and not env_vars_added[0]:
                        print("\n" + "=" * 70)
                        print("MULTISHOT: Adding environment variables to Deadline job info")
                        print("=" * 70)

                        # Write environment variables
                        # Format: EnvironmentKeyValue0=KEY=VALUE
                        env_index = 0
                        for key, value in env_vars.items():
                            env_line = "EnvironmentKeyValue{}={}={}\n".format(env_index, key, value)
                            self._handle.write(env_line)
                            print("  Added: {} = {}".format(key, value))
                            env_index += 1

                        # Ensure job environment is merged with worker environment
                        # UseJobEnvironmentOnly=false means merge (default behavior)
                        self._handle.write("UseJobEnvironmentOnly=false\n")
                        print("  Set: UseJobEnvironmentOnly = false (merge with worker env)")

                        print("=" * 70 + "\n")
                        env_vars_added[0] = True

                        # Debug: Try to read back the file to verify
                        try:
                            file_path = self._handle.name
                            print("DEBUG: Job info file path: {}".format(file_path))
                        except:
                            pass

                    self._closed = True
                    return self._handle.close()

                def __enter__(self):
                    return self

                def __exit__(self, *args):
                    self.close()

                def __getattr__(self, name):
                    return getattr(self._handle, name)

            def patched_open(file, mode='r', *args, **kwargs):
                """Patched open that wraps job info file handles."""
                handle = original_open(file, mode, *args, **kwargs)

                # Check if this is a job info file being written
                # Pattern: nuke_submit_info%d.job (NOT nuke_plugin_info%d.job)
                if mode in ('w', 'w+', 'wb', 'wb+') and isinstance(file, str) and 'nuke_submit_info' in file and file.endswith('.job'):
                    print("MULTISHOT: Intercepting job info file: {}".format(file))
                    return FileHandleWrapper(handle, is_job_info=True)

                return handle

            # Temporarily replace open function
            builtins.open = patched_open

            try:
                # Call original SubmitJob with all arguments
                return SubmitNukeToDeadline._multishot_original_submit_job(*args, **kwargs)
            finally:
                # Restore original open function
                builtins.open = original_open

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

