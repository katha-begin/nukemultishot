"""
Utility to fix invisible knobs in existing Nuke scripts.

This removes all multishot knobs that have the +INVISIBLE flag and recreates them
without the flag so they survive Deadline's file processing.
"""

import logging

logger = logging.getLogger(__name__)


def fix_invisible_knobs():
    """
    Remove and recreate all multishot knobs without +INVISIBLE flag.
    
    This fixes scripts that were created with the old code that used +INVISIBLE.
    Deadline strips knobs with +INVISIBLE flag, so we need to remove it.
    """
    try:
        import nuke
        
        root = nuke.root()
        
        print("\n" + "=" * 80)
        print("FIXING INVISIBLE KNOBS")
        print("=" * 80)
        
        # List of knobs to fix
        knobs_to_fix = [
            'multishot_variables',
            'multishot_context',
            'multishot_custom',
            'project',
            'ep',
            'seq',
            'shot',
            'PROJ_ROOT',
            'IMG_ROOT'
        ]
        
        # Store current values before removing
        saved_values = {}
        for knob_name in knobs_to_fix:
            if knob_name in root.knobs():
                saved_values[knob_name] = root[knob_name].value()
                print(f"  Saved {knob_name} = {saved_values[knob_name]}")
        
        print("\n🗑️  Removing old knobs with +INVISIBLE flag...")
        
        # Remove all multishot knobs
        for knob_name in knobs_to_fix:
            if knob_name in root.knobs():
                root.removeKnob(root[knob_name])
                print(f"  Removed: {knob_name}")
        
        print("\n✨ Creating new knobs WITHOUT +INVISIBLE flag...")

        # Create Multishot tab if it doesn't exist
        if 'multishot_tab' not in root.knobs():
            tab = nuke.Tab_Knob('multishot_tab', 'Multishot')
            root.addKnob(tab)
            print("  Created Multishot tab")

        # Recreate knobs WITHOUT +INVISIBLE flag
        for knob_name in knobs_to_fix:
            if knob_name in saved_values:
                # Create new knob
                knob = nuke.String_Knob(knob_name, knob_name)
                # DON'T set INVISIBLE flag!
                root.addKnob(knob)
                # Restore value
                root[knob_name].setValue(saved_values[knob_name])
                print(f"  Created: {knob_name} = {saved_values[knob_name]}")
        
        print("\n" + "=" * 80)
        print("✅ FIXED! All knobs recreated without +INVISIBLE flag")
        print("=" * 80)
        print("\n⚠️  IMPORTANT: Save your script now! (Ctrl+S)")
        print("=" * 80 + "\n")
        
        nuke.message(
            "✅ Fixed invisible knobs!\n\n"
            "All multishot knobs have been recreated without the +INVISIBLE flag.\n\n"
            "⚠️ IMPORTANT: Save your script now! (Ctrl+S)"
        )
        
        return True
        
    except Exception as e:
        error_msg = f"Error fixing invisible knobs: {e}"
        logger.error(error_msg)
        print(f"\n❌ ERROR: {error_msg}")
        import traceback
        traceback.print_exc()
        
        try:
            import nuke
            nuke.message(f"❌ Error fixing knobs:\n\n{e}")
        except:
            pass
        
        return False


if __name__ == "__main__":
    # Can be run from Script Editor
    fix_invisible_knobs()

