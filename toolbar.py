"""
Nuke toolbar integration for the Multishot Workflow System.

This file adds Multishot buttons to Nuke's toolbar.
"""

try:
    import nuke
    import os
    from multishot.utils.logging import get_logger
    
    logger = get_logger(__name__)
    
    def get_icon_path(icon_name: str) -> str:
        """Get the path to an icon file."""
        current_dir = os.path.dirname(__file__)
        icons_dir = os.path.join(current_dir, "icons")
        return os.path.join(icons_dir, icon_name)
    
    def create_multishot_toolbar():
        """Create Multishot toolbar buttons."""
        try:
            # Get the main toolbar
            toolbar = nuke.toolbar("Nodes")
            
            # Create Multishot group
            multishot_toolbar = toolbar.addMenu("Multishot", icon="multishot_logo.png")

            # Add Browser button
            multishot_toolbar.addCommand(
                "Browser",
                "multishot.ui.show_browser()",
                tooltip="Open Multishot Browser",
                icon="browser.png"
            )

            # Add Node Manager button
            multishot_toolbar.addCommand(
                "Node Manager",
                "multishot.ui.show_node_manager()",
                tooltip="Open Node Manager",
                icon="node_manager.png"
            )
            
            # Add separator
            multishot_toolbar.addSeparator()
            
            # Add custom nodes
            multishot_toolbar.addCommand(
                "Read",
                "nuke.createNode('MultishotRead')",
                tooltip="Create Multishot Read Node",
                icon="read_node.png"
            )

            multishot_toolbar.addCommand(
                "Write",
                "nuke.createNode('MultishotWrite')",
                tooltip="Create Multishot Write Node",
                icon="write_node.png"
            )

            multishot_toolbar.addCommand(
                "Switch",
                "nuke.createNode('MultishotSwitch')",
                tooltip="Create Multishot Switch Node",
                icon="switch_node.png"
            )
            
            logger.info("Multishot toolbar created successfully")
            
        except Exception as e:
            logger.error(f"Error creating Multishot toolbar: {e}")
            print(f"Error creating Multishot toolbar: {e}")
    
    def create_context_toolbar():
        """Create context-aware toolbar buttons."""
        try:
            # Get the main toolbar
            toolbar = nuke.toolbar("Nodes")
            
            # Add context buttons to existing Multishot menu
            multishot_toolbar = toolbar.findItem("Multishot")
            if multishot_toolbar:
                multishot_toolbar.addSeparator()
                
                # Add context refresh button
                multishot_toolbar.addCommand(
                    "Refresh Context",
                    "multishot.get_variable_manager().refresh_context()",
                    tooltip="Refresh shot context from current filename",
                    icon="refresh.png"
                )

                # Add quick shot switcher
                multishot_toolbar.addCommand(
                    "Quick Switch",
                    "multishot.ui.show_quick_switcher()",
                    tooltip="Quick shot context switcher",
                    icon="quick_switch.png"
                )
            
            logger.info("Context toolbar buttons added successfully")
            
        except Exception as e:
            logger.error(f"Error creating context toolbar: {e}")
            print(f"Error creating context toolbar: {e}")
    
    def setup_toolbar_integration():
        """Setup complete toolbar integration."""
        try:
            create_multishot_toolbar()
            create_context_toolbar()
            
            # Add keyboard shortcuts
            setup_keyboard_shortcuts()
            
        except Exception as e:
            logger.error(f"Error setting up toolbar integration: {e}")
            print(f"Error setting up toolbar integration: {e}")
    
    def setup_keyboard_shortcuts():
        """Setup keyboard shortcuts for Multishot functions."""
        try:
            # Browser shortcut (Ctrl+Shift+M)
            nuke.menu('Nuke').addCommand(
                'Multishot/Browser',
                'multishot.ui.show_browser()',
                'ctrl+shift+m'
            )
            
            # Node Manager shortcut (Ctrl+Shift+N)
            nuke.menu('Nuke').addCommand(
                'Multishot/Node Manager',
                'multishot.ui.show_node_manager()',
                'ctrl+shift+n'
            )
            
            # Quick context refresh (F5)
            nuke.menu('Nuke').addCommand(
                'Multishot/Refresh Context',
                'multishot.get_variable_manager().refresh_context()',
                'F5'
            )
            
            logger.info("Keyboard shortcuts setup completed")
            
        except Exception as e:
            logger.error(f"Error setting up keyboard shortcuts: {e}")
            print(f"Error setting up keyboard shortcuts: {e}")
    
    # Setup toolbar when this file is loaded
    if nuke.GUI:
        # Defer toolbar creation until Nuke is fully loaded
        nuke.addOnCreate(setup_toolbar_integration, nodeClass='Root')
    
except ImportError:
    # Not in Nuke environment
    pass
except Exception as e:
    print(f"Error in toolbar.py: {e}")
    import traceback
    traceback.print_exc()
