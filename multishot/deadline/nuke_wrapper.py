#!/usr/bin/env python
"""
Nuke Wrapper for Deadline Rendering

This script wraps the Nuke executable to fix OCIO-related issues in script files
before Nuke loads them. This prevents "Bad value for viewerProcess" errors in batch mode.

Usage:
    python nuke_wrapper.py <nuke_executable> <nuke_args...>

Example:
    python nuke_wrapper.py /home/rocky/Nuke16.0v6/Nuke16.0 -V 2 -t /path/to/script.nk
"""

import os
import re
import sys
import subprocess


def fix_viewer_process_in_script(script_path):
    """
    Fix viewerProcess settings in a Nuke script file.
    
    This removes or fixes invalid viewerProcess values that cause errors in batch mode.
    
    Args:
        script_path: Path to the .nk script file
        
    Returns:
        True if modifications were made, False otherwise
    """
    if not os.path.exists(script_path):
        return False
    
    print("\n" + "=" * 70)
    print("MULTISHOT: Fixing OCIO settings in script file")
    print("=" * 70)
    print("Script: {}".format(script_path))
    
    try:
        # Read the script file
        with open(script_path, 'r') as f:
            content = f.read()
        
        original_content = content
        modifications = []
        
        # Fix viewerProcess with any value - set to "None"
        # This is safe because Viewer nodes are not used in batch rendering
        pattern = r'(Viewer\s*\{[^}]*?)viewerProcess\s+"[^"]*"'
        
        def replace_viewer_process(match):
            modifications.append("  Fixed viewerProcess in Viewer node")
            return match.group(1) + 'viewerProcess "None"'
        
        content = re.sub(pattern, replace_viewer_process, content, flags=re.DOTALL)
        
        # Check if any modifications were made
        if content != original_content:
            # Write back to file
            with open(script_path, 'w') as f:
                f.write(content)
            
            print("\nModifications made:")
            for mod in modifications:
                print(mod)
            print("=" * 70 + "\n")
            return True
        else:
            print("No OCIO fixes needed")
            print("=" * 70 + "\n")
            return False
            
    except Exception as e:
        print("ERROR: Could not fix script file: {}".format(e))
        import traceback
        traceback.print_exc()
        print("=" * 70 + "\n")
        return False


def set_ocio_from_script(script_path):
    """
    Read OCIO path from script and set OCIO environment variable BEFORE launching Nuke.

    Args:
        script_path: Path to the .nk script file

    Returns:
        OCIO path if found, None otherwise
    """
    if not os.path.exists(script_path):
        return None

    print("\n" + "=" * 70)
    print("MULTISHOT: Setting OCIO environment variable from script")
    print("=" * 70)
    print("Script: {}".format(script_path))

    try:
        # Read the script file
        with open(script_path, 'r') as f:
            content = f.read()

        # Find customOCIOConfigPath in the script
        # Pattern: customOCIOConfigPath <path>
        pattern = r'customOCIOConfigPath\s+([^\s\n]+)'
        match = re.search(pattern, content)

        if match:
            ocio_path = match.group(1)
            print("Found customOCIOConfigPath in script: {}".format(ocio_path))

            # Convert Windows path to Linux path (case-insensitive)
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
                    print("Converted to Linux path: {}".format(ocio_path))
                    break

            # Check if file exists
            if os.path.exists(ocio_path):
                print("OCIO config file EXISTS: {}".format(ocio_path))
                print("Setting OCIO environment variable...")
                os.environ['OCIO'] = ocio_path
                print("OCIO environment variable set to: {}".format(os.environ.get('OCIO')))
                print("=" * 70 + "\n")
                return ocio_path
            else:
                print("ERROR: OCIO config file DOES NOT EXIST: {}".format(ocio_path))
                print("=" * 70 + "\n")
                return None
        else:
            print("No customOCIOConfigPath found in script")
            print("=" * 70 + "\n")
            return None

    except Exception as e:
        print("ERROR: Could not read OCIO from script: {}".format(e))
        import traceback
        traceback.print_exc()
        print("=" * 70 + "\n")
        return None


def main():
    """
    Main entry point for Nuke wrapper.

    Args:
        sys.argv[1]: Nuke executable path
        sys.argv[2:]: Nuke arguments (including script path)
    """
    if len(sys.argv) < 2:
        print("ERROR: No Nuke executable provided")
        print("Usage: python nuke_wrapper.py <nuke_executable> <nuke_args...>")
        sys.exit(1)

    nuke_exe = sys.argv[1]
    nuke_args = sys.argv[2:]

    # Find the script path in the arguments
    script_path = None
    for i, arg in enumerate(nuke_args):
        if arg.endswith('.nk'):
            script_path = arg
            break

    # CRITICAL: Set OCIO environment variable BEFORE launching Nuke
    if script_path:
        set_ocio_from_script(script_path)
        fix_viewer_process_in_script(script_path)

    # Launch Nuke with the original arguments
    cmd = [nuke_exe] + nuke_args
    print("Launching Nuke: {}".format(' '.join(cmd)))
    print("OCIO environment variable: {}".format(os.environ.get('OCIO', 'NOT SET')))

    try:
        # Use subprocess to launch Nuke and wait for it to complete
        result = subprocess.call(cmd)
        sys.exit(result)
    except Exception as e:
        print("ERROR: Could not launch Nuke: {}".format(e))
        sys.exit(1)


if __name__ == "__main__":
    main()

