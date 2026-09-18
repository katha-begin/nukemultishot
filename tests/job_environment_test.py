"""
Tests for the Deadline job info environment block.

Run from the repo root:
    python -m unittest tests.job_environment_test
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from multishot.deadline.submit import merge_job_environment

# What the studio submitter writes onto every Nuke job.
STUDIO_JOB_INFO = "\n".join([
    "Plugin=Nuke",
    "Name=Ep02_sq0323_SH3180_comp_comp_v002.nk",
    "EnvironmentKeyValue0=OCIO=/mnt/ppr_dev_t/pipeline/ocio/aces_2.0/studio-config.ocio",
    "EnvironmentKeyValue1=NUKE_DISABLE_GPU_ACCELERATION=1",
    "EnvironmentKeyValue2=DISPLAY=",
    "EnvironmentKeyValue3=QT_QPA_PLATFORM=offscreen",
    "EnvironmentKeyValue4=LIBGL_ALWAYS_SOFTWARE=1",
    "Frames=1001",
])


def as_dict(env_lines):
    out = {}
    for line in env_lines:
        if not line.startswith("EnvironmentKeyValue"):
            continue
        _, _, assignment = line.partition("=")
        key, _, value = assignment.partition("=")
        out[key] = value
    return out


def indices(env_lines):
    return [int(line[len("EnvironmentKeyValue"):line.index("=")])
            for line in env_lines if line.startswith("EnvironmentKeyValue")]


class TestMergeJobEnvironment(unittest.TestCase):
    def test_existing_entries_are_preserved(self):
        _, env_lines = merge_job_environment(STUDIO_JOB_INFO, {"NUKE_PATH": "/mnt/ppr_dev_t/ms"})
        merged = as_dict(env_lines)
        # The old code restarted at 0 and overwrote these, silently losing them.
        self.assertEqual(merged["NUKE_DISABLE_GPU_ACCELERATION"], "1")
        self.assertEqual(merged["QT_QPA_PLATFORM"], "offscreen")
        self.assertEqual(merged["LIBGL_ALWAYS_SOFTWARE"], "1")
        self.assertEqual(merged["NUKE_PATH"], "/mnt/ppr_dev_t/ms")

    def test_indices_are_contiguous_from_zero(self):
        # Deadline stops reading at the first missing index, so a gap discards
        # every remaining variable.
        _, env_lines = merge_job_environment(STUDIO_JOB_INFO, {"NUKE_PATH": "/x"})
        self.assertEqual(indices(env_lines), list(range(len(indices(env_lines)))))

    def test_dropping_ocio_keeps_indices_contiguous(self):
        _, env_lines = merge_job_environment(
            STUDIO_JOB_INFO, {"NUKE_PATH": "/x"}, drop_keys=["OCIO"])
        self.assertNotIn("OCIO", as_dict(env_lines))
        self.assertEqual(indices(env_lines), list(range(len(indices(env_lines)))))

    def test_ocio_kept_when_not_dropped(self):
        _, env_lines = merge_job_environment(STUDIO_JOB_INFO, {})
        self.assertIn("OCIO", as_dict(env_lines))

    def test_our_values_win_over_existing(self):
        _, env_lines = merge_job_environment(
            STUDIO_JOB_INFO, {"OCIO": "/mnt/ppr_dev_t/custom.ocio"})
        self.assertEqual(as_dict(env_lines)["OCIO"], "/mnt/ppr_dev_t/custom.ocio")

    def test_non_environment_lines_are_kept(self):
        kept_lines, env_lines = merge_job_environment(STUDIO_JOB_INFO, {})
        self.assertIn("Plugin=Nuke", kept_lines)
        self.assertIn("Frames=1001", kept_lines)
        for line in kept_lines:
            self.assertFalse(line.startswith("EnvironmentKeyValue"))

    def test_use_job_environment_only_written_once(self):
        content = STUDIO_JOB_INFO + "\nUseJobEnvironmentOnly=false"
        kept_lines, env_lines = merge_job_environment(content, {})
        combined = kept_lines + env_lines
        self.assertEqual(
            sum(1 for line in combined if line.lower().startswith("usejobenvironmentonly")), 1)

    def test_empty_job_info(self):
        kept_lines, env_lines = merge_job_environment("", {"NUKE_PATH": "/x"})
        self.assertEqual(as_dict(env_lines), {"NUKE_PATH": "/x"})
        self.assertEqual(indices(env_lines), [0])


if __name__ == "__main__":
    unittest.main()
