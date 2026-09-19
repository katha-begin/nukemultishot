"""
Tests for bypassing OFX nodes the render farm does not have.

Run from the repo root:
    python -m unittest tests.ofx_bypass_test
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from multishot.deadline.ofx_bypass import (
    bypass_ofx_in_script_text,
    script_needs_bypass,
)

SCRIPT = """Root {
 name X:/EGA/shot.nk
}
Grade {
 name Grade1
}
OFXcom.revisionfx.RSMB_v3 {
 inputs 2
 motionVectors 1
 name RSMB1
 xpos 100
}
Merge2 {
 name Merge1
}
"""


class TestNeedsBypass(unittest.TestCase):
    def test_detects_rsmb(self):
        self.assertTrue(script_needs_bypass(SCRIPT))

    def test_lowercase_variant(self):
        self.assertTrue(script_needs_bypass("OFXcom.revisionfx.rsmb_v3 {\n name a\n}\n"))

    def test_script_without_rsmb(self):
        self.assertFalse(script_needs_bypass("Grade {\n name Grade1\n}\n"))

    def test_sapphire_is_left_alone(self):
        # Deliberate: Sapphire has only ever warned on the farm, never errored.
        text = "OFXcom.genarts.sapphire.stylize.s_vignette_v1 {\n name V1\n}\n"
        self.assertFalse(script_needs_bypass(text))
        self.assertEqual(bypass_ofx_in_script_text(text)[1], [])


class TestBypass(unittest.TestCase):
    def test_disable_is_inserted(self):
        new_text, bypassed = bypass_ofx_in_script_text(SCRIPT)
        self.assertEqual(bypassed, ["RSMB1"])
        block = new_text.split("OFXcom.revisionfx.RSMB_v3 {")[1].split("}")[0]
        self.assertIn("disable true", block)

    def test_other_nodes_untouched(self):
        new_text, _ = bypass_ofx_in_script_text(SCRIPT)
        self.assertIn("Grade {\n name Grade1\n}", new_text)
        self.assertIn("Merge2 {\n name Merge1\n}", new_text)
        self.assertEqual(new_text.count("disable true"), 1)

    def test_node_knobs_are_preserved(self):
        new_text, _ = bypass_ofx_in_script_text(SCRIPT)
        for knob in ("inputs 2", "motionVectors 1", "name RSMB1", "xpos 100"):
            self.assertIn(knob, new_text)

    def test_existing_disable_is_not_duplicated(self):
        text = "OFXcom.revisionfx.RSMB_v3 {\n disable false\n name RSMB1\n}\n"
        new_text, _ = bypass_ofx_in_script_text(text)
        self.assertEqual(new_text.count("disable"), 1)
        self.assertIn("disable true", new_text)

    def test_multiple_nodes(self):
        text = SCRIPT + "OFXcom.revisionfx.RSMB_v3 {\n name RSMB2\n}\n"
        new_text, bypassed = bypass_ofx_in_script_text(text)
        self.assertEqual(bypassed, ["RSMB1", "RSMB2"])
        self.assertEqual(new_text.count("disable true"), 2)

    def test_node_inside_a_group_is_handled(self):
        text = (
            "Group {\n name Group1\n}\n"
            "Group {\n"
            " name Group2\n"
            " OFXcom.revisionfx.RSMB_v3 {\n"
            "  name RSMB_inner\n"
            " }\n"
            "}\n"
        )
        new_text, bypassed = bypass_ofx_in_script_text(text)
        self.assertEqual(bypassed, ["RSMB_inner"])
        self.assertIn("disable true", new_text)
        self.assertIn("name RSMB_inner", new_text)

    def test_trailing_newline_preserved(self):
        self.assertTrue(bypass_ofx_in_script_text(SCRIPT)[0].endswith("\n"))

    def test_script_without_rsmb_is_unchanged(self):
        text = "Grade {\n name Grade1\n}\n"
        new_text, bypassed = bypass_ofx_in_script_text(text)
        self.assertEqual(new_text, text)
        self.assertEqual(bypassed, [])


if __name__ == "__main__":
    unittest.main()
