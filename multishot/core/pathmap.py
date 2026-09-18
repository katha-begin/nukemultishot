"""
Windows <-> Linux path translation, driven by Deadline's own path mapping rules.

Artists work from mapped Windows drives; the render farm is Linux. Deadline
already holds the studio's drive->mount table in Repository Options (Tools >
Configure Repository Options > Mapped Paths) - it is what produces the
``CheckPathMapping: Swapped "X:/..." with "/mnt/igloo_ega_x/..."`` line in a
render log. What it does NOT do here is rewrite paths *inside* the .nk, because
the Nuke plugin reports ``Enable Path Mapping: False``.

So we read Deadline's table and apply it ourselves. The rules stay configured in
one studio-managed place instead of being hardcoded in pipeline code; add a drive
in Repository Options and it is picked up with no code change. The table below is
only a fallback for when Deadline cannot be queried (an artist workstation
without the client installed, a worker where deadlinecommand fails).

The important entry point is :func:`install_filename_filter`. A Nuke
``filenameFilter`` is consulted every time Nuke resolves a file path - including
*while the .nk is still being parsed*. That matters because nodes such as
``Camera3``/``ReadGeo`` with ``read_from_file true`` load their file during the
parse, long before ``onScriptLoad`` (or anything else in Python) gets to run. A
callback cannot rescue those nodes; a filename filter can, and it does it
without modifying the artist's script.
"""

import os
import platform
import subprocess

# Fallback only - the live rules come from Deadline. Keep in sync with
# Repository Options if you rely on it.
DEFAULT_DRIVE_MAP = {
    'T:': '/mnt/ppr_dev_t',
    'V:': '/mnt/igloo_swa_v',
    'W:': '/mnt/igloo_swa_w',
    'X:': '/mnt/igloo_ega_x',
    'Y:': '/mnt/igloo_ega_y',
}

# Populated on first use by get_rules(); list of (source, destination) prefixes,
# longest source first so a longer rule always wins over a shorter one.
_cached_rules = None
_cached_source = None


def _normalise_prefix(value):
    """Trim a rule prefix to a comparable form: forward slashes, no trailing slash."""
    return value.strip().replace('\\', '/').rstrip('/')


def _find_deadline_command():
    """Locate deadlinecommand, or None if the Deadline client is not installed."""
    candidates = []
    deadline_path = os.environ.get('DEADLINE_PATH', '')
    if deadline_path:
        candidates.append(deadline_path)
    candidates.extend([
        '/opt/Thinkbox/Deadline10/bin',
        'C:/Program Files/Thinkbox/Deadline10/bin',
    ])

    name = 'deadlinecommand.exe' if platform.system() == 'Windows' else 'deadlinecommand'
    for directory in candidates:
        candidate = os.path.join(directory, name)
        if os.path.exists(candidate):
            return candidate
    return None


def parse_path_mappings(text):
    """Parse ``deadlinecommand -GetPathMappings`` output into (source, dest) pairs.

    The output is one rule per line, e.g.::

        T:/ --> /mnt/ppr_dev_t/
        X:/ --> /mnt/igloo_ega_x/
    """
    rules = []
    for line in (text or '').splitlines():
        if '-->' not in line:
            continue
        source, _, destination = line.partition('-->')
        source = _normalise_prefix(source)
        destination = _normalise_prefix(destination)
        if source and destination:
            rules.append((source, destination))
    return rules


def load_deadline_mappings(timeout=20):
    """Ask Deadline for the studio's path mapping rules. Returns [] on any failure."""
    command = _find_deadline_command()
    if not command:
        return []

    try:
        startupinfo = None
        if platform.system() == 'Windows' and hasattr(subprocess, 'STARTUPINFO'):
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        proc = subprocess.Popen(
            [command, '-GetPathMappings'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            startupinfo=startupinfo,
        )
        out, _ = proc.communicate(timeout=timeout)
        if proc.returncode != 0:
            return []
        if not isinstance(out, str):
            out = out.decode('utf-8', 'replace')
        return parse_path_mappings(out)
    except Exception:
        # Never let path mapping discovery take Nuke down with it.
        return []


def get_rules(refresh=False):
    """Return the active (source, destination) rules, longest source first.

    Queried from Deadline once per session and cached - the filenameFilter runs
    for every path Nuke resolves, so this must never shell out per call.
    """
    global _cached_rules, _cached_source

    if _cached_rules is not None and not refresh:
        return _cached_rules

    rules = load_deadline_mappings()
    source = 'Deadline path mapping'
    if not rules:
        rules = [(drive, mount) for drive, mount in DEFAULT_DRIVE_MAP.items()]
        source = 'built-in fallback table'

    _cached_rules = sorted(rules, key=lambda rule: len(rule[0]), reverse=True)
    _cached_source = source
    return _cached_rules


def get_rules_source():
    """Where the active rules came from - useful in render logs."""
    if _cached_rules is None:
        get_rules()
    return _cached_source


def _make_absolute(path):
    """Turn a drive-relative path into an absolute one.

    "V:SWA/a.exr" means "SWA under the current directory on V:" - never what the
    pipeline intends, and it would not match a "V:/" rule.
    """
    if len(path) >= 2 and path[1] == ':' and (len(path) == 2 or path[2] != '/'):
        return path[:2] + '/' + path[2:]
    return path


def to_linux(path):
    """Translate a Windows path to its Linux mount. Other paths pass through."""
    if not path:
        return path

    candidate = _make_absolute(path.replace('\\', '/'))
    lowered = candidate.lower()
    for source, destination in get_rules():
        lowered_source = source.lower()
        if lowered == lowered_source:
            return destination
        if lowered.startswith(lowered_source + '/'):
            return destination + candidate[len(source):]
    return path


def to_windows(path):
    """Translate a Linux mount back to its Windows drive. Inverse of :func:`to_linux`."""
    if not path:
        return path

    candidate = path.replace('\\', '/')
    # Destination first, longest destination wins.
    for source, destination in sorted(get_rules(),
                                      key=lambda rule: len(rule[1]), reverse=True):
        if candidate == destination:
            return source + '/'
        if candidate.startswith(destination + '/'):
            return source + candidate[len(destination):]
    return path


def unmapped_drive(path):
    """Return the drive letter of a Windows path we have no rule for, else None.

    Lets callers fail loudly rather than shipping an untranslatable path to the
    farm, where it only surfaces as a file-not-found part way through a render.
    """
    if not path or len(path) < 2 or path[1] != ':':
        return None
    if to_linux(path) != path:
        return None
    return path[0]


def install_filename_filter(verbose=False):
    """Register a Nuke filenameFilter that maps Windows drives to Linux mounts.

    Only does anything on Linux (the render nodes); on an artist's Windows box
    the paths are already correct and must be left alone. Safe to call more than
    once - the filter is registered at most once per session.

    Returns True if a filter was registered by this call.
    """
    if platform.system() != 'Linux':
        return False

    try:
        import nuke
    except ImportError:
        return False

    if getattr(nuke, '_multishot_filename_filter_installed', False):
        return False

    # Resolve the rules now, once, so the filter itself never shells out.
    rules = get_rules()

    def _multishot_filename_filter(filename):
        mapped = to_linux(filename)
        if verbose and mapped != filename:
            print('Multishot filenameFilter: {} -> {}'.format(filename, mapped))
        return mapped

    nuke.addFilenameFilter(_multishot_filename_filter)
    nuke._multishot_filename_filter_installed = True

    if verbose:
        print('Multishot: {} rule(s) from {}'.format(len(rules), get_rules_source()))
        for source, destination in rules:
            print('  {} -> {}'.format(source, destination))
    return True
