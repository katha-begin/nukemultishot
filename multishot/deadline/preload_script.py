#!/usr/bin/env python
"""
Deadline Pre-Load Script for Multishot Nuke Scripts

This script runs BEFORE Nuke is launched to fix OCIO-related issues in the .nk script file.
It modifies the script file to remove or fix invalid viewerProcess and display settings
that would cause errors in batch mode.

This is registered in the Deadline job submission as a PreLoad script.
"""

import os
import re
import sys


def fix_viewer_process_in_script(script_path):
    """
    Fix viewerProcess settings in a Nuke script file.
    
    This removes or fixes invalid viewerProcess values that cause errors in batch mode:
    - "ACES 1.0 - SDR Video (sRGB - Display)" -> "None"
    - Any viewerProcess with "(Display)" in the name -> "None"
    
    Args:
        script_path: Path to the .nk script file
        
    Returns:
        True if modifications were made, False otherwise
    """
    if not os.path.exists(script_path):
        print("ERROR: Script file not found: {}".format(script_path))
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
        
        # Pattern 1: Fix viewerProcess with display names
        # Example: viewerProcess "ACES 1.0 - SDR Video (sRGB - Display)"
        pattern1 = r'viewerProcess\s+"[^"]*\([^)]*Display\)[^"]*"'
        matches1 = re.findall(pattern1, content)
        if matches1:
            for match in matches1:
                modifications.append("  Found: {}".format(match))
            content = re.sub(pattern1, 'viewerProcess "None"', content)
            modifications.append("  -> Changed to: viewerProcess \"None\"")
        
        # Pattern 2: Fix viewerProcess with ACES transforms
        # Example: viewerProcess "ACES 1.0 - SDR Video"
        pattern2 = r'viewerProcess\s+"ACES[^"]*"'
        matches2 = re.findall(pattern2, content)
        if matches2:
            for match in matches2:
                if match not in matches1:  # Don't double-count
                    modifications.append("  Found: {}".format(match))
            content = re.sub(pattern2, 'viewerProcess "None"', content)
            modifications.append("  -> Changed to: viewerProcess \"None\"")
        
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
    Main entry point for Deadline PreLoad script.
    
    Deadline passes the script path as a command-line argument.
    """
    if len(sys.argv) < 2:
        print("ERROR: No script path provided")
        print("Usage: python preload_script.py <script_path>")
        sys.exit(1)
    
    script_path = sys.argv[1]
    
    # Fix the script
    success = fix_viewer_process_in_script(script_path)
    
    # Exit with success code
    sys.exit(0 if success else 0)  # Always exit 0 to not block rendering


if __name__ == "__main__":
    main()

