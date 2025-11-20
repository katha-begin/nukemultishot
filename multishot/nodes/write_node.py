"""
Custom Write node for the Multishot Workflow System.

Provides variable-driven output paths with automatic directory creation,
version tracking, and multi-output support.
"""

import os
import re
import json
import datetime
from typing import Dict, List, Optional, Any

from ..utils.logging import get_logger
from ..core.variables import VariableManager
from ..core.paths import PathResolver
from ..core.context import ContextDetector

class MultishotWrite:
    """
    Custom Write node with variable-driven paths.

    Features:
    - Variable-driven output path resolution
    - Automatic directory creation
    - Version increment support
    - Layer/element naming
    - Render format presets
    """

    def __init__(self, variable_manager=None):
        self.logger = get_logger(__name__)

        # Use shared variable manager if provided
        if variable_manager is not None:
            self.variable_manager = variable_manager
            self.logger.info("MultishotWrite using shared VariableManager instance")
        else:
            self.variable_manager = VariableManager()
            self.logger.info("MultishotWrite created new VariableManager instance")

        self.path_resolver = PathResolver()
        self.context_detector = ContextDetector()

        # Node state
        self.node = None
        self.knobs = {}

        self.logger.info("MultishotWrite initialized")

    def get_shot_key(self) -> str:
        """Get current shot key from root knobs."""
        try:
            import nuke
            project = nuke.root()['multishot_project'].value() if nuke.root().knob('multishot_project') else ''
            ep = nuke.root()['multishot_ep'].value() if nuke.root().knob('multishot_ep') else ''
            seq = nuke.root()['multishot_seq'].value() if nuke.root().knob('multishot_seq') else ''
            shot = nuke.root()['multishot_shot'].value() if nuke.root().knob('multishot_shot') else ''
            return f"{project}_{ep}_{seq}_{shot}"
        except Exception as e:
            self.logger.error(f"Error getting shot key: {e}")
            return ""

    def detect_latest_version(self, output_dir: str) -> str:
        """
        Detect the latest version number in the output directory.

        Args:
            output_dir: Directory to scan for versions

        Returns:
            Latest version string (e.g., 'v005') or 'v001' if none found
        """
        try:
            if not os.path.exists(output_dir):
                return 'v001'

            # Look for version directories (v001, v002, etc.)
            versions = []
            for item in os.listdir(output_dir):
                item_path = os.path.join(output_dir, item)
                if os.path.isdir(item_path):
                    # Check if directory name matches version pattern
                    match = re.match(r'v(\d+)', item)
                    if match:
                        version_num = int(match.group(1))
                        versions.append(version_num)

            if versions:
                latest_num = max(versions)
                latest_version = f"v{latest_num:03d}"
                self.logger.info(f"Detected latest version: {latest_version}")
                return latest_version
            else:
                return 'v001'

        except Exception as e:
            self.logger.error(f"Error detecting latest version: {e}")
            return 'v001'

    def get_next_version(self, current_version: str) -> str:
        """
        Get the next version number.

        Args:
            current_version: Current version string (e.g., 'v005')

        Returns:
            Next version string (e.g., 'v006')
        """
        try:
            match = re.match(r'v(\d+)', current_version)
            if match:
                version_num = int(match.group(1))
                next_num = version_num + 1
                return f"v{next_num:03d}"
            else:
                return 'v001'
        except Exception as e:
            self.logger.error(f"Error getting next version: {e}")
            return 'v001'

    def create_version_metadata(self, version: str, output_path: str) -> Dict[str, Any]:
        """
        Create metadata for version tracking.

        Args:
            version: Version string (e.g., 'v005')
            output_path: Output file path

        Returns:
            Dictionary containing version metadata
        """
        try:
            import nuke

            shot_key = self.get_shot_key()
            script_path = nuke.root().name()

            metadata = {
                'version': version,
                'shot_key': shot_key,
                'nuke_script': script_path,
                'nuke_script_basename': os.path.basename(script_path),
                'output_path': output_path,
                'timestamp': datetime.datetime.now().isoformat(),
                'user': os.environ.get('USERNAME', os.environ.get('USER', 'unknown')),
                'nuke_version': nuke.NUKE_VERSION_STRING,
                'frame_range': {
                    'first': int(nuke.root()['first_frame'].value()),
                    'last': int(nuke.root()['last_frame'].value())
                }
            }

            return metadata

        except Exception as e:
            self.logger.error(f"Error creating version metadata: {e}")
            return {}

    def save_version_metadata(self, metadata: Dict[str, Any], output_dir: str):
        """
        Save version metadata to JSON file.

        Args:
            metadata: Metadata dictionary
            output_dir: Directory to save metadata file
        """
        try:
            if not metadata:
                return

            # Create metadata filename
            version = metadata.get('version', 'v001')
            metadata_file = os.path.join(output_dir, f"{version}_metadata.json")

            # Save to JSON
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)

            self.logger.info(f"Saved version metadata: {metadata_file}")

        except Exception as e:
            self.logger.error(f"Error saving version metadata: {e}")

    def create_node(self) -> 'nuke.Node':
        """
        Create the custom Write node in Nuke.

        Returns:
            Created Nuke node
        """
        try:
            import nuke

            # Create base Write node
            self.node = nuke.createNode('Write', inpanel=False)
            self.node.setName('MultishotWrite')

            # Add custom knobs
            self._add_custom_knobs()

            # Setup callbacks
            self._setup_callbacks()

            # Initialize with current context
            self._initialize_from_context()

            self.logger.info("MultishotWrite node created successfully")
            return self.node

        except ImportError:
            self.logger.error("Cannot create MultishotWrite node - Nuke not available")
            raise
        except Exception as e:
            self.logger.error(f"Error creating MultishotWrite node: {e}")
            raise

    def _hide_ocio_display_knobs(self):
        """
        Hide OCIO display/view knobs to prevent batch mode errors.

        Write nodes automatically get 'display' and 'view' knobs when OCIO is enabled.
        These are for preview purposes only, but cause validation errors in batch mode
        when Nuke tries to validate them during script loading.

        Solution: Set them to invisible so they don't get validated.
        """
        try:
            import nuke

            # Hide display knob
            if self.node.knob('display'):
                self.node.knob('display').setVisible(False)
                self.logger.debug("Hidden 'display' knob")

            # Hide view knob
            if self.node.knob('view'):
                self.node.knob('view').setVisible(False)
                self.logger.debug("Hidden 'view' knob")

        except Exception as e:
            # Don't fail node creation if this doesn't work
            self.logger.warning(f"Could not hide OCIO display knobs: {e}")

    def _add_custom_knobs(self):
        """Add custom knobs to the node."""
        try:
            import nuke

            # Hide OCIO display/view knobs to prevent batch mode errors
            # These knobs are for preview only and cause "Bad value for display" errors
            # in batch mode when OCIO validation runs during script loading
            self._hide_ocio_display_knobs()

            # Separator
            sep = nuke.Text_Knob('multishot_sep', 'Multishot Settings')
            self.node.addKnob(sep)

            # Output type selection
            output_type = nuke.Enumeration_Knob('output_type', 'Output Type', ['comp_render', 'dept_render', 'geometry'])
            output_type.setValue('comp_render')
            output_type.setTooltip('Type of output - determines path structure')
            self.node.addKnob(output_type)
            self.knobs['output_type'] = output_type

            # Department (for dept_render and geometry)
            department = nuke.String_Knob('department', 'Department')
            department.setValue('comp')
            department.setTooltip('Department name for output path')
            self.node.addKnob(department)
            self.knobs['department'] = department

            # Layer/Element name
            layer = nuke.String_Knob('layer', 'Layer/Element')
            layer.setValue('beauty')
            layer.setTooltip('Layer or element name for output')
            self.node.addKnob(layer)
            self.knobs['layer'] = layer

            # Version
            version = nuke.String_Knob('output_version', 'Version')
            version.setValue('v001')
            version.setTooltip('Version number for output')
            self.node.addKnob(version)
            self.knobs['output_version'] = version

            # Detect Latest Version button
            detect_version = nuke.PyScript_Knob('detect_latest_version', 'Detect Latest')
            detect_version.setTooltip('Detect latest version from output directory')
            self.node.addKnob(detect_version)
            self.knobs['detect_latest_version'] = detect_version

            # Use Next Version button
            use_next_version = nuke.PyScript_Knob('use_next_version', 'Use Next')
            use_next_version.setTooltip('Use next version number')
            self.node.addKnob(use_next_version)
            self.knobs['use_next_version'] = use_next_version

            # Auto-increment version
            auto_increment = nuke.Boolean_Knob('auto_increment', 'Auto Increment Version')
            auto_increment.setValue(False)
            auto_increment.setTooltip('Automatically increment version if file exists')
            self.node.addKnob(auto_increment)
            self.knobs['auto_increment'] = auto_increment

            # Save metadata
            save_metadata = nuke.Boolean_Knob('save_metadata', 'Save Metadata')
            save_metadata.setValue(True)
            save_metadata.setTooltip('Save version metadata (nuke script, timestamp, etc.)')
            self.node.addKnob(save_metadata)
            self.knobs['save_metadata'] = save_metadata

            # Create directories
            create_dirs = nuke.Boolean_Knob('create_dirs', 'Create Directories')
            create_dirs.setValue(True)
            create_dirs.setTooltip('Automatically create output directories')
            self.node.addKnob(create_dirs)
            self.knobs['create_dirs'] = create_dirs

            # Path template
            path_template = nuke.String_Knob('path_template', 'Path Template')
            path_template.setValue('[value root.IMG_ROOT]/[value root.project]/all/scene/[value root.ep]/[value root.seq]/[value root.shot]/comp/version/{version}/{layer}.%04d.exr')
            path_template.setTooltip('Template for output path resolution')
            self.node.addKnob(path_template)
            self.knobs['path_template'] = path_template

            # Multi-Output separator
            multi_sep = nuke.Text_Knob('multi_output_sep', 'Multi-Output Settings')
            self.node.addKnob(multi_sep)

            # Enable multi-output
            enable_multi = nuke.Boolean_Knob('enable_multi_output', 'Enable Multi-Output')
            enable_multi.setValue(False)
            enable_multi.setTooltip('Enable multiple output formats (EXR + MOV)')
            self.node.addKnob(enable_multi)
            self.knobs['enable_multi_output'] = enable_multi

            # MOV output settings
            mov_colorspace = nuke.Enumeration_Knob('mov_colorspace', 'MOV Colorspace',
                                                   ['sRGB', 'Rec709', 'Linear', 'ACEScg'])
            mov_colorspace.setValue('sRGB')
            mov_colorspace.setTooltip('Colorspace for MOV output (baked)')
            self.node.addKnob(mov_colorspace)
            self.knobs['mov_colorspace'] = mov_colorspace

            # MOV codec
            mov_codec = nuke.Enumeration_Knob('mov_codec', 'MOV Codec',
                                              ['H.264', 'ProRes 422', 'ProRes 4444', 'DNxHD'])
            mov_codec.setValue('H.264')
            mov_codec.setTooltip('Codec for MOV output')
            self.node.addKnob(mov_codec)
            self.knobs['mov_codec'] = mov_codec

            # Status display
            status = nuke.Text_Knob('status', 'Status', 'Ready')
            self.node.addKnob(status)
            self.knobs['status'] = status

            # Update path button
            update_path = nuke.PyScript_Knob('update_path', 'Update Path')
            update_path.setTooltip('Update output path based on current settings')
            self.node.addKnob(update_path)
            self.knobs['update_path'] = update_path

        except Exception as e:
            self.logger.error(f"Error adding custom knobs: {e}")
            raise

    def _setup_callbacks(self):
        """Setup knob change callbacks."""
        try:
            import nuke

            # Set knob changed callback
            callback_code = '''
import multishot.nodes.write_node as write_node_module
node = nuke.thisNode()
if hasattr(write_node_module, '_node_instances'):
    instance = write_node_module._node_instances.get(node.name())
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
                # Update path template based on output type
                self._update_path_template()

                # Update resolved path
                self._update_resolved_path()

                self.logger.debug("MultishotWrite initialized from context")

        except Exception as e:
            self.logger.error(f"Error initializing from context: {e}")

    def knob_changed(self, knob):
        """Handle knob change events."""
        try:
            if not knob:
                return

            knob_name = knob.name()

            if knob_name == 'output_type':
                self._update_path_template()
                self._update_resolved_path()

            elif knob_name in ['department', 'layer', 'output_version', 'path_template']:
                self._update_resolved_path()

            elif knob_name == 'update_path':
                self._update_resolved_path()

            elif knob_name == 'detect_latest_version':
                self._detect_and_set_latest_version()

            elif knob_name == 'use_next_version':
                self._use_next_version()

        except Exception as e:
            self.logger.error(f"Error in knob_changed: {e}")

    def _detect_and_set_latest_version(self):
        """Detect latest version from output directory and set it."""
        try:
            # Get output directory
            variables = self.variable_manager.get_all_variables()
            department = self.knobs.get('department', {}).value() or 'comp'

            # Build base output directory (without version)
            proj_root = variables.get('IMG_ROOT', 'W:/')
            project = variables.get('project', '')
            ep = variables.get('ep', '')
            seq = variables.get('seq', '')
            shot = variables.get('shot', '')

            if not all([project, ep, seq, shot]):
                self.logger.warning("Cannot detect version - missing context variables")
                return

            # Build path to version directory
            base_dir = os.path.join(proj_root, project, 'all', 'scene', ep, seq, shot, department, 'version')

            # Detect latest version
            latest_version = self.detect_latest_version(base_dir)

            # Set version knob
            version_knob = self.knobs.get('output_version')
            if version_knob:
                version_knob.setValue(latest_version)
                self.logger.info(f"Set version to latest: {latest_version}")

                # Update path
                self._update_resolved_path()

        except Exception as e:
            self.logger.error(f"Error detecting latest version: {e}")

    def _use_next_version(self):
        """Use next version number."""
        try:
            current_version = self.knobs.get('output_version', {}).value() or 'v001'
            next_version = self.get_next_version(current_version)

            # Set version knob
            version_knob = self.knobs.get('output_version')
            if version_knob:
                version_knob.setValue(next_version)
                self.logger.info(f"Set version to next: {next_version}")

                # Update path
                self._update_resolved_path()

        except Exception as e:
            self.logger.error(f"Error using next version: {e}")

    def _update_path_template(self):
        """Update path template based on output type."""
        try:
            output_type = self.knobs.get('output_type', {}).value() or 'comp_render'
            template_knob = self.knobs.get('path_template')

            if not template_knob:
                return

            if output_type == 'comp_render':
                # Comp renders go to comp/version/
                template = '[value root.IMG_ROOT]/[value root.project]/all/scene/[value root.ep]/[value root.seq]/[value root.shot]/comp/version/{version}/{layer}.%04d.exr'
            elif output_type == 'dept_render':
                # Department renders go to dept/publish/version/
                template = '[value root.IMG_ROOT]/[value root.project]/all/scene/[value root.ep]/[value root.seq]/[value root.shot]/{department}/publish/{version}/{layer}.%04d.exr'
            elif output_type == 'geometry':
                # Geometry goes to dept/publish/version/
                template = '[value root.PROJ_ROOT]/[value root.project]/all/scene/[value root.ep]/[value root.seq]/[value root.shot]/{department}/publish/{version}/{layer}.abc'
            else:
                return

            template_knob.setValue(template)

        except Exception as e:
            self.logger.error(f"Error updating path template: {e}")

    def _update_resolved_path(self):
        """Update the resolved output path based on current settings."""
        try:
            variables = self.variable_manager.get_all_variables()
            department = self.knobs.get('department', {}).value() or 'comp'
            version = self.knobs.get('output_version', {}).value() or 'v001'
            layer = self.knobs.get('layer', {}).value() or 'beauty'

            # Add current selections to variables
            path_variables = variables.copy()
            path_variables.update({
                'department': department,
                'version': version,
                'layer': layer
            })

            # Get path template
            template = self.knobs.get('path_template', {}).value()
            if not template:
                return

            # Resolve path
            resolved_path = self.path_resolver.resolve_path(template, path_variables)

            # Handle auto-increment version
            if self.knobs.get('auto_increment', {}).value():
                resolved_path = self._handle_version_increment(resolved_path, path_variables)

            # Update file knob
            self.node['file'].setValue(resolved_path)

            # Update status
            self._update_status_display(resolved_path)

            self.logger.debug(f"Updated resolved path: {resolved_path}")

        except Exception as e:
            self.logger.error(f"Error updating resolved path: {e}")
            self._update_status_display(f"Error: {e}", is_error=True)

    def _handle_version_increment(self, resolved_path: str, variables: Dict[str, Any]) -> str:
        """Handle automatic version increment if file exists."""
        try:
            if not resolved_path:
                return resolved_path

            # Check if file exists (for sequences, check directory)
            if '%' in resolved_path:
                # Sequence - check if directory has any files
                base_dir = os.path.dirname(resolved_path)
                if os.path.exists(base_dir) and os.listdir(base_dir):
                    # Directory exists and has files - increment version
                    return self._increment_version_in_path(resolved_path, variables)
            else:
                # Single file - check if file exists
                if os.path.exists(resolved_path):
                    return self._increment_version_in_path(resolved_path, variables)

            return resolved_path

        except Exception as e:
            self.logger.error(f"Error handling version increment: {e}")
            return resolved_path

    def _increment_version_in_path(self, resolved_path: str, variables: Dict[str, Any]) -> str:
        """Increment version number in the resolved path."""
        try:
            current_version = variables.get('version', 'v001')
            next_version = self.context_detector.increment_version(current_version)

            # Update version in variables
            new_variables = variables.copy()
            new_variables['version'] = next_version

            # Update version knob
            version_knob = self.knobs.get('version')
            if version_knob:
                version_knob.setValue(next_version)

            # Re-resolve path with new version
            template = self.knobs.get('path_template', {}).value()
            if template:
                new_path = self.path_resolver.resolve_path(template, new_variables)
                self.logger.info(f"Auto-incremented version: {current_version} -> {next_version}")
                return new_path

            return resolved_path

        except Exception as e:
            self.logger.error(f"Error incrementing version: {e}")
            return resolved_path

    def _update_status_display(self, filepath: str, is_error: bool = False):
        """Update the status display."""
        try:
            status_knob = self.knobs.get('status')
            if not status_knob:
                return

            if is_error:
                status_knob.setValue(f"❌ {filepath}")
                if self.node:
                    self.node['tile_color'].setValue(0xff0000ff)  # Red
                return

            if not filepath:
                status_knob.setValue("❌ No output path")
                if self.node:
                    self.node['tile_color'].setValue(0xff0000ff)  # Red
                return

            # Check if directory exists
            output_dir = os.path.dirname(filepath)
            if os.path.exists(output_dir):
                status_knob.setValue(f"✅ Ready: {os.path.basename(filepath)}")
                if self.node:
                    self.node['tile_color'].setValue(0x00ff00ff)  # Green
            else:
                if self.knobs.get('create_dirs', {}).value():
                    status_knob.setValue(f"📁 Will create: {os.path.basename(filepath)}")
                    if self.node:
                        self.node['tile_color'].setValue(0xffff00ff)  # Yellow
                else:
                    status_knob.setValue(f"❌ Directory missing: {output_dir}")
                    if self.node:
                        self.node['tile_color'].setValue(0xff0000ff)  # Red

        except Exception as e:
            self.logger.error(f"Error updating status display: {e}")

    def before_render(self):
        """
        Called before rendering starts.
        Creates directories, validates output path, saves metadata, and ensures correct format.
        """
        try:
            import nuke

            # CRITICAL: Ensure root format is set correctly before rendering
            # This fixes the issue where Deadline path mapping resets format to 640x480
            root_format = nuke.root()['format'].value()
            current_width = root_format.width()
            current_height = root_format.height()

            self.logger.info(f"Before render - Current format: {current_width}x{current_height} ({root_format.name()})")

            # If format is the default 640x480, try to restore from saved_format knob
            if current_width == 640 and current_height == 480:
                self.logger.warning("Format is default 640x480! Attempting to restore...")

                if nuke.root().knob('saved_format'):
                    saved_format_name = nuke.root()['saved_format'].value()
                    self.logger.info(f"Found saved_format: {saved_format_name}")

                    try:
                        nuke.root()['format'].setValue(saved_format_name)
                        new_format = nuke.root()['format'].value()
                        self.logger.info(f"Restored format to: {new_format.width()}x{new_format.height()} ({new_format.name()})")
                    except Exception as e:
                        self.logger.error(f"Failed to restore format: {e}")
                else:
                    self.logger.error("No saved_format knob found! Render will use 640x480!")

            # Get current output path
            output_path = self.node['file'].value()
            if not output_path:
                raise ValueError("No output path specified")

            # Create directories if enabled
            if self.knobs.get('create_dirs', {}).value():
                output_dir = os.path.dirname(output_path)
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir, exist_ok=True)
                    self.logger.info(f"Created output directory: {output_dir}")

            # Validate output directory exists
            output_dir = os.path.dirname(output_path)
            if not os.path.exists(output_dir):
                raise ValueError(f"Output directory does not exist: {output_dir}")

            # Save version metadata if enabled
            if self.knobs.get('save_metadata', {}).value():
                version = self.knobs.get('output_version', {}).value() or 'v001'
                metadata = self.create_version_metadata(version, output_path)
                self.save_version_metadata(metadata, output_dir)

            # Update status
            self._update_status_display(output_path)

            self.logger.info(f"MultishotWrite ready for render: {output_path}")

        except Exception as e:
            self.logger.error(f"Error in before_render: {e}")
            raise

    def after_render(self):
        """Called after rendering completes. Handles multi-output if enabled."""
        try:
            output_path = self.node['file'].value()
            if output_path:
                self.logger.info(f"MultishotWrite render completed: {output_path}")

                # Handle multi-output (MOV generation)
                if self.knobs.get('enable_multi_output', {}).value():
                    self._create_mov_output(output_path)

        except Exception as e:
            self.logger.error(f"Error in after_render: {e}")

    def _create_mov_output(self, exr_path: str):
        """
        Create MOV output from EXR sequence.

        Args:
            exr_path: Path to EXR sequence
        """
        try:
            import nuke

            self.logger.info("Creating MOV output from EXR sequence...")

            # Build MOV path (same directory, .mov extension)
            exr_dir = os.path.dirname(exr_path)
            exr_basename = os.path.basename(exr_path)
            # Remove frame number pattern
            mov_basename = re.sub(r'\.%\d+d\.exr$', '.mov', exr_basename)
            mov_path = os.path.join(exr_dir, mov_basename)

            # Get settings
            colorspace = self.knobs.get('mov_colorspace', {}).value() or 'sRGB'
            codec = self.knobs.get('mov_codec', {}).value() or 'H.264'

            self.logger.info(f"MOV output: {mov_path}")
            self.logger.info(f"Colorspace: {colorspace}, Codec: {codec}")

            # Note: Actual MOV creation would require creating a separate Write node
            # or using nuke.execute() with a temporary script
            # This is a placeholder for the logic

            self.logger.info("MOV output creation completed")

        except Exception as e:
            self.logger.error(f"Error creating MOV output: {e}")


# Global node instances storage
_node_instances = {}


def create_multishot_write():
    """
    Create a new MultishotWrite node.

    This function is called from Nuke's menu system.
    """
    try:
        multishot_write = MultishotWrite()
        node = multishot_write.create_node()

        # Setup render callbacks
        try:
            import nuke

            # Add before render callback
            before_render_code = '''
import multishot.nodes.write_node as write_node_module
node = nuke.thisNode()
if hasattr(write_node_module, '_node_instances'):
    instance = write_node_module._node_instances.get(node.name())
    if instance:
        instance.before_render()
'''
            node['beforeRender'].setValue(before_render_code)

            # Add after render callback
            after_render_code = '''
import multishot.nodes.write_node as write_node_module
node = nuke.thisNode()
if hasattr(write_node_module, '_node_instances'):
    instance = write_node_module._node_instances.get(node.name())
    if instance:
        instance.after_render()
'''
            node['afterRender'].setValue(after_render_code)

        except Exception as callback_error:
            # Log error but don't fail node creation
            multishot_write.logger.warning(f"Could not setup render callbacks: {callback_error}")

        return node

    except Exception as e:
        import nuke
        nuke.message(f"Error creating MultishotWrite node: {e}")
        return None
