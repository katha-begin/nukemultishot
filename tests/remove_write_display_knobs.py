"""
Remove Display/View Knobs from Write Nodes

This script removes the 'display' and 'view' knobs from Write nodes that cause
"Bad value for display : sRGB - Display" errors on Deadline.

These knobs are part of the "Output Transform" feature in Nuke 16+.
They're for preview purposes only and cause validation errors in batch mode.

Run this in Nuke Script Editor BEFORE submitting to Deadline:

Python 3 (Nuke 16+):
    exec(open('T:/pipeline/development/nuke/nukemultishot/tests/remove_write_display_knobs.py').read())
    remove_write_display_knobs()
    nuke.scriptSave()

Python 2 (Nuke 13-15):
    execfile('T:/pipeline/development/nuke/nukemultishot/tests/remove_write_display_knobs.py')
    remove_write_display_knobs()
    nuke.scriptSave()
"""

def remove_write_display_knobs():
    """
    Remove display and view knobs from all Write nodes.

    These knobs are part of Nuke 16's "Output Transform" feature.
    They cause OCIO validation errors in batch mode because they
    reference display devices that OCIO tries to validate during script loading.

    Returns:
        int: Number of knobs removed
    """
    try:
        import nuke

        print("=" * 70)
        print("REMOVING DISPLAY/VIEW KNOBS FROM WRITE NODES")
        print("(Output Transform feature - Nuke 16+)")
        print("=" * 70)

        removed_count = 0

        # Process all Write nodes
        write_nodes = nuke.allNodes('Write')
        if not write_nodes:
            print("\nNo Write nodes found in script")
            print("=" * 70)
            return 0

        print("\nFound {} Write node(s)".format(len(write_nodes)))
        print("\nProcessing:")

        for node in write_nodes:
            node_name = node.name()
            node_removed = 0

            # Check if node has output transform enabled
            if node.knob('useOCIODisplayView'):
                use_output_transform = node.knob('useOCIODisplayView').value()
                if use_output_transform:
                    print("  {}: Output Transform is ENABLED".format(node_name))
                    # Disable output transform
                    try:
                        node.knob('useOCIODisplayView').setValue(False)
                        print("    -> Disabled Output Transform")
                        removed_count += 1
                    except Exception as e:
                        print("    -> Could not disable: {}".format(e))

            # Remove 'display' knob
            if node.knob('display'):
                try:
                    node.removeKnob(node.knob('display'))
                    print("  {}: Removed 'display' knob".format(node_name))
                    node_removed += 1
                    removed_count += 1
                except Exception as e:
                    print("  {}: Could not remove 'display' knob: {}".format(node_name, e))

            # Remove 'view' knob
            if node.knob('view'):
                try:
                    node.removeKnob(node.knob('view'))
                    print("  {}: Removed 'view' knob".format(node_name))
                    node_removed += 1
                    removed_count += 1
                except Exception as e:
                    print("  {}: Could not remove 'view' knob: {}".format(node_name, e))

            if node_removed == 0 and not (node.knob('useOCIODisplayView') and node.knob('useOCIODisplayView').value()):
                print("  {}: No display/view knobs found".format(node_name))
        
        print("\n" + "=" * 70)
        if removed_count > 0:
            print("SUCCESS: Removed/disabled {} item(s)".format(removed_count))
            print("\nIMPORTANT: SAVE YOUR SCRIPT NOW!")
            print("  nuke.scriptSave()")
            print("\nWhat this does:")
            print("  - Disables Output Transform feature (Nuke 16+)")
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
    Check which Write nodes have display/view knobs or Output Transform enabled.
    """
    try:
        import nuke

        print("=" * 70)
        print("CHECKING WRITE NODES FOR DISPLAY/VIEW KNOBS")
        print("(Output Transform feature - Nuke 16+)")
        print("=" * 70)

        write_nodes = nuke.allNodes('Write')
        if not write_nodes:
            print("\nNo Write nodes found in script")
            print("=" * 70)
            return

        print("\nFound {} Write node(s):\n".format(len(write_nodes)))

        has_issues = False
        for node in write_nodes:
            node_name = node.name()
            issues = []

            # Check Output Transform setting
            if node.knob('useOCIODisplayView'):
                use_output_transform = node.knob('useOCIODisplayView').value()
                if use_output_transform:
                    issues.append("Output Transform=ENABLED")

            if node.knob('display'):
                display_value = node.knob('display').value()
                issues.append("display='{}'".format(display_value))

            if node.knob('view'):
                view_value = node.knob('view').value()
                issues.append("view='{}'".format(view_value))

            if issues:
                print("  {}:".format(node_name))
                for issue in issues:
                    print("    - {}".format(issue))
                has_issues = True
            else:
                print("  {}: OK (no display/view knobs)".format(node_name))

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

