"""
Tests for Windows <-> Linux path translation.

Run from the repo root:
    python -m unittest tests.pathmap_test
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import multishot.core.pathmap as pathmap
from multishot.core.pathmap import (
    DEFAULT_DRIVE_MAP as DRIVE_MAP,
    to_linux,
    to_windows,
    unmapped_drive,
)

# Pin the rules to the built-in table so the suite does not depend on whether a
# Deadline client is installed on the machine running it.
pathmap._cached_rules = sorted(
    [(d, m) for d, m in DRIVE_MAP.items()], key=lambda r: len(r[0]), reverse=True)
pathmap._cached_source = "built-in fallback table (pinned for tests)"
from multishot.deadline.farm_script import FarmScriptManager, _join_under_root


class TestToLinux(unittest.TestCase):
    def test_every_mapped_drive(self):
        for drive, mount in DRIVE_MAP.items():
            self.assertEqual(to_linux(drive + "/EGA/shot.exr"), mount + "/EGA/shot.exr")

    def test_lowercase_drive_letters(self):
        # farm_script.py used to list uppercase drives only, so "v:/..." was
        # handed to the farm unconverted.
        self.assertEqual(to_linux("v:/SWA/a.exr"), "/mnt/igloo_swa_v/SWA/a.exr")
        self.assertEqual(to_linux("y:/EGA/a.exr"), "/mnt/igloo_ega_y/EGA/a.exr")

    def test_backslashes(self):
        self.assertEqual(to_linux("V:\\SWA\\a.exr"), "/mnt/igloo_swa_v/SWA/a.exr")
        self.assertEqual(to_linux("x:\\EGA\\a.abc"), "/mnt/igloo_ega_x/EGA/a.abc")

    def test_drive_relative_path_is_made_absolute(self):
        # "V:SWA" means "SWA under the current directory on V:" - never what the
        # pipeline intends.
        self.assertEqual(to_linux("V:SWA/a.exr"), "/mnt/igloo_swa_v/SWA/a.exr")

    def test_already_linux_is_untouched(self):
        self.assertEqual(to_linux("/mnt/igloo_swa_v/SWA/a.exr"), "/mnt/igloo_swa_v/SWA/a.exr")

    def test_unmapped_drive_is_untouched(self):
        self.assertEqual(to_linux("Z:/other/a.exr"), "Z:/other/a.exr")

    def test_empty_and_none(self):
        self.assertEqual(to_linux(""), "")
        self.assertIsNone(to_linux(None))


class TestToWindows(unittest.TestCase):
    def test_round_trip(self):
        for drive, mount in DRIVE_MAP.items():
            original = drive + "/EGA/all/scene/shot.exr"
            self.assertEqual(to_windows(to_linux(original)), original)

    def test_mount_root(self):
        self.assertEqual(to_windows("/mnt/igloo_ega_x"), "X:/")

    def test_prefix_is_not_partially_matched(self):
        self.assertEqual(to_windows("/mnt/igloo_swa_v_backup/a.exr"), "/mnt/igloo_swa_v_backup/a.exr")


class TestUnmappedDrive(unittest.TestCase):
    def test_reports_unknown_drive(self):
        self.assertEqual(unmapped_drive("Z:/other/a.exr"), "Z")

    def test_mapped_drive_returns_none(self):
        self.assertIsNone(unmapped_drive("V:/SWA/a.exr"))
        self.assertIsNone(unmapped_drive("v:/SWA/a.exr"))

    def test_linux_path_returns_none(self):
        self.assertIsNone(unmapped_drive("/mnt/igloo_swa_v/a.exr"))


class TestFarmScriptPaths(unittest.TestCase):
    """Farm dir must be absolute, not drive-relative."""

    def setUp(self):
        self.shot = {
            "PROJ_ROOT": "V:/",
            "project": "SWA",
            "ep": "Ep02",
            "seq": "sq0010",
            "shot": "SH0010",
        }

    def test_farm_directory_is_absolute(self):
        farm_dir = FarmScriptManager().get_farm_directory(self.shot)
        # The bug produced "V:SWA/all/..." which resolves against the current
        # directory on V:, silently writing the farm script somewhere else.
        self.assertEqual(
            farm_dir,
            "V:/SWA/all/scene/Ep02/sq0010/SH0010/comp/farm",
        )
        self.assertNotIn("V:SWA", farm_dir)

    def test_farm_directory_on_linux_root(self):
        shot = dict(self.shot, PROJ_ROOT="/mnt/igloo_swa_v/")
        self.assertEqual(
            FarmScriptManager().get_farm_directory(shot),
            "/mnt/igloo_swa_v/SWA/all/scene/Ep02/sq0010/SH0010/comp/farm",
        )

    def test_join_under_root_keeps_forward_slashes(self):
        self.assertEqual(_join_under_root("X:\\", "EGA", "all"), "X:/EGA/all")

    def test_convert_uses_shared_table(self):
        manager = FarmScriptManager()
        self.assertEqual(
            manager._convert_windows_to_linux_path("v:/SWA/a.exr"),
            "/mnt/igloo_swa_v/SWA/a.exr",
        )
        self.assertEqual(
            manager._convert_windows_to_linux_path("Y:\\EGA\\all"),
            "/mnt/igloo_ega_y/EGA/all",
        )


if __name__ == "__main__":
    unittest.main()
