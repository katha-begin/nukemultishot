#!/usr/bin/env python
"""
Deadline Pre-Render Script: Fix OCIO Display Settings

This script runs BEFORE Nuke loads the script file and fixes OCIO display
device names that are incorrectly used as colorspaces.

Usage:
1. Copy this file to: <DeadlineRepository>/custom/scripts/Jobs/
2. In Deadline job submission, set "Pre Render Script" to this file
3. Or add it to the Nuke plugin configuration as a default pre-render script

The script will:
- Read the .nk file
- Replace display device names with proper colorspaces
- Save the fixed file
- Nuke will then load the fixed file without errors
"""

from __future__ import print_function
import os
import re
import sys

def fix_ocio_in_nuke_script(script_path):
    """
    Fix OCIO display device names in a Nuke script file.
    
    Args:
        script_path: Path to the .nk file
        
    Returns:
        True if fixes were applied, False otherwise
    """
    if not os.path.exists(script_path):
        print("ERROR: Script file not found: {}".format(script_path))
        return False
    
    print("Deadline Pre-Render: Fixing OCIO settings in {}".format(script_path))
    
    # Read the script file
    try:
        with open(script_path, 'r') as f:
            content = f.read()
    except Exception as e:
        print("ERROR: Could not read script file: {}".format(e))
        return False
    
    # Map of display device names to proper colorspaces
    replacements = {
        # Display device names that should be colorspaces
        'colorspace "sRGB - Display"': 'colorspace "sRGB - Texture"',
        'colorspace sRGB\\ -\\ Display': 'colorspace sRGB\\ -\\ Texture',
        'colorspace {sRGB - Display}': 'colorspace {sRGB - Texture}',
        
        'colorspace "Rec.1886 Rec.709 - Display"': 'colorspace "Rec.709 - Display"',
        'colorspace Rec.1886\\ Rec.709\\ -\\ Display': 'colorspace Rec.709\\ -\\ Display',
        'colorspace {Rec.1886 Rec.709 - Display}': 'colorspace {Rec.709 - Display}',
        
        'colorspace "Rec.1886 Rec.2020 - Display"': 'colorspace "Rec.2020 - Display"',
        'colorspace Rec.1886\\ Rec.2020\\ -\\ Display': 'colorspace Rec.2020\\ -\\ Display',
        'colorspace {Rec.1886 Rec.2020 - Display}': 'colorspace {Rec.2020 - Display}',
    }
    
    # Apply replacements
    fixed_content = content
    fixes_applied = 0
    
    for old_value, new_value in replacements.items():
        if old_value in fixed_content:
            count = fixed_content.count(old_value)
            fixed_content = fixed_content.replace(old_value, new_value)
            fixes_applied += count
            print("  Replaced '{}' -> '{}' ({} occurrences)".format(
                old_value, new_value, count))
    
    # If no fixes needed, return
    if fixes_applied == 0:
        print("  No OCIO fixes needed")
        return False
    
    # Write the fixed content back
    try:
        with open(script_path, 'w') as f:
            f.write(fixed_content)
        print("  Applied {} OCIO fixes to script file".format(fixes_applied))
        return True
    except Exception as e:
        print("ERROR: Could not write fixed script file: {}".format(e))
        return False

def main():
    """
    Main entry point for Deadline pre-render script.
    Deadline provides the script path via environment variable or command line.
    """
    print("=" * 60)
    print("Deadline Pre-Render Script: Fix OCIO Display Settings")
    print("=" * 60)
    
    # Get script path from Deadline environment variables
    script_path = None
    
    # Try different environment variables that Deadline might set
    env_vars = [
        'DEADLINE_NUKE_SCRIPT_FILE',
        'DEADLINE_PLUGIN_SCRIPT_FILE', 
        'NUKE_SCRIPT_FILE',
    ]
    
    for env_var in env_vars:
        if env_var in os.environ:
            script_path = os.environ[env_var]
            print("Found script path from {}: {}".format(env_var, script_path))
            break
    
    # If not found in environment, try command line arguments
    if not script_path and len(sys.argv) > 1:
        script_path = sys.argv[1]
        print("Found script path from command line: {}".format(script_path))
    
    if not script_path:
        print("ERROR: Could not determine script path")
        print("Environment variables checked: {}".format(env_vars))
        print("Command line arguments: {}".format(sys.argv))
        return 1
    
    # Fix the script
    success = fix_ocio_in_nuke_script(script_path)
    
    if success:
        print("SUCCESS: OCIO settings fixed")
        return 0
    else:
        print("INFO: No OCIO fixes applied (may not be needed)")
        return 0

if __name__ == '__main__':
    sys.exit(main())

