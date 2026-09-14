"""
Custom Read node for the Multishot Workflow System.

Provides variable-driven file paths with version selection and approval status.
"""

import os
import re
import json
from typing import Dict, List, Optional, Any

from ..utils.logging import get_logger
from ..core.variables import VariableManager
from ..core.paths import PathResolver
from ..core.scanner import DirectoryScanner

class MultishotRead:
    """
    Custom Read node with variable-driven paths.

    Features:
    - Variable-driven file path resolution
    - Version selection dropdown
    - Asset type detection (images, geometry, cameras)
    - Approval status visualization
    - Missing frame handling configuration
    """

    def __init__(self, variable_manager=None):
        self.logger = get_logger(__name__)

        # Use provided variable_manager or create new one
        if variable_manager is not None:
            self.variable_manager = variable_manager
            self.logger.info("MultishotRead using shared VariableManager instance")
        else:
            self.variable_manager = VariableManager()
            self.logger.info("MultishotRead created new VariableManager instance")

        self.path_resolver = PathResolver()
        self.scanner = DirectoryScanner()

        # Node state
        self.node = None
        self.knobs = {}

        self.logger.info("MultishotRead initialized")

    def create_node(self) -> 'nuke.Node':
        """
        Create the custom Read node in Nuke.

        Returns:
            Created Nuke node
        """
        try:
            import nuke

            # ✅ CRITICAL FIX: Save current context before creating node
            # Even nuke.nodes.Read() might trigger internal context reset
            saved_context = {}
            context_knobs = ['multishot_project', 'multishot_ep', 'multishot_seq', 'multishot_shot']
            for knob_name in context_knobs:
                if nuke.root().knob(knob_name):
                    saved_context[knob_name] = str(nuke.root()[knob_name].value())

            self.logger.debug(f"Saved context before node creation: {saved_context}")

            # Create base Read node using nuke.nodes.Read() to avoid context reset
            # DO NOT use nuke.createNode() as it resets root knobs!
            self.node = nuke.nodes.Read()
            self.node.setName('MultishotRead')

            # ✅ CRITICAL FIX: Restore context after creating node
            for knob_name, value in saved_context.items():
                if nuke.root().knob(knob_name):
                    nuke.root()[knob_name].setValue(value)

            self.logger.debug(f"Restored context after node creation: {saved_context}")

            # Add custom knobs
            self._add_custom_knobs()

            # Setup callbacks
            self._setup_callbacks()

            # Initialize with current context
            self._initialize_from_context()

            self.logger.info("MultishotRead node created successfully")
            return self.node

        except ImportError:
            self.logger.error("Cannot create MultishotRead node - Nuke not available")
            raise
        except Exception as e:
            self.logger.error(f"Error creating MultishotRead node: {e}")
            raise

    def _add_custom_knobs(self):
        """Add custom knobs to the node."""
        try:
            import nuke

            # Separator
            sep = nuke.Text_Knob('multishot_sep', 'Multishot Settings')
            self.node.addKnob(sep)

            # Department selection
            department = nuke.Enumeration_Knob('department', 'Department', ['lighting', 'fx', 'comp', 'anim', 'layout'])
            department.setValue('lighting')
            department.setTooltip('Department for asset lookup')
            self.node.addKnob(department)
            self.knobs['department'] = department

            # ✅ CRITICAL FIX: Read node already has a 'version' knob (Float)!
            # We need to use a different name: 'shot_version' instead of 'version'
            # This will be a String_Knob that persists correctly
            shot_version = nuke.String_Knob('shot_version', 'Version')
            shot_version.setValue('v001')
            shot_version.setTooltip('Version for current shot - managed by Multishot Manager')
            self.node.addKnob(shot_version)
            self.knobs['shot_version'] = shot_version

            # Layer/Element name
            layer = nuke.File_Knob('layer', 'Layer/Element')
            layer.setValue('MASTER_CHAR_A')
            layer.setTooltip('Layer or element name (e.g., MASTER_CHAR_A, beauty, diffuse)')
            self.node.addKnob(layer)
            self.knobs['layer'] = layer

            # File pattern (relative path from version directory)
            file_pattern = nuke.File_Knob('file_pattern', 'File Pattern')
            file_pattern.setValue('MASTER_CHAR_A/MASTER_CHAR_A.%04d.exr')
            file_pattern.setTooltip('File pattern relative to version directory (supports sub-components)')
            self.node.addKnob(file_pattern)
            self.knobs['file_pattern'] = file_pattern

            # Hidden knob to store per-shot versions as JSON
            shot_versions = nuke.File_Knob('shot_versions', '')
            shot_versions.setValue('{}')
            shot_versions.setVisible(False)
            shot_versions.setTooltip('Per-shot version storage (JSON)')
            self.node.addKnob(shot_versions)
            self.knobs['shot_versions'] = shot_versions

            # Status display
            status = nuke.Text_Knob('status', 'Status', 'Ready')
            self.node.addKnob(status)
            self.knobs['status'] = status

            # Build Path button
            build_path = nuke.PyScript_Knob('build_path', 'Build Path')
            build_path.setCommand('''
import multishot.nodes.read_node as read_node_module
node = nuke.thisNode()
if node.name() in read_node_module._node_instances:
    instance = read_node_module._node_instances[node.name()]
    instance.build_expression_path()
''')
            self.node.addKnob(build_path)
            self.knobs['build_path'] = build_path

            # Refresh button (scan versions, update path)
            refresh = nuke.PyScript_Knob('refresh', 'Refresh')
            refresh.setCommand('''
import multishot.nodes.read_node as read_node_module
node = nuke.thisNode()
if node.name() in read_node_module._node_instances:
    instance = read_node_module._node_instances[node.name()]
    instance.refresh_node()
''')
            self.node.addKnob(refresh)
            self.knobs['refresh'] = refresh

        except Exception as e:
            self.logger.error(f"Error adding custom knobs: {e}")
            raise

    def _setup_callbacks(self):
        """Setup knob change callbacks."""
        try:
            import nuke

            # Store reference to this instance in the node
            self.node.addKnob(nuke.Text_Knob('multishot_instance', '', ''))
            self.node['multishot_instance'].setVisible(False)

            # Set knob changed callback
            callback_code = '''
import multishot.nodes.read_node as read_node_module
node = nuke.thisNode()
if hasattr(read_node_module, '_node_instances'):
    instance = read_node_module._node_instances.get(node.name())
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
            # Build initial expression path
            self.build_expression_path()
            self.logger.debug("MultishotRead initialized from context")

        except Exception as e:
            self.logger.error(f"Error initializing from context: {e}")

    def knob_changed(self, knob):
        """Handle knob change events."""
        try:
            if not knob:
                return

            knob_name = knob.name()

            # Rebuild path when department or layer changes
            if knob_name in ['department', 'layer']:
                self.build_expression_path()

        except Exception as e:
            self.logger.error(f"Error in knob_changed: {e}")

    def build_expression_path(self):
        """Build expression-based file path using root knobs and node knobs."""
        try:
            import nuke

            # Get values from node knobs
            department = self.node['department'].value() if self.node.knob('department') else 'lighting'
            layer = self.node['layer'].value() if self.node.knob('layer') else 'MASTER_CHAR_A'
            node_name = self.node.name()

            # ✅ Use file_pattern if available (supports sub-components like Cryptomatte)
            if self.node.knob('file_pattern') and self.node['file_pattern'].value():
                file_pattern = self.node['file_pattern'].value()
                self.logger.info(f"[BUILD_PATH] Using file_pattern: {file_pattern}")
            else:
                # Fallback to old format
                file_pattern = f"{layer}/{layer}.%04d.exr"
                self.logger.info(f"[BUILD_PATH] Using default pattern: {file_pattern}")

            self.logger.info(f"[BUILD_PATH] Node: {node_name}, Department: {department}, Layer: {layer}")

            # Build expression path using node's shot_version knob and file pattern
            # Format: [value root.IMG_ROOT][value root.project]/all/scene/[value root.ep]/[value root.seq]/[value root.shot]/lighting/publish/[value parent.NodeName.shot_version]/{file_pattern}
            #
            # CRITICAL FIX: Use fromUserText() to properly set TCL expressions
            # When using setValue() with TCL expressions, they may not evaluate in batch mode
            # fromUserText() ensures expressions are properly marked for evaluation
            file_path = (
                f"[value root.IMG_ROOT][value root.project]/all/scene/"
                f"[value root.ep]/[value root.seq]/[value root.shot]/"
                f"{department}/publish/[value parent.{node_name}.shot_version]/{file_pattern}"
            )

            # Set file path using fromUserText() to ensure expressions are evaluated
            self.node['file'].fromUserText(file_path)

            # ✅ FIX: Set first/last frame to use root knobs
            # This ensures the Read node uses the correct frame range from the script
            # Without this, the expressions might evaluate incorrectly and get "baked" into the script
            # Note: first/last are Int_Knob, so we use setExpression() not fromUserText()
            if self.node.knob('first'):
                self.node['first'].setExpression('[value root.first_frame]')
                self.logger.debug("[BUILD_PATH] Set first frame to [value root.first_frame]")

            if self.node.knob('last'):
                self.node['last'].setExpression('[value root.last_frame]')
                self.logger.debug("[BUILD_PATH] Set last frame to [value root.last_frame]")

            # Update status
            self.node['status'].setValue(f"Path: {department}/{layer}")

            self.logger.info(f"[BUILD_PATH] Built expression path: {file_path}")

        except Exception as e:
            self.logger.error(f"Error building expression path: {e}")
            if self.node.knob('status'):
                self.node['status'].setValue(f"Error: {e}")

    def refresh_node(self):
        """Refresh node: scan versions and rebuild path."""
        try:
            # Rebuild expression path
            self.build_expression_path()

            # Update status
            self.node['status'].setValue("Refreshed")

            self.logger.info("Node refreshed")

        except Exception as e:
            self.logger.error(f"Error refreshing node: {e}")
            if self.node.knob('status'):
                self.node['status'].setValue(f"Error: {e}")

    def get_shot_key(self, project=None, ep=None, seq=None, shot=None):
        """
        Build shot key from context.

        Args:
            project, ep, seq, shot: Context values. If None, read from root knobs.

        Returns:
            Shot key string (e.g., "SWA_Ep01_sq0010_SH0010")
        """
        try:
            import nuke

            # Get from root knobs if not provided
            if project is None:
                project = nuke.root()['multishot_project'].value() if nuke.root().knob('multishot_project') else ''
            if ep is None:
                ep = nuke.root()['multishot_ep'].value() if nuke.root().knob('multishot_ep') else ''
            if seq is None:
                seq = nuke.root()['multishot_seq'].value() if nuke.root().knob('multishot_seq') else ''
            if shot is None:
                shot = nuke.root()['multishot_shot'].value() if nuke.root().knob('multishot_shot') else ''

            # Build key
            shot_key = f"{project}_{ep}_{seq}_{shot}"
            return shot_key

        except Exception as e:
            self.logger.error(f"Error building shot key: {e}")
            return ""

    def get_version_for_shot(self, shot_key=None):
        """
        Get version stored for a specific shot.

        Args:
            shot_key: Shot key string. If None, uses current shot from root knobs.

        Returns:
            Version string (e.g., "v001"), v001 if none is stored
        """
        try:
            if shot_key is None:
                shot_key = self.get_shot_key()
            return get_shot_version(self.node, shot_key) or 'v001'

        except Exception as e:
            self.logger.error(f"Error getting version for shot: {e}")
            return 'v001'

    def set_version_for_shot(self, version, shot_key=None):
        """
        Set version for a specific shot.

        Args:
            version: Version string (e.g., "v001")
            shot_key: Shot key string. If None, uses current shot from root knobs.
        """
        try:
            # Get the ACTUAL current shot from root knobs
            current_shot_key = self.get_shot_key()
            if shot_key is None:
                shot_key = current_shot_key

            set_shot_version(self.node, version, shot_key, current_shot_key)

            # Rebuild path when the node switched to this version
            if shot_key == current_shot_key:
                self.build_expression_path()

            self.logger.info(f"Set version for shot {shot_key}: {version}")

        except Exception as e:
            self.logger.error(f"Error setting version for shot: {e}")
            print(f"   ❌ [SET_VERSION] Error: {e}")




# Global node instances storage
_node_instances = {}

# Version directory names: v001, v002, v001_001
VERSION_PATTERN = re.compile(r'^v(\d+)(?:_(\d+))?$', re.IGNORECASE)


def version_sort_key(version: str):
    """Sort key for version names: v001 < v002 < v002_001 < v010."""
    match = VERSION_PATTERN.match(version)
    if not match:
        return (-1, -1)
    return (int(match.group(1)), int(match.group(2) or 0))


def _get_shot_versions(node) -> Dict[str, str]:
    """Read the per-shot versions JSON stored on a MultishotRead node."""
    shot_versions_str = node['shot_versions'].value() if node.knob('shot_versions') else ''
    return json.loads(shot_versions_str) if shot_versions_str else {}


def get_shot_version(node, shot_key: str) -> Optional[str]:
    """
    Get the version stored for a shot on a MultishotRead node.

    Reads the node's knobs directly, so it works for any live node - including
    nodes whose _node_instances entry is missing or points at a deleted node.

    Returns:
        Version string, or None if no version was stored for the shot
    """
    return _get_shot_versions(node).get(shot_key)


def set_shot_version(node, version: str, shot_key: str, current_shot_key: Optional[str]):
    """
    Store the version for a shot on a MultishotRead node.

    Args:
        node: MultishotRead node
        version: Version string (e.g., "v002")
        shot_key: Shot the version is for (e.g., "EGA_Ep02_sq0380_SH3370")
        current_shot_key: Active shot in the script - the node only switches to the
                          version when shot_key is the active shot
    """
    shot_versions = _get_shot_versions(node)
    shot_versions[shot_key] = version
    node['shot_versions'].setValue(json.dumps(shot_versions))

    if shot_key == current_shot_key:
        apply_shot_version(node, version)


def apply_shot_version(node, version: str):
    """Switch a MultishotRead node to a version."""
    node['shot_version'].setValue(version)

    # A copied Read keeps [value parent.<original>.shot_version] in its path and would
    # follow the original node's version, so point the path at this node's own knob
    file_knob = node.knob('file')
    if file_knob:
        path = file_knob.value()
        own_version = f"[value parent.{node.name()}.shot_version]"
        fixed_path = re.sub(r'\[value parent\.[A-Za-z0-9_]+\.shot_version\]', lambda match: own_version, path)
        if fixed_path != path:
            file_knob.setValue(fixed_path)


def get_file_pattern(node) -> str:
    """Image pattern relative to the version directory (e.g., MASTER_CHAR_A/MASTER_CHAR_A_CRYPTO.%04d.exr)."""
    if node.knob('file_pattern') and node['file_pattern'].value():
        return node['file_pattern'].value()
    layer = node['layer'].value() if node.knob('layer') else 'MASTER_CHAR_A'
    return f"{layer}/{layer}.%04d.exr"


def get_publish_dir(img_root: str, shot_data: Dict[str, str], department: str) -> str:
    """Directory holding a department's published render versions for a shot."""
    return os.path.join(img_root, shot_data['project'], 'all', 'scene',
                        shot_data['ep'], shot_data['seq'], shot_data['shot'], department, 'publish')


def find_layer_versions(publish_dir: str, file_pattern: str) -> List[str]:
    """
    List versions in a publish directory that contain an image, oldest first.

    Args:
        publish_dir: Department publish directory (e.g., Y:/EGA/all/scene/Ep02/sq0380/SH3370/lighting/publish)
        file_pattern: Image pattern relative to the version directory
                      (e.g., "MASTER_CHAR_A/MASTER_CHAR_A_CRYPTO.%04d.exr")

    Returns:
        Version names (e.g., ['v001', 'v002']) - versions with an empty or missing layer are skipped
    """
    if not publish_dir or not os.path.isdir(publish_dir):
        return []

    image_dir, image = os.path.split(file_pattern)

    # Frame tokens (%04d, ####) match any frame number
    parts = re.split(r'(%0?\d*d|#+)', image)
    image_regex = re.compile('^' + ''.join(r'\d+' if i % 2 else re.escape(part) for i, part in enumerate(parts)) + '$')

    versions = []
    try:
        for version in os.listdir(publish_dir):
            version_image_dir = os.path.join(publish_dir, version, image_dir)
            if VERSION_PATTERN.match(version) and os.path.isdir(version_image_dir):
                if any(image_regex.match(filename) for filename in os.listdir(version_image_dir)):
                    versions.append(version)
    except OSError:
        pass

    return sorted(versions, key=version_sort_key)


def resolve_shot_version(node, shot_key: str, publish_dir: str) -> str:
    """
    Version a MultishotRead node should use for a shot.

    Returns:
        The version stored for the shot, else the latest version on disk that
        contains the node's image, else v001
    """
    version = get_shot_version(node, shot_key)
    if version:
        return version

    versions = find_layer_versions(publish_dir, get_file_pattern(node))
    return versions[-1] if versions else 'v001'


def _is_attached(node, node_name: str) -> bool:
    """True if a stored node object still points at a live node with this name."""
    try:
        return node is not None and node.name() == node_name
    except Exception:
        # "A PythonObject is not attached to a node" - node deleted or script reloaded
        return False


def get_read_node_name(department: str, layer: str, image_name: str) -> str:
    """
    Build a MultishotRead node name that is unique for each image in a layer.

    Args:
        department: Department name (e.g., "lighting")
        layer: Layer directory name (e.g., "MASTER_CHAR_A")
        image_name: File name without frame and extension
                    (e.g., "MASTER_CHAR_A", "MASTER_CHAR_A_CRYPTO", "MASTER_CHAR_A.Cryptomatte_node")

    Returns:
        Node name (e.g., "MultishotRead_lighting_MASTER_CHAR_A_CRYPTO")
    """
    element = image_name if image_name.startswith(layer) else f"{layer}_{image_name}"
    return re.sub(r'[^a-zA-Z0-9_]', '_', f"MultishotRead_{department}_{element}")


def restore_multishot_instances(variable_manager=None):
    """
    Restore MultishotRead instances for existing nodes in the script.

    This should be called when:
    - Opening a saved Nuke script
    - After loading the multishot module

    Args:
        variable_manager: Optional VariableManager instance to share state
    """
    try:
        import nuke
        from ..utils.logging import get_logger

        logger = get_logger(__name__)

        print("\n🔄 [RESTORE] Restoring MultishotRead instances...")

        # Find all MultishotRead nodes in the script
        restored_count = 0
        for node in nuke.allNodes():
            if node.knob('multishot_sep'):  # Is a MultishotRead node
                node_name = node.name()

                # Keep an existing instance only if it still points at this node. Reloading the
                # script (Render button, File > Open) or cut/paste leaves dead node objects behind
                existing = _node_instances.get(node_name)
                if existing is not None and _is_attached(existing.node, node_name):
                    print(f"   ⏭️  [RESTORE] Instance already exists for: {node_name}")
                    continue

                print(f"   🔧 [RESTORE] Restoring instance for: {node_name}")

                # Create MultishotRead instance
                multishot_read = MultishotRead(variable_manager=variable_manager)
                multishot_read.node = node  # Attach to existing node

                # Store knob references
                multishot_read.knobs = {
                    'department': node.knob('department'),
                    'shot_version': node.knob('shot_version'),
                    'layer': node.knob('layer'),
                    'file_pattern': node.knob('file_pattern'),
                    'shot_versions': node.knob('shot_versions'),
                    'status': node.knob('status'),
                }

                # Register instance
                _node_instances[node_name] = multishot_read

                print(f"   ✅ [RESTORE] Restored instance: {node_name}")
                restored_count += 1

        print(f"✅ [RESTORE] Restored {restored_count} MultishotRead instances\n")
        logger.info(f"Restored {restored_count} MultishotRead instances")

        return restored_count

    except ImportError:
        print("⚠️  [RESTORE] Nuke not available")
        return 0
    except Exception as e:
        print(f"❌ [RESTORE] Error restoring instances: {e}")
        import traceback
        traceback.print_exc()
        return 0


def create_multishot_read(variable_manager=None):
    """
    Create a new MultishotRead node.

    This function is called from Nuke's menu system or from the browser.

    Args:
        variable_manager: Optional VariableManager instance to share state with browser

    Returns:
        Created Nuke node or None if failed
    """
    try:
        multishot_read = MultishotRead(variable_manager=variable_manager)
        node = multishot_read.create_node()
        return node

    except Exception as e:
        import nuke
        nuke.message(f"Error creating MultishotRead node: {e}")
        return None
