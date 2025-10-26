#==============================================================================
#                           ---- About ----
#==============================================================================
"""
    DESCRIPTION: This script copies nodes and reconnects them after pasting
                 Inspired by Sebastian Schutt's version https://youtu.be/jpdbNuVCOjg?si=ksk5yydlFIDgN3cV
                 But with some additional logic to make copying from one script to another more stable 
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

def copy_paste_reconnect(mode='copy'):
    """
    Manages copying and pasting nodes while preserving their inputs
    Uses temporary knobs which are cleaned up after the operation
    """
    # --- [ Temporary knobs ] ---
    TEMP_TAB_NAME = '_temp_data_tab'
    COPIED_NODES_KNOB_NAME = '_temp_copied_nodes'
    CONNECTIONS_KNOB_NAME = '_temp_input_connections'

    # --- [ Copy Logic ] ---
    if mode == 'copy':
        nodes = nuke.selectedNodes()
        if not nodes:
            nuke.message('No node(s) selected.\nSelect some to perform copy operation')
            return

        copied_node_names = [n.name() for n in nodes]
        copied_nodes_string = ";".join(copied_node_names)

        for node in nodes:
            temp_tab = nuke.Tab_Knob(TEMP_TAB_NAME, 'Temp Data')
            node.addKnob(temp_tab)

            copied_list_knob = nuke.String_Knob(COPIED_NODES_KNOB_NAME, 'Copied Nodes')
            node.addKnob(copied_list_knob)
            node[COPIED_NODES_KNOB_NAME].setValue(copied_nodes_string)
            
            connection_info = {}
            for i in range(node.inputs()):
                input_node = node.input(i)
                if input_node and input_node.name() not in copied_node_names:
                    connection_info[i] = input_node.name()

            if connection_info:
                data_string = ";".join(["%s:%s" % (index, name) for index, name in connection_info.items()])
                connections_knob = nuke.String_Knob(CONNECTIONS_KNOB_NAME, 'Temp Connections')
                node.addKnob(connections_knob)
                node[CONNECTIONS_KNOB_NAME].setValue(data_string)

        nuke.nodeCopy('%clipboard%')

        # --- [ Clean Up ] ---
        for node in nodes:
            for knob_name in [CONNECTIONS_KNOB_NAME, COPIED_NODES_KNOB_NAME, TEMP_TAB_NAME]:
                if knob_name in node.knobs():
                    node.removeKnob(node.knob(knob_name))

    # --- [ Paste Logic ] ---
    elif mode == 'paste':
        nuke.nodePaste('%clipboard%')
        
        nodes = nuke.selectedNodes()
        if not nodes:
            return

        for node in nodes:
            if CONNECTIONS_KNOB_NAME in node.knobs():
                data_string = node[CONNECTIONS_KNOB_NAME].value()
                connections = data_string.split(';')
                
                for conn in connections:
                    if ':' in conn:
                        try:
                            index_str, node_name = conn.split(':')
                            input_index = int(index_str)
                            target_node = nuke.toNode(node_name)
                            
                            if target_node:
                                node.setInput(input_index, target_node)
                            else:
                                pass
                                
                        except:
                            pass

            # --- [ Clean Up ] ---
            for knob_name in [CONNECTIONS_KNOB_NAME, COPIED_NODES_KNOB_NAME, TEMP_TAB_NAME]:
                if knob_name in node.knobs():
                    node.removeKnob(node.knob(knob_name))