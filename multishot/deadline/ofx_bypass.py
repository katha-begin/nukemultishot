"""
Bypass OFX nodes that are not installed on the render farm.

ReelSmart Motion Blur (RSMB) is not installed on the workers - there is no
/usr/OFX/Plugins and OFX_PLUGIN_PATH is unset - so any comp whose render path
touches it dies at graph build:

    ERROR: RSMB1: 'OFXcom.revisionfx.RSMB_v3': unknown command. This is most
    likely from a corrupt .nk file, or from a missing or unlicensed plug-in.
    Can't render from that Node.

Setting a node's ``disable`` knob makes Nuke pass input 0 straight through, so
the comp still renders - without motion blur. That is a deliberate trade: no
motion blur beats no render. Re-enable this properly by licensing RSMB on the
workers.

The transform works on the .nk TEXT rather than the live script, so the
artist's open session is never modified and nothing has to be saved over their
file. The caller writes the result to a separate farm copy.
"""

import re

# Only RSMB. Sapphire is left alone deliberately: it has only ever produced a
# node-name warning on the farm, never a load error, so bypassing it would
# silently drop effects nobody asked us to remove.
RSMB_CLASS_RE = re.compile(r'^(\s*)(OFXcom\.revisionfx\.[Rr][Ss][Mm][Bb][^\s{]*)\s*\{\s*$')

_DISABLE_RE = re.compile(r'^\s*disable\s')
_NAME_RE = re.compile(r'^\s*name\s+(\S+)')


def bypass_ofx_in_script_text(text, class_re=RSMB_CLASS_RE):
    """Return (new_text, bypassed_node_names) with matching nodes disabled.

    A disabled node passes its first input through, which is what "bypass"
    means here. Any existing ``disable`` line inside a matched block is dropped
    first so the value cannot be set twice.
    """
    lines = text.splitlines()
    out = []
    bypassed = []

    index = 0
    total = len(lines)
    while index < total:
        line = lines[index]
        match = class_re.match(line)
        if not match:
            out.append(line)
            index += 1
            continue

        indent = match.group(1)
        out.append(line)
        index += 1

        # Copy the node block, dropping any existing disable, and remember the
        # node name for the report. Brace depth handles nodes inside Groups.
        depth = 1
        block = []
        name = None
        while index < total and depth > 0:
            inner = lines[index]
            depth += inner.count('{') - inner.count('}')
            if depth <= 0:
                break
            if not _DISABLE_RE.match(inner):
                block.append(inner)
                name_match = _NAME_RE.match(inner)
                if name_match:
                    name = name_match.group(1)
            index += 1

        out.append(indent + ' disable true')
        out.extend(block)
        if index < total:
            out.append(lines[index])  # the closing brace
            index += 1
        bypassed.append(name or match.group(2))

    new_text = '\n'.join(out)
    if text.endswith('\n'):
        new_text += '\n'
    return new_text, bypassed


def script_needs_bypass(text, class_re=RSMB_CLASS_RE):
    """True if the script contains any node class we would bypass."""
    return any(class_re.match(line) for line in text.splitlines())
