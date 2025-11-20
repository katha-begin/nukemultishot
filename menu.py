"""
Nuke menu integration for the Multishot Workflow System.

This file sets up the Multishot menu in Nuke's menu bar.
"""

try:
    import nuke
    import multishot
    from multishot.utils.logging import get_logger
    
    logger = get_logger(__name__)
    
    def setup_multishot_menu():
        """Setup the Multishot menu in Nuke."""
        try:
            # Get the main menu bar
            menubar = nuke.menu('Nuke')
            
            # Create Multishot menu
            multishot_menu = menubar.addMenu('Multishot')
            
            # Add main commands
            multishot_menu.addCommand(
                'Browser', 
                'multishot.ui.show_browser()',
                tooltip='Open the Multishot Browser for project navigation'
            )
            
            multishot_menu.addCommand(
                'Multishot Manager',
                'import multishot.ui; multishot.ui.show_multishot_manager()',
                tooltip='Manage shots and versions in multi-shot workflow'
            )

            multishot_menu.addCommand(
                'Node Manager (Old)',
                'multishot.ui.show_node_manager()',
                tooltip='[Deprecated] Old node manager - use Multishot Manager instead'
            )

            multishot_menu.addSeparator()

            # Add utility commands
            multishot_menu.addCommand(
                'Fix Invisible Knobs',
                'from multishot.utils.fix_invisible_knobs import fix_invisible_knobs; fix_invisible_knobs()',
                tooltip='Remove +INVISIBLE flag from multishot knobs (fixes Deadline stripping issue)'
            )

            multishot_menu.addSeparator()

            # Add Deadline submission
            multishot_menu.addCommand(
                'Submit to Deadline',
                'import multishot.deadline; multishot.deadline.submit_to_deadline()',
                tooltip='Submit to Deadline with automatic environment variable setup'
            )

            multishot_menu.addCommand(
                'Submit to Deadline (Vanilla - No Callbacks)',
                'import multishot.deadline; multishot.deadline.submit_to_deadline_vanilla()',
                tooltip='Submit to Deadline with ALL callbacks disabled (for testing)'
            )

            multishot_menu.addSeparator()

            # Add utility commands
            multishot_menu.addCommand(
                'Refresh Context',
                'multishot.get_variable_manager().refresh_context()',
                tooltip='Refresh the current shot context from filename'
            )

            multishot_menu.addCommand(
                'Show Variables',
                'multishot.ui.show_variables_dialog()',
                tooltip='View and edit current variables'
            )

            multishot_menu.addSeparator()
            
            # Add help and about
            multishot_menu.addCommand(
                'Documentation',
                'multishot.ui.show_documentation()',
                tooltip='Open Multishot documentation'
            )
            
            multishot_menu.addCommand(
                'About',
                'multishot.ui.show_about()',
                tooltip='About Multishot Workflow System'
            )
            
            logger.info("Multishot menu setup completed")
            
        except Exception as e:
            logger.error(f"Error setting up Multishot menu: {e}")
            print(f"Error setting up Multishot menu: {e}")
    
    def setup_nodes_menu():
        """Setup Multishot nodes in the Nodes menu."""
        try:
            # Get the Nodes menu
            nodes_menu = nuke.menu('Nodes')
            
            # Create Multishot submenu
            multishot_nodes = nodes_menu.addMenu('Multishot')
            
            # Add custom nodes
            multishot_nodes.addCommand(
                'Read',
                'import multishot.nodes.read_node; multishot.nodes.read_node.create_multishot_read()',
                tooltip='Create a Multishot Read node with variable-driven paths'
            )

            multishot_nodes.addCommand(
                'Write',
                'import multishot.nodes.write_node; multishot.nodes.write_node.create_multishot_write()',
                tooltip='Create a Multishot Write node with variable-driven paths and auto directory creation'
            )

            multishot_nodes.addCommand(
                'Switch',
                'import multishot.nodes.switch_node; multishot.nodes.switch_node.create_multishot_switch()',
                tooltip='Create a Multishot Switch node with variable-based switching'
            )
            
            multishot_nodes.addCommand(
                'Write',
                'nuke.createNode("MultishotWrite")',
                tooltip='Create a Multishot Write node with variable-driven paths'
            )
            
            multishot_nodes.addCommand(
                'Switch',
                'nuke.createNode("MultishotSwitch")',
                tooltip='Create a Multishot Switch node for shot-based switching'
            )
            
            logger.info("Multishot nodes menu setup completed")
            
        except Exception as e:
            logger.error(f"Error setting up Multishot nodes menu: {e}")
            print(f"Error setting up Multishot nodes menu: {e}")
    
    # Setup menus when this file is loaded
    if nuke.GUI:
        setup_multishot_menu()
        setup_nodes_menu()
    
except ImportError:
    # Not in Nuke environment
    pass
except Exception as e:
    print(f"Error in menu.py: {e}")
    import traceback
    traceback.print_exc()
