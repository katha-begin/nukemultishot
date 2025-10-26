#==============================================================================
#                           ---- About ----
#==============================================================================
"""
    DESCRIPTION: This script allows you to scale node positions relative to each other
                 Scaling can be done in biased or center modes
                 Scaling is relative to the Node Graphs zoom level
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

# --- [  Import PySide based on nuke version ] --- 
if nuke.NUKE_VERSION_MAJOR < 11:
    from PySide import QtCore, QtGui
    QtWidgets = QtGui
elif nuke.NUKE_VERSION_MAJOR < 16:
    from PySide2 import QtWidgets, QtCore, QtGui
else:
    from PySide6 import QtWidgets, QtCore, QtGui

#===============================================================================
#                       ---- Globals ----
#===============================================================================

# --- [ Cache for original positions and sizes ] ---
_og_cache = {}

# --- [ Default settings for biased mode scaling ] ---
_h_center = 'left'
_v_center = 'top'

# --- [ directional flags, for biased and center modes ] ---
_AXIS_FLAGS = {
    'bdwidth':         (True,  False),
    'bdwidth_center':  (True,  False),
    'bdheight':        (False, True),
    'bdheight_center': (False, True),
    'bdboth_center':   (True,  True),
    'bdboth_top':      (True,  True),
    'bdboth_bottom':   (True,  True),
}

#===============================================================================
#                       ---- Scripts ----
#===============================================================================

def scale_node_dimensions(mode='increase', direction='bdwidth'):
    """
    mode:      'increase' or 'decrease'
    direction: one of keys in _AXIS_FLAGS

    Scales selected nodes up or down based on mode
    What to scale (width/height) determined by _AXIS_FLAGS. This is used to bind hotkeys to certain functions
    In biased scaling, where to scale from is determined by the _h_center and _v_center globals
    """
    global _og_cache, _h_center, _v_center

    if direction not in _AXIS_FLAGS:
        raise ValueError("Unknown direction: %s" % direction)

    sel = nuke.selectedNodes()
    if not sel:
        return
    bd_sel = [n for n in sel if n.Class() == 'BackdropNode']
    node_sel = [n for n in sel if n.Class() != 'BackdropNode']

    # --- [ Makes scale delta relative to zoom level ] ---
    zoom = nuke.zoom()
    delta = int(10.0 / zoom) * (-1 if mode == 'decrease' else 1)

    axis_w, axis_h = _AXIS_FLAGS[direction]

    # --- [ Invert horizontal delta if _h_center = right for width adjustments
    if axis_w and direction.startswith('bdwidth') and _h_center == 'right':
        delta = -delta
    # --- [ Invert vertical delta for bdheight if _v_center = bottom ] ---
    if axis_h and direction == 'bdheight' and _v_center == 'bottom':
        delta = -delta

    # --- [ Determine center pivot ] ---
    if direction == 'bdwidth':
        px = 0.0 if _h_center == 'left' else 1.0
        py = 0.0
    elif direction == 'bdwidth_center':
        px, py = 0.5, 0.0
    elif direction == 'bdheight':
        px = 0.0
        py = 0.0 if _v_center == 'top' else 1.0
    elif direction == 'bdheight_center':
        px, py = 0.0, 0.5
    elif direction == 'bdboth_center':
        px, py = 0.5, 0.5
    elif direction in ('bdboth_top', 'bdboth_bottom'):
        px = 0.0 if _h_center == 'left' else 1.0
        py = 0.0 if _v_center == 'top' else 1.0

    # --- [ Cache Update ] ---
    key = (tuple(sel), mode, direction, _h_center, _v_center)
    if _og_cache.get('key') != key:
        _og_cache.clear()
        _og_cache['key'] = key
        _og_cache['orig_bd'] = {
            bd: (bd.xpos(), bd.ypos(), bd['bdwidth'].value(), bd['bdheight'].value())
            for bd in bd_sel
        }
        _og_cache['orig_ctr'] = {
            n: (n.xpos() + n.screenWidth() / 2.0,
                n.ypos() + n.screenHeight() / 2.0)
            for n in node_sel
        }
        # --- [ Compute BBox ] ---
        xs, ys, xws, yhs = [], [], [], []
        for x, y, w, h in _og_cache['orig_bd'].values():
            xs.append(x); ys.append(y)
            xws.append(x + w); yhs.append(y + h)
        for cx, cy in _og_cache['orig_ctr'].values():
            xs.append(cx); ys.append(cy)
            xws.append(cx); yhs.append(cy)
        box_x0, box_y0 = min(xs), min(ys)
        orig_w = max(xws) - box_x0
        orig_h = max(yhs) - box_y0
        _og_cache['orig_bbox'] = (box_x0, box_y0, orig_w, orig_h)
        _og_cache['curr_w'], _og_cache['curr_h'] = orig_w, orig_h

    # --- [ Retrieve Cache ] ---
    orig_bd = _og_cache['orig_bd']
    orig_ctr = _og_cache['orig_ctr']
    box_x0, box_y0, orig_w, orig_h = _og_cache['orig_bbox']
    curr_w, curr_h = _og_cache['curr_w'], _og_cache['curr_h']

    new_w = curr_w + delta if axis_w else curr_w
    new_h = curr_h + delta if axis_h else curr_h
    if axis_w: new_w = max(25, new_w)
    if axis_h: new_h = max(25, new_h)

    scale_w = new_w / orig_w if orig_w else 1.0
    scale_h = new_h / orig_h if orig_h else 1.0

    # --- [ Absolute Center ] ---
    px_abs = box_x0 + px * orig_w
    py_abs = box_y0 + py * orig_h

    # --- [ Scale Backdrops ] ---
    for bd, (ox, oy, ow, oh) in orig_bd.items():
        if axis_w: bd['bdwidth'].setValue(ow * scale_w)
        if axis_h: bd['bdheight'].setValue(oh * scale_h)
        nx = px_abs + (ox - px_abs) * scale_w
        ny = py_abs + (oy - py_abs) * scale_h
        bd.setXpos(int(round(nx)))
        bd.setYpos(int(round(ny)))

    # --- [ Scale Nodes ] ---
    for n, (cx, cy) in orig_ctr.items():
        ncx = px_abs + (cx - px_abs) * scale_w
        ncy = py_abs + (cy - py_abs) * scale_h
        w, h = n.screenWidth(), n.screenHeight()
        n.setXpos(int(round(ncx - w / 2.0)))
        n.setYpos(int(round(ncy - h / 2.0)))

    _og_cache['curr_w'], _og_cache['curr_h'] = new_w, new_h


class NodeGraphBuddySettingsDialog(QtWidgets.QDialog):
    """Settings Panel For Choosing Biased Modes Center Scaling Point"""
    def __init__(self, parent=None):
        super(NodeGraphBuddySettingsDialog, self).__init__(parent)
        self.setWindowTitle("NodeGraphBuddy Scale - Settings")
        layout = QtWidgets.QVBoxLayout()

        settings_label = QtWidgets.QLabel("Biased Scale:\nChoose Scale Direction")
        font = QtGui.QFont()
        font.setBold(True)
        settings_label.setFont(font)
        layout.addWidget(settings_label)

        form_layout = QtWidgets.QFormLayout()
        
        # --- [ Horizontal Center ] ---
        self.h_combo = QtWidgets.QComboBox()
        self.h_combo.addItems(["Left To Right", "Right To Left"])
        self.h_combo.setCurrentIndex(0 if _h_center == 'left' else 1)
        form_layout.addRow("Horizontal:", self.h_combo)
        
        # --- [ Vertical Center ] ---
        self.v_combo = QtWidgets.QComboBox()
        self.v_combo.addItems(["Top To Bottom", "Bottom To Top"])
        self.v_combo.setCurrentIndex(0 if _v_center == 'top' else 1)
        form_layout.addRow("Vertical:", self.v_combo)
        layout.addLayout(form_layout)

        btn_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

        self.setLayout(layout)

    def getValues(self):
        """Gets Panel Values"""
        h_val = 'left' if self.h_combo.currentText() == 'Left To Right' else 'right'
        v_val = 'top' if self.v_combo.currentText() == 'Top To Bottom' else 'bottom'
        return h_val, v_val


def scale_node_dimension_settings():
    """Launches Settings Panel"""
    global _h_center, _v_center
    parent = nuke.mainWindow() if hasattr(nuke, 'mainWindow') else None
    dialog = NodeGraphBuddySettingsDialog(parent)
    if dialog.exec_() == QtWidgets.QDialog.Accepted:
        _h_center, _v_center = dialog.getValues()