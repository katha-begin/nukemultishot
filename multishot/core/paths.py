"""
Path resolution system for the Multishot Workflow System.

Resolves template-based paths using variables with support for hierarchical
variable substitution and path validation.
"""

import os
import re
from typing import Dict, Any, Optional, List
from ..utils.logging import get_logger
from ..utils.config import ConfigManager

class PathResolver:
    """
    Resolves template-based paths using variables.

    Supports variable substitution in path templates like:
    {PROJ_ROOT}{project}/scene/{ep}/{seq}/{shot}/{department}/version/
    """

    def __init__(self):
        self.logger = get_logger(__name__)
        self.config_manager = ConfigManager()

        # Compile regex for variable detection
        self._variable_pattern = re.compile(r'\{([^}]+)\}')

        self.logger.info("PathResolver initialized")

    def resolve_path(self, template: str, variables: Dict[str, Any]) -> str:
        """
        Resolve a path template using provided variables.

        Args:
            template: Path template with {variable} placeholders
            variables: Dictionary of variable values

        Returns:
            Resolved path string
        """
        if not template:
            return ""

        resolved = template

        # Find all variables in template
        matches = self._variable_pattern.findall(template)

        missing_vars = []

        for var_name in matches:
            var_value = variables.get(var_name)

            if var_value is not None:
                # Replace the variable placeholder
                placeholder = f"{{{var_name}}}"
                resolved = resolved.replace(placeholder, str(var_value))
                self.logger.debug(f"Resolved {placeholder} -> {var_value}")
            else:
                missing_vars.append(var_name)

        # Only warn if there are missing variables and it's not a common optional variable
        if missing_vars:
            optional_vars = {'version', 'element', 'frame', 'ext', 'variance'}
            critical_missing = [var for var in missing_vars if var not in optional_vars]

            if critical_missing:
                self.logger.warning(f"Critical variables missing in template '{template}': {critical_missing}")
            elif len(missing_vars) > 0:
                self.logger.debug(f"Optional variables missing in template '{template}': {missing_vars}")

        # Normalize path separators for current platform
        resolved = os.path.normpath(resolved)

        self.logger.debug(f"Resolved path: {template} -> {resolved}")
        return resolved

    def get_nuke_file_path(self, variables: Dict[str, Any]) -> str:
        """
        Get resolved path for Nuke files (always comp department).

        Args:
            variables: Context variables

        Returns:
            Resolved Nuke file directory path
        """
        template = self.config_manager.get_path_template("nuke_files")
        if not template:
            # Fallback template - nuke files always go to comp
            template = "{PROJ_ROOT}{project}/all/scene/{ep}/{seq}/{shot}/comp/version/"

        return self.resolve_path(template, variables)

    def get_comp_render_path(self, variables: Dict[str, Any], versioned: bool = False) -> str:
        """
        Get resolved path for comp render files.

        Args:
            variables: Context variables
            versioned: Whether to include version subdirectory

        Returns:
            Resolved comp render directory path
        """
        template_key = "comp_renders_versioned" if versioned else "comp_renders"
        template = self.config_manager.get_path_template(template_key)
        if not template:
            # Fallback template
            if versioned:
                template = "{IMG_ROOT}{project}/all/scene/{ep}/{seq}/{shot}/comp/version/{version}/"
            else:
                template = "{IMG_ROOT}{project}/all/scene/{ep}/{seq}/{shot}/comp/version/"

        return self.resolve_path(template, variables)

    def get_department_render_path(self, variables: Dict[str, Any], department: str, versioned: bool = False) -> str:
        """
        Get resolved path for department render files.

        Args:
            variables: Context variables
            department: Department name (lighting, anim, etc.)
            versioned: Whether to include version subdirectory

        Returns:
            Resolved department render directory path
        """
        # Add department to variables for template resolution
        dept_variables = variables.copy()
        dept_variables['department'] = department

        template_key = "department_renders_versioned" if versioned else "department_renders"
        template = self.config_manager.get_path_template(template_key)
        if not template:
            # Fallback template
            if versioned:
                template = "{IMG_ROOT}{project}/all/scene/{ep}/{seq}/{shot}/{department}/publish/{version}/"
            else:
                template = "{IMG_ROOT}{project}/all/scene/{ep}/{seq}/{shot}/{department}/publish/"

        return self.resolve_path(template, dept_variables)

    def get_render_path(self, variables: Dict[str, Any]) -> str:
        """
        Get resolved path for render files.

        Args:
            variables: Context variables

        Returns:
            Resolved render directory path
        """
        template = self.config_manager.get_path_template("renders")
        if not template:
            # Fallback template
            template = "{IMG_ROOT}{project}/scene/{ep}/{seq}/{shot}/{department}/publish/{version}/"

        return self.resolve_path(template, variables)

    def get_geometry_path(self, variables: Dict[str, Any], department: str, versioned: bool = False) -> str:
        """
        Get resolved path for geometry files.

        Args:
            variables: Context variables
            department: Department name (anim, layout, etc.)
            versioned: Whether to include version subdirectory

        Returns:
            Resolved geometry directory path
        """
        # Add department to variables for template resolution
        geo_variables = variables.copy()
        geo_variables['department'] = department

        template_key = "geometry_versioned" if versioned else "geometry"
        template = self.config_manager.get_path_template(template_key)
        if not template:
            # Fallback template
            if versioned:
                template = "{PROJ_ROOT}{project}/all/scene/{ep}/{seq}/{shot}/{department}/publish/{version}/"
            else:
                template = "{PROJ_ROOT}{project}/all/scene/{ep}/{seq}/{shot}/{department}/publish/"

        return self.resolve_path(template, geo_variables)

    def get_camera_path(self, variables: Dict[str, Any], department: str, versioned: bool = False) -> str:
        """
        Get resolved path for camera files.

        Args:
            variables: Context variables
            department: Department name (layout, anim, etc.)
            versioned: Whether to include version subdirectory

        Returns:
            Resolved camera directory path
        """
        # Add department to variables for template resolution
        cam_variables = variables.copy()
        cam_variables['department'] = department

        template_key = "camera_versioned" if versioned else "camera"
        template = self.config_manager.get_path_template(template_key)
        if not template:
            # Fallback template
            if versioned:
                template = "{PROJ_ROOT}{project}/all/scene/{ep}/{seq}/{shot}/{department}/publish/{version}/"
            else:
                template = "{PROJ_ROOT}{project}/all/scene/{ep}/{seq}/{shot}/{department}/publish/"

        return self.resolve_path(template, cam_variables)

    def get_full_file_path(self, path_type: str, filename: str, variables: Dict[str, Any]) -> str:
        """
        Get full file path including filename.

        Args:
            path_type: Type of path (nuke_files, renders, geometry, camera)
            filename: Filename to append
            variables: Context variables

        Returns:
            Full file path
        """
        # Get directory path based on type
        if path_type == "nuke_files":
            dir_path = self.get_nuke_file_path(variables)
        elif path_type == "renders":
            dir_path = self.get_render_path(variables)
        elif path_type == "geometry":
            dir_path = self.get_geometry_path(variables)
        elif path_type == "camera":
            dir_path = self.get_camera_path(variables)
        else:
            self.logger.error(f"Unknown path type: {path_type}")
            return ""

        # Combine directory and filename
        full_path = os.path.join(dir_path, filename)
        return os.path.normpath(full_path)

    def find_variables_in_template(self, template: str) -> List[str]:
        """
        Find all variable names in a template.

        Args:
            template: Path template

        Returns:
            List of variable names found
        """
        if not template:
            return []

        matches = self._variable_pattern.findall(template)
        return list(set(matches))  # Remove duplicates

    def validate_template(self, template: str, variables: Dict[str, Any]) -> List[str]:
        """
        Validate a path template against available variables.

        Args:
            template: Path template to validate
            variables: Available variables

        Returns:
            List of validation issues (empty if valid)
        """
        issues = []

        if not template:
            issues.append("Template is empty")
            return issues

        # Find required variables
        required_vars = self.find_variables_in_template(template)

        # Check if all required variables are available
        for var_name in required_vars:
            if var_name not in variables:
                issues.append(f"Missing variable: {var_name}")
            elif not variables[var_name]:
                issues.append(f"Empty variable: {var_name}")

        return issues

    def path_exists(self, template: str, variables: Dict[str, Any]) -> bool:
        """
        Check if resolved path exists on filesystem.

        Args:
            template: Path template
            variables: Variables for resolution

        Returns:
            True if path exists
        """
        try:
            resolved_path = self.resolve_path(template, variables)
            exists = os.path.exists(resolved_path)
            self.logger.debug(f"Path exists check: {resolved_path} -> {exists}")
            return exists
        except Exception as e:
            self.logger.error(f"Error checking path existence: {e}")
            return False

    def create_directory(self, template: str, variables: Dict[str, Any]) -> bool:
        """
        Create directory from resolved template.

        Args:
            template: Path template
            variables: Variables for resolution

        Returns:
            True if directory was created or already exists
        """
        try:
            resolved_path = self.resolve_path(template, variables)

            if os.path.exists(resolved_path):
                self.logger.debug(f"Directory already exists: {resolved_path}")
                return True

            os.makedirs(resolved_path, exist_ok=True)
            self.logger.info(f"Created directory: {resolved_path}")
            return True

        except Exception as e:
            self.logger.error(f"Error creating directory: {e}")
            return False

    def get_relative_path(self, full_path: str, base_template: str, variables: Dict[str, Any]) -> str:
        """
        Get relative path from a base template.

        Args:
            full_path: Full path to make relative
            base_template: Base path template
            variables: Variables for base resolution

        Returns:
            Relative path
        """
        try:
            base_path = self.resolve_path(base_template, variables)
            rel_path = os.path.relpath(full_path, base_path)
            self.logger.debug(f"Relative path: {full_path} -> {rel_path} (base: {base_path})")
            return rel_path
        except Exception as e:
            self.logger.error(f"Error getting relative path: {e}")
            return full_path

    def substitute_variables_in_string(self, text: str, variables: Dict[str, Any]) -> str:
        """
        Substitute variables in any string (not just paths).

        Args:
            text: Text with {variable} placeholders
            variables: Variable values

        Returns:
            Text with variables substituted
        """
        if not text:
            return ""

        result = text
        matches = self._variable_pattern.findall(text)

        for var_name in matches:
            var_value = variables.get(var_name)
            if var_value is not None:
                placeholder = f"{{{var_name}}}"
                result = result.replace(placeholder, str(var_value))

        return result

    def get_path_info(self, template: str, variables: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get detailed information about a resolved path.

        Args:
            template: Path template
            variables: Variables for resolution

        Returns:
            Dictionary with path information
        """
        resolved = self.resolve_path(template, variables)

        info = {
            'template': template,
            'resolved': resolved,
            'exists': os.path.exists(resolved),
            'is_absolute': os.path.isabs(resolved),
            'variables_used': self.find_variables_in_template(template),
            'validation_issues': self.validate_template(template, variables)
        }

        if os.path.exists(resolved):
            info.update({
                'is_file': os.path.isfile(resolved),
                'is_directory': os.path.isdir(resolved),
                'size': os.path.getsize(resolved) if os.path.isfile(resolved) else None
            })

        return info

    def get_common_paths(self, variables: Dict[str, Any]) -> Dict[str, str]:
        """
        Get all common resolved paths for current context.

        Args:
            variables: Context variables

        Returns:
            Dictionary of path_type -> resolved_path
        """
        paths = {}

        try:
            paths['nuke_files'] = self.get_nuke_file_path(variables)
            paths['renders'] = self.get_render_path(variables)
            paths['geometry'] = self.get_geometry_path(variables)
            paths['camera'] = self.get_camera_path(variables)
        except Exception as e:
            self.logger.error(f"Error getting common paths: {e}")

        return paths

    def normalize_path_separators(self, path: str) -> str:
        """
        Normalize path separators for current platform.

        Args:
            path: Path to normalize

        Returns:
            Normalized path
        """
        if not path:
            return ""

        return os.path.normpath(path)

    def is_network_path(self, path: str) -> bool:
        """
        Check if path is a network path.

        Args:
            path: Path to check

        Returns:
            True if network path
        """
        if not path:
            return False

        # Windows UNC paths
        if path.startswith('\\\\') or path.startswith('//'):
            return True

        # Mapped network drives (Windows)
        if len(path) >= 2 and path[1] == ':' and path[0].upper() in 'VWXYZ':
            return True

        return False
