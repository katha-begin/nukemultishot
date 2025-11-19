"""
Fix Root Node OCIO Display Settings

This script fixes the Root node's OCIO display settings that cause
"Bad value for display : sRGB - Display" errors on Deadline.

The issue is that the Root node stores default display/view settings
that may reference display device names that OCIO considers invalid.

Run this in Nuke Script Editor BEFORE submitting to Deadline.
"""

def fix_root_ocio_display():
    """
    Fix Root node OCIO display settings.
    
    This removes or resets problematic display/view settings in the Root node
    that cause OCIO validation errors in batch mode.
    """
    try:
        import nuke
        
        print("=" * 60)
        print("Checking Root node OCIO display settings...")
        print("=" * 60)
        
        root = nuke.root()
        fixed_count = 0
        
        # List of knobs that might contain problematic display settings
        ocio_knobs = [
            'defaultViewerLUT',
            'monitorLut',
            'int8Lut',
            'int16Lut',
            'logLut',
            'floatLut',
        ]
        
        print("\nChecking Root node knobs:")
        for knob_name in ocio_knobs:
            if root.knob(knob_name):
                current_value = root.knob(knob_name).value()
                print("  {}: '{}'".format(knob_name, current_value))
                
                # If it contains "- Display", it's problematic
                if isinstance(current_value, str) and '- Display' in current_value:
                    print("    -> PROBLEMATIC! Contains '- Display'")
                    # Try to set to a safe default
                    try:
                        root.knob(knob_name).setValue('default')
                        print("    -> Changed to 'default'")
                        fixed_count += 1
                    except:
                        try:
                            root.knob(knob_name).setValue('')
                            print("    -> Changed to '' (empty)")
                            fixed_count += 1
                        except:
                            print("    -> Could not change")
        
        # Check Viewer nodes
        print("\nChecking Viewer nodes:")
        for viewer in nuke.allNodes('Viewer'):
            print("  Viewer: '{}'".format(viewer.name()))
            
            # Check viewerProcess knob
            if viewer.knob('viewerProcess'):
                current_value = viewer.knob('viewerProcess').value()
                print("    viewerProcess: '{}'".format(current_value))
                
                if isinstance(current_value, str) and '- Display' in current_value:
                    print("      -> PROBLEMATIC! Contains '- Display'")
                    try:
                        viewer.knob('viewerProcess').setValue('None')
                        print("      -> Changed to 'None'")
                        fixed_count += 1
                    except:
                        print("      -> Could not change")
        
        # Check if OCIO config is set
        print("\nChecking OCIO config:")
        if root.knob('customOCIOConfigPath'):
            ocio_path = root.knob('customOCIOConfigPath').value()
            print("  customOCIOConfigPath: '{}'".format(ocio_path))
            
            # Suggest removing OCIO config for batch mode
            print("\n  RECOMMENDATION:")
            print("  For Deadline rendering, consider REMOVING the customOCIOConfigPath")
            print("  from the Root node. Nuke will use the default OCIO config or")
            print("  the OCIO environment variable set by Deadline.")
            print("\n  To remove it, run:")
            print("    nuke.root().knob('customOCIOConfigPath').setValue('')")
        
        print("\n" + "=" * 60)
        if fixed_count > 0:
            print("Fixed {} OCIO display settings".format(fixed_count))
            print("\nIMPORTANT: Save your script now!")
            print("  nuke.scriptSave()")
        else:
            print("No OCIO display settings needed fixing")
        print("=" * 60)
        
        return fixed_count
        
    except Exception as e:
        print("Error fixing Root OCIO display settings: {}".format(e))
        import traceback
        traceback.print_exc()
        return 0


def remove_ocio_config_from_root():
    """
    Remove the customOCIOConfigPath from the Root node.
    
    This forces Nuke to use the OCIO environment variable or default config,
    which can avoid validation errors during script loading.
    """
    try:
        import nuke
        
        root = nuke.root()
        if root.knob('customOCIOConfigPath'):
            current_path = root.knob('customOCIOConfigPath').value()
            if current_path:
                print("Removing customOCIOConfigPath from Root node")
                print("  Current: '{}'".format(current_path))
                root.knob('customOCIOConfigPath').setValue('')
                print("  Removed!")
                print("\nIMPORTANT: Save your script now!")
                print("  nuke.scriptSave()")
                return True
            else:
                print("customOCIOConfigPath is already empty")
                return False
        else:
            print("customOCIOConfigPath knob not found")
            return False
            
    except Exception as e:
        print("Error removing OCIO config: {}".format(e))
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    # Run the fix
    fix_root_ocio_display()
    
    print("\n" + "=" * 60)
    print("NEXT STEPS:")
    print("=" * 60)
    print("1. Review the changes above")
    print("2. If you want to remove the OCIO config path, run:")
    print("     remove_ocio_config_from_root()")
    print("3. Save your script:")
    print("     nuke.scriptSave()")
    print("4. Submit to Deadline")
    print("=" * 60)

