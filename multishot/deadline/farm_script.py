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

    def _convert_windows_to_linux_path(self, path: str) -> str:
        """
        Convert Windows paths to Linux paths for Deadline render farm.

        Args:
            path: Windows path (e.g., V:/SWA/...)

        Returns:
            Linux path (e.g., /mnt/igloo_swa_v/SWA/...)
        """
        # Path mappings
        path_mappings = {
            'V:/': '/mnt/igloo_swa_v/',
            'V:\\': '/mnt/igloo_swa_v/',
            'W:/': '/mnt/igloo_swa_w/',
            'W:\\': '/mnt/igloo_swa_w/',
            'T:/': '/mnt/ppr_dev_t/',
            'T:\\': '/mnt/ppr_dev_t/'
        }

        converted_path = path
        for win_path, linux_path in path_mappings.items():
            if converted_path.startswith(win_path):
                converted_path = converted_path.replace(win_path, linux_path, 1)
                break

        # Replace backslashes with forward slashes
        converted_path = converted_path.replace('\\', '/')

        return converted_path

    def remove_all_callbacks(self):
        """
        Remove all multishot callbacks from the script for vanilla Deadline submission.

        This removes:
        - onScriptLoad callback
        - beforeRender callbacks on Write nodes
        - afterRender callbacks on Write nodes
        """
        try:
            import nuke

            self.logger.info("Removing all callbacks for vanilla Deadline submission...")

            # Remove onScriptLoad callback
            if nuke.root().knob('onScriptLoad'):
                original_callback = nuke.root()['onScriptLoad'].value()
                if original_callback:
                    self.logger.info(f"Removing onScriptLoad callback ({len(original_callback)} chars)")
                    nuke.root()['onScriptLoad'].setValue('')

            # Remove beforeRender and afterRender from all Write nodes
            write_nodes = nuke.allNodes('Write')
            callback_count = 0

            for node in write_nodes:
                # Remove beforeRender
                if node.knob('beforeRender'):
                    before_callback = node['beforeRender'].value()
                    if before_callback:
                        node['beforeRender'].setValue('')
                        callback_count += 1

                # Remove afterRender
                if node.knob('afterRender'):
                    after_callback = node['afterRender'].value()
                    if after_callback:
                        node['afterRender'].setValue('')
                        callback_count += 1

            self.logger.info(f"Removed callbacks from {callback_count} Write node knobs")

        except Exception as e:
            self.logger.error(f"Error removing callbacks: {e}")
            raise

    def bake_expressions_to_static(self):
        """
        Bake all expressions in the script to static values and convert to Linux paths.

        This includes:
        - Read node file paths and frame ranges
        - Write node file paths
        - Convert Windows paths (V:/, W:/, T:/) to Linux paths for render farm
        - Any other expressions that need to be evaluated
        """
        try:
            import nuke

            self.logger.info("Baking expressions to static values and converting to Linux paths...")

            # Bake Read nodes
            read_count = 0
            for node in nuke.allNodes('Read'):
                try:
                    # Bake file path and convert to Linux
                    if node.knob('file'):
                        file_path = node['file'].evaluate()
                        linux_path = self._convert_windows_to_linux_path(file_path)
                        node['file'].setValue(linux_path)
                        if file_path != linux_path:
                            self.logger.debug(f"Converted path: {file_path} -> {linux_path}")

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
                    # Bake file path and convert to Linux
                    if node.knob('file'):
                        file_path = node['file'].evaluate()
                        linux_path = self._convert_windows_to_linux_path(file_path)
                        node['file'].setValue(linux_path)
                        if file_path != linux_path:
                            self.logger.debug(f"Converted path: {file_path} -> {linux_path}")

                    # CRITICAL: Set format on Write node to prevent 640x480 default
                    # This ensures the correct resolution even if onScriptLoad callback fails
                    if node.knob('format'):
                        root_format = nuke.root()['format'].value()
                        node['format'].setValue(root_format.name())
                        self.logger.info(f"Set format on Write '{node.name()}': {root_format.name()} ({root_format.width()}x{root_format.height()})")

                    write_count += 1
                    self.logger.debug(f"Baked Write node: {node.name()}")

                except Exception as e:
                    self.logger.warning(f"Could not bake Write node {node.name()}: {e}")

            # Convert root knobs (PROJ_ROOT, IMG_ROOT) to Linux paths
            root_knobs_converted = 0
            for knob_name in ['PROJ_ROOT', 'IMG_ROOT']:
                if nuke.root().knob(knob_name):
                    try:
                        knob_value = nuke.root()[knob_name].value()
                        linux_value = self._convert_windows_to_linux_path(knob_value)
                        if knob_value != linux_value:
                            nuke.root()[knob_name].setValue(linux_value)
                            root_knobs_converted += 1
                            self.logger.debug(f"Converted root knob {knob_name}: {knob_value} -> {linux_value}")
                    except Exception as e:
                        self.logger.warning(f"Could not convert root knob {knob_name}: {e}")

            self.logger.info(f"Baked {read_count} Read nodes and {write_count} Write nodes")
            if root_knobs_converted > 0:
                self.logger.info(f"Converted {root_knobs_converted} root knobs to Linux paths")

        except Exception as e:
            self.logger.error(f"Error baking expressions: {e}")
            raise

    def create_farm_script(self, shot_data: dict, original_script_path: str, disable_callbacks: bool = False) -> str:
        """
        Create a farm script with baked expressions.

        Args:
            shot_data: Shot context (project, ep, seq, shot)
            original_script_path: Path to original Nuke script
            disable_callbacks: If True, remove all multishot callbacks for vanilla submission

        Returns:
            Path to created farm script
        """
        try:
            import nuke

            # Get farm script path
            farm_script_path = self.get_farm_script_path(shot_data, original_script_path)

            # Remove callbacks if requested (for vanilla testing)
            if disable_callbacks:
                self.logger.info("VANILLA MODE: Disabling all callbacks")
                self.remove_all_callbacks()

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

    def detect_write_node_dependencies(self, write_nodes: List) -> List:
        """
        Detect dependencies between Write nodes based on node graph.

        Args:
            write_nodes: List of Write node objects

        Returns:
            List of Write nodes sorted by dependency order (upstream first)
        """
        try:
            import nuke

            self.logger.info("Detecting Write node dependencies...")

            # Build dependency graph
            dependencies = {}  # {write_node: [dependent_write_nodes]}

            for write_node in write_nodes:
                dependencies[write_node] = []

                # Check if this Write node's output is used by other Write nodes
                for other_write in write_nodes:
                    if write_node == other_write:
                        continue

                    # Check if other_write depends on write_node
                    if self._is_dependent(other_write, write_node):
                        dependencies[write_node].append(other_write)

            # Topological sort to get render order
            sorted_writes = self._topological_sort(write_nodes, dependencies)

            self.logger.info(f"Detected render order: {[w.name() for w in sorted_writes]}")
            return sorted_writes

        except Exception as e:
            self.logger.error(f"Error detecting dependencies: {e}")
            # Return original order if detection fails
            return write_nodes

    def _is_dependent(self, node_a, node_b) -> bool:
        """
        Check if node_a depends on node_b (i.e., node_b is upstream of node_a).

        Args:
            node_a: Downstream node
            node_b: Potential upstream node

        Returns:
            True if node_a depends on node_b
        """
        try:
            import nuke

            # Get all dependencies of node_a
            visited = set()
            to_visit = [node_a]

            while to_visit:
                current = to_visit.pop(0)

                if current in visited:
                    continue

                visited.add(current)

                # Check if we found node_b
                if current == node_b:
                    return True

                # Add all inputs to visit list
                for i in range(current.inputs()):
                    input_node = current.input(i)
                    if input_node and input_node not in visited:
                        to_visit.append(input_node)

            return False

        except Exception as e:
            self.logger.warning(f"Error checking dependency: {e}")
            return False

    def _topological_sort(self, nodes: List, dependencies: dict) -> List:
        """
        Topological sort of nodes based on dependencies.

        Args:
            nodes: List of nodes
            dependencies: Dict of {node: [dependent_nodes]}

        Returns:
            Sorted list of nodes (upstream first)
        """
        try:
            # Calculate in-degree for each node
            in_degree = {node: 0 for node in nodes}

            for node, dependents in dependencies.items():
                for dependent in dependents:
                    in_degree[dependent] += 1

            # Start with nodes that have no dependencies
            queue = [node for node in nodes if in_degree[node] == 0]
            sorted_nodes = []

            while queue:
                # Sort queue by node name for consistent ordering
                queue.sort(key=lambda n: n.name())

                node = queue.pop(0)
                sorted_nodes.append(node)

                # Reduce in-degree for dependent nodes
                for dependent in dependencies.get(node, []):
                    in_degree[dependent] -= 1
                    if in_degree[dependent] == 0:
                        queue.append(dependent)

            # If not all nodes are sorted, there's a cycle - return original order
            if len(sorted_nodes) != len(nodes):
                self.logger.warning("Circular dependency detected, using original order")
                return nodes

            return sorted_nodes

        except Exception as e:
            self.logger.error(f"Error in topological sort: {e}")
            return nodes

