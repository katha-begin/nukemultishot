"""
Single source of truth for Windows <-> Linux path translation.

Artists work from mapped Windows drives; the Deadline render farm is Linux and
has studio path mapping DISABLED (the render log reports
``Enable Path Mapping: False``), so every drive letter has to be translated by us.

Before this module the drive table was copy-pasted into nine places that had
already drifted apart (``farm_script.py`` was missing every lowercase drive, and
``nuke_wrapper.py`` disagreed with itself about backslash escaping). Everything
should import from here instead.

The important entry point is :func:`install_filename_filter`. A Nuke
``filenameFilter`` is consulted every time Nuke resolves a file path - including
*while the .nk is still being parsed*. That matters because nodes such as
``Camera3``/``ReadGeo`` with ``read_from_file true`` load their file during the
parse, long before ``onScriptLoad`` (or anything else in Python) gets to run. A
callback cannot rescue those nodes; a filename filter can, and it does it
without modifying the artist's script.
"""

DRIVE_MAP = {
    'T:': '/mnt/ppr_dev_t',
    'V:': '/mnt/igloo_swa_v',
    'W:': '/mnt/igloo_swa_w',
    'X:': '/mnt/igloo_ega_x',
    'Y:': '/mnt/igloo_ega_y',
}

# Reverse lookup, longest mount first so /mnt/igloo_swa_v never matches a prefix
# of a longer mount name.
MOUNT_MAP = dict((mount, drive) for drive, mount in DRIVE_MAP.items())
_MOUNTS_LONGEST_FIRST = sorted(MOUNT_MAP, key=len, reverse=True)


def to_linux(path):
    """Translate a Windows path to its Linux mount. Returns other paths unchanged.

    Handles either slash style and either drive-letter case, so ``v:\\SWA``,
    ``V:/SWA`` and ``v:/SWA`` all land on ``/mnt/igloo_swa_v/SWA``.
    """
    if not path:
        return path

    normalised = path.replace('\\', '/')
    mount = DRIVE_MAP.get(normalised[:2].upper())
    if mount is None:
        return path

    remainder = normalised[2:]
    if not remainder.startswith('/'):
        # "V:SWA/..." is drive-relative on Windows, not an absolute path. Treat
        # it as absolute rather than silently gluing the mount onto it.
        remainder = '/' + remainder
    return mount + remainder


def to_windows(path):
    """Translate a Linux mount back to its Windows drive. Inverse of :func:`to_linux`."""
    if not path:
        return path

    normalised = path.replace('\\', '/')
    for mount in _MOUNTS_LONGEST_FIRST:
        if normalised == mount or normalised.startswith(mount + '/'):
            return MOUNT_MAP[mount] + '/' + normalised[len(mount):].lstrip('/')
    return path


def unmapped_drive(path):
    """Return the drive letter of a Windows path we have no mount for, else None.

    Used to fail loudly instead of shipping an untranslatable path to the farm,
    where it only surfaces as a file-not-found part way through a render.
    """
    if not path or len(path) < 2 or path[1] != ':':
        return None
    if path[:2].upper() in DRIVE_MAP:
        return None
    return path[0]


def install_filename_filter(verbose=False):
    """Register a Nuke filenameFilter that maps Windows drives to Linux mounts.

    Only does anything on Linux (the render nodes); on an artist's Windows box
    the paths are already correct and must be left alone. Safe to call more than
    once - the filter is registered at most once per session.

    Returns True if a filter was registered by this call.
    """
    import platform

    if platform.system() != 'Linux':
        return False

    try:
        import nuke
    except ImportError:
        return False

    if getattr(nuke, '_multishot_filename_filter_installed', False):
        return False

    def _multishot_filename_filter(filename):
        mapped = to_linux(filename)
        if verbose and mapped != filename:
            print('Multishot filenameFilter: {} -> {}'.format(filename, mapped))
        return mapped

    nuke.addFilenameFilter(_multishot_filename_filter)
    nuke._multishot_filename_filter_installed = True
    return True
