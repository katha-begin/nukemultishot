#==============================================================================
#                           ---- About ----
#==============================================================================
"""
    DESCRIPTION: This script collects all the various buddy system features
                 and binds them to hotkeys and/or menu items    
    AUTHOR:      Hiram Gifford
    CONTACT:     hiramgifford.com
"""
VERSION = "01.03"
PUBLISH_DATE = "2025-09-21"
DOCUMENTATION = "https://www.hiramgifford.com/buddy-system"

#==============================================================================
#                       ---- How To Install ----
#==============================================================================
"""
    Step #1:    Copy folder into your .nuke directory e.g. "C:/Users/Hiram/.nuke" (this folder might be hidden)
    Step #2:    Put the line below in your menu.py
    
                    nuke.pluginAddPath('./BuddySystem')
                    
    Step #3:    Launch nuke and you should see a new tool bar item called "BuddySystem"

    Issues:     Please report issues via the contact forum, and provide the following information:
                    1) nuke version e.g. -> 12.2v11
                    2) BuddySystem version e.g. -> 01.00.00
                    3) operating system e.g. -> Windows, Linux, Mac
                    4) What feature you were trying to use at the time of the error
                    5) The error you see in the terminal and/or script editor
"""
#===============================================================================
#                        ---- Imports ----
#===============================================================================

import nuke
import nukescripts
import webbrowser

#===============================================================================
#                   ---- Variables & Menus ----
#===============================================================================
"""
Add required directories
If your pipeline doesn't allow for new plugin paths, contact your TDs for help 
"""
nuke.pluginAddPath('./Icons')
nuke.pluginAddPath('./Scripts')
nuke.pluginAddPath('./Tools')

"""Create buddy system menu item"""
if nuke.NUKE_VERSION_MAJOR < 11:
    toolbar = nuke.menu('Nodes')
    buddySystem = toolbar.addMenu('BuddySystem', icon = "BuddySystemIcon.png")
else:
    buddySystem = toolbar.addMenu('BuddySystem', icon = "BuddySystemIcon.png")

#===============================================================================
#              ---- NodeGraphBuddy Scripts & Hotkeys ----
#===============================================================================
"""
You can change the hotkeys here, just swap the binding near the end of each line 
If you prefer to not use hotkeys, leave the binding empty e.g. -> ''
"""

#---------------------------------[ Adjust - Distribute And Align ]-----------------------------------

import node_graph_buddy_distribute_nodes
buddySystem.addCommand('Scripts/Adjust/                 --- Distribute | Align ---', 'webbrowser.open("https://www.hiramgifford.com/buddy-system/node-graph-buddy#distribute-align-anchor-link")')
buddySystem.addCommand('Scripts/Adjust/Distribute | Align', 'node_graph_buddy_distribute_nodes.auto_distribute_nodes(align=True, process_clusters=False)', '*')
buddySystem.addCommand('Scripts/Adjust/Distribute | Align By Cluster', 'node_graph_buddy_distribute_nodes.auto_distribute_nodes(align=True, process_clusters=True)', 'Shift+*')

import node_graph_buddy_align_nodes
buddySystem.addCommand('Scripts/Adjust/Align | Stack | Match Vertically', 'node_graph_buddy_align_nodes.align_nodes_advanced(align_direction="vertical", stack_direction="right", align_direction_bd="right")', 'Right', shortcutContext=2)
buddySystem.addCommand('Scripts/Adjust/Align | Stack | Match Vertically Alt', 'node_graph_buddy_align_nodes.align_nodes_advanced(align_direction="vertical", stack_direction="left", align_direction_bd="left")', 'Left', shortcutContext=2)
buddySystem.addCommand('Scripts/Adjust/Align | Stack | Match Horizontally', 'node_graph_buddy_align_nodes.align_nodes_advanced(align_direction="horizontal", stack_direction="up", align_direction_bd="top")', 'Up', shortcutContext=2)
buddySystem.addCommand('Scripts/Adjust/Align | Stack | Match Horizontally Alt', 'node_graph_buddy_align_nodes.align_nodes_advanced(align_direction="horizontal", stack_direction="down", align_direction_bd="bottom")', 'Down', shortcutContext=2)

import node_graph_buddy_align_nodes_upstream
buddySystem.addCommand('Scripts/Adjust/Align Upstream', 'node_graph_buddy_align_nodes_upstream.align_upstream_nodes()', 'PgUp', shortcutContext=2)

#---------------------------------[ Adjust - Mirror ]-----------------------------------

import node_graph_buddy_mirror_nodes
buddySystem.addCommand('Scripts/Adjust/                 --- Mirror ---', 'webbrowser.open("https://www.hiramgifford.com/buddy-system/node-graph-buddy#mirror-anchor-link")')
buddySystem.addCommand('Scripts/Adjust/Mirror Horizontally', 'node_graph_buddy_mirror_nodes.mirror_nodes(direction="horizontal")', 'Alt+M')
buddySystem.addCommand('Scripts/Adjust/Mirror Vertically', 'node_graph_buddy_mirror_nodes.mirror_nodes(direction="vertical")', 'Ctrl+Alt+M')

#---------------------------------[ Adjust - Backdrops ]-----------------------------------

import node_graph_buddy_adjust_backdrops
buddySystem.addCommand('Scripts/Adjust/                 --- Backdrops ---', 'webbrowser.open("https://www.hiramgifford.com/buddy-system/node-graph-buddy#resize-backdrop-anchor-link")')
buddySystem.addCommand('Scripts/Adjust/Increase Z Order', 'node_graph_buddy_adjust_backdrops.adjust_z_order(mode="Increase")', 'Ctrl+Shift+Alt++')
buddySystem.addCommand('Scripts/Adjust/Decrease Z Order', 'node_graph_buddy_adjust_backdrops.adjust_z_order(mode="Decrease")', 'Ctrl+Shift+Alt+-')
buddySystem.addCommand('Scripts/Adjust/Increase Font Size', 'node_graph_buddy_adjust_backdrops.adjust_font_size(mode="Increase")', 'Ctrl+Shift+Alt+PgUp')
buddySystem.addCommand('Scripts/Adjust/Decrease Font Size', 'node_graph_buddy_adjust_backdrops.adjust_font_size(mode="Decrease")', 'Ctrl+Shift+Alt+PgDown')
buddySystem.addCommand('Scripts/Adjust/Resize Backdrop to Nodes', 'node_graph_buddy_adjust_backdrops.resize_backdrop(padding=100)', 'Ctrl+Shift+Alt+*')
buddySystem.addCommand('Scripts/Adjust/Sort Z Order By Size', 'node_graph_buddy_adjust_backdrops.sort_backdrops_by_size_and_zorder()', 'Ctrl+Shift+Alt+Z')

#---------------------------------[ Scale - Biased ]-----------------------------------

import node_graph_buddy_scale_nodes
buddySystem.addCommand('Scripts/Scale/                 --- Scale: Biased ---', 'webbrowser.open("https://www.hiramgifford.com/buddy-system/node-graph-buddy#scale-biased-anchor-link")')
buddySystem.addCommand('Scripts/Scale/Decrease Height', 'node_graph_buddy_scale_nodes.scale_node_dimensions(mode="decrease", direction="bdheight")', 'Ctrl+Shift+Up', shortcutContext=2)
buddySystem.addCommand('Scripts/Scale/Increase Height', 'node_graph_buddy_scale_nodes.scale_node_dimensions(mode="increase", direction="bdheight")', 'Ctrl+Shift+Down', shortcutContext=2)
buddySystem.addCommand('Scripts/Scale/Decrease Width', 'node_graph_buddy_scale_nodes.scale_node_dimensions(mode="decrease", direction="bdwidth")', 'Ctrl+Shift+Left', shortcutContext=2)
buddySystem.addCommand('Scripts/Scale/Increase Width', 'node_graph_buddy_scale_nodes.scale_node_dimensions(mode="increase", direction="bdwidth")', 'Ctrl+Shift+Right', shortcutContext=2)
buddySystem.addCommand('Scripts/Scale/Increase Uniform', 'node_graph_buddy_scale_nodes.scale_node_dimensions(mode="increase", direction="bdboth_top")', 'Ctrl+Shift++', shortcutContext=2)
buddySystem.addCommand('Scripts/Scale/Decrease Uniform', 'node_graph_buddy_scale_nodes.scale_node_dimensions(mode="decrease", direction="bdboth_bottom")', 'Ctrl+Shift+-', shortcutContext=2)
buddySystem.addCommand('Scripts/Scale/Settings', 'node_graph_buddy_scale_nodes.scale_node_dimension_settings()', 'Ctrl+Shift+Home', shortcutContext=2)

#---------------------------------[ Scale - Center ]-----------------------------------

buddySystem.addCommand('Scripts/Scale/                 --- Scale: Center ---', 'webbrowser.open("https://www.hiramgifford.com/buddy-system/node-graph-buddy#scale-center-anchor-link")')
buddySystem.addCommand('Scripts/Scale/Decrease Scale Height', 'node_graph_buddy_scale_nodes.scale_node_dimensions(mode="increase", direction="bdheight_center")', 'Shift+Up', shortcutContext=2)
buddySystem.addCommand('Scripts/Scale/Increase Scale Height', 'node_graph_buddy_scale_nodes.scale_node_dimensions(mode="decrease", direction="bdheight_center")', 'Shift+Down', shortcutContext=2)
buddySystem.addCommand('Scripts/Scale/Decrease Scale Width', 'node_graph_buddy_scale_nodes.scale_node_dimensions(mode="decrease", direction="bdwidth_center")', 'Shift+Left', shortcutContext=2)
buddySystem.addCommand('Scripts/Scale/Increase Scale Width', 'node_graph_buddy_scale_nodes.scale_node_dimensions(mode="increase", direction="bdwidth_center")', 'Shift+Right', shortcutContext=2)
buddySystem.addCommand('Scripts/Scale/Increase Scale Uniform', 'node_graph_buddy_scale_nodes.scale_node_dimensions(mode="increase", direction="bdboth_center")', 'Shift++', shortcutContext=2)
buddySystem.addCommand('Scripts/Scale/Decrease Scale Uniform', 'node_graph_buddy_scale_nodes.scale_node_dimensions(mode="decrease", direction="bdboth_center")', 'Shift+-', shortcutContext=2)

#---------------------------------[ Create ]-----------------------------------

import node_graph_buddy_create_backdrop
buddySystem.addCommand('Scripts/Create/Create Blur Or Backdrop', 'node_graph_buddy_create_backdrop.create_backdrop(advanced=False)', 'B')
buddySystem.addCommand('Scripts/Create/Create Blur Or Backdrop Advanced', 'node_graph_buddy_create_backdrop.create_backdrop(advanced=True)', 'Shift+B')

#---------------------------------[ Utilities - General ]-----------------------------------

buddySystem.addCommand('Scripts/Utilities/                 --- General ---', 'webbrowser.open("https://www.hiramgifford.com/buddy-system/node-graph-buddy#utilities")')
import node_graph_buddy_smart_select_all
buddySystem.addCommand('Scripts/Utilities/Smart Select All', 'node_graph_buddy_smart_select_all.smart_select_all(select_contents=True)', 'Ctrl+A', shortcutContext=2)
buddySystem.addCommand('Scripts/Utilities/Smart Select Backdrops', 'node_graph_buddy_smart_select_all.smart_select_all(select_contents=False)', 'Ctrl+Shift+A', shortcutContext=2)

import node_graph_buddy_label_node
buddySystem.addCommand('Scripts/Utilities/Set Node Label', 'node_graph_buddy_label_node.label_and_recenter_nodes(auto_case=True)', 'A', shortcutContext=2)

import node_graph_buddy_copy_paste_reconnect
buddySystem.addCommand('Scripts/Utilities/Copy Reconnect', 'node_graph_buddy_copy_paste_reconnect.copy_paste_reconnect(mode="copy")', 'Ctrl+Alt+Shift+C')
buddySystem.addCommand('Scripts/Utilities/Paste Reconnect', 'node_graph_buddy_copy_paste_reconnect.copy_paste_reconnect(mode="paste")', 'Ctrl+Alt+Shift+V')

import node_graph_buddy_paste_to_multiple
buddySystem.addCommand('Scripts/Utilities/Paste To Multiple', 'node_graph_buddy_paste_to_multiple.multipaste_and_select()', 'Shift+V')

import node_graph_buddy_toggle_disable
buddySystem.addCommand('Scripts/Utilities/Toggle Disable', 'node_graph_buddy_toggle_disable.toggle_disable()', 'Shift+D')


#---------------------------------[ Utilities - Panels ]-----------------------------------

buddySystem.addCommand('Scripts/Utilities/                 --- Panels ---', 'webbrowser.open("https://www.hiramgifford.com/buddy-system/node-graph-buddy#write-node-manager-anchor-link")')
import node_graph_buddy_write_node_manager
nuke.menu('Pane').addCommand('NodeGraphBuddy - Write Node Manager', "nukescripts.panels.restorePanel('hg.buddysystem.WriteNodeManager')")
nukescripts.panels.registerWidgetAsPanel('node_graph_buddy_write_node_manager.WriteOrderPanel', 'NodeGraphBuddy - Write Node Manager', 'hg.buddysystem.WriteNodeManager')
buddySystem.addCommand('Scripts/Utilities/Write Node Manager', 'node_graph_buddy_write_node_manager.show_floating_panel()','Ctrl+Shift+W')

import node_graph_buddy_bbox_manager
nuke.menu('Pane').addCommand('NodeGraphBuddy - BBox Manager', "nukescripts.panels.restorePanel('hg.buddysystem.BBoxManager')")
nukescripts.panels.registerWidgetAsPanel('node_graph_buddy_bbox_manager.BoundingBoxInfoPanel', 'NodeGraphBuddy - BBox Manager', 'hg.buddysystem.BBoxManager')
buddySystem.addCommand('Scripts/Utilities/BBox Manager', 'node_graph_buddy_bbox_manager.show_floating_panel()','')

import node_graph_buddy_nodeoriety_node_counter 
nuke.menu('Pane').addCommand('NodeGraphBuddy - Nodeoriety Node Counter', "nukescripts.panels.restorePanel('hg.buddysystem.Nodeoriety')")
nukescripts.panels.registerWidgetAsPanel('node_graph_buddy_nodeoriety_node_counter.NodeorietyPanel', 'NodeGraphBuddy - Nodeoriety Node Counter', 'hg.buddysystem.Nodeoriety')
buddySystem.addCommand('Scripts/Utilities/Nodeoriety Node Counter', 'node_graph_buddy_nodeoriety_node_counter.show_floating_panel()','')

#===============================================================================
#                           ---- Buddy Tools ----
#===============================================================================

#---------------------------------[ ! Warning ! ]-----------------------------------
"""
BuddySystem Tools are stored as Grizmos (Gizmofied Groups) for easy importing, but should not be turned into proper gizmos
If you turn these tools into Gizmos many of the dynamic knobs, and features will no work properly. Please leave them as Grizmos, or groups

You can change the hotkeys here, just modify the bindings at the end of each line
If you prefer to tab search and not use hotkeys, leave the binding empty e.g. -> ''
"""
buddySystem.addCommand('Tools/AnimBuddy', 'nuke.createNode("AnimBuddy")', 'Alt+Shift+A')
buddySystem.addCommand('Tools/CardBuddy', 'nuke.createNode("CardBuddy")', 'Alt+Shift+C')
buddySystem.addCommand('Tools/DepthBuddy', 'nuke.createNode("DepthBuddy")', 'Alt+Shift+Z')
buddySystem.addCommand('Tools/MaskBuddy', 'nuke.createNode("MaskBuddy")', 'Alt+Shift+M')
buddySystem.addCommand('Tools/ProjectionBuddy', 'nuke.createNode("ProjectionBuddy")', 'Alt+Shift+P')
buddySystem.addCommand('Tools/ReflectionBuddy', 'nuke.createNode("ReflectionBuddy")', 'Alt+Shift+R')

#===============================================================================
#                           ---- Fun Stuff ----
#===============================================================================

import fun_rotate_nodes
buddySystem.addCommand('Fun/Rotate Nodes', 'fun_rotate_nodes.rotate_nodes()', '')

import fun_node_randomizer
buddySystem.addCommand('Fun/Node Randomizer', 'fun_node_randomizer.show_randomize_panel()', '')

import fun_caesar_shift
buddySystem.addCommand('Fun/Caesar Shift Labels', 'fun_caesar_shift.show_caesar_shift_label()', '')

#===============================================================================
#                    ---- Documentation | Version ----
#===============================================================================

buddySystem.addSeparator()

"""Opens the documentation URL in your default web browser"""
buddySystem.addCommand('Documentation', 'webbrowser.open(DOCUMENTATION)')

"""Displays the version number and other info"""
buddySystem.addCommand("Version " + VERSION, 'nuke.message("""BuddySystem \nVersion {0} | {1} \n<a href="https://www.hiramgifford.com/"><font color=#b16ec2>hiramgifford.com</font></a>""")'.format(VERSION, PUBLISH_DATE))