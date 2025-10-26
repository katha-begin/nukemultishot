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

# Import core modules
from . import core
from . import nodes
from . import ui
from . import utils

# Import main functionality
from .core.variables import VariableManager
from .core.scanner import DirectoryScanner
from .core.paths import PathResolver
from .core.context import ContextDetector

# Import UI components
from .ui.browser import MultishotBrowser
from .ui.node_manager import NodeManager
from .ui.multishot_manager import MultishotManagerDialog

# Import utilities
from .utils.config import ConfigManager
from .utils.logging import get_logger
from .utils.version import VersionManager
from .utils.approval import ApprovalManager

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
    'VariableManager',
    'DirectoryScanner',
    'PathResolver',
    'ContextDetector',
    'MultishotBrowser',
    'NodeManager',
    'MultishotManagerDialog',
    'ConfigManager',
    'VersionManager',
    'ApprovalManager',
    'get_variable_manager',
    'get_config_manager',
    'get_logger',
    'initialize',
    'cleanup'
]
