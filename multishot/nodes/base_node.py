"""
Base node class for custom Multishot nodes.

This module will be implemented in Task 5.
"""

from ..utils.logging import get_logger

class BaseMultishotNode:
    """Base class for all custom Multishot nodes."""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.logger.info("BaseMultishotNode initialized (stub)")
