"""
Disable OCIO Config for Deadline Rendering

This script removes the OCIO config from the Root node so that Deadline
renders use Nuke's default OCIO config instead of a custom one.

This avoids "Bad value for display : sRGB - Display" errors.

Run this in Nuke Script Editor BEFORE submitting to Deadline.
"""

def disable_ocio_for_deadline():
    """
    Disable custom OCIO config for Deadline rendering.
    
    This removes the customOCIOConfigPath from the Root node,
    forcing Nuke to use its default OCIO config.
    
    Returns:
        bool: True if changes were made, False otherwise
    """
    try:
        import nuke
        
        print("=" * 70)
        print("DISABLING CUSTOM OCIO CONFIG FOR DEADLINE")
        print("=" * 70)
        
        root = nuke.root()
        changes_made = False
        
        # Remove customOCIOConfigPath
        if root.knob('customOCIOConfigPath'):
            current_path = root.knob('customOCIOConfigPath').value()
            if current_path:
                print("\n1. Removing customOCIOConfigPath from Root node:")
                print("   Current: '{}'".format(current_path))
                root.knob('customOCIOConfigPath').setValue('')
                print("   Status: REMOVED")
                changes_made = True
            else:
                print("\n1. customOCIOConfigPath: Already empty")
        
        # Set all Viewer nodes to use default/none
        print("\n2. Setting Viewer nodes to 'None':")
        viewer_count = 0
        for viewer in nuke.allNodes('Viewer'):
            if viewer.knob('viewerProcess'):
                current_value = viewer.knob('viewerProcess').value()
                if current_value != 'None':
                    viewer.knob('viewerProcess').setValue('None')
                    print("   Viewer '{}': '{}' -> 'None'".format(viewer.name(), current_value))
                    viewer_count += 1
                    changes_made = True
                else:
                    print("   Viewer '{}': Already 'None'".format(viewer.name()))
        
        if viewer_count == 0:
            print("   No Viewer nodes needed changes")
        
        # Summary
        print("\n" + "=" * 70)
        if changes_made:
            print("CHANGES MADE - SAVE YOUR SCRIPT NOW!")
            print("\nRun this command to save:")
            print("  nuke.scriptSave()")
            print("\nWhat this means:")
            print("  - Nuke will use its default OCIO config (sRGB/Rec.709)")
            print("  - No custom OCIO validation errors on Deadline")
            print("  - Renders will use Linear colorspace by default")
            print("  - You can still set specific colorspaces on Read/Write nodes")
        else:
            print("NO CHANGES NEEDED")
            print("  - customOCIOConfigPath is already empty")
            print("  - Viewer nodes are already set to 'None'")
        print("=" * 70)
        
        return changes_made
        
    except Exception as e:
        print("\nERROR: {}".format(e))
        import traceback
        traceback.print_exc()
        return False


def check_ocio_status():
    """
    Check current OCIO configuration status.
    """
    try:
        import nuke
        
        print("=" * 70)
        print("CURRENT OCIO STATUS")
        print("=" * 70)
        
        root = nuke.root()
        
        # Check customOCIOConfigPath
        if root.knob('customOCIOConfigPath'):
            ocio_path = root.knob('customOCIOConfigPath').value()
            if ocio_path:
                print("\ncustomOCIOConfigPath: SET")
                print("  Path: '{}'".format(ocio_path))
                print("  Status: WILL CAUSE DEADLINE ERRORS")
            else:
                print("\ncustomOCIOConfigPath: NOT SET")
                print("  Status: OK FOR DEADLINE")
        
        # Check Viewer nodes
        print("\nViewer Nodes:")
        viewers = nuke.allNodes('Viewer')
        if viewers:
            for viewer in viewers:
                if viewer.knob('viewerProcess'):
                    value = viewer.knob('viewerProcess').value()
                    status = "OK" if value == 'None' else "MAY CAUSE ISSUES"
                    print("  '{}': '{}' ({})".format(viewer.name(), value, status))
        else:
            print("  No Viewer nodes found")
        
        # Check Read/Write nodes
        print("\nRead Nodes:")
        read_nodes = nuke.allNodes('Read')
        if read_nodes:
            for node in read_nodes[:5]:  # Show first 5
                if node.knob('colorspace'):
                    cs = node.knob('colorspace').value()
                    status = "ISSUE" if '- Display' in cs else "OK"
                    print("  '{}': '{}' ({})".format(node.name(), cs, status))
            if len(read_nodes) > 5:
                print("  ... and {} more Read nodes".format(len(read_nodes) - 5))
        else:
            print("  No Read nodes found")
        
        print("\nWrite Nodes:")
        write_nodes = nuke.allNodes('Write')
        if write_nodes:
            for node in write_nodes[:5]:  # Show first 5
                if node.knob('colorspace'):
                    cs = node.knob('colorspace').value()
                    status = "ISSUE" if '- Display' in cs else "OK"
                    print("  '{}': '{}' ({})".format(node.name(), cs, status))
            if len(write_nodes) > 5:
                print("  ... and {} more Write nodes".format(len(write_nodes) - 5))
        else:
            print("  No Write nodes found")
        
        print("=" * 70)
        
    except Exception as e:
        print("\nERROR: {}".format(e))
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    # First check status
    check_ocio_status()
    
    print("\n")
    
    # Then disable OCIO
    disable_ocio_for_deadline()

