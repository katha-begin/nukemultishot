#==============================================================================
#                           ---- About ----
#==============================================================================
"""
    DESCRIPTION: This script allows you to align nodes in the x or y axis via the arrow keys
                 If the nodes are already aligned it will preform a stack operation
                 If only backdrops are selected it will preform alignment and then size matching, instead of stacking
                 If nodes and backdrops are selected, it will align their backdrops while keeping their nodes relative to it
    AUTHOR:      Hiram Gifford
    CONTACT:     hiramgifford.com
    VERSION:     01.01
    PUBLISHED:   2025-07-12
    DOCS:        https://www.hiramgifford.com/buddy-system/node-graph-buddy

"""
#==============================================================================
#                       ---- How To Install ----
#==============================================================================
"""
    Step #0:     See installation instructions for BuddySystem
"""
#===============================================================================
#                          ---- Imports ----
#===============================================================================

import nuke

#===============================================================================
#                       ---- Scripts ----
#===============================================================================

def _get_node_width(node):
    """Returns the width of a node"""
    if node.Class() == 'BackdropNode':
        return int(node.knob('bdwidth').value())
    return node.screenWidth()

def _get_node_height(node):
    """Returns the height of a node"""
    if node.Class() == 'BackdropNode':
        return int(node.knob('bdheight').value())
    return node.screenHeight()

def stack_nodes_vertically(nodes, direction='down'):
    """
    Stacks nodes vertically
    direction='up': stacks below the highest node
    direction='down': stacks above the lowest node
    """
    if len(nodes) < 2: return

    # --- [ Determine stack based on direction ] ---
    if direction == 'up':
        anchor_node = min(nodes, key=lambda n: n.ypos())
        other_nodes = sorted([n for n in nodes if n != anchor_node], key=lambda n: n.ypos())
    else:
        anchor_node = max(nodes, key=lambda n: n.ypos())
        other_nodes = sorted([n for n in nodes if n != anchor_node], key=lambda n: n.ypos(), reverse=True)

    # --- [ Stack the nodes ] ---
    PADDING = 6
    MIN_NODE_HEIGHT = 18
    ref_x_center = anchor_node.xpos() + (_get_node_width(anchor_node) / 2.0)

    if direction == 'up':
        current_y = anchor_node.ypos() + max(_get_node_height(anchor_node), MIN_NODE_HEIGHT) + PADDING
        for node in other_nodes:
            target_x = ref_x_center - (_get_node_width(node) / 2.0)
            node.setYpos(int(round(current_y)))
            node.setXpos(int(round(target_x)))
            current_y += max(_get_node_height(node), MIN_NODE_HEIGHT) + PADDING
    else:
        current_y = anchor_node.ypos() - PADDING
        for node in other_nodes:
            node_height = max(_get_node_height(node), MIN_NODE_HEIGHT)
            target_y = current_y - node_height
            target_x = ref_x_center - (_get_node_width(node) / 2.0)
            node.setYpos(int(round(target_y)))
            node.setXpos(int(round(target_x)))
            current_y = target_y - PADDING

def stack_nodes_horizontally(nodes, direction='right'):
    """
    Stacks nodes horizontally
    direction='left': stacks to the right of the left most node
    direction='right': stacks to the left of the right most node
    """
    if len(nodes) < 2: return

    # --- [ Determine stack based on direction ] ---
    if direction == 'left':
        anchor_node = min(nodes, key=lambda n: n.xpos())
        other_nodes = sorted([n for n in nodes if n != anchor_node], key=lambda n: n.xpos())
    else:
        anchor_node = max(nodes, key=lambda n: n.xpos())
        other_nodes = sorted([n for n in nodes if n != anchor_node], key=lambda n: n.xpos(), reverse=True)

    # --- [ Stack the nodes ] ---
    PADDING = 15
    MIN_NODE_WIDTH = 20
    ref_y_center = anchor_node.ypos() + (_get_node_height(anchor_node) / 2.0)

    if direction == 'left':
        current_x = anchor_node.xpos() + max(_get_node_width(anchor_node), MIN_NODE_WIDTH) + PADDING
        for node in other_nodes:
            target_y = ref_y_center - (_get_node_height(node) / 2.0)
            node.setXpos(int(round(current_x)))
            node.setYpos(int(round(target_y)))
            current_x += max(_get_node_width(node), MIN_NODE_WIDTH) + PADDING
    else:
        current_x = anchor_node.xpos() - PADDING
        for node in other_nodes:
            node_width = max(_get_node_width(node), MIN_NODE_WIDTH)
            target_x = current_x - node_width
            target_y = ref_y_center - (_get_node_height(node) / 2.0)
            node.setXpos(int(round(target_x)))
            node.setYpos(int(round(target_y)))
            current_x = target_x - PADDING

def align_nodes_advanced(align_direction='vertical', stack_direction=None, align_direction_bd='top'):
    """
    Aligns or stacks nodes based on direction and current alignment state
    align_direction='vertical' or 'horizontal': The alignment axis
    stack_direction='up'/'down' or 'left'/'right': The stack direction
    align_direction_bd: 'top', 'bottom', 'left', 'right': Alignment for backdrop only selections
    """
    all_selected = nuke.selectedNodes()
    if len(all_selected) < 2:
        return

    try:
        nuke.Undo().begin('Align/Stack Nodes')

        all_are_backdrops = all(n.Class() == 'BackdropNode' for n in all_selected)

        if all_are_backdrops:
            # --- [ If all nodes are backdrops use this dedicated alignment and match mode] ---
            reference_node = all_selected[0]
            other_nodes = all_selected[1:]

            if align_direction_bd == 'top':
                ref_y = reference_node.ypos()
                is_aligned = all(abs(n.ypos() - ref_y) < 1 for n in all_selected)
                if is_aligned:
                    # --- [ If backdrops are already top aligned match height ] ---
                    ref_height = reference_node.knob('bdheight').value()
                    for node in other_nodes:
                        node.knob('bdheight').setValue(ref_height)
                else:
                    for node in other_nodes:
                        node.setYpos(int(round(ref_y)))

            elif align_direction_bd == 'left':
                ref_x = reference_node.xpos()
                is_aligned = all(abs(n.xpos() - ref_x) < 1 for n in all_selected)
                if is_aligned:
                    # --- [ If backdrops are already left aligned match width ] ---
                    ref_width = reference_node.knob('bdwidth').value()
                    for node in other_nodes:
                        node.knob('bdwidth').setValue(ref_width)
                else:
                    for node in other_nodes:
                        node.setXpos(int(round(ref_x)))

            elif align_direction_bd == 'bottom':
                ref_bottom_y = reference_node.ypos() + _get_node_height(reference_node)
                is_aligned = all(abs((n.ypos() + _get_node_height(n)) - ref_bottom_y) < 1 for n in all_selected)
                if is_aligned:
                    # --- [ If backdrops are already bottom aligned match height and realign ] ---
                    ref_height = reference_node.knob('bdheight').value()
                    for node in other_nodes:
                        node.knob('bdheight').setValue(ref_height)
                        node.setYpos(int(round(ref_bottom_y - ref_height)))
                else:
                    for node in other_nodes:
                        node_height = _get_node_height(node)
                        node.setYpos(int(round(ref_bottom_y - node_height)))

            elif align_direction_bd == 'right':
                ref_right_x = reference_node.xpos() + _get_node_width(reference_node)
                is_aligned = all(abs((n.xpos() + _get_node_width(n)) - ref_right_x) < 1 for n in all_selected)
                if is_aligned:
                    # --- [ If backdrops are already right aligned match width and realign ] ---
                    ref_width = reference_node.knob('bdwidth').value()
                    for node in other_nodes:
                        node.knob('bdwidth').setValue(ref_width)
                        node.setXpos(int(round(ref_right_x - ref_width)))
                else:
                    for node in other_nodes:
                        node_width = _get_node_width(node)
                        node.setXpos(int(round(ref_right_x - node_width)))

            return

        # --- [ Check for stacking conditions using node centers ] ---
        # --- [ This logic is only reached if the selection is mixed or contains no backdrops ] ---
        if align_direction == 'horizontal':
            ref_center_x = all_selected[0].xpos() + (_get_node_width(all_selected[0]) / 2.0)
            is_aligned = all(abs((n.xpos() + (_get_node_width(n) / 2.0)) - ref_center_x) < 1 for n in all_selected)

            if is_aligned:
                final_stack_dir = stack_direction if stack_direction in ['up', 'down'] else 'down'
                # --- [ Nodes are already vertically aligned so stack them instead ] ---
                stack_nodes_vertically(all_selected, direction=final_stack_dir)
                return

        elif align_direction == 'vertical':
            ref_center_y = all_selected[0].ypos() + (_get_node_height(all_selected[0]) / 2.0)
            is_aligned = all(abs((n.ypos() + (_get_node_height(n) / 2.0)) - ref_center_y) < 1 for n in all_selected)

            if is_aligned:
                final_stack_dir = stack_direction if stack_direction in ['left', 'right'] else 'right'
                # --- [ Nodes are already horizontally aligned so stack them instead ] ---
                stack_nodes_horizontally(all_selected, direction=final_stack_dir)
                return

        # --- [ Alignment logic for backdrops and nodes] ---
        reference_node = all_selected[0]
        node_to_parent_map = {}
        selected_backdrops = [n for n in all_selected if n.Class() == 'BackdropNode']
        selected_backdrops.sort(key=lambda bd: bd.knob('bdwidth').value() * bd.knob('bdheight').value())
        selected_nodes_set = set(all_selected)

        for bd in selected_backdrops:
            nodes_inside = bd.getNodes()
            for node in nodes_inside:
                if node in selected_nodes_set and node not in node_to_parent_map and node != bd:
                    node_to_parent_map[node] = bd
 
        groups = {}
        
        # --- [ queen_bd is the largest nonnested backdrop ] ---
        for node in all_selected:
            queen_bd = node
            while node_to_parent_map.get(queen_bd):
                queen_bd = node_to_parent_map.get(queen_bd)
            groups.setdefault(queen_bd, []).append(node)

        reference_leader = reference_node
        while node_to_parent_map.get(reference_leader):
            reference_leader = node_to_parent_map.get(reference_leader)

        ref_x_center = reference_leader.xpos() + _get_node_width(reference_leader) / 2.0
        ref_y_center = reference_leader.ypos() + _get_node_height(reference_leader) / 2.0

        for queen_bd, members in groups.items():
            if queen_bd == reference_leader:
                continue

            delta_x, delta_y = 0.0, 0.0

            if align_direction == 'vertical':
                target_x = ref_x_center - (_get_node_width(queen_bd) / 2.0)
                delta_x = target_x - queen_bd.xpos()
            elif align_direction == 'horizontal':
                target_y = ref_y_center - (_get_node_height(queen_bd) / 2.0)
                delta_y = target_y - queen_bd.ypos()

            for node_to_move in members:
                node_to_move.setXpos(int(round(node_to_move.xpos() + delta_x)))
                node_to_move.setYpos(int(round(node_to_move.ypos() + delta_y)))
    finally:
        nuke.Undo().end()