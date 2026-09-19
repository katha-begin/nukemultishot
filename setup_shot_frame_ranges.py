#!/usr/bin/env python
"""
Write per-shot frame-range JSON files from a shot/duration list.

The Multishot Manager reads a shot's frame range from

    {PROJ_ROOT}/{project}/all/scene/{ep}/{seq}/{shot}/.{ep}_{seq}_{shot}.json

and falls back to 1001-1100 when that file is missing (which is why shots show
yellow in the Manager). This writes those files.

Only the shot name and its duration are known here, not which sequence a shot
belongs to, so each shot's directory is located by scanning the scene tree.
Shots that cannot be found, or that appear under more than one sequence, are
reported rather than guessed at.

Dry run (default - shows what it would do, writes nothing):

    python setup_shot_frame_ranges.py --proj-root X:/ --project EGA --ep Ep02

Apply:

    python setup_shot_frame_ranges.py --proj-root X:/ --project EGA --ep Ep02 --write

Existing files are left alone unless --overwrite is given.
"""

import argparse
import json
import os
import sys

# Frames start at 1001; a duration of N means 1001 .. 1001 + N - 1.
START_FRAME = 1001

# shot  duration
SHOT_DURATIONS_TEXT = """
SH1340 40
SH2020 96
SH2030 140
SH2040 24
SH2050 29
SH2060 72
SH2070 178
SH2080 141
SH2090 73
SH2100 166
SH2110 103
SH2120 39
SH2130 87
SH2140 89
SH2150 162
SH2160 103
SH2170 44
SH2180 85
SH2190 50
SH2200 34
SH2210 80
SH2220 72
SH2230 59
SH2240 70
SH2250 132
SH2260 139
SH2630 27
SH2640 33
SH2650 41
SH2660 100
SH2670 150
SH2680 91
SH2690 72
SH2700 58
SH2710 75
SH2720 68
SH2730 24
SH2740 50
SH2750 119
SH2760 51
SH2770 69
SH2780 27
SH2790 56
SH2800 81
SH2810 21
SH2820 47
SH2830 104
SH2840 70
SH2850 100
SH2860 151
SH2870 34
SH2880 56
SH2890 152
SH2900 90
SH2910 39
SH2920 23
SH2930 52
SH2940 51
SH2950 111
SH2960 91
SH2970 108
SH2980 50
SH2990 157
SH3000 53
SH3010 50
SH3020 89
SH3030 26
SH3040 66
SH3050 35
SH3060 69
SH3070 28
SH3080 32
SH3090 130
SH3100 20
SH3110 85
SH3120 52
SH3130 56
SH3140 52
SH3150 45
SH3160 24
SH3170 80
SH3180 52
SH3190 104
SH3200 72
SH3210 130
SH3220 33
SH3230 66
SH3240 104
SH3250 35
SH3260 69
SH3270 65
SH3270A 65
SH3280 92
SH3290 127
SH3300 144
SH3310 73
SH3320 30
SH3330 23
SH3340 24
SH3350 40
SH3360 98
SH3370 123
SH3380 59
SH3390 72
SH3400 23
SH3410 142
SH3420 60
SH3430 72
SH3440 19
SH3450 90
SH3460 103
SH3470 41
SH3480 123
SH3490 128
SH3500 28
SH3510 46
SH3520 96
SH3540 40
SH3550 42
SH3560 98
SH3570 150
SH3580 42
SH3590 83
SH3600 23
SH3610 44
SH3620 242
SH3630 123
SH3640 131
SH3650 24
SH3660 21
SH3670 50
SH3680 22
SH3690 54
SH3700 16
SH3710 20
SH3720 61
SH3730 100
SH3740 97
SH3750 151
SH3760 48
SH3770 56
SH3780 58
SH3790 149
SH3800 29
SH3810 100
SH3820 36
SH3825 26
SH3830 55
SH4080 24
SH4090 37
SH4100 32
SH4110 41
SH4120 24
SH4130 56
SH4230 33
SH4240 52
SH4250 104
SH4260 36
SH4270 31
SH4280 87
SH4290 24
SH4300 26
SH4310 174
SH4320 77
SH4330 112
SH4340 135
SH4350 184
SH4360 190
SH4370 52
SH4380 82
SH4390 247
SH4400 65
SH4410 68
SH4420 77
SH4430 38
SH4440 113
SH4450 67
SH4460 53
SH4470 247
SH4480 39
SH4490 115
SH4500 67
SH4510 49
SH4520 65
SH4530 99
SH4540 123
SH4550 24
SH4560 47
SH4570 56
SH4580 123
SH4590 195
SH4600 51
SH4610 57
SH4620 109
SH4630 50
SH4640 154
SH4660 52
SH4670 119
SH4680 44
SH4690 51
SH4700 62
SH4710 114
SH4720 39
SH4730 124
SH4740 58
SH4750 68
SH4760 60
SH4770 239
SH4780 163
SH4790 260
SH4790A 260
SH4800 142
SH4800A 142
SH4810 67
SH4810A 67
SH4820 59
SH4820A 59
SH4830 96
SH4840 77
SH4850 167
SH4860 83
SH4870 55
SH4880 24
SH4890 25
SH4900 38
SH4910 24
SH4920 44
SH4930 50
SH4940 123
SH4950 47
SH4960 134
SH4970 99
SH4980 119
SH4990 71
SH5000 67
SH5010 119
SH5020 26
SH5030 219
SH5040 216
SH5050 120
SH5060 20
SH5070 22
SH5080 105
SH5090 43
SH5100 76
SH5110 90
SH5120 91
SH5130 24
SH5140 46
SH5150 56
SH5270 42
SH5280 32
SH5290 41
SH5300 59
SH5310 26
SH5320 46
SH5330 39
SH5340 25
SH5350 25
SH5360 22
SH5370 19
SH5380 10
SH5390 31
SH5400 26
SH5410 37
SH5420 24
SH5430 56
SH5440 34
SH5450 28
SH5460 52
SH5470 24
SH5480 29
SH5490 31
SH5500 31
SH5510 39
SH5520 48
SH5530 38
SH5540 37
SH5550 56
SH5560 37
SH5570 50
SH5580 32
SH5630 37
SH5640 22
SH5650 50
SH5650A 50
SH5660 54
SH5670 65
SH5680 53
SH5680A 53
SH5685 40
SH5690 75
SH5690A 75
SH5700 73
SH5710 55
SH5710A 55
SH5720 159
SH5730 68
SH5730A 68
SH5740 112
SH5750 75
SH5760 66
SH5760A 66
SH5770 113
SH5780 82
SH5790 56
SH5800 84
SH5810 94
SH5810A 94
SH5820 13
SH5820A 13
SH5830 24
SH5830A 24
SH5840 24
SH5850 20
SH5860 56
SH5860A 56
SH5870 74
SH5870A 74
SH5880 32
SH5890 40
SH5890A 40
SH5900 23
SH5900A 23
SH5910 41
SH5910A 41
SH5920 46
SH5930 77
SH5930A 77
SH5940 31
SH5950 69
"""


def parse_durations(text=SHOT_DURATIONS_TEXT):
    """Parse the "SHOT duration" table into an ordered list of (shot, duration)."""
    entries = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        parts = line.split()
        if len(parts) != 2:
            raise ValueError("Cannot parse line: {!r}".format(line))
        shot, duration = parts[0], int(parts[1])
        if duration < 1:
            raise ValueError("Duration must be >= 1 for {}".format(shot))
        entries.append((shot, duration))
    return entries


def frame_range(duration, start=START_FRAME):
    """A duration of N frames starting at `start` ends at start + N - 1."""
    return start, start + duration - 1


def find_shot_dirs(scene_root, ep_filter=None):
    """Map shot name -> [full paths], by scanning {scene_root}/{ep}/{seq}/{shot}."""
    found = {}
    if not os.path.isdir(scene_root):
        return found

    for ep in sorted(os.listdir(scene_root)):
        if ep_filter and ep != ep_filter:
            continue
        ep_dir = os.path.join(scene_root, ep)
        if not os.path.isdir(ep_dir):
            continue
        for seq in sorted(os.listdir(ep_dir)):
            seq_dir = os.path.join(ep_dir, seq)
            if not os.path.isdir(seq_dir):
                continue
            for shot in sorted(os.listdir(seq_dir)):
                shot_dir = os.path.join(seq_dir, shot)
                if os.path.isdir(shot_dir):
                    found.setdefault(shot, []).append((ep, seq, shot_dir))
    return found


def build_payload(duration):
    first, last = frame_range(duration)
    return {
        "frameRange": {
            "start": first,
            "end": last,
        }
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--proj-root', default='X:/', help='PROJ_ROOT (default: X:/)')
    parser.add_argument('--project', default='EGA', help='Project name (default: EGA)')
    parser.add_argument('--ep', default=None, help='Only touch this episode, e.g. Ep02')
    parser.add_argument('--write', action='store_true',
                        help='Actually write the files (default is a dry run)')
    parser.add_argument('--overwrite', action='store_true',
                        help='Replace existing JSON files instead of skipping them')
    args = parser.parse_args(argv)

    entries = parse_durations()
    scene_root = os.path.join(args.proj_root, args.project, 'all', 'scene')
    scene_root = os.path.normpath(scene_root)

    print("Scene root : {}".format(scene_root))
    print("Shots      : {}".format(len(entries)))
    print("Mode       : {}".format("WRITE" if args.write else "dry run (use --write to apply)"))
    print("")

    shot_dirs = find_shot_dirs(scene_root, args.ep)
    if not shot_dirs:
        print("ERROR: no shots found under {} - is the drive mounted and --project right?".format(scene_root))
        return 1

    written = skipped = missing = 0
    ambiguous = []

    for shot, duration in entries:
        locations = shot_dirs.get(shot)
        if not locations:
            print("  NOT FOUND  {:<10} (no directory under {})".format(shot, scene_root))
            missing += 1
            continue
        if len(locations) > 1:
            ambiguous.append((shot, [os.path.join(ep, seq) for ep, seq, _ in locations]))
            continue

        ep, seq, shot_dir = locations[0]
        json_path = os.path.join(shot_dir, ".{}_{}_{}.json".format(ep, seq, shot))
        first, last = frame_range(duration)

        if os.path.exists(json_path) and not args.overwrite:
            print("  EXISTS     {:<10} {}/{}  {}-{}  (use --overwrite to replace)".format(
                shot, ep, seq, first, last))
            skipped += 1
            continue

        if args.write:
            with open(json_path, 'w') as handle:
                json.dump(build_payload(duration), handle, indent=4)
                handle.write("\n")
        print("  {:<10} {:<10} {}/{}  {}-{}  ({} frames)".format(
            "WROTE" if args.write else "would write", shot, ep, seq, first, last, duration))
        written += 1

    if ambiguous:
        print("\nAMBIGUOUS - the same shot name exists under more than one sequence,")
        print("so I will not guess which one you mean. Resolve these by hand:")
        for shot, places in ambiguous:
            print("  {:<10} {}".format(shot, ", ".join(places)))

    print("\n{} {}, {} already present, {} not found, {} ambiguous".format(
        written, "written" if args.write else "to write", skipped, missing, len(ambiguous)))
    if not args.write and written:
        print("Nothing was written. Re-run with --write to apply.")
    return 0


if __name__ == '__main__':
    sys.exit(main())
