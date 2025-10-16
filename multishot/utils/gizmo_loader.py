"""
Gizmo and Toolset Loader for Multishot Workflow System.

Automatically discovers and registers gizmos and toolsets from:
- Tier 1 (Repository): /gizmo and /toolset directories
- Tier 2 (Project): {root}/{project}/all/library/gizmo and toolset

Features:
- Auto-registration to Nuke menu
- Hierarchical loading (Tier 1 + Tier 2)
- Support for .gizmo and .nk files
- Organized menu structure
"""

import os
import nuke
from typing import List, Dict, Optional
from ..utils.logger import get_logger


class GizmoLoader:
    """
    Manages loading and registration of gizmos and toolsets.
    
    Supports two-tier loading:
    - Tier 1: Repository-level gizmos/toolsets
    - Tier 2: Project-level gizmos/toolsets
    """
    
    def __init__(self, variable_manager=None):
        """
        Initialize GizmoLoader.
        
        Args:
            variable_manager: Optional VariableManager instance for project paths
        """
        self.logger = get_logger(__name__)
        self.variable_manager = variable_manager
        self.loaded_gizmos = []
        self.loaded_toolsets = []
        
        # Get repository root (where init.py is located)
        self.repo_root = self._get_repo_root()
        
    def _get_repo_root(self) -> str:
        """Get the repository root directory."""
        try:
            # Get the directory where this file is located
            current_file = os.path.abspath(__file__)
            # Go up: gizmo_loader.py -> utils -> multishot -> repo_root
            repo_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
            return repo_root
        except Exception as e:
            self.logger.error(f"Error getting repo root: {e}")
            return ""
    
    def get_tier1_paths(self) -> Dict[str, str]:
        """
        Get Tier 1 (repository-level) paths.
        
        Returns:
            Dictionary with 'gizmo' and 'toolset' paths
        """
        return {
            'gizmo': os.path.join(self.repo_root, 'gizmo'),
            'toolset': os.path.join(self.repo_root, 'toolset')
        }
    
    def get_tier2_paths(self) -> Dict[str, str]:
        """
        Get Tier 2 (project-level) paths.
        
        Returns:
            Dictionary with 'gizmo' and 'toolset' paths, or empty if no project context
        """
        if not self.variable_manager:
            return {}
        
        try:
            variables = self.variable_manager.get_all_variables()
            proj_root = variables.get('PROJ_ROOT', '')
            project = variables.get('project', '')
            
            if not proj_root or not project:
                return {}
            
            base_path = os.path.join(proj_root, project, 'all', 'library')
            
            return {
                'gizmo': os.path.join(base_path, 'gizmo'),
                'toolset': os.path.join(base_path, 'toolset')
            }
        except Exception as e:
            self.logger.error(f"Error getting tier 2 paths: {e}")
            return {}
    
    def discover_gizmos(self, directory: str) -> List[Dict[str, str]]:
        """
        Discover all .gizmo files in a directory.
        
        Args:
            directory: Path to search for gizmos
            
        Returns:
            List of dictionaries with 'name', 'path', and 'category' keys
        """
        gizmos = []
        
        if not os.path.exists(directory):
            self.logger.debug(f"Gizmo directory does not exist: {directory}")
            return gizmos
        
        try:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.endswith('.gizmo'):
                        filepath = os.path.join(root, file)
                        name = os.path.splitext(file)[0]
                        
                        # Get category from subdirectory
                        rel_path = os.path.relpath(root, directory)
                        category = rel_path if rel_path != '.' else 'Uncategorized'
                        
                        gizmos.append({
                            'name': name,
                            'path': filepath,
                            'category': category
                        })
                        
            self.logger.info(f"Discovered {len(gizmos)} gizmos in {directory}")
            return gizmos
            
        except Exception as e:
            self.logger.error(f"Error discovering gizmos in {directory}: {e}")
            return []
    
    def discover_toolsets(self, directory: str) -> List[Dict[str, str]]:
        """
        Discover all .nk toolset files in a directory.
        
        Args:
            directory: Path to search for toolsets
            
        Returns:
            List of dictionaries with 'name', 'path', and 'category' keys
        """
        toolsets = []
        
        if not os.path.exists(directory):
            self.logger.debug(f"Toolset directory does not exist: {directory}")
            return toolsets
        
        try:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.endswith('.nk'):
                        filepath = os.path.join(root, file)
                        name = os.path.splitext(file)[0]
                        
                        # Get category from subdirectory
                        rel_path = os.path.relpath(root, directory)
                        category = rel_path if rel_path != '.' else 'Uncategorized'
                        
                        toolsets.append({
                            'name': name,
                            'path': filepath,
                            'category': category
                        })
                        
            self.logger.info(f"Discovered {len(toolsets)} toolsets in {directory}")
            return toolsets
            
        except Exception as e:
            self.logger.error(f"Error discovering toolsets in {directory}: {e}")
            return []
    
    def register_gizmo(self, gizmo_info: Dict[str, str], menu_path: str):
        """
        Register a single gizmo to Nuke menu.
        
        Args:
            gizmo_info: Dictionary with 'name', 'path', 'category'
            menu_path: Base menu path (e.g., 'Multishot/Gizmos')
        """
        try:
            name = gizmo_info['name']
            path = gizmo_info['path']
            category = gizmo_info['category']
            
            # Build full menu path
            if category and category != 'Uncategorized':
                full_menu_path = f"{menu_path}/{category}/{name}"
            else:
                full_menu_path = f"{menu_path}/{name}"
            
            # Create menu command
            command = f"nuke.createNode('{path}')"
            
            # Add to Nuke menu
            nuke.menu('Nodes').addCommand(full_menu_path, command)
            
            self.loaded_gizmos.append(gizmo_info)
            self.logger.debug(f"Registered gizmo: {full_menu_path}")
            
        except Exception as e:
            self.logger.error(f"Error registering gizmo {gizmo_info.get('name', 'unknown')}: {e}")
    
    def register_toolset(self, toolset_info: Dict[str, str], menu_path: str):
        """
        Register a single toolset to Nuke menu.
        
        Args:
            toolset_info: Dictionary with 'name', 'path', 'category'
            menu_path: Base menu path (e.g., 'Multishot/Toolsets')
        """
        try:
            name = toolset_info['name']
            path = toolset_info['path']
            category = toolset_info['category']
            
            # Build full menu path
            if category and category != 'Uncategorized':
                full_menu_path = f"{menu_path}/{category}/{name}"
            else:
                full_menu_path = f"{menu_path}/{name}"
            
            # Create menu command to load toolset
            command = f"nuke.nodePaste('{path}')"
            
            # Add to Nuke menu
            nuke.menu('Nodes').addCommand(full_menu_path, command)
            
            self.loaded_toolsets.append(toolset_info)
            self.logger.debug(f"Registered toolset: {full_menu_path}")
            
        except Exception as e:
            self.logger.error(f"Error registering toolset {toolset_info.get('name', 'unknown')}: {e}")
    
    def load_all(self):
        """
        Load and register all gizmos and toolsets from both tiers.
        
        Loading order:
        1. Tier 1 (Repository) gizmos
        2. Tier 2 (Project) gizmos
        3. Tier 1 (Repository) toolsets
        4. Tier 2 (Project) toolsets
        """
        self.logger.info("Loading gizmos and toolsets...")
        
        # Get paths
        tier1_paths = self.get_tier1_paths()
        tier2_paths = self.get_tier2_paths()
        
        # Load Tier 1 Gizmos
        if tier1_paths.get('gizmo'):
            gizmos = self.discover_gizmos(tier1_paths['gizmo'])
            for gizmo in gizmos:
                self.register_gizmo(gizmo, 'Multishot/Gizmos/Repository')
        
        # Load Tier 2 Gizmos
        if tier2_paths.get('gizmo'):
            gizmos = self.discover_gizmos(tier2_paths['gizmo'])
            for gizmo in gizmos:
                self.register_gizmo(gizmo, 'Multishot/Gizmos/Project')
        
        # Load Tier 1 Toolsets
        if tier1_paths.get('toolset'):
            toolsets = self.discover_toolsets(tier1_paths['toolset'])
            for toolset in toolsets:
                self.register_toolset(toolset, 'Multishot/Toolsets/Repository')
        
        # Load Tier 2 Toolsets
        if tier2_paths.get('toolset'):
            toolsets = self.discover_toolsets(tier2_paths['toolset'])
            for toolset in toolsets:
                self.register_toolset(toolset, 'Multishot/Toolsets/Project')
        
        self.logger.info(f"Loaded {len(self.loaded_gizmos)} gizmos and {len(self.loaded_toolsets)} toolsets")
    
    def get_loaded_summary(self) -> str:
        """Get a summary of loaded gizmos and toolsets."""
        return (
            f"Gizmos: {len(self.loaded_gizmos)}\n"
            f"Toolsets: {len(self.loaded_toolsets)}"
        )


def load_gizmos_and_toolsets(variable_manager=None):
    """
    Convenience function to load all gizmos and toolsets.
    
    Args:
        variable_manager: Optional VariableManager instance
    """
    loader = GizmoLoader(variable_manager)
    loader.load_all()
    return loader

