"""
Custom Nuke nodes for the Multishot Workflow System.

This module contains custom Read, Write, and Switch nodes that support
variable-driven paths and multishot workflows.
"""

# Import custom nodes
from .read_node import MultishotRead, create_multishot_read
from .write_node import MultishotWrite, create_multishot_write
from .write_gizmo import MultishotWriteGizmo, create_multishot_write_gizmo
from .switch_node import MultishotSwitch, create_multishot_switch
from .base_node import BaseMultishotNode

def register_all_nodes():
    """Register all custom nodes with Nuke."""
    try:
        import nuke
        
        # Register custom nodes
        nuke.menu('Nodes').addCommand('Multishot/Read', 'multishot.nodes.create_multishot_read()')
        nuke.menu('Nodes').addCommand('Multishot/Write', 'multishot.nodes.create_multishot_write()')
        nuke.menu('Nodes').addCommand('Multishot/Write Gizmo', 'multishot.nodes.create_multishot_write_gizmo()')
        nuke.menu('Nodes').addCommand('Multishot/Switch', 'multishot.nodes.create_multishot_switch()')

        print("Multishot custom nodes registered successfully")
        
    except ImportError:
        # Not in Nuke environment
        print("Warning: Not in Nuke environment, skipping node registration")
    except Exception as e:
        print(f"Error registering custom nodes: {e}")

__all__ = [
    'MultishotRead',
    'MultishotWrite',
    'MultishotWriteGizmo',
    'MultishotSwitch',
    'BaseMultishotNode',
    'register_all_nodes',
    'create_multishot_read',
    'create_multishot_write',
    'create_multishot_write_gizmo',
    'create_multishot_switch'
]
