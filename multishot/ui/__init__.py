"""
User interface components for the Multishot Workflow System.

This module contains the main browser UI, node management interface,
and custom widgets for the multishot workflow.
"""

from .browser import MultishotBrowser
from .node_manager import NodeManager, NodeManagerDialog
from .multishot_manager import MultishotManagerDialog
from .qt_utils import get_qt_modules, create_nuke_panel

# Global instances to prevent garbage collection
_browser_instance = None
_multishot_manager_instance = None
_node_manager_instance = None
_shared_variable_manager = None

def get_shared_variable_manager():
    """Get or create the shared VariableManager instance."""
    global _shared_variable_manager
    if _shared_variable_manager is None:
        from ..core.variables import VariableManager
        _shared_variable_manager = VariableManager()
    return _shared_variable_manager

def setup_ui_integration():
    """Setup UI integration with Nuke."""
    try:
        import nuke

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
        print(f"Error setting up UI integration: {e}")

def show_browser():
    """Show the main multishot browser."""
    global _browser_instance
    try:
        # ✅ Restore MultishotRead instances from existing nodes
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
        print(f"Error showing browser: {e}")
        import traceback
        traceback.print_exc()

def show_node_manager():
    """Show the node manager interface."""
    global _node_manager_instance
    try:
        # Get shared variable manager
        variable_manager = get_shared_variable_manager()

        # Always create new instance to refresh data
        _node_manager_instance = NodeManagerDialog(variable_manager=variable_manager)

        # Use exec_() to keep dialog open (modal)
        _node_manager_instance.exec_()

    except Exception as e:
        print(f"Error showing node manager: {e}")
        import traceback
        traceback.print_exc()

def show_multishot_manager():
    """Show the multishot manager interface as a dockable panel."""
    global _multishot_manager_instance

    try:
        print("Opening Multishot Manager...")

        # ✅ Restore MultishotRead instances from existing nodes
        from ..nodes.read_node import restore_multishot_instances
        variable_manager = get_shared_variable_manager()
        restore_multishot_instances(variable_manager)
        print(f"Got variable manager: {variable_manager}")

        # Create or reuse instance
        if _multishot_manager_instance is None:
            print("Creating new Multishot Manager instance...")
            _multishot_manager_instance = MultishotManagerDialog(variable_manager=variable_manager)
            print("Instance created successfully")
        else:
            print("Reusing existing Multishot Manager instance...")
            # Refresh existing instance
            _multishot_manager_instance._load_shots()  # This restores current_shot_key
            _multishot_manager_instance._refresh_table(update_current_shot=False)  # Don't overwrite!
            print("Instance refreshed")

        # Show as regular Qt widget (simple and reliable)
        print("Showing as Qt widget...")
        _multishot_manager_instance.show()
        _multishot_manager_instance.raise_()
        _multishot_manager_instance.activateWindow()
        print(f"✅ Widget shown successfully")
        print(f"   Visible: {_multishot_manager_instance.isVisible()}")
        print(f"   Size: {_multishot_manager_instance.width()}x{_multishot_manager_instance.height()}")
        print(f"   Position: ({_multishot_manager_instance.x()}, {_multishot_manager_instance.y()})")

    except Exception as e:
        print(f"❌ Error showing multishot manager: {e}")
        import traceback
        traceback.print_exc()

def show_about():
    """Show about dialog."""
    try:
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
        print(f"Error showing about dialog: {e}")

def show_variables_dialog():
    """Show variables dialog."""
    try:
        from .variables_dialog import VariablesDialog
        dialog = VariablesDialog()
        dialog.exec_()
    except Exception as e:
        print(f"Error showing variables dialog: {e}")
        import traceback
        traceback.print_exc()

def show_documentation():
    """Show documentation - stub for now."""
    try:
        from .qt_utils import get_qt_modules, get_nuke_main_window
        QtCore, QtWidgets, QtGui, Signal, Slot = get_qt_modules()

        dialog = QtWidgets.QMessageBox(get_nuke_main_window())
        dialog.setWindowTitle("Documentation")
        dialog.setText("Documentation")
        dialog.setInformativeText("Please refer to the README.md file for documentation.")
        dialog.setIcon(QtWidgets.QMessageBox.Information)
        dialog.exec_()
    except Exception as e:
        print(f"Error showing documentation: {e}")

def show_quick_switcher():
    """Show quick switcher - stub for now."""
    try:
        from .qt_utils import get_qt_modules, get_nuke_main_window
        QtCore, QtWidgets, QtGui, Signal, Slot = get_qt_modules()

        dialog = QtWidgets.QMessageBox(get_nuke_main_window())
        dialog.setWindowTitle("Quick Switcher")
        dialog.setText("Quick Switcher")
        dialog.setInformativeText("This feature will be implemented in Task 4.")
        dialog.setIcon(QtWidgets.QMessageBox.Information)
        dialog.exec_()
    except Exception as e:
        print(f"Error showing quick switcher: {e}")

__all__ = [
    'MultishotBrowser',
    'NodeManager',
    'MultishotManagerDialog',
    'setup_ui_integration',
    'show_browser',
    'show_node_manager',
    'show_multishot_manager',
    'show_about',
    'show_variables_dialog',
    'show_documentation',
    'show_quick_switcher'
]
