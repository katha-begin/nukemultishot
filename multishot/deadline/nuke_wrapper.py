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
    
    # Fix the script if found
    if script_path:
        fix_viewer_process_in_script(script_path)
    
    # Launch Nuke with the original arguments
    cmd = [nuke_exe] + nuke_args
    print("Launching Nuke: {}".format(' '.join(cmd)))
    
    try:
        # Use subprocess to launch Nuke and wait for it to complete
        result = subprocess.call(cmd)
        sys.exit(result)
    except Exception as e:
        print("ERROR: Could not launch Nuke: {}".format(e))
        sys.exit(1)


if __name__ == "__main__":
    main()

