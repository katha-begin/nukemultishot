#==============================================================================
#                           ---- About ----
#==============================================================================
"""
    DESCRIPTION: This script allows you to paste your copied nodes to multiple selected nodes
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

def multipaste_and_select():
    """Pastes the nodes in your clipboard to any number of selected nodes"""
    initial_selection = nuke.selectedNodes()
    if not initial_selection:
        nuke.message("Please select at least one node to paste to")
        return

    # --- [ Get all nodes that exist before paste ] ---
    nodes_before = set(nuke.allNodes())

    # --- [ Paste Logic ] ---
    for target_node in initial_selection:
        for n in nuke.selectedNodes():
            n.setSelected(False)
            
        target_node.setSelected(True)
        
        nuke.nodePaste('%clipboard%')

    # --- [ Get all nodes that exist after paste ] ---
    nodes_after = set(nuke.allNodes())

    # --- [ Find the difference and select only new nodes] ---
    newly_pasted_nodes = nodes_after - nodes_before

    for n in nuke.selectedNodes():
        n.setSelected(False)
        
    if newly_pasted_nodes:
        for node in newly_pasted_nodes:
            node.setSelected(True)
    else:
        pass