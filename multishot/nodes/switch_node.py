"""
Custom Switch node for the Multishot Workflow System.

This module provides a dynamic multishot_switch that routes inputs
based on root.shot matching shot names (supports comma-separated lists).

The gizmo is located at: gizmo/Utilities/multishot_switch.gizmo

How it works:
- User clicks "Add Shot Input" to create new inputs dynamically
- Each input has a shot names field (comma-separated, e.g. "SH010, SH020")
- root.shot is matched against all shot names
- Routes to matching input, or Input 0 (main) as fallback
"""

from ..utils.logging import get_logger

# Colors for inputs (cycling)
INPUT_COLORS = [
    ('#ff5555', 0xff5555ff),  # Red
    ('#55cc55', 0x55cc55ff),  # Green
    ('#5588ff', 0x5588ffff),  # Blue
    ('#ffcc00', 0xffcc00ff),  # Yellow
    ('#cc55ff', 0xcc55ffff),  # Purple
    ('#55ffff', 0x55ffffff),  # Cyan
    ('#ff55ff', 0xff55ffff),  # Magenta
    ('#ffaa55', 0xffaa55ff),  # Orange
]


def create_multishot_switch():
    """
    Create a new multishot_switch gizmo.

    Returns:
        Created Nuke node or None on error
    """
    try:
        import nuke
        node = nuke.createNode('multishot_switch')
        return node
    except Exception as e:
        logger = get_logger(__name__)
        logger.error(f"Error creating multishot_switch: {e}")
        return None


def add_shot_input(node):
    """
    Add a new shot input to the multishot_switch node.

    Args:
        node: The multishot_switch Group node
    """
    import nuke

    count = int(node['input_count'].value()) + 1
    node['input_count'].setValue(count)

    # Get color for this input
    color_html, color_int = INPUT_COLORS[(count - 1) % len(INPUT_COLORS)]

    # Add shot name knob
    shot_knob = nuke.String_Knob(
        'shot_input_%d' % count,
        '<font color="%s">Input %d Shots</font>' % (color_html, count)
    )
    shot_knob.setTooltip('Shot names for Input %d (comma-separated, e.g. SH010, SH020, SH030)' % count)
    node.addKnob(shot_knob)

    # Add Input node inside group
    node.begin()

    input_node = nuke.createNode('Input', inpanel=False)
    input_node['name'].setValue('Input%d' % count)
    input_node.setXpos(count * 150)
    input_node.setYpos(-200)

    node.end()

    # Update switch connections
    update_switch(node)

    print("Added Input %d. Connect your shot comp to the new input arrow." % count)


def remove_last_input(node):
    """
    Remove the last shot input from the multishot_switch node.

    Args:
        node: The multishot_switch Group node
    """
    import nuke

    count = int(node['input_count'].value())

    if count <= 0:
        nuke.message('No shot inputs to remove.')
        return

    # Remove knob
    try:
        node.removeKnob(node['shot_input_%d' % count])
    except:
        pass

    # Remove input node
    node.begin()
    inp = nuke.toNode('Input%d' % count)
    if inp:
        nuke.delete(inp)
    node.end()

    node['input_count'].setValue(count - 1)

    # Update switch
    update_switch(node)


def set_shot_from_root(node, input_num=None):
    """
    Add current root.shot value to the specified input (or last input).

    Args:
        node: The multishot_switch Group node
        input_num: Input number to set (default: last input)
    """
    import nuke

    count = int(node['input_count'].value())
    if count <= 0:
        nuke.message('No shot inputs. Click "Add Shot Input" first.')
        return

    if input_num is None:
        input_num = count

    knob_name = 'shot_input_%d' % input_num
    if knob_name not in node.knobs():
        nuke.message('Input %d does not exist.' % input_num)
        return

    try:
        shot = nuke.root()['shot'].value()
    except:
        nuke.message('Could not read root.shot')
        return

    knob = node[knob_name]
    current = knob.value().strip()

    if current:
        # Append if not already there
        shots = [s.strip() for s in current.split(',')]
        if shot not in shots:
            shots.append(shot)
            knob.setValue(', '.join(shots))
            print("Added '%s' to Input %d" % (shot, input_num))
        else:
            print("'%s' already in Input %d" % (shot, input_num))
    else:
        knob.setValue(shot)
        print("Set Input %d to '%s'" % (input_num, shot))


def update_switch(node):
    """
    Update the internal Switch node connections and expression.

    Args:
        node: The multishot_switch Group node
    """
    import nuke

    count = int(node['input_count'].value())

    node.begin()

    # Find switch
    switch = nuke.toNode('ShotSwitch')
    if not switch:
        print("Error: ShotSwitch not found inside group")
        node.end()
        return

    # Connect inputs to switch
    main_input = nuke.toNode('Input0')
    if main_input:
        switch.setInput(0, main_input)

    for i in range(1, count + 1):
        inp = nuke.toNode('Input%d' % i)
        if inp:
            switch.setInput(i, inp)

    # Set switch expression
    if count > 0:
        # Build Python expression for matching
        expr_lines = ['ret = 0']
        expr_lines.append('try:')
        expr_lines.append('    shot = nuke.root()["shot"].value()')

        for i in range(1, count + 1):
            expr_lines.append('    shots_%d = [s.strip() for s in nuke.thisParent()["shot_input_%d"].value().split(",") if s.strip()]' % (i, i))
            expr_lines.append('    if shot in shots_%d: ret = %d' % (i, i))

        expr_lines.append('except: pass')
        expr_lines.append('ret')

        expr = '\n'.join(expr_lines)
        switch['which'].setExpression(expr, 'python')
    else:
        switch['which'].setValue(0)
        switch['which'].clearAnimated()

    # Connect switch to output
    output = nuke.toNode('Output1')
    if output:
        output.setInput(0, switch)

    node.end()

    # Update tile color based on current input
    _update_tile_color(node)


def _update_tile_color(node):
    """Update node tile color based on active input."""
    import nuke

    try:
        node.begin()
        switch = nuke.toNode('ShotSwitch')
        if switch:
            which = int(switch['which'].value())
            if which == 0:
                node['tile_color'].setValue(0x7f7f7fff)  # Gray for main
            else:
                _, color_int = INPUT_COLORS[(which - 1) % len(INPUT_COLORS)]
                node['tile_color'].setValue(color_int)
        node.end()
    except:
        pass


# Alias for backward compatibility
MultishotSwitch = None
