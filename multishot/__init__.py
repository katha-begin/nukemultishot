"""
Nuke Multishot Workflow System

A comprehensive multishot workflow system for Nuke that provides variable-driven 
asset management, context-aware file operations, and streamlined shot-based 
compositing workflows.

Author: Multishot Development Team
Version: 1.0.0
Compatible with: Nuke 14.x, 15.x, 16.x
"""

__version__ = "1.0.0"
__author__ = "Multishot Development Team"
__email__ = "support@multishot.com"

# Import core modules (safe for batch mode)
from . import core
from . import nodes
from . import utils

# Import main functionality (safe for batch mode)
from .core.variables import VariableManager
from .core.scanner import DirectoryScanner
from .core.paths import PathResolver
from .core.context import ContextDetector

# Import utilities (safe for batch mode)
from .utils.config import ConfigManager
from .utils.logging import get_logger
from .utils.version import VersionManager
from .utils.approval import ApprovalManager

# UI components are imported lazily to avoid Qt/display errors in batch mode
# They will be imported when needed by get_ui_class() functions

# Global instances
_variable_manager = None
_config_manager = None
_logger = None

def get_variable_manager():
    """Get the global variable manager instance."""
    global _variable_manager
    if _variable_manager is None:
        _variable_manager = VariableManager()
    return _variable_manager

def get_config_manager():
    """Get the global configuration manager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager

def get_logger():
    """Get the global logger instance."""
    global _logger
    if _logger is None:
        from .utils.logging import get_logger as _get_logger
        _logger = _get_logger('multishot')
    return _logger

def get_multishot_browser():
    """
    Get MultishotBrowser class (lazy import to avoid Qt errors in batch mode).

    Returns:
        MultishotBrowser class
    """
    from .ui.browser import MultishotBrowser
    return MultishotBrowser

def get_node_manager():
    """
    Get NodeManager class (lazy import to avoid Qt errors in batch mode).

    Returns:
        NodeManager class
    """
    from .ui.node_manager import NodeManager
    return NodeManager

def get_multishot_manager_dialog():
    """
    Get MultishotManagerDialog class (lazy import to avoid Qt errors in batch mode).

    Returns:
        MultishotManagerDialog class
    """
    from .ui.multishot_manager import MultishotManagerDialog
    return MultishotManagerDialog

def initialize():
    """Initialize the multishot system."""
    try:
        logger = get_logger()
        logger.info("Initializing Multishot Workflow System v%s", __version__)

        # Initialize core components
        config_manager = get_config_manager()
        variable_manager = get_variable_manager()

        # Load third-party gizmo packages (NukeSurvivalToolkit, BuddySystem, etc.)
        logger.info("Loading third-party gizmo packages...")
        from .utils.gizmo_loader import load_third_party_packages
        try:
            third_party_loader = load_third_party_packages()
            logger.info(third_party_loader.get_loaded_summary())
        except Exception as e:
            logger.warning(f"Error loading third-party packages: {e}")

        # Load regular gizmos and toolsets
        logger.info("Loading gizmos and toolsets...")
        from .utils.gizmo_loader import load_gizmos_and_toolsets
        try:
            gizmo_loader = load_gizmos_and_toolsets(variable_manager)
            logger.info(gizmo_loader.get_loaded_summary())
        except Exception as e:
            logger.warning(f"Error loading gizmos and toolsets: {e}")

        # Register custom nodes
        from .nodes import register_all_nodes
        register_all_nodes()

        # Setup UI integration
        from .ui import setup_ui_integration
        setup_ui_integration()

        logger.info("Multishot Workflow System initialized successfully")
        return True

    except Exception as e:
        print(f"Error initializing Multishot Workflow System: {e}")
        import traceback
        traceback.print_exc()
        return False

def cleanup():
    """Cleanup the multishot system."""
    try:
        logger = get_logger()
        logger.info("Cleaning up Multishot Workflow System")
        
        # Cleanup global instances
        global _variable_manager, _config_manager, _logger
        _variable_manager = None
        _config_manager = None
        _logger = None
        
        logger.info("Multishot Workflow System cleanup completed")
        
    except Exception as e:
        print(f"Error during cleanup: {e}")

# Export main classes and functions
__all__ = [
    # Core classes (safe for batch mode)
    'VariableManager',
    'DirectoryScanner',
    'PathResolver',
    'ContextDetector',
    'ConfigManager',
    'VersionManager',
    'ApprovalManager',
    # Lazy import functions for UI classes (to avoid Qt errors in batch mode)
    'get_multishot_browser',
    'get_node_manager',
    'get_multishot_manager_dialog',
    # Global instance getters
    'get_variable_manager',
    'get_config_manager',
    'get_logger',
    # Initialization functions
    'initialize',
    'cleanup'
]

# Provide backward compatibility by creating lazy properties
def __getattr__(name):
    """
    Lazy import for UI components to avoid Qt/display errors in batch mode.
    This allows code like 'from multishot import MultishotBrowser' to still work,
    but only imports the UI component when it's actually accessed.
    """
    if name == 'MultishotBrowser':
        return get_multishot_browser()
    elif name == 'NodeManager':
        return get_node_manager()
    elif name == 'MultishotManagerDialog':
        return get_multishot_manager_dialog()
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
