"""
Tests for projects on their own drives (EGA on X:/ and Y:/).

Run from the repo root:
    python -m unittest tests.ega_project_roots_test
"""

import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from multishot.core.scanner import DirectoryScanner
from multishot.deadline import nuke_wrapper
from multishot.deadline.farm_script import FarmScriptManager

SHOT = ("Ep02", "sq0380", "SH3310")


class TestScannerProjectImgRoot(unittest.TestCase):
    """Browser Renders tab: renders are scanned under the project's IMG_ROOT."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.roots = {name: os.path.join(self.tmp, name).replace("\\", "/") + "/" for name in "VWXY"}

        self.scanner = DirectoryScanner()
        self.scanner.config_manager.set("roots", {"PROJ_ROOT": self.roots["V"], "IMG_ROOT": self.roots["W"]})
        self.scanner.config_manager.set("projects", {
            "SWA": {"PROJ_ROOT": self.roots["V"], "IMG_ROOT": self.roots["W"]},
            "EGA": {"PROJ_ROOT": self.roots["X"], "IMG_ROOT": self.roots["Y"]},
        })

        # EGA shot: department folder on PROJ_ROOT (X), renders on IMG_ROOT (Y)
        shot_dir = os.path.join("EGA", "all", "scene", *SHOT)
        os.makedirs(os.path.join(self.roots["X"], shot_dir, "lighting", "version"))
        layer_dir = os.path.join(self.roots["Y"], shot_dir, "lighting", "publish", "v006", "BG")
        comp_dir = os.path.join(self.roots["Y"], shot_dir, "comp", "version", "v006")
        os.makedirs(layer_dir)
        os.makedirs(comp_dir)
        for frame in (1001, 1002):
            open(os.path.join(layer_dir, f"BG.{frame}.exr"), "w").close()
            open(os.path.join(comp_dir, f"comp.{frame}.exr"), "w").close()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_department_renders_found_under_project_img_root(self):
        assets = self.scanner.scan_all_department_assets(self.roots["X"], "EGA", *SHOT)
        self.assertEqual(assets.get("lighting", {}).get("renders"), ["v006/BG/BG.1001-1002.exr"])

    def test_comp_renders_found_under_project_img_root(self):
        renders = self.scanner.scan_comp_renders(self.roots["X"], "EGA", *SHOT)
        self.assertEqual(renders, ["v006/comp.1001-1002.exr"])


class TestEgaLinuxPathMapping(unittest.TestCase):
    """Deadline: EGA drives X:/ and Y:/ convert to their Linux mounts."""

    def test_farm_script_converts_ega_drives(self):
        manager = FarmScriptManager()
        self.assertEqual(manager._convert_windows_to_linux_path("X:/EGA/all/scene"), "/mnt/igloo_ega_x/EGA/all/scene")
        self.assertEqual(manager._convert_windows_to_linux_path("Y:\\EGA\\all\\scene"), "/mnt/igloo_ega_y/EGA/all/scene")

    def test_nuke_wrapper_converts_ega_roots_in_script(self):
        tmp = tempfile.mkdtemp()
        try:
            script_path = os.path.join(tmp, "shot.nk")
            with open(script_path, "w") as f:
                f.write('Root {\n multishot_custom {"PROJ_ROOT":"X:/","IMG_ROOT":"Y:/"}\n PROJ_ROOT X:/\n IMG_ROOT Y:/\n}\n')

            self.assertTrue(nuke_wrapper.fix_multishot_paths_in_script(script_path))

            with open(script_path) as f:
                content = f.read()
            self.assertIn('{"PROJ_ROOT":"/mnt/igloo_ega_x/","IMG_ROOT":"/mnt/igloo_ega_y/"}', content)
            self.assertIn("PROJ_ROOT /mnt/igloo_ega_x/", content)
            self.assertIn("IMG_ROOT /mnt/igloo_ega_y/", content)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
