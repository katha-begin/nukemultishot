"""
CompPass Node - AOV/LightGroup Compositing Controller

A dynamic Group node that:
1. Scans connected Read node for AOV/LightGroup layers
2. Lets users select which layers to include
3. Builds Shuffle/Exposure/Grade/Merge chain for selected layers
4. Provides per-layer controls (exposure, gain, view toggle)
"""

from ..utils.logging import get_logger

logger = get_logger(__name__)


# Layer prefixes to detect (user can customize)
DEFAULT_LAYER_PREFIXES = ['BeautyAux', 'LightGroup', 'RGBA_']


def get_available_layers(node, prefixes=None):
    """
    Scan a node for available AOV/LightGroup layers.

    Args:
        node: Nuke node to scan (typically a Read node)
        prefixes: List of layer prefixes to match (default: BeautyAux, LightGroup, RGBA_)

    Returns:
        List of layer names found
    """
    if prefixes is None:
        prefixes = DEFAULT_LAYER_PREFIXES

    try:
        all_channels = node.channels()
        layers = set()

        for chan in all_channels:
            layer_name = chan.split('.')[0]
            # Check if layer matches any prefix
            for prefix in prefixes:
                if layer_name.startswith(prefix):
                    layers.add(layer_name)
                    break

        return sorted(list(layers))

    except Exception as e:
        logger.error(f"Error scanning layers: {e}")
        return []


def clean_layer_name(layer):
    """Convert layer name to safe knob name."""
    return layer.replace('-', '_').replace('.', '_').replace(' ', '_')


def create_comppass_node():
    """
    Create a new CompPass node.

    This creates an empty Group node with UI controls.
    User must click "Scan Layers" to populate available layers.
    """
    import nuke

    # Get selected node (should be Read node or similar)
    sel = nuke.selectedNodes()
    if not sel:
        nuke.message("Please select a Read node or node with AOV layers first.")
        return None

    source_node = sel[0]

    # Create the group node
    group = nuke.createNode('Group', inpanel=False)
    group['name'].setValue('CompPass')
    group['tile_color'].setValue(0x7aa9ffff)
    group['note_font'].setValue('Verdana Bold')

    # Position below source
    group.setXpos(source_node.xpos())
    group.setYpos(source_node.ypos() + 150)
    group.setInput(0, source_node)

    # Create basic internal structure
    group.begin()

    input_node = nuke.createNode('Input', inpanel=False)
    input_node['name'].setValue('Input1')
    input_node.setXpos(0)
    input_node.setYpos(0)

    output_node = nuke.createNode('Output', inpanel=False)
    output_node['name'].setValue('Output1')
    output_node.setInput(0, input_node)
    output_node.setXpos(0)
    output_node.setYpos(200)

    group.end()

    # Add user knobs
    _add_comppass_knobs(group)

    logger.info("CompPass node created")
    return group



def _add_comppass_knobs(group):
    """Add user control knobs to the CompPass group."""
    import nuke

    # Main tab
    tab = nuke.Tab_Knob('comppass_tab', 'CompPass')
    group.addKnob(tab)

    # Info text
    info = nuke.Text_Knob('info', '', '<b>AOV/LightGroup Compositor</b>')
    group.addKnob(info)

    # Divider
    div1 = nuke.Text_Knob('div1', '')
    group.addKnob(div1)

    # Layer prefix filter
    prefix_knob = nuke.String_Knob('layer_prefixes', 'Layer Prefixes')
    prefix_knob.setValue('BeautyAux,LightGroup,RGBA_')
    prefix_knob.setTooltip('Comma-separated prefixes to filter layers')
    group.addKnob(prefix_knob)

    # Scan button
    scan_btn = nuke.PyScript_Knob('scan_layers', 'Scan Layers')
    scan_btn.setTooltip('Scan input for available AOV/LightGroup layers')
    scan_cmd = '''
import multishot.nodes.comppass_node as cp
cp.scan_layers_callback(nuke.thisNode())
'''
    scan_btn.setValue(scan_cmd)
    group.addKnob(scan_btn)

    # Divider
    div2 = nuke.Text_Knob('div2', '')
    group.addKnob(div2)

    # Available layers (multiline display)
    avail = nuke.Multiline_Eval_String_Knob('available_layers', 'Available Layers')
    avail.setValue('')
    avail.setEnabled(False)
    avail.setTooltip('Layers found in input node')
    group.addKnob(avail)

    # Selected layers (user editable)
    selected = nuke.Multiline_Eval_String_Knob('selected_layers', 'Selected Layers')
    selected.setValue('')
    selected.setTooltip('Layers to include (one per line). Edit to add/remove.')
    group.addKnob(selected)

    # Divider
    div3 = nuke.Text_Knob('div3', '')
    group.addKnob(div3)

    # Build button
    build_btn = nuke.PyScript_Knob('build_network', 'Build Network')
    build_btn.setTooltip('Build the AOV compositing network for selected layers')
    build_cmd = '''
import multishot.nodes.comppass_node as cp
cp.build_network_callback(nuke.thisNode())
'''
    build_btn.setValue(build_cmd)
    group.addKnob(build_btn)

    # Rebuild button
    rebuild_btn = nuke.PyScript_Knob('rebuild_network', 'Rebuild')
    rebuild_btn.setTooltip('Clear and rebuild the network')
    rebuild_btn.setFlag(nuke.STARTLINE)
    rebuild_cmd = '''
import multishot.nodes.comppass_node as cp
cp.rebuild_network_callback(nuke.thisNode())
'''
    rebuild_btn.setValue(rebuild_cmd)
    group.addKnob(rebuild_btn)

    # Clear button
    clear_btn = nuke.PyScript_Knob('clear_network', 'Clear')
    clear_btn.setTooltip('Remove all internal nodes (keep input/output)')
    clear_cmd = '''
import multishot.nodes.comppass_node as cp
cp.clear_network_callback(nuke.thisNode())
'''
    clear_btn.setValue(clear_cmd)
    group.addKnob(clear_btn)

    # Divider
    div4 = nuke.Text_Knob('div4', '')
    group.addKnob(div4)

    # Status
    status = nuke.Text_Knob('status', 'Status', 'Ready - Click "Scan Layers" to start')
    group.addKnob(status)


def scan_layers_callback(group):
    """Callback for Scan Layers button."""
    import nuke

    try:
        # Get input node
        input_node = group.input(0)
        if not input_node:
            group['status'].setValue('<font color="red">No input connected!</font>')
            return

        # Get prefixes from knob
        prefix_str = group['layer_prefixes'].value()
        prefixes = [p.strip() for p in prefix_str.split(',') if p.strip()]

        # Scan for layers
        layers = get_available_layers(input_node, prefixes)

        if not layers:
            group['status'].setValue('<font color="orange">No matching layers found</font>')
            group['available_layers'].setValue('')
            return

        # Update available layers display
        group['available_layers'].setValue('\n'.join(layers))

        # If selected is empty, auto-populate with all found layers
        if not group['selected_layers'].value().strip():
            group['selected_layers'].setValue('\n'.join(layers))

        group['status'].setValue(f'<font color="green">Found {len(layers)} layers</font>')

    except Exception as e:
        logger.error(f"Error scanning layers: {e}")
        group['status'].setValue(f'<font color="red">Error: {e}</font>')


def clear_network_callback(group):
    """Clear internal nodes (keep Input/Output)."""
    import nuke

    try:
        group.begin()

        # Find and delete all nodes except Input1 and Output1
        nodes_to_delete = []
        for node in nuke.allNodes():
            if node.name() not in ['Input1', 'Output1']:
                nodes_to_delete.append(node)

        for node in nodes_to_delete:
            nuke.delete(node)

        # Reconnect Input to Output
        input_node = nuke.toNode('Input1')
        output_node = nuke.toNode('Output1')
        if input_node and output_node:
            output_node.setInput(0, input_node)

        group.end()

        # Remove dynamic knobs (layer controls)
        _remove_layer_knobs(group)

        group['status'].setValue('Network cleared')

    except Exception as e:
        logger.error(f"Error clearing network: {e}")
        group['status'].setValue(f'<font color="red">Error: {e}</font>')
        try:
            group.end()
        except:
            pass


def _remove_layer_knobs(group):
    """Remove dynamically created layer control knobs and AOV Controls tab."""
    import nuke

    # Find and remove knobs that start with layer-specific prefixes
    knobs_to_remove = []
    for knob_name in group.knobs():
        if knob_name.startswith(('exp_', 'gain_', 'view_', 'sep_', 'layer_div_', 'enable_')):
            knobs_to_remove.append(knob_name)

    # Also remove the AOV Controls tab if it exists
    if 'aov_controls' in group.knobs():
        knobs_to_remove.append('aov_controls')

    for knob_name in knobs_to_remove:
        try:
            group.removeKnob(group[knob_name])
        except:
            pass


def rebuild_network_callback(group):
    """Clear and rebuild the network."""
    clear_network_callback(group)
    build_network_callback(group)


def build_network_callback(group):
    """Build the AOV compositing network for selected layers."""
    import nuke

    try:
        # Get selected layers
        selected_text = group['selected_layers'].value().strip()
        if not selected_text:
            group['status'].setValue('<font color="orange">No layers selected</font>')
            return

        layers = [l.strip() for l in selected_text.split('\n') if l.strip()]

        if len(layers) < 1:
            group['status'].setValue('<font color="orange">Select at least one layer</font>')
            return

        # Clear existing network first
        clear_network_callback(group)

        # Build the network
        _build_internal_network(group, layers)

        # Add layer control knobs
        _add_layer_control_knobs(group, layers)

        # Link knobs to internal nodes
        _link_knobs_to_nodes(group, layers)

        group['status'].setValue(f'<font color="green">Built network with {len(layers)} layers</font>')

    except Exception as e:
        logger.error(f"Error building network: {e}")
        group['status'].setValue(f'<font color="red">Error: {e}</font>')



def _build_internal_network(group, layers):
    """Build Shuffle/Exposure/Grade/Merge chain inside the group."""
    import nuke

    group.begin()

    input_node = nuke.toNode('Input1')
    output_node = nuke.toNode('Output1')

    # Layout settings
    base_x = 0
    base_y = 100
    h_space = 400
    v_dot = 80
    v_shuffle = 180
    v_exposure = 280
    v_grade = 380
    v_merge = 500

    dots = []
    shuffles = []
    exposures = []
    grades = []
    merges = []

    # Create dot chain
    for i in range(len(layers)):
        dot = nuke.createNode('Dot', inpanel=False)
        dot.setXpos(base_x + i * h_space + 34)  # +34 to center dot
        dot.setYpos(base_y + v_dot)
        if i == 0:
            dot.setInput(0, input_node)
            dot['label'].setValue("AOV IN")
            dot['note_font_size'].setValue(24)
        else:
            dot.setInput(0, dots[-1])
        dots.append(dot)

    # Create Shuffle/Exposure/Grade for each layer
    for i, layer in enumerate(layers):
        clean_layer = clean_layer_name(layer)

        # Shuffle - extract AOV layer
        sh = nuke.createNode('Shuffle', inpanel=False)
        sh['in'].setValue(layer)
        sh.setInput(0, dots[i])
        sh['label'].setValue(layer)
        sh['name'].setValue(f'{clean_layer}_Shuffle')
        sh.setXpos(base_x + i * h_space)
        sh.setYpos(base_y + v_shuffle)
        shuffles.append(sh)

        # EXPTool - exposure control
        exp = nuke.createNode('EXPTool', inpanel=False)
        exp.setInput(0, sh)
        exp['mode'].setValue('Stops')
        exp['label'].setValue(f'Exp: {layer}')
        exp['name'].setValue(f'{clean_layer}_Exposure')
        exp.setXpos(base_x + i * h_space)
        exp.setYpos(base_y + v_exposure)
        exposures.append(exp)

        # Grade - gain/color control
        grade = nuke.createNode('Grade', inpanel=False)
        grade.setInput(0, exp)
        grade['label'].setValue(f'Grade: {layer}')
        grade['name'].setValue(f'{clean_layer}_Grade')
        grade['white'].setSingleValue(False)  # Enable per-channel
        grade.setXpos(base_x + i * h_space)
        grade.setYpos(base_y + v_grade)
        grades.append(grade)

    # Create Multiply node for first layer (to allow disabling it)
    # This goes BEFORE the merge chain
    first_clean_layer = clean_layer_name(layers[0])
    first_mult = nuke.createNode('Multiply', inpanel=False)
    first_mult['name'].setValue(f'{first_clean_layer}_Disable')
    first_mult['label'].setValue(f'Disable: {layers[0]}')
    first_mult.setInput(0, grades[0])
    first_mult.setXpos(base_x)
    first_mult.setYpos(base_y + v_merge - 50)

    # Create additive merge chain
    # Flow: first_mult -> Merge(+grade[1]) -> Merge(+grade[2]) -> ... -> final_merge
    if len(grades) >= 2:
        # Start with first_mult (which has grades[0] as input)
        prev = first_mult
        for i in range(1, len(grades)):
            clean_layer = clean_layer_name(layers[i])
            m = nuke.createNode('Merge2', inpanel=False)
            m['operation'].setValue('plus')
            m.setInput(0, prev)  # A input - previous result
            m.setInput(1, grades[i])  # B input - next AOV
            m.setXpos(base_x + i * h_space)
            m.setYpos(base_y + v_merge)
            m['label'].setValue(f'+ {layers[i]}')
            m['name'].setValue(f'{clean_layer}_Merge')
            merges.append(m)
            prev = m
        # final_merge is the LAST merge node (combined result of all AOVs)
        final_merge = merges[-1]
    else:
        # Single layer - just use the Multiply as final
        final_merge = first_mult

    # Create Switch for viewing individual layers
    # Input 0 = Combined (final_merge = last Merge node)
    # Input 1, 2, 3... = Individual AOV grades
    switch = nuke.createNode('Switch', inpanel=False)
    switch['name'].setValue('AOV_ViewSwitch')
    switch['label'].setValue('View Switch')

    # Connect input 0 to final_merge (the LAST merge, combined result)
    switch.setInput(0, final_merge)
    # Connect individual grades to inputs 1, 2, 3...
    for i, grade in enumerate(grades):
        switch.setInput(i + 1, grade)

    switch.setXpos(final_merge.xpos() if hasattr(final_merge, 'xpos') else 0)
    switch.setYpos(base_y + v_merge + 120)

    # Connect output
    output_node.setInput(0, switch)
    output_node.setXpos(switch.xpos())
    output_node.setYpos(switch.ypos() + 100)

    group.end()



def _add_layer_control_knobs(group, layers):
    """Add per-layer control knobs to the group."""
    import nuke

    # Add AOV Controls tab
    try:
        aov_tab = nuke.Tab_Knob('aov_controls', 'AOV Controls')
        group.addKnob(aov_tab)
    except:
        pass  # Tab might already exist

    for i, layer in enumerate(layers):
        clean_layer = clean_layer_name(layer)

        # Layer separator/label
        sep = nuke.Text_Knob(f'sep_{clean_layer}', layer)
        group.addKnob(sep)

        # View toggle
        view_knob = nuke.Boolean_Knob(f'view_{clean_layer}', 'View Only')
        view_knob.setValue(False)
        view_knob.setFlag(nuke.STARTLINE)
        view_knob.setTooltip(f'View only this layer ({layer})')
        group.addKnob(view_knob)

        # Enable toggle
        enable_knob = nuke.Boolean_Knob(f'enable_{clean_layer}', 'Enable')
        enable_knob.setValue(True)
        enable_knob.setTooltip(f'Enable/disable this layer in the merge')
        group.addKnob(enable_knob)

        # Exposure knob
        exp_knob = nuke.Double_Knob(f'exp_{clean_layer}', 'Exposure')
        exp_knob.setValue(0.0)
        exp_knob.setRange(-5.0, 5.0)
        exp_knob.setTooltip('Exposure adjustment in stops')
        group.addKnob(exp_knob)

        # Gain knob (RGB Color)
        gain_knob = nuke.Color_Knob(f'gain_{clean_layer}', 'Gain')
        gain_knob.setValue([1.0, 1.0, 1.0])
        gain_knob.setTooltip('RGB gain multiplier')
        group.addKnob(gain_knob)

        # Divider between layers
        if i < len(layers) - 1:
            div = nuke.Text_Knob(f'layer_div_{clean_layer}', '')
            group.addKnob(div)


def _link_knobs_to_nodes(group, layers):
    """Link group knobs to internal nodes via expressions."""
    import nuke

    group.begin()

    for i, layer in enumerate(layers):
        clean_layer = clean_layer_name(layer)

        # Find internal nodes
        exp_node = nuke.toNode(f'{clean_layer}_Exposure')
        grade_node = nuke.toNode(f'{clean_layer}_Grade')
        merge_node = nuke.toNode(f'{clean_layer}_Merge')
        disable_node = nuke.toNode(f'{clean_layer}_Disable')

        if exp_node:
            # Link exposure channels to group knob
            exp_node['red'].setExpression(f'parent.exp_{clean_layer}')
            exp_node['green'].setExpression(f'parent.exp_{clean_layer}')
            exp_node['blue'].setExpression(f'parent.exp_{clean_layer}')

        if grade_node:
            # Link gain (white) channels to group knob
            grade_node['white'].setExpression(f'parent.gain_{clean_layer}.r', 0)
            grade_node['white'].setExpression(f'parent.gain_{clean_layer}.g', 1)
            grade_node['white'].setExpression(f'parent.gain_{clean_layer}.b', 2)

        # Link enable to disable mechanism
        if i == 0 and disable_node:
            # First layer uses Multiply node - set value to 0 when disabled
            disable_node['value'].setExpression(f'parent.enable_{clean_layer}')
        elif merge_node:
            # Other layers use Merge disable
            merge_node['disable'].setExpression(f'1-parent.enable_{clean_layer}')

    # Setup switch expression for view toggles
    switch_node = nuke.toNode('AOV_ViewSwitch')
    if switch_node:
        # Build expression: 0 + 1*view_layer1 + 2*view_layer2 + ...
        switch_expr = "0"
        for i, layer in enumerate(layers):
            clean_layer = clean_layer_name(layer)
            switch_expr += f" + {i + 1}*parent.view_{clean_layer}"
        switch_node['which'].setExpression(switch_expr)

    group.end()
