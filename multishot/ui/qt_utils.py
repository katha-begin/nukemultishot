"""
Qt compatibility utilities for the Multishot Workflow System.

Handles PySide2/PySide6 compatibility and Nuke panel integration.
"""

import sys
from typing import Optional, Tuple, Any
from ..utils.logging import get_logger

logger = get_logger(__name__)

# Qt modules - will be set during import
QtCore = None
QtWidgets = None
QtGui = None
Signal = None
Slot = None

def get_qt_modules() -> Tuple[Any, Any, Any, Any, Any]:
    """
    Get Qt modules with automatic PySide2/PySide6 detection.
    
    Returns:
        Tuple of (QtCore, QtWidgets, QtGui, Signal, Slot)
    """
    global QtCore, QtWidgets, QtGui, Signal, Slot
    
    if QtCore is not None:
        return QtCore, QtWidgets, QtGui, Signal, Slot
    
    # Try PySide6 first (Nuke 16+)
    try:
        from PySide6 import QtCore, QtWidgets, QtGui
        from PySide6.QtCore import Signal, Slot
        logger.info("Using PySide6 for Qt interface")
        return QtCore, QtWidgets, QtGui, Signal, Slot
        
    except ImportError:
        pass
    
    # Fallback to PySide2 (Nuke 14-15)
    try:
        from PySide2 import QtCore, QtWidgets, QtGui
        from PySide2.QtCore import Signal, Slot
        logger.info("Using PySide2 for Qt interface")
        return QtCore, QtWidgets, QtGui, Signal, Slot
        
    except ImportError:
        pass
    
    # Last resort - try PyQt5
    try:
        from PyQt5 import QtCore, QtWidgets, QtGui
        from PyQt5.QtCore import pyqtSignal as Signal, pyqtSlot as Slot
        logger.warning("Using PyQt5 for Qt interface (not recommended)")
        return QtCore, QtWidgets, QtGui, Signal, Slot
        
    except ImportError:
        pass
    
    raise ImportError("No compatible Qt library found (PySide6, PySide2, or PyQt5)")

def is_nuke_available() -> bool:
    """Check if we're running inside Nuke."""
    try:
        import nuke
        return True
    except ImportError:
        return False

def get_nuke_main_window():
    """Get Nuke's main window for parenting dialogs."""
    if not is_nuke_available():
        return None
    
    try:
        import nuke
        QtCore, QtWidgets, QtGui, Signal, Slot = get_qt_modules()
        
        # Get Nuke's main window
        for widget in QtWidgets.QApplication.topLevelWidgets():
            if widget.objectName() == "NukeMainWindow":
                return widget
        
        # Fallback - return the first top-level widget
        widgets = QtWidgets.QApplication.topLevelWidgets()
        if widgets:
            return widgets[0]
            
    except Exception as e:
        logger.error(f"Error getting Nuke main window: {e}")
    
    return None

def create_nuke_panel(widget, title: str = "Multishot Panel", width: int = 400, height: int = 600):
    """
    Create a Nuke panel containing the specified widget.
    
    Args:
        widget: Qt widget to embed in the panel
        title: Panel title
        width: Panel width
        height: Panel height
    
    Returns:
        Nuke panel object or the widget itself if not in Nuke
    """
    if not is_nuke_available():
        # Not in Nuke - show as standalone dialog
        QtCore, QtWidgets, QtGui, Signal, Slot = get_qt_modules()
        
        dialog = QtWidgets.QDialog()
        dialog.setWindowTitle(title)
        dialog.resize(width, height)
        
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(widget)
        dialog.setLayout(layout)
        
        return dialog
    
    try:
        import nukescripts
        
        # Create Nuke panel
        panel = nukescripts.PythonPanel(title)
        panel.setMinimumSize(width, height)
        
        # Add widget to panel
        panel.addKnob(nukescripts.PythonPanel.PythonCustomKnob(widget, title))
        
        return panel
        
    except Exception as e:
        logger.error(f"Error creating Nuke panel: {e}")
        # Fallback to regular dialog
        QtCore, QtWidgets, QtGui, Signal, Slot = get_qt_modules()
        
        dialog = QtWidgets.QDialog(get_nuke_main_window())
        dialog.setWindowTitle(title)
        dialog.resize(width, height)
        
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(widget)
        dialog.setLayout(layout)
        
        return dialog

def create_base_widget_class():
    """Create BaseWidget class dynamically to handle Qt import issues."""
    try:
        QtCore, QtWidgets, QtGui, Signal, Slot = get_qt_modules()

        class BaseWidget(QtWidgets.QWidget):
            """Base widget class with Qt compatibility."""

            def __init__(self, parent=None):
                super().__init__(parent)
                self.logger = get_logger(self.__class__.__name__)

            def show_error(self, title: str, message: str) -> None:
                """Show an error message dialog."""
                QtCore, QtWidgets, QtGui, Signal, Slot = get_qt_modules()
                QtWidgets.QMessageBox.critical(self, title, message)

            def show_warning(self, title: str, message: str) -> None:
                """Show a warning message dialog."""
                QtCore, QtWidgets, QtGui, Signal, Slot = get_qt_modules()
                QtWidgets.QMessageBox.warning(self, title, message)

            def show_info(self, title: str, message: str) -> None:
                """Show an information message dialog."""
                QtCore, QtWidgets, QtGui, Signal, Slot = get_qt_modules()
                QtWidgets.QMessageBox.information(self, title, message)

            def ask_question(self, title: str, message: str) -> bool:
                """Show a yes/no question dialog."""
                QtCore, QtWidgets, QtGui, Signal, Slot = get_qt_modules()
                reply = QtWidgets.QMessageBox.question(
                    self, title, message,
                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                    QtWidgets.QMessageBox.No
                )
                return reply == QtWidgets.QMessageBox.Yes

        return BaseWidget

    except Exception:
        # Fallback for testing environment
        class MockBaseWidget:
            def __init__(self, parent=None):
                self.logger = get_logger(self.__class__.__name__)

            def show_error(self, title: str, message: str) -> None:
                print(f"Error: {title} - {message}")

            def show_warning(self, title: str, message: str) -> None:
                print(f"Warning: {title} - {message}")

            def show_info(self, title: str, message: str) -> None:
                print(f"Info: {title} - {message}")

            def ask_question(self, title: str, message: str) -> bool:
                print(f"Question: {title} - {message}")
                return True

        return MockBaseWidget

def create_base_dialog_class():
    """Create BaseDialog class dynamically to handle Qt import issues."""
    try:
        QtCore, QtWidgets, QtGui, Signal, Slot = get_qt_modules()

        class BaseDialog(QtWidgets.QDialog):
            """Base dialog class with Qt compatibility."""

            def __init__(self, parent=None, title: str = "Multishot Dialog"):
                # Use Nuke main window as parent if available
                if parent is None:
                    parent = get_nuke_main_window()

                super().__init__(parent)
                self.setWindowTitle(title)
                self.logger = get_logger(self.__class__.__name__)

            def center_on_parent(self) -> None:
                """Center the dialog on its parent."""
                if self.parent():
                    parent_rect = self.parent().geometry()
                    dialog_rect = self.geometry()

                    x = parent_rect.x() + (parent_rect.width() - dialog_rect.width()) // 2
                    y = parent_rect.y() + (parent_rect.height() - dialog_rect.height()) // 2

                    self.move(x, y)

        return BaseDialog

    except Exception:
        # Fallback for testing environment
        class MockBaseDialog:
            def __init__(self, parent=None, title: str = "Multishot Dialog"):
                self.logger = get_logger(self.__class__.__name__)

            def center_on_parent(self) -> None:
                pass

            def exec_(self):
                return True

            def accept(self):
                pass

        return MockBaseDialog

# Create the classes
BaseWidget = create_base_widget_class()
BaseDialog = create_base_dialog_class()

# Initialize Qt modules on import (with fallback for testing)
try:
    QtCore, QtWidgets, QtGui, Signal, Slot = get_qt_modules()
    logger.info("Qt modules initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Qt modules: {e}")
    # Create mock objects for testing environment
    class MockQt:
        def __init__(self):
            pass
        def __getattr__(self, name):
            return MockQt()
        def __call__(self, *args, **kwargs):
            return MockQt()

    QtCore = QtWidgets = QtGui = Signal = Slot = MockQt()
