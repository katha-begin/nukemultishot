"""
MultishotWrite Gizmo wrapper.

Creates a Gizmo (Group node) that wraps the MultishotWrite functionality
with internal Write nodes for EXR and MOV output.
"""

import os
import json
import datetime
import re
from typing import Dict, Any, Optional

from ..utils.logging import get_logger
from ..core.variables import VariableManager
from ..core.paths import PathResolver


class MultishotWriteGizmo:
    """
    Gizmo wrapper for MultishotWrite with multi-output support.
    
    Creates a Group node containing:
    - Input (from upstream)
    - Write node for EXR output
    - Colorspace node for MOV
    - Write node for MOV output
    - Output (to downstream)
    """
    
    def __init__(self, variable_manager=None):
        self.logger = get_logger(__name__)
        
        # Use shared variable manager if provided
        if variable_manager is not None:
            self.variable_manager = variable_manager
        else:
            self.variable_manager = VariableManager()
            
        self.path_resolver = PathResolver()
        
        # Node references
        self.group = None
        self.write_exr = None
        self.write_mov = None
        self.colorspace = None
        self.knobs = {}
        
        self.logger.info("MultishotWriteGizmo initialized")
    
    def create_gizmo(self) -> 'nuke.Node':
        """
        Create the MultishotWrite Gizmo.
        
        Returns:
            The created Group node
        """
        try:
            import nuke
            
            # Create Group node
            self.group = nuke.nodes.Group()
            self.group.setName('MultishotWrite')
            
            # Enter the group to add internal nodes
            self.group.begin()
            
            # Create internal node network
            self._create_internal_network()
            
            # Exit the group
            self.group.end()
            
            # Add custom knobs to the group
            self._add_custom_knobs()
            
            # Set up callbacks
            self._setup_callbacks()
            
            # Initialize from context
            self._initialize_from_context()
            
            self.logger.info("MultishotWrite Gizmo created successfully")
            return self.group
            
        except ImportError:
            self.logger.error("Cannot create MultishotWrite Gizmo - Nuke not available")
            raise
        except Exception as e:
            self.logger.error(f"Error creating MultishotWrite Gizmo: {e}")
            raise
    
    def _create_internal_network(self):
        """Create the internal node network inside the Group."""
        try:
            import nuke
            
            # Input node
            input_node = nuke.nodes.Input()
            input_node.setXYpos(0, 0)
            
            # EXR Write node
            self.write_exr = nuke.nodes.Write()
            self.write_exr.setName('Write_EXR')
            self.write_exr['file_type'].setValue('exr')
            self.write_exr.setInput(0, input_node)
            self.write_exr.setXYpos(0, 100)
            
            # Colorspace node for MOV (baked colorspace)
            self.colorspace = nuke.nodes.Colorspace()
            self.colorspace.setName('Colorspace_MOV')
            self.colorspace.setInput(0, input_node)
            self.colorspace.setXYpos(200, 100)
            
            # MOV Write node
            self.write_mov = nuke.nodes.Write()
            self.write_mov.setName('Write_MOV')
            self.write_mov['file_type'].setValue('mov')
            self.write_mov.setInput(0, self.colorspace)
            self.write_mov.setXYpos(200, 200)
            
            # Disable MOV write by default
            self.write_mov['disable'].setValue(True)
            
            # Output node (connected to EXR write for passthrough)
            output_node = nuke.nodes.Output()
            output_node.setInput(0, input_node)
            output_node.setXYpos(0, 300)
            
            self.logger.debug("Internal network created")
            
        except Exception as e:
            self.logger.error(f"Error creating internal network: {e}")
            raise
    
    def _add_custom_knobs(self):
        """Add custom knobs to the Group node."""
        try:
            import nuke
            
            # Separator
            sep = nuke.Text_Knob('multishot_sep', 'Multishot Settings')
            self.group.addKnob(sep)
            
            # Output type
            output_type = nuke.Enumeration_Knob('output_type', 'Output Type', 
                                                ['comp_render', 'dept_render', 'geometry'])
            output_type.setValue('comp_render')
            output_type.setTooltip('Type of output - determines path structure')
            self.group.addKnob(output_type)
            self.knobs['output_type'] = output_type
            
            # Department
            department = nuke.String_Knob('department', 'Department')
            department.setValue('comp')
            department.setTooltip('Department name for output path')
            self.group.addKnob(department)
            self.knobs['department'] = department
            
            # Layer/Element name
            layer = nuke.String_Knob('layer', 'Layer/Element')
            layer.setValue('beauty')
            layer.setTooltip('Layer or element name for output')
            self.group.addKnob(layer)
            self.knobs['layer'] = layer
            
            # Version
            version = nuke.String_Knob('output_version', 'Version')
            version.setValue('v001')
            version.setTooltip('Version number for output')
            self.group.addKnob(version)
            self.knobs['output_version'] = version
            
            # Detect Latest Version button
            detect_version = nuke.PyScript_Knob('detect_latest_version', 'Detect Latest')
            detect_version.setTooltip('Detect latest version from output directory')
            self.group.addKnob(detect_version)
            self.knobs['detect_latest_version'] = detect_version
            
            # Use Next Version button
            use_next_version = nuke.PyScript_Knob('use_next_version', 'Use Next')
            use_next_version.setTooltip('Use next version number')
            self.group.addKnob(use_next_version)
            self.knobs['use_next_version'] = use_next_version
            
            # Save metadata
            save_metadata = nuke.Boolean_Knob('save_metadata', 'Save Metadata')
            save_metadata.setValue(True)
            save_metadata.setTooltip('Save version metadata (nuke script, timestamp, etc.)')
            self.group.addKnob(save_metadata)
            self.knobs['save_metadata'] = save_metadata
            
            # Create directories
            create_dirs = nuke.Boolean_Knob('create_dirs', 'Create Directories')
            create_dirs.setValue(True)
            create_dirs.setTooltip('Automatically create output directories')
            self.group.addKnob(create_dirs)
            self.knobs['create_dirs'] = create_dirs
            
            # Multi-Output separator
            multi_sep = nuke.Text_Knob('multi_output_sep', 'Multi-Output Settings')
            self.group.addKnob(multi_sep)
            
            # Enable multi-output
            enable_multi = nuke.Boolean_Knob('enable_multi_output', 'Enable Multi-Output')
            enable_multi.setValue(False)
            enable_multi.setTooltip('Enable multiple output formats (EXR + MOV)')
            self.group.addKnob(enable_multi)
            self.knobs['enable_multi_output'] = enable_multi
            
            # MOV colorspace
            mov_colorspace = nuke.Enumeration_Knob('mov_colorspace', 'MOV Colorspace',
                                                   ['sRGB', 'Rec709', 'linear', 'ACEScg'])
            mov_colorspace.setValue('sRGB')
            mov_colorspace.setTooltip('Colorspace for MOV output (baked)')
            self.group.addKnob(mov_colorspace)
            self.knobs['mov_colorspace'] = mov_colorspace
            
            # MOV codec
            mov_codec = nuke.Enumeration_Knob('mov_codec', 'MOV Codec',
                                              ['mov64', 'mov32'])
            mov_codec.setValue('mov64')
            mov_codec.setTooltip('Codec for MOV output')
            self.group.addKnob(mov_codec)
            self.knobs['mov_codec'] = mov_codec
            
            # Status display
            status = nuke.Text_Knob('status', 'Status', 'Ready')
            self.group.addKnob(status)
            self.knobs['status'] = status
            
            # Update path button
            update_path = nuke.PyScript_Knob('update_path', 'Update Path')
            update_path.setTooltip('Update output paths based on current settings')
            self.group.addKnob(update_path)
            self.knobs['update_path'] = update_path
            
            self.logger.debug("Custom knobs added")
            
        except Exception as e:
            self.logger.error(f"Error adding custom knobs: {e}")
            raise
    
    def _setup_callbacks(self):
        """Set up knob change callbacks."""
        try:
            import nuke
            
            # Store reference to this instance in the node
            # This allows callbacks to access the instance methods
            self.group.addKnob(nuke.Text_Knob('_gizmo_instance', ''))
            self.group['_gizmo_instance'].setVisible(False)
            
            # Set up knobChanged callback
            callback_code = """
import multishot.nodes.write_gizmo as write_gizmo_module

# Get the gizmo instance from global registry
node = nuke.thisNode()
instance = write_gizmo_module.get_gizmo_instance(node.name())

if instance:
    knob = nuke.thisKnob()
    instance.knob_changed(knob)
"""
            
            self.group['knobChanged'].setValue(callback_code)
            
            # Register this instance globally
            register_gizmo_instance(self.group.name(), self)
            
            self.logger.debug("Callbacks set up")
            
        except Exception as e:
            self.logger.error(f"Error setting up callbacks: {e}")

    def _initialize_from_context(self):
        """Initialize gizmo with current context variables."""
        try:
            # Update paths based on current context
            self._update_paths()
            self.logger.debug("MultishotWrite Gizmo initialized from context")
        except Exception as e:
            self.logger.error(f"Error initializing from context: {e}")

    def knob_changed(self, knob):
        """Handle knob change events."""
        try:
            if not knob:
                return

            knob_name = knob.name()

            if knob_name == 'output_type':
                self._update_paths()

            elif knob_name in ['department', 'layer', 'output_version']:
                self._update_paths()

            elif knob_name == 'update_path':
                self._update_paths()

            elif knob_name == 'detect_latest_version':
                self._detect_and_set_latest_version()

            elif knob_name == 'use_next_version':
                self._use_next_version()

            elif knob_name == 'enable_multi_output':
                self._toggle_multi_output()

            elif knob_name == 'mov_colorspace':
                self._update_mov_colorspace()

        except Exception as e:
            self.logger.error(f"Error in knob_changed: {e}")

    def _update_paths(self):
        """Update output paths for both EXR and MOV writes."""
        try:
            variables = self.variable_manager.get_all_variables()
            department = self.group['department'].value() or 'comp'
            version = self.group['output_version'].value() or 'v001'
            layer = self.group['layer'].value() or 'beauty'

            # Build path variables
            path_variables = variables.copy()
            path_variables.update({
                'department': department,
                'version': version,
                'layer': layer
            })

            # Build EXR path
            exr_template = (
                '[value root.IMG_ROOT]/[value root.project]/all/scene/'
                '[value root.ep]/[value root.seq]/[value root.shot]/'
                f'{department}/version/{version}/{layer}.%04d.exr'
            )

            # Build MOV path
            mov_template = (
                '[value root.IMG_ROOT]/[value root.project]/all/scene/'
                '[value root.ep]/[value root.seq]/[value root.shot]/'
                f'{department}/version/{version}/{layer}.mov'
            )

            # Update Write nodes using fromUserText() to ensure expressions are evaluated
            self.write_exr['file'].fromUserText(exr_template)
            self.write_mov['file'].fromUserText(mov_template)

            # Update status
            self._update_status(exr_template)

            self.logger.debug(f"Paths updated: EXR={exr_template}, MOV={mov_template}")

        except Exception as e:
            self.logger.error(f"Error updating paths: {e}")
            self._update_status(f"Error: {e}", is_error=True)

    def _toggle_multi_output(self):
        """Enable/disable MOV output based on multi-output setting."""
        try:
            enable_multi = self.group['enable_multi_output'].value()

            # Enable/disable MOV write node
            self.write_mov['disable'].setValue(not enable_multi)

            if enable_multi:
                self.logger.info("Multi-output enabled (EXR + MOV)")
            else:
                self.logger.info("Multi-output disabled (EXR only)")

        except Exception as e:
            self.logger.error(f"Error toggling multi-output: {e}")

    def _update_mov_colorspace(self):
        """Update MOV colorspace based on setting."""
        try:
            colorspace_name = self.group['mov_colorspace'].value()

            # Map UI names to Nuke colorspace names
            colorspace_map = {
                'sRGB': 'sRGB',
                'Rec709': 'rec709',
                'linear': 'linear',
                'ACEScg': 'ACEScg'
            }

            nuke_colorspace = colorspace_map.get(colorspace_name, 'sRGB')
            self.colorspace['colorspace_out'].setValue(nuke_colorspace)

            self.logger.debug(f"MOV colorspace set to: {nuke_colorspace}")

        except Exception as e:
            self.logger.error(f"Error updating MOV colorspace: {e}")

    def _update_status(self, message: str, is_error: bool = False):
        """Update status display."""
        try:
            if is_error:
                self.group['status'].setValue(f"❌ {message}")
            else:
                self.group['status'].setValue(f"✅ {message}")
        except Exception as e:
            self.logger.error(f"Error updating status: {e}")

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
        """Detect the latest version number in the output directory."""
        try:
            if not os.path.exists(output_dir):
                return 'v001'

            versions = []
            for item in os.listdir(output_dir):
                item_path = os.path.join(output_dir, item)
                if os.path.isdir(item_path):
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
        """Get the next version number."""
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

    def _detect_and_set_latest_version(self):
        """Detect latest version from output directory and set it."""
        try:
            variables = self.variable_manager.get_all_variables()
            department = self.group['department'].value() or 'comp'

            proj_root = variables.get('IMG_ROOT', 'W:/')
            project = variables.get('project', '')
            ep = variables.get('ep', '')
            seq = variables.get('seq', '')
            shot = variables.get('shot', '')

            if not all([project, ep, seq, shot]):
                self.logger.warning("Cannot detect version - missing context variables")
                self._update_status("Missing context variables", is_error=True)
                return

            base_dir = os.path.join(proj_root, project, 'all', 'scene', ep, seq, shot, department, 'version')
            latest_version = self.detect_latest_version(base_dir)

            self.group['output_version'].setValue(latest_version)
            self.logger.info(f"Set version to latest: {latest_version}")

            self._update_paths()

        except Exception as e:
            self.logger.error(f"Error detecting latest version: {e}")
            self._update_status(f"Error: {e}", is_error=True)

    def _use_next_version(self):
        """Use next version number."""
        try:
            current_version = self.group['output_version'].value() or 'v001'
            next_version = self.get_next_version(current_version)

            self.group['output_version'].setValue(next_version)
            self.logger.info(f"Set version to next: {next_version}")

            self._update_paths()

        except Exception as e:
            self.logger.error(f"Error using next version: {e}")
            self._update_status(f"Error: {e}", is_error=True)

    def create_version_metadata(self, version: str, output_path: str) -> Dict[str, Any]:
        """Create metadata for version tracking."""
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
        """Save version metadata to JSON file."""
        try:
            if not metadata:
                return

            version = metadata.get('version', 'v001')
            metadata_file = os.path.join(output_dir, f"{version}_metadata.json")

            # Create directory if needed
            os.makedirs(output_dir, exist_ok=True)

            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)

            self.logger.info(f"Saved version metadata: {metadata_file}")

        except Exception as e:
            self.logger.error(f"Error saving version metadata: {e}")

    def before_render(self):
        """Called before rendering starts."""
        try:
            # Get output path from EXR write
            output_path = self.write_exr['file'].value()
            if not output_path:
                raise ValueError("No output path specified")

            # Create directories if enabled
            if self.group['create_dirs'].value():
                output_dir = os.path.dirname(output_path)
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir, exist_ok=True)
                    self.logger.info(f"Created output directory: {output_dir}")

            # Save metadata if enabled
            if self.group['save_metadata'].value():
                version = self.group['output_version'].value() or 'v001'
                output_dir = os.path.dirname(output_path)
                metadata = self.create_version_metadata(version, output_path)
                self.save_version_metadata(metadata, output_dir)

            self.logger.info(f"MultishotWrite Gizmo ready for render: {output_path}")

        except Exception as e:
            self.logger.error(f"Error in before_render: {e}")
            raise


# Global registry for gizmo instances
_gizmo_instances = {}


def register_gizmo_instance(node_name: str, instance: MultishotWriteGizmo):
    """Register a gizmo instance globally."""
    global _gizmo_instances
    _gizmo_instances[node_name] = instance


def get_gizmo_instance(node_name: str) -> Optional[MultishotWriteGizmo]:
    """Get a gizmo instance by node name."""
    global _gizmo_instances
    return _gizmo_instances.get(node_name)


def create_multishot_write_gizmo(variable_manager=None) -> 'nuke.Node':
    """
    Create a MultishotWrite Gizmo.

    Args:
        variable_manager: Optional shared VariableManager instance

    Returns:
        The created Group node
    """
    gizmo = MultishotWriteGizmo(variable_manager=variable_manager)
    return gizmo.create_gizmo()


__all__ = [
    'MultishotWriteGizmo',
    'create_multishot_write_gizmo',
    'get_gizmo_instance',
    'register_gizmo_instance'
]

