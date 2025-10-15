"""
Context detection system for the Multishot Workflow System.

Detects shot context from filenames and directory paths using pattern matching.
"""

import os
import re
from typing import Dict, Optional, List, Tuple
from ..utils.logging import get_logger
from ..utils.config import ConfigManager

class ContextDetector:
    """
    Detects shot context from filenames and paths.

    Supports the naming convention:
    {ep}_{seq}_{shot}_{department}_{variance}_{version}.nk
    Example: Ep01_sq0110_SH0520_comp_v001.nk
    """

    def __init__(self):
        self.logger = get_logger(__name__)
        self.config_manager = ConfigManager()

        # Compile regex patterns for performance
        self._filename_pattern = self._compile_filename_pattern()
        self._path_patterns = self._compile_path_patterns()

        self.logger.info("ContextDetector initialized")

    def _compile_filename_pattern(self) -> re.Pattern:
        """
        Compile regex pattern for filename parsing.

        Pattern: {ep}_{seq}_{shot}_{department}_{variance}_{version}.nk
        Example: Ep01_sq0110_SH0520_comp_v001.nk
        """
        # Pattern breakdown:
        # - ep: Ep\d+ (Ep01, Ep02, etc.)
        # - seq: sq\d+ (sq0110, sq0120, etc.)
        # - shot: SH\d+ (SH0520, SH0530, etc.)
        # - department: [a-zA-Z]+ (comp, lighting, fx, etc.)
        # - variance: [a-zA-Z0-9_]* (optional)
        # - version: v\d+(_\d+)? (v001, v001_001, etc.)

        pattern = (
            r'(?P<ep>Ep\d+)_'                    # Episode: Ep01
            r'(?P<seq>sq\d+)_'                   # Sequence: sq0110
            r'(?P<shot>SH\d+)_'                  # Shot: SH0520
            r'(?P<department>[a-zA-Z]+)_'        # Department: comp
            r'(?:(?P<variance>[a-zA-Z0-9_]+)_)?'  # Variance: optional
            r'(?P<version>v\d+(?:_\d+)?)'        # Version: v001 or v001_001
            r'\.nk$'                             # Extension: .nk
        )

        return re.compile(pattern, re.IGNORECASE)

    def _compile_path_patterns(self) -> Dict[str, re.Pattern]:
        """Compile regex patterns for path parsing."""
        patterns = {}

        # Nuke file path pattern
        # V:/SWA/all/scene/Ep01/sq0110/SH0520/comp/version/
        patterns['nuke_path'] = re.compile(
            r'.*[/\\](?P<project>\w+)[/\\].*[/\\]scene[/\\]'
            r'(?P<ep>Ep\d+)[/\\]'
            r'(?P<seq>sq\d+)[/\\]'
            r'(?P<shot>SH\d+)[/\\]'
            r'(?P<department>[a-zA-Z]+)[/\\]',
            re.IGNORECASE
        )

        # Render path pattern
        # W:/SWA/all/scene/Ep01/sq0090/SH0450/lighting/publish/v005/
        patterns['render_path'] = re.compile(
            r'.*[/\\](?P<project>\w+)[/\\].*[/\\]scene[/\\]'
            r'(?P<ep>Ep\d+)[/\\]'
            r'(?P<seq>sq\d+)[/\\]'
            r'(?P<shot>SH\d+)[/\\]'
            r'(?P<department>[a-zA-Z]+)[/\\]publish[/\\]'
            r'(?P<version>v\d+(?:_\d+)?)[/\\]',
            re.IGNORECASE
        )

        return patterns

    def detect_from_filepath(self, filepath: str) -> Optional[Dict[str, str]]:
        """
        Detect context from a complete file path.

        Args:
            filepath: Full path to file

        Returns:
            Dictionary of detected context variables or None
        """
        if not filepath:
            return None

        # First try to detect from filename
        filename = os.path.basename(filepath)
        context = self.detect_from_filename(filename)

        if context:
            # Try to enhance with path information
            path_context = self.detect_from_path(filepath)
            if path_context:
                # Merge path context, preferring filename context for conflicts
                for key, value in path_context.items():
                    if key not in context:
                        context[key] = value
        else:
            # Fallback to path-only detection
            context = self.detect_from_path(filepath)

        if context:
            self.logger.info(f"Detected context from {filepath}: {context}")
        else:
            self.logger.warning(f"Could not detect context from {filepath}")

        return context

    def detect_from_filename(self, filename: str) -> Optional[Dict[str, str]]:
        """
        Detect context from filename only.

        Args:
            filename: Filename to parse

        Returns:
            Dictionary of detected context variables or None
        """
        if not filename:
            return None

        match = self._filename_pattern.match(filename)
        if match:
            context = match.groupdict()

            # Remove None values (optional groups)
            context = {k: v for k, v in context.items() if v is not None}

            self.logger.debug(f"Detected context from filename {filename}: {context}")
            return context

        self.logger.debug(f"No context detected from filename: {filename}")
        return None

    def detect_from_path(self, path: str) -> Optional[Dict[str, str]]:
        """
        Detect context from directory path.

        Args:
            path: Directory path to parse

        Returns:
            Dictionary of detected context variables or None
        """
        if not path:
            return None

        # Normalize path separators
        normalized_path = path.replace('\\', '/')

        # Try each path pattern
        for pattern_name, pattern in self._path_patterns.items():
            match = pattern.search(normalized_path)
            if match:
                context = match.groupdict()

                # Remove None values
                context = {k: v for k, v in context.items() if v is not None}

                self.logger.debug(f"Detected context from path {path} using {pattern_name}: {context}")
                return context

        self.logger.debug(f"No context detected from path: {path}")
        return None

    def detect_project_from_path(self, path: str) -> Optional[str]:
        """
        Detect project name from path.

        Args:
            path: Path to analyze

        Returns:
            Project name or None
        """
        if not path:
            return None

        # Look for common project path patterns
        normalized_path = path.replace('\\', '/')

        # Try to find project name in path
        # Pattern: .../PROJECT/all/scene/... or .../PROJECT/scene/...
        project_pattern = re.compile(r'[/\\](\w+)[/\\](?:all[/\\])?scene[/\\]', re.IGNORECASE)
        match = project_pattern.search(normalized_path)

        if match:
            project = match.group(1)
            self.logger.debug(f"Detected project from path: {project}")
            return project

        return None

    def validate_context(self, context: Dict[str, str]) -> Tuple[bool, List[str]]:
        """
        Validate detected context.

        Args:
            context: Context dictionary to validate

        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []

        if not context:
            issues.append("Context is empty")
            return False, issues

        # Check required fields
        required_fields = ['ep', 'seq', 'shot']
        for field in required_fields:
            if field not in context or not context[field]:
                issues.append(f"Missing required field: {field}")

        # Validate field formats
        if 'ep' in context:
            if not re.match(r'^Ep\d+$', context['ep'], re.IGNORECASE):
                issues.append(f"Invalid episode format: {context['ep']} (expected: Ep##)")

        if 'seq' in context:
            if not re.match(r'^sq\d+$', context['seq'], re.IGNORECASE):
                issues.append(f"Invalid sequence format: {context['seq']} (expected: sq####)")

        if 'shot' in context:
            if not re.match(r'^SH\d+$', context['shot'], re.IGNORECASE):
                issues.append(f"Invalid shot format: {context['shot']} (expected: SH####)")

        if 'version' in context:
            if not re.match(r'^v\d+(?:_\d+)?$', context['version'], re.IGNORECASE):
                issues.append(f"Invalid version format: {context['version']} (expected: v### or v###_###)")

        is_valid = len(issues) == 0
        return is_valid, issues

    def generate_filename(self, context: Dict[str, str], extension: str = '.nk') -> str:
        """
        Generate filename from context variables.

        Args:
            context: Context variables
            extension: File extension

        Returns:
            Generated filename
        """
        # Required fields
        required = ['ep', 'seq', 'shot', 'department', 'version']

        # Check if all required fields are present
        missing = [field for field in required if field not in context or not context[field]]
        if missing:
            raise ValueError(f"Missing required context fields: {missing}")

        # Build filename parts
        parts = [
            context['ep'],
            context['seq'],
            context['shot'],
            context['department']
        ]

        # Add variance if present
        if context.get('variance'):
            parts.append(context['variance'])

        # Add version
        parts.append(context['version'])

        # Join with underscores and add extension
        filename = '_'.join(parts) + extension

        self.logger.debug(f"Generated filename: {filename}")
        return filename

    def suggest_context_from_current_script(self) -> Optional[Dict[str, str]]:
        """
        Suggest context based on current Nuke script.

        Returns:
            Suggested context or None
        """
        try:
            import nuke
            script_name = nuke.root().name()

            if script_name and script_name != "Root":
                return self.detect_from_filepath(script_name)

        except ImportError:
            self.logger.debug("Nuke not available for context suggestion")
        except Exception as e:
            self.logger.error(f"Error suggesting context from current script: {e}")

        return None

    def get_context_templates(self) -> Dict[str, Dict[str, str]]:
        """
        Get predefined context templates.

        Returns:
            Dictionary of template name -> context variables
        """
        templates = {
            'episode_01_comp': {
                'project': 'SWA',
                'ep': 'Ep01',
                'seq': 'sq0110',
                'shot': 'SH0520',
                'department': 'comp',
                'version': 'v001'
            },
            'episode_01_lighting': {
                'project': 'SWA',
                'ep': 'Ep01',
                'seq': 'sq0110',
                'shot': 'SH0520',
                'department': 'lighting',
                'version': 'v001'
            },
            'episode_02_fx': {
                'project': 'SWA',
                'ep': 'Ep02',
                'seq': 'sq0210',
                'shot': 'SH0630',
                'department': 'fx',
                'version': 'v001'
            }
        }

        return templates

    def parse_version_string(self, version_str: str) -> Optional[Tuple[int, Optional[int]]]:
        """
        Parse version string into components.

        Args:
            version_str: Version string (e.g., "v001", "v001_002")

        Returns:
            Tuple of (major_version, minor_version) or None
        """
        if not version_str:
            return None

        # Match v### or v###_###
        match = re.match(r'^v(\d+)(?:_(\d+))?$', version_str, re.IGNORECASE)
        if match:
            major = int(match.group(1))
            minor = int(match.group(2)) if match.group(2) else None
            return (major, minor)

        return None

    def increment_version(self, version_str: str) -> str:
        """
        Increment version string.

        Args:
            version_str: Current version string

        Returns:
            Incremented version string
        """
        parsed = self.parse_version_string(version_str)
        if not parsed:
            return "v001"

        major, minor = parsed

        if minor is not None:
            # Increment minor version
            return f"v{major:03d}_{minor+1:03d}"
        else:
            # Increment major version
            return f"v{major+1:03d}"

    def create_sub_version(self, version_str: str) -> str:
        """
        Create first sub-version from a major version.

        Args:
            version_str: Current version string (e.g., "v001")

        Returns:
            Sub-version string (e.g., "v001_001")
        """
        parsed = self.parse_version_string(version_str)
        if not parsed:
            return "v001_001"

        major, minor = parsed

        if minor is not None:
            # Already a sub-version, increment it
            return f"v{major:03d}_{minor+1:03d}"
        else:
            # Create first sub-version
            return f"v{major:03d}_001"
