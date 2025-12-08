"""
Custom Switch node for the Multishot Workflow System.

This module provides the multishot_switch gizmo that routes inputs
based on root.shot matching shot slot knobs.

The gizmo is located at: gizmo/Utilities/multishot_switch.gizmo

How it works:
- Reads shot name from root.shot
- Compares against shotA, shotB, shotC, shotD, shotE knobs
- Each slot supports comma-separated shot names (e.g. "SH010, SH020")
- Uses TCL expression with lsearch to route to matching input (1-5)
- Falls back to input 0 (main) if no match
"""

from ..utils.logging import get_logger


def create_multishot_switch():
    """
    Create a new multishot_switch gizmo.

    This function is called from Nuke's menu system.
    Creates the gizmo/Utilities/multishot_switch.gizmo node.

    Returns:
        Created Nuke node or None on error
    """
    try:
        import nuke

        # Create the gizmo (requires plugin path to be set)
        node = nuke.createNode('multishot_switch')
        return node

    except Exception as e:
        logger = get_logger(__name__)
        logger.error(f"Error creating multishot_switch: {e}")
        try:
            import nuke
            nuke.message(f"Error creating multishot_switch: {e}\n\nMake sure the gizmo directory is in your plugin path.")
        except:
            pass
        return None


# Alias for backward compatibility
MultishotSwitch = None  # Class removed - use gizmo instead
