"""
Farm Script Management for Multishot Workflow System.

Handles creation, versioning, and cleanup of farm scripts.
"""

import os
import re
from typing import Optional, List

from ..utils.logging import get_logger


class FarmScriptManager:
    """Manages farm script creation and versioning."""
    
    MAX_VERSIONS = 5  # Keep last 5 versions
    
    def __init__(self):
        self.logger = get_logger(__name__)
        
    def get_farm_script_path(self, shot_data: dict, original_script_path: str) -> str:
        """
        Build farm script path with versioning.
        
        Args:
            shot_data: Shot context (project, ep, seq, shot)
            original_script_path: Path to original Nuke script
            
        Returns:
            Path to farm script with version number
            
        Example:
            Original: V:/SWA/all/scene/Ep02/sq0010/SH0010/comp/version/Ep02_sq0010_SH0010_comp_v004.nk
            Farm:     V:/SWA/all/scene/Ep02/sq0010/SH0010/comp/farm/Ep02_sq0010_SH0010_comp_v004_farm.001.nk
        """
        try:
            # Get PROJ_ROOT
            proj_root = shot_data.get('PROJ_ROOT', 'V:/')
            if proj_root.endswith('/') or proj_root.endswith('\\'):
                proj_root = proj_root[:-1]
            
            # Build farm directory path
            farm_dir = os.path.join(
                proj_root,
                shot_data['project'],
                'all',
                'scene',
                shot_data['ep'],
                shot_data['seq'],
                shot_data['shot'],
                'comp',
                'farm'
            )
            
            # Get original filename without extension
            original_filename = os.path.basename(original_script_path)
            base_name, ext = os.path.splitext(original_filename)
            
            # Build farm script base name
            farm_base = f"{base_name}_farm"
            
            # Get next version number
            version_num = self._get_next_version(farm_dir, farm_base, ext)
            
            # Build full path
            farm_filename = f"{farm_base}.{version_num:03d}{ext}"
            farm_path = os.path.join(farm_dir, farm_filename)
            
            self.logger.info(f"Farm script path: {farm_path}")
            return farm_path
            
        except Exception as e:
            self.logger.error(f"Error building farm script path: {e}")
            raise
            
    def _get_next_version(self, farm_dir: str, base_name: str, ext: str) -> int:
        """
        Get next version number and cleanup old versions.
        
        Args:
            farm_dir: Farm directory path
            base_name: Base filename (e.g., "Ep02_sq0010_SH0010_comp_v004_farm")
            ext: File extension (e.g., ".nk")
            
        Returns:
            Next version number (1-based)
        """
        try:
            # Create farm directory if it doesn't exist
            if not os.path.exists(farm_dir):
                os.makedirs(farm_dir)
                self.logger.info(f"Created farm directory: {farm_dir}")
                return 1
            
            # Find existing versions
            pattern = re.compile(rf"^{re.escape(base_name)}\.(\d{{3}}){re.escape(ext)}$")
            versions = []
            
            for filename in os.listdir(farm_dir):
                match = pattern.match(filename)
                if match:
                    version_num = int(match.group(1))
                    versions.append((version_num, filename))
            
            if not versions:
                return 1
            
            # Sort by version number
            versions.sort(key=lambda x: x[0])
            
            # Get next version
            next_version = versions[-1][0] + 1
            
            # Cleanup old versions (keep last MAX_VERSIONS - 1, since we're adding a new one)
            if len(versions) >= self.MAX_VERSIONS:
                # Delete oldest versions
                to_delete = versions[:len(versions) - self.MAX_VERSIONS + 1]
                for version_num, filename in to_delete:
                    file_path = os.path.join(farm_dir, filename)
                    try:
                        os.remove(file_path)
                        self.logger.info(f"Deleted old farm script: {filename}")
                    except Exception as e:
                        self.logger.warning(f"Could not delete {filename}: {e}")
            
            return next_version
            
        except Exception as e:
            self.logger.error(f"Error getting next version: {e}")
            return 1
            
    def get_farm_directory(self, shot_data: dict) -> str:
        """
        Get farm directory path for a shot.
        
        Args:
            shot_data: Shot context (project, ep, seq, shot)
            
        Returns:
            Farm directory path
        """
        proj_root = shot_data.get('PROJ_ROOT', 'V:/')
        if proj_root.endswith('/') or proj_root.endswith('\\'):
            proj_root = proj_root[:-1]
        
        farm_dir = os.path.join(
            proj_root,
            shot_data['project'],
            'all',
            'scene',
            shot_data['ep'],
            shot_data['seq'],
            shot_data['shot'],
            'comp',
            'farm'
        )
        
        return farm_dir

    def bake_expressions_to_static(self):
        """
        Bake all expressions in the script to static values.

        This includes:
        - Read node file paths and frame ranges
        - Write node file paths
        - Any other expressions that need to be evaluated
        """
        try:
            import nuke

            self.logger.info("Baking expressions to static values...")

            # Bake Read nodes
            read_count = 0
            for node in nuke.allNodes('Read'):
                try:
                    # Bake file path
                    if node.knob('file'):
                        file_path = node['file'].evaluate()
                        node['file'].setValue(file_path)

                    # Bake frame range
                    if node.knob('first'):
                        first_frame = int(node['first'].value())
                        node['first'].setValue(first_frame)

                    if node.knob('last'):
                        last_frame = int(node['last'].value())
                        node['last'].setValue(last_frame)

                    read_count += 1
                    self.logger.debug(f"Baked Read node: {node.name()}")

                except Exception as e:
                    self.logger.warning(f"Could not bake Read node {node.name()}: {e}")

            # Bake Write nodes
            write_count = 0
            for node in nuke.allNodes('Write'):
                try:
                    # Bake file path
                    if node.knob('file'):
                        file_path = node['file'].evaluate()
                        node['file'].setValue(file_path)

                    write_count += 1
                    self.logger.debug(f"Baked Write node: {node.name()}")

                except Exception as e:
                    self.logger.warning(f"Could not bake Write node {node.name()}: {e}")

            self.logger.info(f"Baked {read_count} Read nodes and {write_count} Write nodes")

        except Exception as e:
            self.logger.error(f"Error baking expressions: {e}")
            raise

    def create_farm_script(self, shot_data: dict, original_script_path: str) -> str:
        """
        Create a farm script with baked expressions.

        Args:
            shot_data: Shot context (project, ep, seq, shot)
            original_script_path: Path to original Nuke script

        Returns:
            Path to created farm script
        """
        try:
            import nuke

            # Get farm script path
            farm_script_path = self.get_farm_script_path(shot_data, original_script_path)

            # Bake all expressions
            self.bake_expressions_to_static()

            # Save farm script
            self.logger.info(f"Saving farm script: {farm_script_path}")
            nuke.scriptSaveAs(farm_script_path, overwrite=1)

            # Reload original script (so user's work is unchanged)
            self.logger.info(f"Reloading original script: {original_script_path}")
            nuke.scriptOpen(original_script_path)

            self.logger.info(f"Farm script created successfully: {farm_script_path}")
            return farm_script_path

        except Exception as e:
            self.logger.error(f"Error creating farm script: {e}")
            raise

