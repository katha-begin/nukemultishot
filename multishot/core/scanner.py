"""
Directory scanner for the Multishot Workflow System.

Provides filesystem scanning capabilities to discover project structure,
populate dropdowns, and detect available assets with caching for performance.
"""

import os
import re
import time
from typing import Dict, List, Optional, Set, Any, Tuple
from collections import defaultdict

from ..utils.logging import get_logger
from ..utils.config import ConfigManager
from .paths import PathResolver
from .context import ContextDetector

class DirectoryScanner:
    """
    Scans directories for multishot project structure.

    Provides caching, pattern matching, and hierarchical discovery
    of episodes, sequences, shots, departments, and versions.
    """

    def __init__(self, cache_timeout: int = 300):
        """
        Initialize the directory scanner.

        Args:
            cache_timeout: Cache timeout in seconds (default: 5 minutes)
        """
        self.logger = get_logger(__name__)
        self.config_manager = ConfigManager()
        self.path_resolver = PathResolver()
        self.context_detector = ContextDetector()

        # Cache settings
        self.cache_timeout = cache_timeout
        self._cache = {}

        # Compile regex patterns for directory matching
        self._patterns = self._compile_patterns()

        # Auto-detect and configure project if possible
        self._auto_configure_project()

        self.logger.info(f"DirectoryScanner initialized with {cache_timeout}s cache timeout")

    def _auto_configure_project(self):
        """Auto-detect and configure project based on current context."""
        try:
            # Try to detect project from current Nuke script
            current_project = None
            project_root = None

            # Method 1: From current Nuke script path
            try:
                import nuke
                script_path = nuke.root().name()
                if script_path and script_path != 'Root':
                    context = self.context_detector.detect_from_filepath(script_path)
                    if context and 'project' in context:
                        current_project = context['project']
                        # Try to find project root
                        project_root = self._find_project_root(script_path, current_project)
            except ImportError:
                pass

            # Method 2: From working directory
            if not current_project:
                cwd = os.getcwd()
                current_project, project_root = self._detect_project_from_path(cwd)

            # Method 3: Look for project config files in common locations
            if not current_project:
                current_project, project_root = self._find_project_configs()

            # Load project config if found
            if current_project and project_root:
                self.logger.info(f"Auto-detected project: {current_project} at {project_root}")
                config = self.config_manager.load_project_config(project_root, current_project)

                # Auto-populate variables
                self._populate_variables_from_config(config, current_project, project_root)
            else:
                self.logger.info("No project auto-detected, using default configuration")

        except Exception as e:
            self.logger.warning(f"Error in auto-configuration: {e}")

    def _find_project_root(self, file_path: str, project: str) -> Optional[str]:
        """Find project root directory from a file path."""
        current_dir = os.path.dirname(os.path.abspath(file_path))

        # Search up the directory tree
        for _ in range(10):  # Max 10 levels up
            # Look for project directory
            project_dir = os.path.join(current_dir, project)
            if os.path.exists(project_dir):
                return current_dir

            # Look for project config file
            config_file = os.path.join(current_dir, f"{project}_config.json")
            if os.path.exists(config_file):
                return current_dir

            parent = os.path.dirname(current_dir)
            if parent == current_dir:  # Reached root
                break
            current_dir = parent

        return None

    def _detect_project_from_path(self, path: str) -> tuple[Optional[str], Optional[str]]:
        """Detect project from directory path structure."""
        # Look for project config files
        current_dir = os.path.abspath(path)

        for _ in range(10):  # Search up to 10 levels
            # Look for JSON config files
            if os.path.exists(current_dir):
                for item in os.listdir(current_dir):
                    if item.endswith('_config.json'):
                        project_name = item.replace('_config.json', '')
                        return project_name, current_dir

            parent = os.path.dirname(current_dir)
            if parent == current_dir:
                break
            current_dir = parent

        return None, None

    def _find_project_configs(self) -> tuple[Optional[str], Optional[str]]:
        """Find project configs in common locations."""
        common_roots = [
            "V:/", "W:/", "T:/pipeline/development/nuke/nukemultishot",
            os.getcwd(), os.path.expanduser("~")
        ]

        for root in common_roots:
            if os.path.exists(root):
                try:
                    for item in os.listdir(root):
                        if item.endswith('_config.json'):
                            project_name = item.replace('_config.json', '')
                            return project_name, root
                except (OSError, PermissionError):
                    continue

        return None, None

    def _populate_variables_from_config(self, config: Dict[str, Any], project: str, project_root: str):
        """Populate variables from loaded config."""
        try:
            from .variables import VariableManager
            vm = VariableManager()

            # Set root paths from config
            roots = config.get('roots', {})
            for key, value in roots.items():
                vm.set_variable(key, value)

            # Set project
            vm.set_variable('project', project)

            # Set other defaults from config
            defaults = config.get('defaults', {})
            for key, value in defaults.items():
                vm.set_variable(key, value)

            self.logger.info(f"Auto-populated {len(roots) + len(defaults) + 1} variables from config")

        except Exception as e:
            self.logger.warning(f"Error populating variables from config: {e}")

    def _compile_patterns(self) -> Dict[str, re.Pattern]:
        """Compile regex patterns for directory matching."""
        patterns = {}

        # Episode pattern: Ep01, Ep02, etc.
        patterns['episode'] = re.compile(r'^Ep\d+$', re.IGNORECASE)

        # Sequence pattern: sq0110, sq0120, etc.
        patterns['sequence'] = re.compile(r'^sq\d+$', re.IGNORECASE)

        # Shot pattern: SH0520, SH0530, etc.
        patterns['shot'] = re.compile(r'^SH\d+$', re.IGNORECASE)

        # Version pattern: v001, v002, v001_001, etc.
        patterns['version'] = re.compile(r'^v\d+(?:_\d+)?$', re.IGNORECASE)

        # Department pattern: ALWAYS dynamic - never use static lists
        # This pattern accepts any valid directory name as a department
        # NO STATIC DEPARTMENT LISTS - departments are discovered from filesystem
        patterns['department'] = re.compile(r'^[a-zA-Z][a-zA-Z0-9_]*$')

        self.logger.debug(f"Compiled dynamic department pattern: {patterns['department'].pattern}")

        return patterns

    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cache entry is still valid."""
        if cache_key not in self._cache:
            return False

        cache_entry = self._cache[cache_key]
        age = time.time() - cache_entry['timestamp']
        return age < self.cache_timeout

    def _get_from_cache(self, cache_key: str) -> Optional[Any]:
        """Get data from cache if valid."""
        if self._is_cache_valid(cache_key):
            self.logger.debug(f"Cache hit for: {cache_key}")
            return self._cache[cache_key]['data']
        return None

    def _set_cache(self, cache_key: str, data: Any) -> None:
        """Set data in cache."""
        self._cache[cache_key] = {
            'data': data,
            'timestamp': time.time()
        }
        self.logger.debug(f"Cached data for: {cache_key}")

    def clear_cache(self) -> None:
        """Clear all cached data."""
        self._cache.clear()
        self.logger.info("Cache cleared")

    def refresh_patterns(self) -> None:
        """Refresh regex patterns and clear cache."""
        self._patterns = self._compile_patterns()
        self.clear_cache()
        self.logger.info("Patterns refreshed and cache cleared")

    def _scan_directory_pattern(self, directory: str, pattern: re.Pattern,
                               max_depth: int = 1) -> List[str]:
        """
        Scan directory for items matching a pattern.

        Args:
            directory: Directory to scan
            pattern: Regex pattern to match
            max_depth: Maximum depth to scan (default: 1)

        Returns:
            List of matching directory names
        """
        matches = []

        if not os.path.exists(directory):
            self.logger.debug(f"Directory does not exist: {directory}")
            return matches

        try:
            for item in os.listdir(directory):
                item_path = os.path.join(directory, item)

                if os.path.isdir(item_path) and pattern.match(item):
                    matches.append(item)

        except (OSError, PermissionError) as e:
            self.logger.warning(f"Error scanning directory {directory}: {e}")

        # Sort naturally (Ep01, Ep02, Ep10, etc.)
        matches.sort(key=self._natural_sort_key)
        return matches

    def _natural_sort_key(self, text: str) -> List:
        """Generate natural sort key for alphanumeric strings."""
        def convert(text):
            return int(text) if text.isdigit() else text.lower()
        return [convert(c) for c in re.split(r'(\d+)', text)]

    def scan_projects(self, project_root: str) -> List[str]:
        """
        Scan for available projects in the project root.

        Args:
            project_root: Root directory path (e.g., "V:/")

        Returns:
            List of project names (e.g., ["SWA", "ProjectB"])
        """
        cache_key = f"projects_{project_root}"
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            return cached

        projects = []

        if not os.path.exists(project_root):
            self.logger.debug(f"Project root does not exist: {project_root}")
            self._set_cache(cache_key, projects)
            return projects

        try:
            for item in os.listdir(project_root):
                item_path = os.path.join(project_root, item)

                if os.path.isdir(item_path):
                    # Check if this looks like a project directory
                    # Look for the "all/scene" structure that indicates a valid project
                    scene_path = os.path.join(item_path, "all", "scene")
                    if os.path.exists(scene_path) and os.path.isdir(scene_path):
                        projects.append(item)
                        self.logger.debug(f"Found project: {item}")

        except (OSError, PermissionError) as e:
            self.logger.warning(f"Error scanning projects in {project_root}: {e}")

        self._set_cache(cache_key, projects)
        self.logger.info(f"Found {len(projects)} projects in {project_root}: {projects}")
        return projects

    def scan_episodes(self, project_root: str, project: str) -> List[str]:
        """
        Scan for available episodes in the project.

        Args:
            project_root: Root directory path (e.g., "V:/")
            project: Project name (e.g., "SWA")

        Returns:
            List of episode names (e.g., ["Ep01", "Ep02"])
        """
        cache_key = f"episodes_{project_root}_{project}"
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            return cached

        # Build path to scene directory (PRD structure: project_root/project/all/scene/)
        scene_path = os.path.join(project_root, project, "all", "scene")
        episodes = self._scan_directory_pattern(scene_path, self._patterns['episode'])

        self._set_cache(cache_key, episodes)
        self.logger.info(f"Found {len(episodes)} episodes in {scene_path}")
        return episodes

    def scan_sequences(self, project_root: str, project: str, episode: str) -> List[str]:
        """
        Scan for available sequences in an episode.

        Args:
            project_root: Root directory path
            project: Project name
            episode: Episode name (e.g., "Ep01")

        Returns:
            List of sequence names (e.g., ["sq0110", "sq0120"])
        """
        cache_key = f"sequences_{project_root}_{project}_{episode}"
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            return cached

        # Build path to episode directory (PRD structure: project_root/project/all/scene/episode/)
        episode_path = os.path.join(project_root, project, "all", "scene", episode)
        sequences = self._scan_directory_pattern(episode_path, self._patterns['sequence'])

        self._set_cache(cache_key, sequences)
        self.logger.info(f"Found {len(sequences)} sequences in {episode}")
        return sequences

    def scan_shots(self, project_root: str, project: str, episode: str, sequence: str) -> List[str]:
        """
        Scan for available shots in a sequence.

        Args:
            project_root: Root directory path
            project: Project name
            episode: Episode name
            sequence: Sequence name (e.g., "sq0110")

        Returns:
            List of shot names (e.g., ["SH0520", "SH0530"])
        """
        cache_key = f"shots_{project_root}_{project}_{episode}_{sequence}"
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            return cached

        # Build path to sequence directory (PRD structure: project_root/project/all/scene/episode/sequence/)
        sequence_path = os.path.join(project_root, project, "all", "scene", episode, sequence)
        shots = self._scan_directory_pattern(sequence_path, self._patterns['shot'])

        self._set_cache(cache_key, shots)
        self.logger.info(f"Found {len(shots)} shots in {episode}/{sequence}")
        return shots

    def scan_departments(self, project_root: str, project: str, episode: str,
                        sequence: str, shot: str) -> List[str]:
        """
        Scan for available departments in a shot.

        Departments are discovered dynamically from the filesystem - no static lists.
        Any valid directory name in the shot directory is considered a department.

        Args:
            project_root: Root directory path
            project: Project name
            episode: Episode name
            sequence: Sequence name
            shot: Shot name (e.g., "SH0520")

        Returns:
            List of department names discovered from filesystem (e.g., ["comp", "lighting", "fx"])
        """
        cache_key = f"departments_{project_root}_{project}_{episode}_{sequence}_{shot}"
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            return cached

        # Build path to shot directory (PRD structure: project_root/project/all/scene/...)
        shot_path = os.path.join(project_root, project, "all", "scene", episode, sequence, shot)

        # Use dynamic pattern - accepts any valid directory name as department
        departments = self._scan_directory_pattern(shot_path, self._patterns['department'])

        self._set_cache(cache_key, departments)
        self.logger.info(f"Found {len(departments)} departments in {episode}/{sequence}/{shot}: {departments}")
        return departments

    def scan_versions(self, directory: str) -> List[str]:
        """
        Scan for available versions in a directory.

        Args:
            directory: Directory to scan for versions

        Returns:
            List of version names (e.g., ["v001", "v002", "v001_001"])
        """
        cache_key = f"versions_{directory}"
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            return cached

        versions = self._scan_directory_pattern(directory, self._patterns['version'])

        self._set_cache(cache_key, versions)
        self.logger.debug(f"Found {len(versions)} versions in {directory}")
        return versions

    def scan_nuke_files(self, directory: str) -> List[Dict[str, Any]]:
        """
        Scan for Nuke files in a directory with context detection.

        Args:
            directory: Directory to scan

        Returns:
            List of dictionaries with file info and detected context
        """
        cache_key = f"nuke_files_{directory}"
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            return cached

        nuke_files = []

        if not os.path.exists(directory):
            self._set_cache(cache_key, nuke_files)
            return nuke_files

        try:
            for item in os.listdir(directory):
                if item.lower().endswith('.nk'):
                    file_path = os.path.join(directory, item)

                    # Detect context from filename
                    context = self.context_detector.detect_from_filepath(file_path)

                    file_info = {
                        'filename': item,
                        'filepath': file_path,
                        'context': context or {},
                        'size': os.path.getsize(file_path),
                        'modified': os.path.getmtime(file_path)
                    }

                    nuke_files.append(file_info)

        except (OSError, PermissionError) as e:
            self.logger.warning(f"Error scanning Nuke files in {directory}: {e}")

        # Sort by modification time (newest first)
        nuke_files.sort(key=lambda x: x['modified'], reverse=True)

        self._set_cache(cache_key, nuke_files)
        self.logger.debug(f"Found {len(nuke_files)} Nuke files in {directory}")
        return nuke_files

    def scan_assets(self, directory: str, asset_types: Optional[List[str]] = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        Scan for asset files in a directory, organized by type.

        Args:
            directory: Directory to scan
            asset_types: List of asset types to scan for (default: all configured types)

        Returns:
            Dictionary of asset_type -> list of asset info dictionaries
        """
        cache_key = f"assets_{directory}_{hash(tuple(asset_types or []))}"
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            return cached

        if asset_types is None:
            asset_types = list(self.config_manager.get("asset_types", {}).keys())

        assets = {asset_type: [] for asset_type in asset_types}

        if not os.path.exists(directory):
            self._set_cache(cache_key, assets)
            return assets

        # Get file extensions for each asset type
        asset_extensions = self.config_manager.get("asset_types", {})

        try:
            for item in os.listdir(directory):
                item_path = os.path.join(directory, item)

                if os.path.isfile(item_path):
                    file_ext = os.path.splitext(item)[1].lower()

                    # Check which asset type this file belongs to
                    for asset_type in asset_types:
                        extensions = asset_extensions.get(asset_type, [])
                        if file_ext in extensions:
                            asset_info = {
                                'filename': item,
                                'filepath': item_path,
                                'extension': file_ext,
                                'size': os.path.getsize(item_path),
                                'modified': os.path.getmtime(item_path)
                            }
                            assets[asset_type].append(asset_info)
                            break

        except (OSError, PermissionError) as e:
            self.logger.warning(f"Error scanning assets in {directory}: {e}")

        # Sort each asset type by filename
        for asset_type in assets:
            assets[asset_type].sort(key=lambda x: x['filename'])

        self._set_cache(cache_key, assets)
        total_assets = sum(len(files) for files in assets.values())
        self.logger.debug(f"Found {total_assets} assets in {directory}")
        return assets

    def _parse_version(self, version: str) -> Optional[Dict[str, int]]:
        """
        Parse a version string into components.

        Args:
            version: Version string (e.g., "v001", "v001_002")

        Returns:
            Dictionary with 'major' and optional 'minor' version numbers
        """
        # Remove 'v' prefix and split on underscore
        version_clean = version.lower().lstrip('v')
        parts = version_clean.split('_')

        try:
            major = int(parts[0])
            minor = int(parts[1]) if len(parts) > 1 else 0
            return {'major': major, 'minor': minor}
        except (ValueError, IndexError):
            return None

    def get_latest_version(self, versions: List[str]) -> Optional[str]:
        """
        Get the latest version from a list of version strings.

        Args:
            versions: List of version strings (e.g., ["v001", "v002", "v001_001"])

        Returns:
            Latest version string or None if no versions
        """
        if not versions:
            return None

        # Parse versions and find the latest
        parsed_versions = []
        for version in versions:
            parsed = self._parse_version(version)
            if parsed:
                parsed_versions.append((parsed, version))

        if not parsed_versions:
            return None

        # Sort by major version, then minor version
        parsed_versions.sort(key=lambda x: (x[0]['major'], x[0]['minor']), reverse=True)
        return parsed_versions[0][1]

    def scan_project_structure(self, project_root: str, project: str) -> Dict[str, Any]:
        """
        Scan the complete project structure and return hierarchical data.

        Args:
            project_root: Root directory path
            project: Project name

        Returns:
            Dictionary with complete project structure
        """
        cache_key = f"project_structure_{project_root}_{project}"
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            return cached

        structure = {
            'project': project,
            'project_root': project_root,
            'episodes': {}
        }

        episodes = self.scan_episodes(project_root, project)

        for episode in episodes:
            structure['episodes'][episode] = {'sequences': {}}
            sequences = self.scan_sequences(project_root, project, episode)

            for sequence in sequences:
                structure['episodes'][episode]['sequences'][sequence] = {'shots': {}}
                shots = self.scan_shots(project_root, project, episode, sequence)

                for shot in shots:
                    structure['episodes'][episode]['sequences'][sequence]['shots'][shot] = {
                        'departments': {}
                    }
                    departments = self.scan_departments(project_root, project, episode, sequence, shot)

                    for department in departments:
                        structure['episodes'][episode]['sequences'][sequence]['shots'][shot]['departments'][department] = {
                            'versions': [],
                            'latest_version': None
                        }

                        # Scan for versions in this department (PRD structure)
                        dept_path = os.path.join(project_root, project, "all", "scene", episode, sequence, shot, department, "version")
                        if os.path.exists(dept_path):
                            versions = self.scan_versions(dept_path)
                            structure['episodes'][episode]['sequences'][sequence]['shots'][shot]['departments'][department]['versions'] = versions
                            structure['episodes'][episode]['sequences'][sequence]['shots'][shot]['departments'][department]['latest_version'] = self.get_latest_version(versions)

        self._set_cache(cache_key, structure)
        self.logger.info(f"Scanned complete project structure for {project}")
        return structure

    def find_files_by_context(self, context: Dict[str, str], file_types: Optional[List[str]] = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        Find files matching the given context.

        Args:
            context: Context dictionary (project, ep, seq, shot, department, etc.)
            file_types: List of file types to search for (default: all)

        Returns:
            Dictionary of file_type -> list of matching files
        """
        results = defaultdict(list)

        # Build search paths based on context
        variables = context.copy()

        # Add root variables
        roots = self.config_manager.get("roots", {})
        variables.update(roots)

        # Get common paths for this context
        common_paths = self.path_resolver.get_common_paths(variables)

        # Search in each path type
        for path_type, path in common_paths.items():
            if os.path.exists(path):
                if path_type == 'nuke_files':
                    nuke_files = self.scan_nuke_files(path)
                    results['nuke'].extend(nuke_files)
                else:
                    assets = self.scan_assets(path, file_types)
                    for asset_type, asset_list in assets.items():
                        results[asset_type].extend(asset_list)

        return dict(results)

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_entries = len(self._cache)
        valid_entries = sum(1 for key in self._cache if self._is_cache_valid(key))

        return {
            'total_entries': total_entries,
            'valid_entries': valid_entries,
            'expired_entries': total_entries - valid_entries,
            'cache_timeout': self.cache_timeout,
            'cache_keys': list(self._cache.keys())
        }

    def scan_all_department_assets(self, project_root: str, project: str, episode: str,
                                  sequence: str, shot: str) -> Dict[str, Dict[str, List[str]]]:
        """
        Recursively scan all departments for assets (renders, geometry, camera).

        Args:
            project_root: Root directory path
            project: Project name
            episode: Episode name
            sequence: Sequence name
            shot: Shot name

        Returns:
            Dictionary with structure:
            {
                'department_name': {
                    'renders': ['v001/layer1/file.1001-1240.exr', ...],
                    'geometry': ['v001/geo.abc', ...],
                    'camera': ['v001/cam.abc', ...]
                }
            }
        """
        cache_key = f"all_assets_{project_root}_{project}_{episode}_{sequence}_{shot}"
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            return cached

        assets = {}

        # Get all departments for this shot
        departments = self.scan_departments(project_root, project, episode, sequence, shot)

        for department in departments:
            dept_assets = {
                'renders': [],
                'geometry': [],
                'camera': []
            }

            # Scan renders (IMG_ROOT)
            img_root = self._get_img_root()
            if img_root:
                render_path = os.path.join(img_root, project, "all", "scene", episode, sequence, shot, department, "publish")
                dept_assets['renders'] = self._scan_recursive_assets(render_path, ['exr', 'png', 'jpg', 'jpeg', 'tiff', 'dpx'])

            # Scan geometry (PROJ_ROOT)
            geo_path = os.path.join(project_root, project, "all", "scene", episode, sequence, shot, department, "publish")
            dept_assets['geometry'] = self._scan_recursive_assets(geo_path, ['abc', 'obj', 'fbx', 'usd', 'usda', 'usdc'])

            # Scan camera (same as geometry)
            dept_assets['camera'] = self._scan_recursive_assets(geo_path, ['abc', 'fbx', 'ma', 'mb'])

            # Only include department if it has assets
            if any(dept_assets.values()):
                assets[department] = dept_assets

        self._set_cache(cache_key, assets)
        self.logger.info(f"Found assets in {len(assets)} departments for {episode}/{sequence}/{shot}")
        return assets

    def _scan_recursive_assets(self, base_path: str, extensions: List[str]) -> List[str]:
        """
        Recursively scan for assets with specific extensions.

        Args:
            base_path: Base directory to scan
            extensions: List of file extensions to look for (without dots)

        Returns:
            List of asset paths with collapsed sequences
        """
        if not os.path.exists(base_path):
            return []

        assets = []

        try:
            # Walk through all subdirectories
            for root, dirs, files in os.walk(base_path):
                # Group files by sequence pattern
                sequences = {}
                single_files = []

                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, base_path)

                    # Check if file has matching extension
                    file_ext = os.path.splitext(file)[1][1:].lower()  # Remove dot and lowercase
                    if file_ext not in [ext.lower() for ext in extensions]:
                        continue

                    # Check if it's part of a sequence (has frame numbers)
                    sequence_match = re.search(r'(.+\.)(\d{3,5})(\.[^.]+)$', file)
                    if sequence_match:
                        prefix = sequence_match.group(1)
                        frame = int(sequence_match.group(2))
                        suffix = sequence_match.group(3)

                        sequence_key = f"{prefix}#####{suffix}"
                        if sequence_key not in sequences:
                            sequences[sequence_key] = {
                                'prefix': prefix,
                                'suffix': suffix,
                                'frames': [],
                                'rel_dir': os.path.dirname(rel_path)
                            }
                        sequences[sequence_key]['frames'].append(frame)
                    else:
                        # Single file
                        single_files.append(rel_path)

                # Process sequences
                for seq_key, seq_data in sequences.items():
                    frames = sorted(seq_data['frames'])
                    if len(frames) > 1:
                        # Collapsed sequence
                        start_frame = frames[0]
                        end_frame = frames[-1]
                        collapsed_name = f"{seq_data['prefix']}{start_frame:04d}-{end_frame:04d}{seq_data['suffix']}"
                        if seq_data['rel_dir']:
                            collapsed_path = os.path.join(seq_data['rel_dir'], collapsed_name).replace('\\', '/')
                        else:
                            collapsed_path = collapsed_name
                        assets.append(collapsed_path)
                    else:
                        # Single frame
                        frame = frames[0]
                        single_name = f"{seq_data['prefix']}{frame:04d}{seq_data['suffix']}"
                        if seq_data['rel_dir']:
                            single_path = os.path.join(seq_data['rel_dir'], single_name).replace('\\', '/')
                        else:
                            single_path = single_name
                        assets.append(single_path)

                # Add single files
                assets.extend([f.replace('\\', '/') for f in single_files])

        except Exception as e:
            self.logger.error(f"Error scanning assets in {base_path}: {e}")

        return sorted(assets)

    def _get_img_root(self) -> str:
        """Get IMG_ROOT from configuration."""
        try:
            from ..utils.config import ConfigManager
            config_manager = ConfigManager()
            roots = config_manager.get("roots", {})
            return roots.get("IMG_ROOT", "")
        except Exception as e:
            self.logger.error(f"Error getting IMG_ROOT: {e}")
            return ""

    def scan_comp_renders(self, project_root: str, project: str, episode: str,
                         sequence: str, shot: str) -> List[str]:
        """
        Scan for comp render files in comp/version/ directory.

        Args:
            project_root: Root directory path (not used for comp renders - uses IMG_ROOT)
            project: Project name
            episode: Episode name
            sequence: Sequence name
            shot: Shot name

        Returns:
            List of comp render files with collapsed sequences
        """
        cache_key = f"comp_renders_{project}_{episode}_{sequence}_{shot}"
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            return cached

        # Comp renders are in IMG_ROOT
        img_root = self._get_img_root()
        if not img_root:
            return []

        comp_path = os.path.join(img_root, project, "all", "scene", episode, sequence, shot, "comp", "version")

        # Scan for image files
        renders = self._scan_recursive_assets(comp_path, ['exr', 'png', 'jpg', 'jpeg', 'tiff', 'dpx', 'mov'])

        self._set_cache(cache_key, renders)
        self.logger.debug(f"Found {len(renders)} comp renders for {episode}/{sequence}/{shot}")
        return renders
