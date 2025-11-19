"""
Fix OCIO Display Settings for Deadline Rendering

This script fixes OCIO display device names that are incorrectly used as colorspaces.
Run this in Nuke GUI BEFORE submitting to Deadline to prevent render errors.

Usage:
    1. Open your Nuke script
    2. Run this script in the Script Editor
    3. Submit to Deadline

The script will:
- Scan all Read and Write nodes
- Replace display device names (e.g., "sRGB - Display") with proper colorspaces (e.g., "sRGB - Texture")
- Save the script with fixes applied
"""

from __future__ import print_function
import nuke

def fix_ocio_display_settings():
    """
    Fix OCIO display device names in the current Nuke script.
    
    Returns:
        int: Number of fixes applied
    """
    print("=" * 60)
    print("Fixing OCIO Display Settings for Deadline")
    print("=" * 60)
    
    # Map of display device names to proper colorspaces
    display_to_colorspace_map = {
        'sRGB - Display': 'sRGB - Texture',
        'Rec.1886 Rec.709 - Display': 'Rec.709 - Display',
        'Rec.1886 Rec.2020 - Display': 'Rec.2020 - Display',
    }
    
    fixed_count = 0
    fixed_nodes = []
    
    # Fix Read nodes
    print("\nChecking Read nodes...")
    for node in nuke.allNodes('Read'):
        try:
            if node.knob('colorspace'):
                current_cs = node.knob('colorspace').value()
                if current_cs in display_to_colorspace_map:
                    new_cs = display_to_colorspace_map[current_cs]
                    node.knob('colorspace').setValue(new_cs)
                    print("  Read '{}': '{}' -> '{}'".format(
                        node.name(), current_cs, new_cs))
                    fixed_nodes.append(node.name())
                    fixed_count += 1
        except Exception as e:
            print("  Warning: Could not check Read node '{}': {}".format(node.name(), e))
    
    # Fix Write nodes
    print("\nChecking Write nodes...")
    for node in nuke.allNodes('Write'):
        try:
            if node.knob('colorspace'):
                current_cs = node.knob('colorspace').value()
                if current_cs in display_to_colorspace_map:
                    new_cs = display_to_colorspace_map[current_cs]
                    node.knob('colorspace').setValue(new_cs)
                    print("  Write '{}': '{}' -> '{}'".format(
                        node.name(), current_cs, new_cs))
                    fixed_nodes.append(node.name())
                    fixed_count += 1
        except Exception as e:
            print("  Warning: Could not check Write node '{}': {}".format(node.name(), e))
    
    # Summary
    print("\n" + "=" * 60)
    if fixed_count > 0:
        print("FIXED {} nodes:".format(fixed_count))
        for node_name in fixed_nodes:
            print("  - {}".format(node_name))
        print("\nSaving script...")
        try:
            nuke.scriptSave()
            print("SUCCESS: Script saved with OCIO fixes")
            print("\nYou can now safely submit to Deadline!")
        except Exception as e:
            print("WARNING: Could not auto-save script: {}".format(e))
            print("Please save the script manually before submitting to Deadline")
    else:
        print("No OCIO fixes needed - script is ready for Deadline")
    print("=" * 60)
    
    return fixed_count

# Run the fix
if __name__ == '__main__':
    try:
        fix_ocio_display_settings()
    except Exception as e:
        print("ERROR: {}".format(e))
        import traceback
        traceback.print_exc()

