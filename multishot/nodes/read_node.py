"""
Custom Read node for the Multishot Workflow System.

Provides variable-driven file paths with version selection and approval status.
"""

import os
import re
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
        Get version for a specific shot.

        Args:
            shot_key: Shot key string. If None, uses current shot from root knobs.

        Returns:
            Version string (e.g., "v001")
        """
        try:
            import json

            # Get current shot key if not provided
            if shot_key is None:
                shot_key = self.get_shot_key()

            print(f"\n🔍 [GET_VERSION] Node: {self.node.name()}, Shot: {shot_key}")

            # Read shot_versions knob
            shot_versions_str = self.node['shot_versions'].value() if self.node.knob('shot_versions') else '{}'
            shot_versions = json.loads(shot_versions_str) if shot_versions_str else {}
            print(f"   📊 [GET_VERSION] shot_versions knob: {shot_versions}")

            # Get version for this shot (default to v001)
            version = shot_versions.get(shot_key, 'v001')
            print(f"   🎯 [GET_VERSION] Returning version: {version}")

            return version

        except Exception as e:
            self.logger.error(f"Error getting version for shot: {e}")
            print(f"   ❌ [GET_VERSION] Error: {e}")
            return 'v001'

    def set_version_for_shot(self, version, shot_key=None):
        """
        Set version for a specific shot.

        Args:
            version: Version string (e.g., "v001")
            shot_key: Shot key string. If None, uses current shot from root knobs.
        """
        try:
            import json

            # Get current shot key if not provided
            if shot_key is None:
                shot_key = self.get_shot_key()

            # Get the ACTUAL current shot from root knobs
            current_shot_key = self.get_shot_key()

            print(f"\n💾 [SET_VERSION] Node: {self.node.name()}")
            print(f"   🎯 [SET_VERSION] Setting version for shot: {shot_key}")
            print(f"   📍 [SET_VERSION] Current shot in script: {current_shot_key}")
            print(f"   📦 [SET_VERSION] Version: {version}")

            # Read current shot_versions
            shot_versions_str = self.node['shot_versions'].value() if self.node.knob('shot_versions') else '{}'
            shot_versions = json.loads(shot_versions_str) if shot_versions_str else {}
            print(f"   📊 [SET_VERSION] Current shot_versions: {shot_versions}")

            # Update version for this shot
            shot_versions[shot_key] = version
            print(f"   ✏️  [SET_VERSION] Updated shot_versions: {shot_versions}")

            # Write back to knob
            self.node['shot_versions'].setValue(json.dumps(shot_versions))
            print(f"   ✅ [SET_VERSION] Saved to shot_versions knob")

            # ✅ ONLY update shot_version knob if we're setting version for the CURRENT shot
            if shot_key == current_shot_key:
                self.node['shot_version'].setValue(version)
                print(f"   ✅ [SET_VERSION] Updated shot_version knob to: {version} (current shot)")

                # Rebuild path
                self.build_expression_path()
                print(f"   ✅ [SET_VERSION] Rebuilt expression path")
            else:
                print(f"   ⏭️  [SET_VERSION] NOT updating shot_version knob (setting for different shot)")
                print(f"   ℹ️  [SET_VERSION] shot_version knob will update when switching to {shot_key}")

            self.logger.info(f"Set version for shot {shot_key}: {version}")

        except Exception as e:
            self.logger.error(f"Error setting version for shot: {e}")
            print(f"   ❌ [SET_VERSION] Error: {e}")




# Global node instances storage
_node_instances = {}


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

                # Check if instance already exists
                if node_name in _node_instances:
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
