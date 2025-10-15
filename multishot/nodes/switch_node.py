"""
Custom Switch node for the Multishot Workflow System.

Provides variable-based switching for shot/sequence/custom variable switching.
"""

import os
import re
from typing import Dict, List, Optional, Any

from ..utils.logging import get_logger
from ..core.variables import VariableManager
from ..core.scanner import DirectoryScanner

class MultishotSwitch:
    """
    Custom Switch node with variable-based switching.

    Features:
    - Variable-based input selection
    - Shot/sequence/custom variable switching
    - Dynamic input management
    - Expression-based switching logic
    """

    def __init__(self):
        self.logger = get_logger(__name__)
        self.variable_manager = VariableManager()
        self.scanner = DirectoryScanner()

        # Node state
        self.node = None
        self.knobs = {}

        self.logger.info("MultishotSwitch initialized")

    def create_node(self) -> 'nuke.Node':
        """
        Create the custom Switch node in Nuke.

        Returns:
            Created Nuke node
        """
        try:
            import nuke

            # Create base Switch node
            self.node = nuke.createNode('Switch', inpanel=False)
            self.node.setName('MultishotSwitch')

            # Add custom knobs
            self._add_custom_knobs()

            # Setup callbacks
            self._setup_callbacks()

            # Initialize with current context
            self._initialize_from_context()

            self.logger.info("MultishotSwitch node created successfully")
            return self.node

        except ImportError:
            self.logger.error("Cannot create MultishotSwitch node - Nuke not available")
            raise
        except Exception as e:
            self.logger.error(f"Error creating MultishotSwitch node: {e}")
            raise

    def _add_custom_knobs(self):
        """Add custom knobs to the node."""
        try:
            import nuke

            # Separator
            sep = nuke.Text_Knob('multishot_sep', 'Multishot Settings')
            self.node.addKnob(sep)

            # Switch mode
            switch_mode = nuke.Enumeration_Knob('switch_mode', 'Switch Mode',
                                              ['manual', 'shot_based', 'sequence_based', 'variable_based'])
            switch_mode.setValue('shot_based')
            switch_mode.setTooltip('Mode for automatic switching')
            self.node.addKnob(switch_mode)
            self.knobs['switch_mode'] = switch_mode

            # Variable name (for variable_based mode)
            variable_name = nuke.String_Knob('variable_name', 'Variable Name')
            variable_name.setValue('shot')
            variable_name.setTooltip('Variable name to use for switching (e.g., "shot", "seq", "project")')
            self.node.addKnob(variable_name)
            self.knobs['variable_name'] = variable_name

            # Input mapping
            input_mapping = nuke.Multiline_Eval_String_Knob('input_mapping', 'Input Mapping')
            input_mapping.setValue('SH0010:0\nSH0020:1\nSH0030:2')
            input_mapping.setTooltip('Mapping of variable values to input indices (value:input)')
            self.node.addKnob(input_mapping)
            self.knobs['input_mapping'] = input_mapping

            # Default input
            default_input = nuke.Int_Knob('default_input', 'Default Input')
            default_input.setValue(0)
            default_input.setTooltip('Default input when no mapping matches')
            self.node.addKnob(default_input)
            self.knobs['default_input'] = default_input

            # Auto-update
            auto_update = nuke.Boolean_Knob('auto_update', 'Auto Update')
            auto_update.setValue(True)
            auto_update.setTooltip('Automatically update switch when variables change')
            self.node.addKnob(auto_update)
            self.knobs['auto_update'] = auto_update

            # Status display
            status = nuke.Text_Knob('status', 'Status', 'Ready')
            self.node.addKnob(status)
            self.knobs['status'] = status

            # Update button
            update = nuke.PyScript_Knob('update', 'Update')
            update.setCommand('nuke.thisNode().knob("update").execute()')
            self.node.addKnob(update)
            self.knobs['update'] = update

            # Generate mapping button
            generate_mapping = nuke.PyScript_Knob('generate_mapping', 'Generate Mapping')
            generate_mapping.setCommand('nuke.thisNode().knob("generate_mapping").execute()')
            self.node.addKnob(generate_mapping)
            self.knobs['generate_mapping'] = generate_mapping

        except Exception as e:
            self.logger.error(f"Error adding custom knobs: {e}")
            raise

    def _setup_callbacks(self):
        """Setup knob change callbacks."""
        try:
            import nuke

            # Set knob changed callback
            callback_code = '''
import multishot.nodes.switch_node as switch_node_module
node = nuke.thisNode()
if hasattr(switch_node_module, '_node_instances'):
    instance = switch_node_module._node_instances.get(node.name())
    if instance:
        instance.knob_changed(nuke.thisKnob())
'''
            self.node.setKnobChanged(callback_code)

            # Store instance reference globally
            import sys
            current_module = sys.modules[__name__]
            if not hasattr(current_module, '_node_instances'):
                current_module._node_instances = {}
            current_module._node_instances[self.node.name()] = self

        except Exception as e:
            self.logger.error(f"Error setting up callbacks: {e}")

    def _initialize_from_context(self):
        """Initialize node with current context variables."""
        try:
            # Get current variables
            variables = self.variable_manager.get_all_variables()

            if variables:
                # Update switch based on current mode
                self._update_switch()

                self.logger.debug("MultishotSwitch initialized from context")

        except Exception as e:
            self.logger.error(f"Error initializing from context: {e}")

    def knob_changed(self, knob):
        """Handle knob change events."""
        try:
            if not knob:
                return

            knob_name = knob.name()

            if knob_name in ['switch_mode', 'variable_name', 'input_mapping', 'default_input']:
                if self.knobs.get('auto_update', {}).value():
                    self._update_switch()

            elif knob_name == 'update':
                self._update_switch()

            elif knob_name == 'generate_mapping':
                self._generate_mapping()

        except Exception as e:
            self.logger.error(f"Error in knob_changed: {e}")

    def _update_switch(self):
        """Update switch input based on current mode and variables."""
        try:
            switch_mode = self.knobs.get('switch_mode', {}).value() or 'shot_based'

            if switch_mode == 'manual':
                # Manual mode - don't change switch input
                self._update_status_display("Manual mode - switch not changed")
                return

            # Get current variables
            variables = self.variable_manager.get_all_variables()

            # Determine variable to use for switching
            if switch_mode == 'shot_based':
                variable_name = 'shot'
            elif switch_mode == 'sequence_based':
                variable_name = 'seq'
            elif switch_mode == 'variable_based':
                variable_name = self.knobs.get('variable_name', {}).value() or 'shot'
            else:
                variable_name = 'shot'

            # Get variable value
            variable_value = variables.get(variable_name, '')

            if not variable_value:
                self._update_status_display(f"No value for variable '{variable_name}'")
                return

            # Parse input mapping
            mapping = self._parse_input_mapping()

            # Find matching input
            input_index = mapping.get(variable_value)

            if input_index is not None:
                # Set switch input
                self.node['which'].setValue(input_index)
                self._update_status_display(f"Switched to input {input_index} for {variable_name}={variable_value}")
                self.logger.info(f"MultishotSwitch: {variable_name}={variable_value} -> input {input_index}")
            else:
                # Use default input
                default_input = self.knobs.get('default_input', {}).value() or 0
                self.node['which'].setValue(default_input)
                self._update_status_display(f"No mapping for {variable_name}={variable_value}, using default input {default_input}")

        except Exception as e:
            self.logger.error(f"Error updating switch: {e}")
            self._update_status_display(f"Error: {e}")

    def _parse_input_mapping(self) -> Dict[str, int]:
        """Parse the input mapping string into a dictionary."""
        try:
            mapping = {}
            mapping_text = self.knobs.get('input_mapping', {}).value() or ''

            for line in mapping_text.split('\n'):
                line = line.strip()
                if not line or ':' not in line:
                    continue

                try:
                    value, input_str = line.split(':', 1)
                    value = value.strip()
                    input_index = int(input_str.strip())
                    mapping[value] = input_index
                except (ValueError, IndexError) as e:
                    self.logger.warning(f"Invalid mapping line: {line} - {e}")
                    continue

            return mapping

        except Exception as e:
            self.logger.error(f"Error parsing input mapping: {e}")
            return {}

    def _generate_mapping(self):
        """Generate input mapping based on current switch mode."""
        try:
            switch_mode = self.knobs.get('switch_mode', {}).value() or 'shot_based'
            variables = self.variable_manager.get_all_variables()

            # Determine what values to generate mapping for
            if switch_mode == 'shot_based':
                values = self._get_available_shots()
            elif switch_mode == 'sequence_based':
                values = self._get_available_sequences()
            elif switch_mode == 'variable_based':
                variable_name = self.knobs.get('variable_name', {}).value() or 'shot'
                if variable_name == 'shot':
                    values = self._get_available_shots()
                elif variable_name == 'seq':
                    values = self._get_available_sequences()
                else:
                    # For other variables, can't auto-generate
                    self._update_status_display(f"Cannot auto-generate mapping for variable '{variable_name}'")
                    return
            else:
                self._update_status_display("Cannot generate mapping for manual mode")
                return

            if not values:
                self._update_status_display("No values found to generate mapping")
                return

            # Generate mapping string
            mapping_lines = []
            for i, value in enumerate(values):
                mapping_lines.append(f"{value}:{i}")

            mapping_text = '\n'.join(mapping_lines)

            # Update input mapping knob
            mapping_knob = self.knobs.get('input_mapping')
            if mapping_knob:
                mapping_knob.setValue(mapping_text)
                self._update_status_display(f"Generated mapping for {len(values)} values")
                self.logger.info(f"Generated mapping: {mapping_text}")

        except Exception as e:
            self.logger.error(f"Error generating mapping: {e}")
            self._update_status_display(f"Error generating mapping: {e}")

    def _get_available_shots(self) -> List[str]:
        """Get available shots for current project/episode/sequence."""
        try:
            variables = self.variable_manager.get_all_variables()

            if not all(k in variables for k in ['project', 'ep', 'seq']):
                return []

            shots = self.scanner.scan_shots(
                variables.get('PROJ_ROOT', ''),
                variables['project'],
                variables['ep'],
                variables['seq']
            )

            return shots

        except Exception as e:
            self.logger.error(f"Error getting available shots: {e}")
            return []

    def _get_available_sequences(self) -> List[str]:
        """Get available sequences for current project/episode."""
        try:
            variables = self.variable_manager.get_all_variables()

            if not all(k in variables for k in ['project', 'ep']):
                return []

            sequences = self.scanner.scan_sequences(
                variables.get('PROJ_ROOT', ''),
                variables['project'],
                variables['ep']
            )

            return sequences

        except Exception as e:
            self.logger.error(f"Error getting available sequences: {e}")
            return []

    def _update_status_display(self, message: str):
        """Update the status display."""
        try:
            status_knob = self.knobs.get('status')
            if status_knob:
                status_knob.setValue(message)

        except Exception as e:
            self.logger.error(f"Error updating status display: {e}")


# Global node instances storage
_node_instances = {}


def create_multishot_switch():
    """
    Create a new MultishotSwitch node.

    This function is called from Nuke's menu system.
    """
    try:
        multishot_switch = MultishotSwitch()
        node = multishot_switch.create_node()
        return node

    except Exception as e:
        import nuke
        nuke.message(f"Error creating MultishotSwitch node: {e}")
        return None
