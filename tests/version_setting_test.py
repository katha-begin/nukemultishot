"""
Tests for MultishotRead version setting and ep/seq/shot names with variance letters.

Run from the repo root:
    python -m unittest tests.version_setting_test
"""

import contextlib
import io
import json
import os
import shutil
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from multishot.core.context import ContextDetector
from multishot.core.scanner import DirectoryScanner
from multishot.nodes import read_node

SHOT_KEY = "EGA_Ep02_sq0380_SH3370"


class FakeKnob:
    def __init__(self, value=""):
        self._value = value

    def value(self):
        return self._value

    def setValue(self, value):
        self._value = value


class FakeNode:
    """Stands in for a MultishotRead nuke.Node (knob access only)."""

    def __init__(self, name, attached=True, **knobs):
        self._name = name
        self.attached = attached
        self._knobs = {key: FakeKnob(value) for key, value in knobs.items()}

    def name(self):
        if not self.attached:
            raise ValueError("A PythonObject is not attached to a node")
        return self._name

    def knob(self, name):
        return self._knobs.get(name)

    def __getitem__(self, name):
        return self._knobs[name]


def make_read(name="MultishotRead_lighting_MASTER_CHAR_A_CRYPTO", shot_versions=None, shot_version="v001",
              file_pattern="MASTER_CHAR_A/MASTER_CHAR_A_CRYPTO.%04d.exr", file_ref_name=None):
    file_path = (f"[value root.IMG_ROOT][value root.project]/all/scene/[value root.ep]/[value root.seq]/"
                 f"[value root.shot]/lighting/publish/[value parent.{file_ref_name or name}.shot_version]/{file_pattern}")
    return FakeNode(name, multishot_sep="Multishot Settings", department="lighting", layer="MASTER_CHAR_A",
                    file_pattern=file_pattern, shot_version=shot_version,
                    shot_versions=json.dumps(shot_versions or {}), file=file_path)


class TestShotVersionKnobs(unittest.TestCase):
    """Versions are read and stored on the node's own knobs, not through _node_instances."""

    def test_set_stores_version_and_switches_current_shot(self):
        node = make_read()
        read_node.set_shot_version(node, "v002", SHOT_KEY, SHOT_KEY)
        self.assertEqual(read_node.get_shot_version(node, SHOT_KEY), "v002")
        self.assertEqual(node["shot_version"].value(), "v002")

    def test_set_for_other_shot_keeps_active_version(self):
        node = make_read()
        read_node.set_shot_version(node, "v002", "EGA_Ep02_sq0380_SH3380", SHOT_KEY)
        self.assertEqual(read_node.get_shot_version(node, "EGA_Ep02_sq0380_SH3380"), "v002")
        self.assertEqual(node["shot_version"].value(), "v001")

    def test_shot_without_stored_version_returns_none(self):
        self.assertIsNone(read_node.get_shot_version(make_read(), SHOT_KEY))

    def test_copied_read_uses_its_own_version_knob(self):
        # Copy/paste renames the node but the file path still reads the original node's version
        node = make_read(name="MultishotRead_lighting_MASTER_CHAR_A_CRYPTO1",
                         file_ref_name="MultishotRead_lighting_MASTER_CHAR_A_CRYPTO")
        read_node.apply_shot_version(node, "v002")
        self.assertIn("[value parent.MultishotRead_lighting_MASTER_CHAR_A_CRYPTO1.shot_version]", node["file"].value())
        self.assertNotIn("[value parent.MultishotRead_lighting_MASTER_CHAR_A_CRYPTO.shot_version]", node["file"].value())


class TestLayerVersions(unittest.TestCase):
    """Default version is the latest one on disk that contains the node's image."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.publish = os.path.join(self.tmp, "publish")
        files = [
            "v001/MASTER_CHAR_A/MASTER_CHAR_A.1091.exr",
            "v002/MASTER_CHAR_A/MASTER_CHAR_A.1001.exr",
            "v002/MASTER_CHAR_A/MASTER_CHAR_A_CRYPTO.1001.exr",
            "v002/MASTER_BG_A/MASTER_BG_A.1001.exr",
            "v002_001/MASTER_CHAR_A/MASTER_CHAR_A.1001.exr",
            "v010/MASTER_CHAR_A/MASTER_CHAR_A.1001.exr",
        ]
        for path in files:
            full_path = os.path.join(self.publish, path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            open(full_path, "w").close()
        os.makedirs(os.path.join(self.publish, "v001", "MASTER_BG_A"))  # empty layer, as on the server

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_lists_versions_containing_image_in_order(self):
        self.assertEqual(read_node.find_layer_versions(self.publish, "MASTER_CHAR_A/MASTER_CHAR_A.%04d.exr"),
                         ["v001", "v002", "v002_001", "v010"])
        self.assertEqual(read_node.find_layer_versions(self.publish, "MASTER_CHAR_A/MASTER_CHAR_A_CRYPTO.%04d.exr"),
                         ["v002"])
        self.assertEqual(read_node.find_layer_versions(self.publish, "MASTER_BG_A/MASTER_BG_A.%04d.exr"), ["v002"])

    def test_unset_shot_resolves_to_latest_version_of_image(self):
        self.assertEqual(read_node.resolve_shot_version(make_read(), SHOT_KEY, self.publish), "v002")
        beauty = make_read(name="MultishotRead_lighting_MASTER_CHAR_A", file_pattern="MASTER_CHAR_A/MASTER_CHAR_A.%04d.exr")
        self.assertEqual(read_node.resolve_shot_version(beauty, SHOT_KEY, self.publish), "v010")

    def test_stored_version_wins_over_latest(self):
        node = make_read(shot_versions={SHOT_KEY: "v001"})
        self.assertEqual(read_node.resolve_shot_version(node, SHOT_KEY, self.publish), "v001")

    def test_no_renders_falls_back_to_v001(self):
        missing = os.path.join(self.tmp, "missing", "publish")
        self.assertEqual(read_node.resolve_shot_version(make_read(), SHOT_KEY, missing), "v001")


class TestRestoreInstances(unittest.TestCase):
    """Reloading the script (Render button) or cut/paste leaves dead node objects in _node_instances."""

    def test_restore_replaces_dead_instance(self):
        live = make_read(name="MultishotRead_lighting_MASTER_CHAR_A")
        stale = mock.Mock()
        stale.node = FakeNode("MultishotRead_lighting_MASTER_CHAR_A", attached=False)
        fake_nuke = mock.Mock()
        fake_nuke.allNodes.return_value = [live]

        class FakeRead:
            def __init__(self, variable_manager=None):
                self.node = None

        # restore prints emoji progress lines, which a Windows console encoding can't show
        with mock.patch.dict(sys.modules, {"nuke": fake_nuke}), \
                mock.patch.object(read_node, "MultishotRead", FakeRead), \
                mock.patch.dict(read_node._node_instances, {live.name(): stale}, clear=True), \
                contextlib.redirect_stdout(io.StringIO()):
            read_node.restore_multishot_instances()
            self.assertIs(read_node._node_instances[live.name()].node, live)


try:
    from multishot.ui.multishot_manager import MultishotManagerDialog
except Exception:  # Qt not installed
    MultishotManagerDialog = None


@unittest.skipUnless(MultishotManagerDialog, "Qt (PySide2/PySide6) not available")
class TestManagerVersions(unittest.TestCase):
    """Set Shot / Update All in Multishot Manager, run against fake nodes and a temp render tree."""

    SH3370 = {"project": "EGA", "ep": "Ep02", "seq": "sq0380", "shot": "SH3370"}
    SH3380 = {"project": "EGA", "ep": "Ep02", "seq": "sq0380", "shot": "SH3380"}

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.img_root = self.tmp.replace("\\", "/") + "/"
        renders = {
            "SH3370": ["v001/MASTER_CHAR_A/MASTER_CHAR_A.1091.exr",
                       "v002/MASTER_CHAR_A/MASTER_CHAR_A.1001.exr", "v002/MASTER_CHAR_A/MASTER_CHAR_A_CRYPTO.1001.exr"],
            "SH3380": ["v003/MASTER_CHAR_A/MASTER_CHAR_A.1001.exr", "v003/MASTER_CHAR_A/MASTER_CHAR_A_CRYPTO.1001.exr"],
        }
        for shot, files in renders.items():
            for path in files:
                full_path = os.path.join(self.tmp, "EGA", "all", "scene", "Ep02", "sq0380", shot, "lighting", "publish", path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                open(full_path, "w").close()

        self.beauty = make_read(name="MultishotRead_lighting_MASTER_CHAR_A", file_pattern="MASTER_CHAR_A/MASTER_CHAR_A.%04d.exr")
        self.crypto = make_read()
        fake_nuke = mock.Mock()
        fake_nuke.allNodes.return_value = [self.beauty, self.crypto]

        img_root = self.img_root

        class ManagerStub:
            _is_multishot_read_node = MultishotManagerDialog._is_multishot_read_node
            _find_shot_data = MultishotManagerDialog._find_shot_data
            _get_node_publish_dir = MultishotManagerDialog._get_node_publish_dir
            _save_current_shot_versions = MultishotManagerDialog._save_current_shot_versions
            _update_nodes_for_shot = MultishotManagerDialog._update_nodes_for_shot
            _update_all_to_latest = MultishotManagerDialog._update_all_to_latest

            def __init__(self):
                self.logger = mock.Mock()
                self.shots_data = [TestManagerVersions.SH3370, TestManagerVersions.SH3380]
                self.current_shot_key = None

            def _get_shot_roots(self, shot_data):
                return {"PROJ_ROOT": "", "IMG_ROOT": img_root}

        self.manager = ManagerStub()
        self.patches = [mock.patch.dict(sys.modules, {"nuke": fake_nuke}), contextlib.redirect_stdout(io.StringIO())]
        for patch in self.patches:
            patch.__enter__()

    def tearDown(self):
        for patch in reversed(self.patches):
            patch.__exit__(None, None, None)
        shutil.rmtree(self.tmp, ignore_errors=True)

    def set_shot(self, shot_data):
        """The version steps of _set_shot: save the shot being left, then switch nodes."""
        self.manager._save_current_shot_versions()
        self.manager._update_nodes_for_shot(shot_data)
        self.manager.current_shot_key = "EGA_Ep02_sq0380_" + shot_data["shot"]

    def test_unset_shots_follow_latest_render_without_being_stored(self):
        self.set_shot(self.SH3370)
        self.assertEqual((self.beauty["shot_version"].value(), self.crypto["shot_version"].value()), ("v002", "v002"))

        self.set_shot(self.SH3380)
        self.assertEqual(self.crypto["shot_version"].value(), "v003")
        self.assertIsNone(read_node.get_shot_version(self.crypto, "EGA_Ep02_sq0380_SH3370"))

    def test_chosen_version_survives_switching_with_dead_registry_entry(self):
        dead = mock.Mock()
        dead.node = FakeNode(self.beauty.name(), attached=False)
        with mock.patch.dict(read_node._node_instances, {self.beauty.name(): dead}, clear=True):
            self.set_shot(self.SH3370)
            # Set Versions dialog Apply for SH3370
            read_node.set_shot_version(self.beauty, "v001", "EGA_Ep02_sq0380_SH3370", "EGA_Ep02_sq0380_SH3370")

            self.set_shot(self.SH3380)
            self.assertEqual(self.beauty["shot_version"].value(), "v003")

            self.set_shot(self.SH3370)
            self.assertEqual(self.beauty["shot_version"].value(), "v001")

    def test_manual_knob_change_is_stored_when_leaving_shot(self):
        self.set_shot(self.SH3370)
        self.beauty["shot_version"].setValue("v001")
        self.set_shot(self.SH3380)
        self.assertEqual(read_node.get_shot_version(self.beauty, "EGA_Ep02_sq0380_SH3370"), "v001")

    def test_update_all_to_latest_stores_latest_for_every_shot(self):
        self.set_shot(self.SH3370)
        from multishot.ui.multishot_manager import QtWidgets
        message_box = QtWidgets.QMessageBox
        with mock.patch.object(message_box, "question", return_value=message_box.Yes), \
                mock.patch.object(message_box, "information"), \
                mock.patch.object(message_box, "critical") as critical:
            self.manager._update_all_to_latest()
        critical.assert_not_called()

        self.assertEqual(read_node.get_shot_version(self.crypto, "EGA_Ep02_sq0380_SH3370"), "v002")
        self.assertEqual(read_node.get_shot_version(self.crypto, "EGA_Ep02_sq0380_SH3380"), "v003")
        self.assertEqual(self.crypto["shot_version"].value(), "v002")


class TestVarianceNames(unittest.TestCase):
    """Episode, sequence and shot names can end with a variance letter (Ep01A, sq0010A, SH0020A)."""

    def setUp(self):
        self.detector = ContextDetector()

    def test_filename_with_variance_letters(self):
        context = self.detector.detect_from_filename("Ep01A_sq0010A_SH0020A_comp_v001.nk")
        self.assertEqual((context["ep"], context["seq"], context["shot"]), ("Ep01A", "sq0010A", "SH0020A"))

    def test_path_with_variance_letters(self):
        context = self.detector.detect_from_path("Y:/EGA/all/scene/Ep01A/seq01A/SH0020A/lighting/publish/v002/")
        self.assertEqual((context["project"], context["ep"], context["seq"], context["shot"]),
                         ("EGA", "Ep01A", "seq01A", "SH0020A"))

    def test_validate_accepts_variance_letters(self):
        self.assertEqual(self.detector.validate_context({"ep": "Ep01A", "seq": "sq0010A", "shot": "SH0020A"}), (True, []))

    def test_scanner_lists_variance_folders(self):
        tmp = tempfile.mkdtemp()
        try:
            root = tmp.replace("\\", "/") + "/"
            scene = os.path.join(tmp, "EGA", "all", "scene")
            for path in ["Ep01/sq0010/SH0020", "Ep01A/sq0010/SH0020", "Ep01A/sq0010A/SH0020", "Ep01A/sq0010A/SH0020A",
                         "Ep01A/sq0010A/SH0020_old", "Ep01A/seq01A/SH0030", "notes"]:
                os.makedirs(os.path.join(scene, path))

            scanner = DirectoryScanner()
            self.assertEqual(scanner.scan_episodes(root, "EGA"), ["Ep01", "Ep01A"])
            self.assertEqual(scanner.scan_sequences(root, "EGA", "Ep01A"), ["seq01A", "sq0010", "sq0010A"])
            self.assertEqual(scanner.scan_shots(root, "EGA", "Ep01A", "sq0010A"), ["SH0020", "SH0020A"])
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
