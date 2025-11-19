"""
Remove Display/View Knobs from Write Nodes

This script removes the 'display' and 'view' knobs from Write nodes that cause
"Bad value for display : sRGB - Display" errors on Deadline.

These knobs are automatically added by Nuke when OCIO is enabled, but they're
for preview purposes only and cause validation errors in batch mode.

Run this in Nuke Script Editor BEFORE submitting to Deadline.
"""

def remove_write_display_knobs():
    """
    Remove display and view knobs from all Write nodes.
    
    These knobs cause OCIO validation errors in batch mode because they
    reference display devices that OCIO tries to validate during script loading.
    
    Returns:
        int: Number of knobs removed
    """
    try:
        import nuke
        
        print("=" * 70)
        print("REMOVING DISPLAY/VIEW KNOBS FROM WRITE NODES")
        print("=" * 70)
        
        removed_count = 0
        
        # Process all Write nodes
        write_nodes = nuke.allNodes('Write')
        if not write_nodes:
            print("\nNo Write nodes found in script")
            print("=" * 70)
            return 0
        
        print(f"\nFound {len(write_nodes)} Write node(s)")
        print("\nProcessing:")
        
        for node in write_nodes:
            node_name = node.name()
            node_removed = 0
            
            # Remove 'display' knob
            if node.knob('display'):
                try:
                    node.removeKnob(node.knob('display'))
                    print(f"  {node_name}: Removed 'display' knob")
                    node_removed += 1
                    removed_count += 1
                except Exception as e:
                    print(f"  {node_name}: Could not remove 'display' knob: {e}")
            
            # Remove 'view' knob
            if node.knob('view'):
                try:
                    node.removeKnob(node.knob('view'))
                    print(f"  {node_name}: Removed 'view' knob")
                    node_removed += 1
                    removed_count += 1
                except Exception as e:
                    print(f"  {node_name}: Could not remove 'view' knob: {e}")
            
            if node_removed == 0:
                print(f"  {node_name}: No display/view knobs found")
        
        print("\n" + "=" * 70)
        if removed_count > 0:
            print(f"SUCCESS: Removed {removed_count} knob(s)")
            print("\nIMPORTANT: SAVE YOUR SCRIPT NOW!")
            print("  nuke.scriptSave()")
            print("\nWhat this does:")
            print("  - Removes preview-only display/view knobs from Write nodes")
            print("  - Prevents OCIO validation errors in batch mode")
            print("  - Does NOT affect colorspace settings")
            print("  - Your OCIO config will still be used")
        else:
            print("No display/view knobs found to remove")
        print("=" * 70)
        
        return removed_count
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return 0


def check_write_display_knobs():
    """
    Check which Write nodes have display/view knobs.
    """
    try:
        import nuke
        
        print("=" * 70)
        print("CHECKING WRITE NODES FOR DISPLAY/VIEW KNOBS")
        print("=" * 70)
        
        write_nodes = nuke.allNodes('Write')
        if not write_nodes:
            print("\nNo Write nodes found in script")
            print("=" * 70)
            return
        
        print(f"\nFound {len(write_nodes)} Write node(s):\n")
        
        has_issues = False
        for node in write_nodes:
            node_name = node.name()
            issues = []
            
            if node.knob('display'):
                display_value = node.knob('display').value()
                issues.append(f"display='{display_value}'")
            
            if node.knob('view'):
                view_value = node.knob('view').value()
                issues.append(f"view='{view_value}'")
            
            if issues:
                print(f"  {node_name}:")
                for issue in issues:
                    print(f"    - {issue}")
                has_issues = True
            else:
                print(f"  {node_name}: OK (no display/view knobs)")
        
        print("\n" + "=" * 70)
        if has_issues:
            print("FOUND PROBLEMATIC KNOBS")
            print("\nThese knobs will cause 'Bad value for display' errors on Deadline.")
            print("\nTo fix, run:")
            print("  remove_write_display_knobs()")
        else:
            print("ALL WRITE NODES ARE OK")
        print("=" * 70)
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    # First check status
    check_write_display_knobs()
    
    print("\n")
    
    # Ask user to confirm
    print("Do you want to remove the display/view knobs? (This will fix the Deadline error)")
    print("Run: remove_write_display_knobs()")

