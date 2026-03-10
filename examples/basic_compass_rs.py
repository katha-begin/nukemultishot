import nuke

def build_dot_pipe_additive_chain_below_read():
    read_node = nuke.selectedNode()
    all_layers = read_node.channels()
    lightgroup_layers = sorted({chan.split('.')[0] for chan in all_layers if chan.startswith('BeautyAux')})

    if len(lightgroup_layers) < 2:
        nuke.message("Need at least two 'BeautyAux*' layers in your Read node!")
        return

    # Create the group node
    group = nuke.createNode('Group', inpanel=False)
    group['name'].setValue('AOV_LightGroup_Controller')
    group['label'].setValue('AOV Light Group Controller\n%d layers' % len(lightgroup_layers))
    
    # Position the group node below the read node
    group.setXpos(read_node.xpos())
    group.setYpos(read_node.ypos() + 200)
    
    # Connect the read node to the group
    group.setInput(0, read_node)
    
    # Enter the group to build the internal network
    group.begin()
    
    # Create Input node inside the group
    input_node = nuke.createNode('Input', inpanel=False)
    input_node['name'].setValue('Input1')
    input_node.setXpos(0)
    input_node.setYpos(0)

    # Layout settings inside the group
    base_x = 0
    base_y = 100
    h_space = 500
    v_dot = 100
    v_shuffle = 250
    v_exposure = 400
    v_grade = 550
    v_merge = 700

    dots = []
    shuffles = []
    exposures = []
    grades = []
    merges = []

    # --- Dots, chained left to right ---
    for i in range(len(lightgroup_layers)):
        dot = nuke.createNode('Dot', inpanel=False)
        dot.setXpos(base_x + i * h_space)
        dot.setYpos(base_y + v_dot)
        if i == 0:
            dot.setInput(0, input_node)
            dot['label'].setValue("AOV IN")
            dot['note_font_size'].setValue(36)
        else:
            dot.setInput(0, dots[-1])
        dots.append(dot)

    # --- Each Shuffle is fed by its Dot ---
    for i, layer in enumerate(lightgroup_layers):
        # Clean layer name for knob names (remove BeautyAux prefix and special chars)
        clean_layer = layer.replace('BeautyAux', '').replace('-', '_').replace('.', '_')
        
        # AOV Shuffle
        sh = nuke.createNode('Shuffle', inpanel=False)
        sh['in'].setValue(layer)
        sh.setInput(0, dots[i])
        sh['label'].setValue(layer)
        sh['name'].setValue('%s_Shuffle' % layer)
        sh.setXpos(dots[i].xpos())
        sh.setYpos(dots[i].ypos() + v_shuffle)
        shuffles.append(sh)
        
        # Exposure node with expression link to group knob
        exposure = nuke.createNode('EXPTool', inpanel=False)
        exposure.setInput(0, sh)
        exposure['mode'].setValue('Stops')
        exposure['label'].setValue('Exposure %s' % layer)
        exposure['name'].setValue('%s_Exposure' % layer)
        exposure.setXpos(dots[i].xpos())
        exposure.setYpos(dots[i].ypos() + v_exposure)
        exposures.append(exposure)
        
        # Grade node with expression link to group knob
        grade = nuke.createNode('Grade', inpanel=False)
        grade.setInput(0, exposure)
        grade['label'].setValue('Grade %s' % layer)
        grade['name'].setValue('%s_Grade' % layer)
        # Set the grade node to use separate RGB channels for gain
        grade['white'].setSingleValue(False)
        grade.setXpos(dots[i].xpos())
        grade.setYpos(dots[i].ypos() + v_grade)
        grades.append(grade)

    # --- Merge chain below processed AOVs ---
    prev = grades[0]
    for i in range(1, len(grades)):
        m = nuke.createNode('Merge2', inpanel=False)
        m['operation'].setValue('plus')
        m.setInput(0, prev)
        m.setInput(1, grades[i])
        m.setXpos(grades[i].xpos())
        m.setYpos(dots[i].ypos() + v_merge)
        m['label'].setValue('Add %s' % lightgroup_layers[i])
        m['name'].setValue('%s_Add' % lightgroup_layers[i])
        merges.append(m)
        prev = m

    # Create Switch node for AOV viewing
    switch = nuke.createNode('Switch', inpanel=False)
    switch['name'].setValue('AOV_Switch')
    switch['label'].setValue('AOV Viewer Switch')
    switch.setInput(0, prev)  # Combined result as input 0
    
    # Connect each processed grade as additional inputs to the switch
    for i, grade in enumerate(grades):
        switch.setInput(i + 1, grade)
    
    switch.setXpos(prev.xpos())
    switch.setYpos(prev.ypos() + 100)

    # Create Output node
    output = nuke.createNode('Output', inpanel=False)
    output.setInput(0, switch)
    output.setXpos(switch.xpos())
    output.setYpos(switch.ypos() + 150)
    
    # Exit the group
    group.end()
    
    # Now add the user controls (knobs) to the group
    with group:
        # Add a tab for the controls
        tab_knob = nuke.Tab_Knob('aov_controls', 'AOV Controls')
        group.addKnob(tab_knob)
        
        # Add exposure and gain controls for each layer
        for i, layer in enumerate(lightgroup_layers):
            clean_layer = layer.replace('BeautyAux', '').replace('-', '_').replace('.', '_')
            
            # Add separator
            sep_knob = nuke.Text_Knob('sep_%s' % clean_layer, layer)
            group.addKnob(sep_knob)
            
            # View toggle for this AOV
            view_knob = nuke.Boolean_Knob('view_%s' % clean_layer, 'View Only')
            view_knob.setValue(False)
            view_knob.setFlag(nuke.STARTLINE)
            group.addKnob(view_knob)
            
            # Exposure knob
            exp_knob = nuke.Double_Knob('exp_%s' % clean_layer, 'Exposure')
            exp_knob.setValue(0.0)
            exp_knob.setRange(-5.0, 5.0)
            group.addKnob(exp_knob)
            
            # Gain knob (RGB Color)
            gain_knob = nuke.Color_Knob('gain_%s' % clean_layer, 'Gain')
            gain_knob.setValue([1.0, 1.0, 1.0])
            group.addKnob(gain_knob)

    # Now link the internal nodes to the group knobs (outside group context)
    for i, layer in enumerate(lightgroup_layers):
        clean_layer = layer.replace('BeautyAux', '').replace('-', '_').replace('.', '_')
        
        # Enter group to access internal nodes
        group.begin()
        
        # Find the internal nodes
        exposure_node = nuke.toNode('%s_Exposure' % layer)
        grade_node = nuke.toNode('%s_Grade' % layer)
        switch_node = nuke.toNode('AOV_Switch')
        
        if exposure_node:
            exposure_node['red'].setExpression('parent.exp_%s' % clean_layer)
            exposure_node['green'].setExpression('parent.exp_%s' % clean_layer)
            exposure_node['blue'].setExpression('parent.exp_%s' % clean_layer)
        
        if grade_node:
            # For Grade node, link each channel of the gain (white parameter) separately
            grade_node['white'].setExpression('parent.gain_%s' % clean_layer, 0)  # Red channel
            grade_node['white'].setExpression('parent.gain_%s' % clean_layer, 1)  # Green channel  
            grade_node['white'].setExpression('parent.gain_%s' % clean_layer, 2)  # Blue channel
        
        # Exit group
        group.end()
    
    # Set up the switch expression for AOV viewing
    group.begin()
    switch_node = nuke.toNode('AOV_Switch')
    if switch_node:
        # Create expression to check which view toggle is active
        switch_expr = "0"  # Default to combined view (input 0)
        for i, layer in enumerate(lightgroup_layers):
            clean_layer = layer.replace('BeautyAux', '').replace('-', '_').replace('.', '_')
            switch_expr += " + %d*parent.view_%s" % (i + 1, clean_layer)
        
        switch_node['which'].setExpression(switch_expr)
    group.end()

    nuke.message("AOV Group Controller created!\nGroup: %s\nLayers processed: %d" % (group.name(), len(lightgroup_layers)))

build_dot_pipe_additive_chain_below_read()
