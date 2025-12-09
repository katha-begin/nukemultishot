"""
User interface components for the Multishot Workflow System.

This module contains the main browser UI, node management interface,
and custom widgets for the multishot workflow.

NOTE: UI components are imported lazily to avoid Qt/display errors in batch mode.
Use the show_*() functions or import directly when needed in GUI mode.
"""

# Import only safe utilities that don't require Qt
# UI classes are imported lazily when needed

# Global instances to prevent garbage collection
_browser_instance = None
_multishot_manager_instance = None
_node_manager_instance = None
_shared_variable_manager = None

# Panel registration constants
MULTISHOT_MANAGER_PANEL_ID = 'com.multishot.MultishotManager'
MULTISHOT_MANAGER_PANEL_NAME = 'Multishot Manager'

def get_shared_variable_manager():
    """Get or create the shared VariableManager instance."""
    global _shared_variable_manager
    if _shared_variable_manager is None:
        from ..core.variables import VariableManager
        _shared_variable_manager = VariableManager()
    return _shared_variable_manager


def _create_multishot_manager_panel():
    """
    Factory function for creating MultishotManagerDialog instance.
    This is called by nukescripts.panels when the panel is created.
    """
    global _multishot_manager_instance

    # Restore MultishotRead instances from existing nodes
    from ..nodes.read_node import restore_multishot_instances
    variable_manager = get_shared_variable_manager()
    restore_multishot_instances(variable_manager)

    # Create instance with docked mode flag
    _multishot_manager_instance = _create_manager_widget(variable_manager, docked=True)
    return _multishot_manager_instance


def _create_manager_widget(variable_manager, docked=False):
    """
    Create MultishotManagerDialog widget.

    Args:
        variable_manager: The VariableManager instance to use
        docked: If True, apply docked panel styling (reduced margins)
    """
    from .multishot_manager import MultishotManagerDialog
    widget = MultishotManagerDialog(variable_manager=variable_manager)

    if docked:
        # Apply docked styling - reduce margins for better panel integration
        widget.setContentsMargins(0, 0, 0, 0)
        if widget.layout():
            widget.layout().setContentsMargins(4, 4, 4, 4)

    return widget


def setup_ui_integration():
    """Setup UI integration with Nuke (only in GUI mode)."""
    try:
        import nuke

        # Only setup UI in GUI mode
        if not nuke.GUI:
            print("Multishot: Batch mode detected, skipping UI integration")
            return

        # Register dockable panels
        _register_dockable_panels()

        # Add to Nuke menu
        menubar = nuke.menu('Nuke')
        multishot_menu = menubar.addMenu('Multishot')

        # Add menu commands
        multishot_menu.addCommand('Browser', 'multishot.ui.show_browser()')
        multishot_menu.addCommand('Multishot Manager', 'multishot.ui.show_multishot_manager()')
        multishot_menu.addCommand('Node Manager', 'multishot.ui.show_node_manager()')
        multishot_menu.addSeparator()
        multishot_menu.addCommand('About', 'multishot.ui.show_about()')

        print("Multishot UI integration setup successfully")

    except ImportError:
        # Not in Nuke environment
        print("Warning: Not in Nuke environment, skipping UI integration")
    except Exception as e:
        print("Error setting up UI integration: {}".format(e))


def _register_dockable_panels():
    """Register all dockable panels with Nuke."""
    try:
        import nuke
        from nukescripts import panels

        # Register Multishot Manager as a dockable panel
        # This adds it to the Pane menu automatically
        panels.registerWidgetAsPanel(
            'multishot.ui._create_multishot_manager_panel',  # Factory function path
            MULTISHOT_MANAGER_PANEL_NAME,                     # Display name
            MULTISHOT_MANAGER_PANEL_ID,                       # Unique ID
            False                                             # Don't create immediately
        )

        # Also add to Pane menu for consistency
        pane_menu = nuke.menu('Pane')
        pane_menu.addCommand(MULTISHOT_MANAGER_PANEL_NAME, _add_multishot_manager_to_pane)

        print("Multishot: Registered dockable panels")

    except Exception as e:
        print("Multishot: Could not register dockable panels: {}".format(e))
        import traceback
        traceback.print_exc()


def _add_multishot_manager_to_pane():
    """Add Multishot Manager panel to the current pane."""
    try:
        from nukescripts import panels

        # Create panel and add to current pane
        panel = panels.registerWidgetAsPanel(
            'multishot.ui._create_multishot_manager_panel',
            MULTISHOT_MANAGER_PANEL_NAME,
            MULTISHOT_MANAGER_PANEL_ID,
            True  # Create instance
        )
        return panel.addToPane()

    except Exception as e:
        print("Error adding Multishot Manager to pane: {}".format(e))
        import traceback
        traceback.print_exc()
        return None

def show_browser():
    """Show the main multishot browser."""
    global _browser_instance
    try:
        # Lazy import UI components
        from .browser import MultishotBrowser
        from .qt_utils import create_nuke_panel

        # Restore MultishotRead instances from existing nodes
        from ..nodes.read_node import restore_multishot_instances
        variable_manager = get_shared_variable_manager()
        restore_multishot_instances(variable_manager)

        # Reuse existing instance if available, otherwise create new one
        if _browser_instance is None:
            # Create browser with shared variable manager
            _browser_instance = MultishotBrowser(variable_manager=variable_manager)

        panel = create_nuke_panel(_browser_instance, 'Multishot Browser')
        panel.show()
    except Exception as e:
        print("Error showing browser: {}".format(e))
        import traceback
        traceback.print_exc()

def show_node_manager():
    """Show the node manager interface."""
    global _node_manager_instance
    try:
        # Lazy import UI components
        from .node_manager import NodeManagerDialog

        # Get shared variable manager
        variable_manager = get_shared_variable_manager()

        # Always create new instance to refresh data
        _node_manager_instance = NodeManagerDialog(variable_manager=variable_manager)

        # Use exec_() to keep dialog open (modal)
        _node_manager_instance.exec_()

    except Exception as e:
        print("Error showing node manager: {}".format(e))
        import traceback
        traceback.print_exc()

def show_multishot_manager(as_panel=True):
    """
    Show the multishot manager interface.

    Args:
        as_panel: If True (default), show as a dockable panel in Nuke.
                  If False, show as a standalone floating window.
    """
    global _multishot_manager_instance

    try:
        import nuke

        print("Opening Multishot Manager...")

        # Restore MultishotRead instances from existing nodes
        from ..nodes.read_node import restore_multishot_instances
        variable_manager = get_shared_variable_manager()
        restore_multishot_instances(variable_manager)
        print("Got variable manager: {}".format(variable_manager))

        if as_panel and nuke.GUI:
            # Try to show as dockable panel
            _show_as_dockable_panel()
        else:
            # Show as standalone floating window
            _show_as_floating_window(variable_manager)

    except ImportError:
        # Not in Nuke - show as standalone
        variable_manager = get_shared_variable_manager()
        _show_as_floating_window(variable_manager)
    except Exception as e:
        print("Error showing multishot manager: {}".format(e))
        import traceback
        traceback.print_exc()


def _show_as_dockable_panel():
    """Show Multishot Manager as a dockable panel."""
    try:
        import nuke
        from nukescripts import panels
        from .qt_utils import find_existing_panel, get_qt_modules

        QtCore, QtWidgets, QtGui, Signal, Slot = get_qt_modules()

        # Check if panel already exists
        existing = find_existing_panel(MULTISHOT_MANAGER_PANEL_ID)
        if existing:
            # Panel exists - find its parent tab widget and activate it
            parent = existing.parentWidget()
            while parent:
                if isinstance(parent, QtWidgets.QTabWidget):
                    # Find and activate the tab containing our widget
                    for i in range(parent.count()):
                        if parent.widget(i) == existing or _is_ancestor(parent.widget(i), existing):
                            parent.setCurrentIndex(i)
                            break
                    break
                # Check if it's a dock widget
                if isinstance(parent, QtWidgets.QDockWidget):
                    parent.raise_()
                    parent.activateWindow()
                    break
                parent = parent.parentWidget()

            # Refresh the existing instance
            if hasattr(existing, '_load_shots'):
                existing._load_shots()
                existing._refresh_table(update_current_shot=False)

            print("Multishot Manager: Activated existing panel")
            return

        # Create new panel and add to default pane
        pane = nuke.getPaneFor('Properties.1')
        panel = panels.registerWidgetAsPanel(
            'multishot.ui._create_multishot_manager_panel',
            MULTISHOT_MANAGER_PANEL_NAME,
            MULTISHOT_MANAGER_PANEL_ID,
            True  # Create instance
        )

        if pane:
            panel.addToPane(pane)
            print("Multishot Manager: Added to Properties pane")
        else:
            panel.show()
            print("Multishot Manager: Showing as floating panel")

    except Exception as e:
        print("Error showing dockable panel, falling back to floating window: {}".format(e))
        import traceback
        traceback.print_exc()
        # Fallback to floating window
        variable_manager = get_shared_variable_manager()
        _show_as_floating_window(variable_manager)


def _is_ancestor(widget, potential_child):
    """Check if potential_child is a descendant of widget."""
    parent = potential_child.parentWidget()
    while parent:
        if parent == widget:
            return True
        parent = parent.parentWidget()
    return False


def _show_as_floating_window(variable_manager):
    """Show Multishot Manager as a standalone floating window."""
    global _multishot_manager_instance

    from .multishot_manager import MultishotManagerDialog

    # Create or reuse instance
    if _multishot_manager_instance is None:
        print("Creating new Multishot Manager instance (floating)...")
        _multishot_manager_instance = MultishotManagerDialog(variable_manager=variable_manager)
        print("Instance created successfully")
    else:
        print("Reusing existing Multishot Manager instance...")
        # Refresh existing instance
        _multishot_manager_instance._load_shots()
        _multishot_manager_instance._refresh_table(update_current_shot=False)
        print("Instance refreshed")

    # Show as regular Qt widget
    print("Showing as floating window...")
    _multishot_manager_instance.show()
    _multishot_manager_instance.raise_()
    _multishot_manager_instance.activateWindow()
    print("Widget shown successfully")

def show_about():
    """Show about dialog."""
    try:
        # Lazy import Qt utilities
        from .qt_utils import get_qt_modules, get_nuke_main_window
        QtCore, QtWidgets, QtGui, Signal, Slot = get_qt_modules()

        dialog = QtWidgets.QMessageBox(get_nuke_main_window())
        dialog.setWindowTitle("About Multishot")
        dialog.setText("Nuke Multishot Workflow System v1.0.0")
        dialog.setInformativeText(
            "A comprehensive multishot workflow system for Nuke.\n\n"
            "Features:\n"
            "• Variable-driven asset management\n"
            "• Context-aware file operations\n"
            "• Custom Read/Write/Switch nodes\n"
            "• Render farm compatibility\n\n"
            "Compatible with Nuke 14.x, 15.x, 16.x"
        )
        dialog.setIcon(QtWidgets.QMessageBox.Information)
        dialog.exec_()
    except Exception as e:
        print("Error showing about dialog: {}".format(e))

def show_variables_dialog():
    """Show variables dialog."""
    try:
        # Lazy import UI components
        from .variables_dialog import VariablesDialog
        dialog = VariablesDialog()
        dialog.exec_()
    except Exception as e:
        print("Error showing variables dialog: {}".format(e))
        import traceback
        traceback.print_exc()

def show_documentation():
    """Show documentation - stub for now."""
    try:
        # Lazy import Qt utilities
        from .qt_utils import get_qt_modules, get_nuke_main_window
        QtCore, QtWidgets, QtGui, Signal, Slot = get_qt_modules()

        dialog = QtWidgets.QMessageBox(get_nuke_main_window())
        dialog.setWindowTitle("Documentation")
        dialog.setText("Documentation")
        dialog.setInformativeText("Please refer to the README.md file for documentation.")
        dialog.setIcon(QtWidgets.QMessageBox.Information)
        dialog.exec_()
    except Exception as e:
        print("Error showing documentation: {}".format(e))

def show_quick_switcher():
    """Show quick switcher - stub for now."""
    try:
        # Lazy import Qt utilities
        from .qt_utils import get_qt_modules, get_nuke_main_window
        QtCore, QtWidgets, QtGui, Signal, Slot = get_qt_modules()

        dialog = QtWidgets.QMessageBox(get_nuke_main_window())
        dialog.setWindowTitle("Quick Switcher")
        dialog.setText("Quick Switcher")
        dialog.setInformativeText("This feature will be implemented in Task 4.")
        dialog.setIcon(QtWidgets.QMessageBox.Information)
        dialog.exec_()
    except Exception as e:
        print("Error showing quick switcher: {}".format(e))

__all__ = [
    # UI classes (lazy imported)
    'MultishotBrowser',
    'NodeManager',
    'NodeManagerDialog',
    'MultishotManagerDialog',
    # Functions
    'setup_ui_integration',
    'show_browser',
    'show_node_manager',
    'show_multishot_manager',
    'show_about',
    'show_variables_dialog',
    'show_documentation',
    'show_quick_switcher',
    'get_shared_variable_manager'
]

# Provide backward compatibility by creating lazy properties
def __getattr__(name):
    """
    Lazy import for UI components to avoid Qt/display errors in batch mode.
    This allows code like 'from multishot.ui import MultishotBrowser' to still work,
    but only imports the UI component when it's actually accessed.
    """
    if name == 'MultishotBrowser':
        from .browser import MultishotBrowser
        return MultishotBrowser
    elif name == 'NodeManager':
        from .node_manager import NodeManager
        return NodeManager
    elif name == 'NodeManagerDialog':
        from .node_manager import NodeManagerDialog
        return NodeManagerDialog
    elif name == 'MultishotManagerDialog':
        from .multishot_manager import MultishotManagerDialog
        return MultishotManagerDialog
    elif name == 'get_qt_modules':
        from .qt_utils import get_qt_modules
        return get_qt_modules
    elif name == 'create_nuke_panel':
        from .qt_utils import create_nuke_panel
        return create_nuke_panel
    raise AttributeError("module '{}' has no attribute '{}'".format(__name__, name))
