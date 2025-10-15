"""
Core functionality for the Multishot Workflow System.

This module contains the core components that handle variable management,
directory scanning, path resolution, and context detection.
"""

from .variables import VariableManager
from .scanner import DirectoryScanner
from .paths import PathResolver
from .context import ContextDetector

__all__ = [
    'VariableManager',
    'DirectoryScanner',
    'PathResolver', 
    'ContextDetector'
]
