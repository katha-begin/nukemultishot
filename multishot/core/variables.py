"""
Variable management system for the Multishot Workflow System.

Handles script-embedded variables for farm compatibility, hierarchical context
detection, and variable resolution.
"""

import json
import re
from typing import Dict, Any, Optional, List
from ..utils.logging import get_logger
from ..utils.config import ConfigManager

class VariableManager:
    """
    Manages variables for multishot workflows.

    Variables are stored in Nuke script knobs for farm compatibility,
    with fallback to project configuration for defaults.
    """

    # Knob names for storing variables in Nuke script
    VARIABLES_KNOB = 'multishot_variables'
    CONTEXT_KNOB = 'multishot_context'
    CUSTOM_KNOB = 'multishot_custom'

    def __init__(self):
        self.logger = get_logger(__name__)
        self.config_manager = ConfigManager()
        self._cached_variables = None
        self._cached_script_id = None  # Track which script the cache belongs to
        self._nuke_available = self._check_nuke_availability()

        if self._nuke_available:
            self.logger.info("VariableManager initialized with Nuke integration")
            self._ensure_knobs_exist()
            self._ensure_root_variables_in_script()
        else:
            self.logger.info("VariableManager initialized in standalone mode")

    def _check_nuke_availability(self) -> bool:
        """Check if Nuke is available."""
        try:
            import nuke
            return True
        except ImportError:
            return False

    def _clear_cache_if_script_changed(self):
        """
        Clear cache if we switched to a different Nuke script.

        This ensures that when you have multiple scripts open in the same Nuke session,
        each script maintains its own independent variables.
        """
        if not self._nuke_available:
            return

        try:
            import nuke
            current_script_id = id(nuke.root())

            # If we switched to a different script, clear the cache
            if self._cached_script_id != current_script_id:
                self._cached_variables = None
                self._cached_script_id = current_script_id
                self.logger.debug(f"Cleared cache - switched to script: {nuke.root().name()}")
        except Exception as e:
            self.logger.error(f"Error checking script change: {e}")

    def _ensure_knobs_exist(self) -> None:
        """Ensure all required knobs exist in the Nuke script."""
        if not self._nuke_available:
            return

        try:
            import nuke
            root = nuke.root()

            # Create variables knob if it doesn't exist
            if self.VARIABLES_KNOB not in root.knobs():
                knob = nuke.String_Knob(self.VARIABLES_KNOB, 'Multishot Variables')
                knob.setFlag(nuke.INVISIBLE)  # Hide from UI
                root.addKnob(knob)
                self.logger.debug(f"Created {self.VARIABLES_KNOB} knob")

            # Create context knob if it doesn't exist
            if self.CONTEXT_KNOB not in root.knobs():
                knob = nuke.String_Knob(self.CONTEXT_KNOB, 'Multishot Context')
                knob.setFlag(nuke.INVISIBLE)  # Hide from UI
                root.addKnob(knob)
                self.logger.debug(f"Created {self.CONTEXT_KNOB} knob")

            # Create custom variables knob if it doesn't exist
            if self.CUSTOM_KNOB not in root.knobs():
                knob = nuke.String_Knob(self.CUSTOM_KNOB, 'Multishot Custom')
                knob.setFlag(nuke.INVISIBLE)  # Hide from UI
                root.addKnob(knob)
                self.logger.debug(f"Created {self.CUSTOM_KNOB} knob")

        except Exception as e:
            self.logger.error(f"Error ensuring knobs exist: {e}")

    def _ensure_root_variables_in_script(self):
        """
        Ensure root variables (PROJ_ROOT, IMG_ROOT) are stored in script knobs.

        PRD 4.1 Compliance: Config is used ONLY for initial population.
        Once stored in script, config is ignored for runtime variable resolution.
        """
        try:
            # Get current custom variables from script (PRIMARY source)
            current_custom = self.get_custom_variables()

            # Check if root variables are already in script
            required_roots = ['PROJ_ROOT', 'IMG_ROOT']
            missing_roots = [key for key in required_roots if key not in current_custom]

            if missing_roots:
                self.logger.info(f"Missing root variables in script: {missing_roots}")

                # ONLY use config for initial population of missing variables
                config_roots = self.config_manager.get("roots", {})

                if config_roots:
                    # Add missing root variables from config (initial population only)
                    for key in missing_roots:
                        if key in config_roots:
                            current_custom[key] = config_roots[key]
                            self.logger.info(f"Initial population of root variable: {key} = {config_roots[key]}")

                    # Store in script knobs (becomes PRIMARY source)
                    success = self.set_custom_variables(current_custom)
                    if success:
                        self.logger.info("Root variables now script-embedded (PRD 4.1 compliant)")
                        # Create individual knobs for direct access
                        self._create_individual_root_knobs(current_custom)
                    else:
                        self.logger.error("Failed to embed root variables in script")
                else:
                    self.logger.warning("No config found for initial root variable population")
            else:
                self.logger.debug("All root variables already script-embedded")
                # Ensure individual knobs exist for existing variables
                root_vars = {k: v for k, v in current_custom.items() if k in required_roots}
                if root_vars:
                    self._create_individual_root_knobs(root_vars)

            # Also ensure context variables have individual knobs
            self._ensure_context_variable_knobs()

        except Exception as e:
            self.logger.error(f"Error ensuring root variables in script: {e}")

    def _create_individual_root_knobs(self, root_variables: Dict[str, str]):
        """Create individual knobs for root variables so they can be accessed as [value root.VARIABLE_NAME]."""
        try:
            import nuke
            root = nuke.root()

            for key, value in root_variables.items():
                # Check if knob already exists
                if key not in root.knobs():
                    # Create string knob for the variable
                    knob = nuke.String_Knob(key, key)
                    knob.setFlag(nuke.INVISIBLE)  # Hide from UI
                    root.addKnob(knob)
                    self.logger.debug(f"Created individual knob: {key}")

                # Set the value
                root[key].setValue(value)
                self.logger.debug(f"Set {key} = {value}")

        except Exception as e:
            self.logger.error(f"Error creating individual root knobs: {e}")

    def _ensure_context_variable_knobs(self):
        """Ensure context variables (project, ep, seq, shot) have individual knobs for [value root.variable] access."""
        try:
            import nuke
            root = nuke.root()

            # Get current context variables
            context_vars = self.get_context_variables()

            for key, value in context_vars.items():
                # Check if knob already exists
                if key not in root.knobs():
                    # Create string knob for the variable
                    knob = nuke.String_Knob(key, key)
                    knob.setFlag(nuke.INVISIBLE)  # Hide from UI
                    root.addKnob(knob)
                    self.logger.debug(f"Created individual context knob: {key}")

                # Set the value
                root[key].setValue(str(value))
                self.logger.debug(f"Set context knob {key} = {value}")

        except Exception as e:
            self.logger.error(f"Error ensuring context variable knobs: {e}")

    def _create_individual_context_knobs(self, context_variables: Dict[str, str]):
        """Create individual knobs for context variables so they can be accessed as [value root.VARIABLE_NAME]."""
        try:
            import nuke
            root = nuke.root()

            for key, value in context_variables.items():
                # Check if knob already exists
                if key not in root.knobs():
                    # Create string knob for the variable
                    knob = nuke.String_Knob(key, key)
                    knob.setFlag(nuke.INVISIBLE)  # Hide from UI
                    root.addKnob(knob)
                    self.logger.debug(f"Created individual context knob: {key}")

                # Set the value
                root[key].setValue(str(value))
                self.logger.debug(f"Set context knob {key} = {value}")

        except Exception as e:
            self.logger.error(f"Error creating individual context knobs: {e}")

    def _get_knob_value(self, knob_name: str) -> str:
        """Get value from a Nuke knob."""
        if not self._nuke_available:
            return ""

        try:
            import nuke
            root = nuke.root()
            if knob_name in root.knobs():
                return root[knob_name].value()
        except ImportError:
            # Nuke not available - this is expected in test environment
            self.logger.debug(f"Nuke not available for getting knob {knob_name}")
            return ""
        except Exception as e:
            self.logger.error(f"Error getting knob value {knob_name}: {e}")

        return ""

    def _set_knob_value(self, knob_name: str, value: str) -> bool:
        """Set value in a Nuke knob."""
        if not self._nuke_available:
            return False

        try:
            import nuke
            root = nuke.root()
            if knob_name in root.knobs():
                root[knob_name].setValue(value)
                return True
        except ImportError:
            # Nuke not available - this is expected in test environment
            self.logger.debug(f"Nuke not available for setting knob {knob_name}")
            return False
        except Exception as e:
            self.logger.error(f"Error setting knob value {knob_name}: {e}")

        return False

    def get_all_variables(self) -> Dict[str, Any]:
        """
        Get all variables from script knobs ONLY (PRD 4.1 - Script-Embedded Variables Primary).

        Config files are NOT used during runtime - only script-embedded variables.
        This ensures farm compatibility and self-contained scripts.

        Returns:
            Dictionary containing all script-embedded variables
        """
        # ✅ FIX: Clear cache if we switched to a different script
        self._clear_cache_if_script_changed()

        variables = {}

        # Get context variables from script knobs
        context_vars = self.get_context_variables()
        variables.update(context_vars)

        # Get custom variables from script knobs (includes root paths)
        custom_vars = self.get_custom_variables()
        variables.update(custom_vars)

        # NO CONFIG FILE ACCESS - PRD 4.1 compliance
        # All variables must be script-embedded for farm compatibility

        return variables

    def get_context_variables(self) -> Dict[str, str]:
        """
        Get context variables (project, episode, sequence, shot, etc.).

        Returns:
            Dictionary of context variables
        """
        # ✅ FIX: Clear cache if we switched to a different script
        self._clear_cache_if_script_changed()

        try:
            context_json = self._get_knob_value(self.CONTEXT_KNOB)
            if context_json:
                return json.loads(context_json)
        except (json.JSONDecodeError, Exception) as e:
            self.logger.error(f"Error loading context variables: {e}")

        return {}

    def set_context_variables(self, variables: Dict[str, str]) -> bool:
        """
        Set context variables.

        Args:
            variables: Dictionary of context variables

        Returns:
            True if successful
        """
        try:
            context_json = json.dumps(variables, indent=2)
            success = self._set_knob_value(self.CONTEXT_KNOB, context_json)

            if success:
                self.logger.info(f"Set context variables: {variables}")
                self._cached_variables = None  # Clear cache

                # Also create individual knobs for direct access
                self._create_individual_context_knobs(variables)

            return success

        except Exception as e:
            self.logger.error(f"Error setting context variables: {e}")
            return False

    def get_custom_variables(self) -> Dict[str, Any]:
        """
        Get custom user-defined variables.

        Returns:
            Dictionary of custom variables
        """
        # ✅ FIX: Clear cache if we switched to a different script
        self._clear_cache_if_script_changed()

        try:
            custom_json = self._get_knob_value(self.CUSTOM_KNOB)
            if custom_json:
                return json.loads(custom_json)
        except (json.JSONDecodeError, Exception) as e:
            self.logger.error(f"Error loading custom variables: {e}")

        return {}

    def set_custom_variables(self, variables: Dict[str, Any]) -> bool:
        """
        Set custom user-defined variables.

        Args:
            variables: Dictionary of custom variables

        Returns:
            True if successful
        """
        try:
            custom_json = json.dumps(variables, indent=2)
            success = self._set_knob_value(self.CUSTOM_KNOB, custom_json)

            if success:
                self.logger.info(f"Set custom variables: {variables}")
                self._cached_variables = None  # Clear cache

            return success

        except Exception as e:
            self.logger.error(f"Error setting custom variables: {e}")
            return False

    def get_variable(self, key: str, default: Any = None) -> Any:
        """
        Get a single variable value.

        Args:
            key: Variable name
            default: Default value if not found

        Returns:
            Variable value or default
        """
        variables = self.get_all_variables()
        return variables.get(key, default)

    def set_variable(self, key: str, value: Any) -> bool:
        """
        Set a single variable value.

        Args:
            key: Variable name
            value: Variable value

        Returns:
            True if successful
        """
        # Determine if this is a context or custom variable
        context_keys = ['project', 'ep', 'seq', 'shot', 'department', 'variance', 'version']

        if key in context_keys:
            context_vars = self.get_context_variables()
            context_vars[key] = str(value)
            return self.set_context_variables(context_vars)
        else:
            custom_vars = self.get_custom_variables()
            custom_vars[key] = value
            return self.set_custom_variables(custom_vars)

    def remove_variable(self, key: str) -> bool:
        """
        Remove a variable.

        Args:
            key: Variable name to remove

        Returns:
            True if successful
        """
        # Try context variables first
        context_vars = self.get_context_variables()
        if key in context_vars:
            del context_vars[key]
            return self.set_context_variables(context_vars)

        # Try custom variables
        custom_vars = self.get_custom_variables()
        if key in custom_vars:
            del custom_vars[key]
            return self.set_custom_variables(custom_vars)

        self.logger.warning(f"Variable '{key}' not found")
        return False

    def clear_all_variables(self) -> bool:
        """
        Clear all variables.

        Returns:
            True if successful
        """
        success1 = self.set_context_variables({})
        success2 = self.set_custom_variables({})

        if success1 and success2:
            self.logger.info("Cleared all variables")
            return True

        return False

    def refresh_context(self) -> bool:
        """
        Refresh context variables from current Nuke script filename.

        Returns:
            True if context was detected and updated
        """
        if not self._nuke_available:
            self.logger.warning("Cannot refresh context - Nuke not available")
            return False

        try:
            import nuke
            script_name = nuke.root().name()

            if not script_name or script_name == "Root":
                self.logger.info("No script loaded, cannot refresh context")
                return False

            # Use context detector to parse filename
            from .context import ContextDetector
            detector = ContextDetector()
            context = detector.detect_from_filepath(script_name)

            if context:
                self.set_context_variables(context)
                self.logger.info(f"Refreshed context from {script_name}: {context}")
                return True
            else:
                self.logger.warning(f"Could not detect context from {script_name}")
                return False

        except Exception as e:
            self.logger.error(f"Error refreshing context: {e}")
            return False

    def refresh_root_variables(self) -> bool:
        """
        Refresh root variables from config and ensure they're stored in script knobs.

        Returns:
            True if successful
        """
        try:
            if self._nuke_available:
                self._ensure_root_variables_in_script()
                self.logger.info("Root variables refreshed in script knobs")
                return True
            else:
                self.logger.warning("Cannot refresh root variables - Nuke not available")
                return False
        except Exception as e:
            self.logger.error(f"Error refreshing root variables: {e}")
            return False

    def get_variable_info(self) -> Dict[str, Any]:
        """
        Get information about all script-embedded variables (PRD 4.1 compliance).

        Only shows variables stored in script knobs, not config file.

        Returns:
            Dictionary with variable information
        """
        context_vars = self.get_context_variables()
        custom_vars = self.get_custom_variables()

        # Extract root variables from custom variables (script-embedded only)
        root_vars = {k: v for k, v in custom_vars.items() if k in ['PROJ_ROOT', 'IMG_ROOT']}

        info = {
            'context_variables': context_vars,
            'custom_variables': custom_vars,
            'root_variables': root_vars,  # From script knobs only
            'total_count': len(context_vars) + len(custom_vars),
            'script_embedded': self._nuke_available,
            'prd_compliant': True  # All variables from script knobs
        }

        return info

    def export_variables(self) -> Dict[str, Any]:
        """
        Export all variables for backup or transfer.

        Returns:
            Dictionary containing all variable data
        """
        return {
            'context': self.get_context_variables(),
            'custom': self.get_custom_variables(),
            'timestamp': self._get_timestamp(),
            'version': '1.0.0'
        }

    def import_variables(self, data: Dict[str, Any]) -> bool:
        """
        Import variables from exported data.

        Args:
            data: Exported variable data

        Returns:
            True if successful
        """
        try:
            if 'context' in data:
                self.set_context_variables(data['context'])

            if 'custom' in data:
                self.set_custom_variables(data['custom'])

            self.logger.info("Variables imported successfully")
            return True

        except Exception as e:
            self.logger.error(f"Error importing variables: {e}")
            return False

    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()

    def validate_variables(self) -> List[str]:
        """
        Validate script-embedded variables (PRD 4.1 compliance).

        Only validates variables stored in script knobs, not config file.

        Returns:
            List of validation issues (empty if all valid)
        """
        issues = []
        variables = self.get_all_variables()  # Script knobs only

        # Check for required context variables in script
        required_context = ['project', 'ep', 'seq', 'shot']
        for key in required_context:
            if not variables.get(key):
                issues.append(f"Missing required context variable in script: {key}")

        # Check root paths are script-embedded
        required_roots = ['PROJ_ROOT', 'IMG_ROOT']
        for root_name in required_roots:
            if not variables.get(root_name):
                issues.append(f"Missing required root variable in script: {root_name}")
            elif not str(variables.get(root_name)).strip():
                issues.append(f"Empty root variable in script: {root_name}")

        # PRD 4.1 compliance check
        if not self._nuke_available:
            issues.append("Script embedding not available - Nuke not detected")

        return issues
