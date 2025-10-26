# Third-Party Gizmo Integration Plan

## 📦 Packages to Integrate

### **1. Nuke Survival Toolkit (NST)**
- **Location:** `gizmo/NukeSurvivalToolkit/`
- **Version:** v2.1.0
- **Author:** Tony Lyons (CreativeLyons)
- **Gizmos:** 200+ gizmos
- **Structure:**
  - `gizmos/` - 200+ .gizmo files
  - `icons/` - Icon files
  - `images/` - Image resources
  - `python/` - Python helper scripts
  - `nk_files/` - Expression nodes and templates
  - `init.py` - Empty (commented out)
  - `menu.py` - Main menu setup script

### **2. BuddySystem**
- **Location:** `gizmo/BuddySystem/`
- **Version:** 01.03
- **Author:** Hiram Gifford
- **Tools:** 6 gizmo tools + 20+ scripts
- **Structure:**
  - `Tools/` - 6 .gizmo files (AnimBuddy, CardBuddy, DepthBuddy, MaskBuddy, ProjectionBuddy, ReflectionBuddy)
  - `Scripts/` - 15+ Python scripts for node graph utilities
  - `Icons/` - Icon files
  - `menu.py` - Main menu setup script

---

## 🎯 Integration Strategy

### **Approach: Plugin Path + Menu Execution**

Both packages are designed to be loaded via `nuke.pluginAddPath()` and have their own `menu.py` files that set up menus and hotkeys. We'll integrate them by:

1. **Add plugin paths** to make gizmos/scripts discoverable
2. **Execute menu.py files** to register menus and hotkeys
3. **Organize under Multishot menu** for consistency
4. **Preserve original functionality** - don't modify their code

---

## 📋 Implementation Plan

### **Phase 1: Enhanced Gizmo Loader**

Create `ThirdPartyGizmoLoader` class that:
- Detects third-party packages in `gizmo/` directory
- Adds plugin paths for each package
- Executes their `menu.py` files
- Tracks loaded packages

### **Phase 2: Package Detection**

Auto-detect packages by looking for:
- `menu.py` file (indicates a package)
- Package structure (gizmos/, icons/, etc.)

**Detected Packages:**
```
gizmo/
├── NukeSurvivalToolkit/  ← Has menu.py
│   ├── gizmos/
│   ├── icons/
│   ├── python/
│   └── menu.py
├── BuddySystem/          ← Has menu.py
│   ├── Tools/
│   ├── Scripts/
│   ├── Icons/
│   └── menu.py
└── (other gizmos)        ← Regular gizmos (existing loader)
```

### **Phase 3: Integration Points**

**In `multishot/__init__.py`:**
```python
def initialize():
    # ... existing code ...
    
    # Load third-party gizmo packages
    from .utils.gizmo_loader import load_third_party_packages
    load_third_party_packages()
    
    # Load regular gizmos and toolsets
    from .utils.gizmo_loader import load_gizmos_and_toolsets
    load_gizmos_and_toolsets(variable_manager)
```

---

## 🔧 Technical Details

### **NukeSurvivalToolkit Integration**

**What menu.py does:**
1. Adds plugin paths:
   ```python
   nuke.pluginAddPath('./gizmos')
   nuke.pluginAddPath('./python')
   nuke.pluginAddPath('./icons')
   nuke.pluginAddPath('./images')
   nuke.pluginAddPath('./nk_files')
   ```

2. Creates menu structure:
   ```python
   toolbar = nuke.menu('Nodes')
   m = toolbar.addMenu('NukeSurvivalToolkit', icon = "SurvivalToolkit.png")
   ```

3. Registers 200+ gizmos organized by category:
   - Image
   - Draw
   - Time
   - Channel
   - Color
   - Filter
   - Keyer
   - Merge
   - Transform
   - 3D
   - Particles
   - Deep
   - CG
   - Curves
   - Utilities

**Integration:**
- Add base path: `gizmo/NukeSurvivalToolkit/`
- Execute `menu.py` in that context
- Menu appears as: `Nodes → NukeSurvivalToolkit → ...`

---

### **BuddySystem Integration**

**What menu.py does:**
1. Adds plugin paths:
   ```python
   nuke.pluginAddPath('./Icons')
   nuke.pluginAddPath('./Scripts')
   nuke.pluginAddPath('./Tools')
   ```

2. Creates menu structure:
   ```python
   buddySystem = toolbar.addMenu('BuddySystem', icon = "BuddySystemIcon.png")
   ```

3. Registers tools and scripts:
   - **Tools:** 6 gizmos (AnimBuddy, CardBuddy, etc.)
   - **Scripts:** Node graph utilities with hotkeys
     - Adjust (distribute, align, mirror, backdrops)
     - Scale (biased, center)
     - Create (backdrop)
     - Utilities (select, label, copy/paste, panels)
     - Fun (rotate, randomizer, caesar shift)

**Integration:**
- Add base path: `gizmo/BuddySystem/`
- Execute `menu.py` in that context
- Menu appears as: `Nodes → BuddySystem → ...`

---

## 🎨 Menu Organization

### **Current Multishot Menu:**
```
Nodes
└── Multishot
    ├── Browser (Ctrl+Shift+M)
    ├── Manager
    ├── Variables
    ├── Gizmos
    │   ├── Repository
    │   └── Project
    └── Toolsets
        ├── Repository
        └── Project
```

### **After Integration:**
```
Nodes
├── Multishot
│   ├── Browser (Ctrl+Shift+M)
│   ├── Manager
│   ├── Variables
│   ├── Gizmos
│   │   ├── Repository
│   │   └── Project
│   └── Toolsets
│       ├── Repository
│       └── Project
├── NukeSurvivalToolkit  ← NEW (200+ gizmos)
│   ├── Documentation
│   ├── Image
│   ├── Draw
│   ├── Time
│   ├── Channel
│   ├── Color
│   ├── Filter
│   ├── Keyer
│   ├── Merge
│   ├── Transform
│   ├── 3D
│   ├── Particles
│   ├── Deep
│   ├── CG
│   ├── Curves
│   └── Utilities
└── BuddySystem          ← NEW (6 tools + scripts)
    ├── Tools
    │   ├── AnimBuddy (Alt+Shift+A)
    │   ├── CardBuddy (Alt+Shift+C)
    │   ├── DepthBuddy (Alt+Shift+Z)
    │   ├── MaskBuddy (Alt+Shift+M)
    │   ├── ProjectionBuddy (Alt+Shift+P)
    │   └── ReflectionBuddy (Alt+Shift+R)
    ├── Scripts
    │   ├── Adjust
    │   ├── Scale
    │   ├── Create
    │   └── Utilities
    └── Fun
```

---

## ⚠️ Important Considerations

### **1. Hotkey Conflicts**

**BuddySystem uses many hotkeys:**
- `B` - Create Blur Or Backdrop
- `Shift+B` - Create Blur Or Backdrop Advanced
- `A` - Set Node Label (shortcutContext=2)
- `Ctrl+A` - Smart Select All (shortcutContext=2)
- Arrow keys for alignment
- `Alt+Shift+[A/C/Z/M/P/R]` - Buddy tools

**Potential conflicts:**
- `Alt+Shift+M` - MaskBuddy vs potential Multishot hotkey
- Arrow keys - BuddySystem alignment vs Nuke defaults

**Solution:**
- Keep BuddySystem hotkeys as-is (they're well-designed)
- Document hotkeys in README
- Users can modify hotkeys in `BuddySystem/menu.py` if needed

### **2. Python Dependencies**

**NukeSurvivalToolkit:**
- Uses `NST_helper.py` for custom functions
- Uses `ColorGradientUi.py` for gradient editor
- All dependencies are included

**BuddySystem:**
- All scripts are self-contained
- Uses PySide/Qt for panels (Nuke 11+)

**Solution:**
- Both packages are self-contained
- No external dependencies needed

### **3. Icon Paths**

Both packages use relative icon paths:
- NST: `icon="SurvivalToolkit.png"`
- BuddySystem: `icon="BuddySystemIcon.png"`

**Solution:**
- Plugin paths handle this automatically
- Icons will load correctly

---

## 📝 Implementation Checklist

- [ ] Create `ThirdPartyGizmoLoader` class
- [ ] Add package detection logic
- [ ] Add plugin path registration
- [ ] Add menu.py execution
- [ ] Integrate into `multishot/__init__.py`
- [ ] Test NukeSurvivalToolkit loading
- [ ] Test BuddySystem loading
- [ ] Test hotkeys don't conflict
- [ ] Update documentation
- [ ] Create user guide for third-party gizmos

---

## 🚀 Benefits

### **For Users:**
1. **200+ Professional Gizmos** from NukeSurvivalToolkit
2. **Powerful Node Graph Tools** from BuddySystem
3. **One-Click Installation** - everything loads automatically
4. **Organized Menus** - clear separation of tools
5. **Preserved Functionality** - original features intact

### **For Pipeline:**
1. **Centralized Management** - all tools in one place
2. **Easy Updates** - just replace package folders
3. **Consistent Loading** - same mechanism for all tools
4. **No Manual Setup** - automatic integration

---

## 📚 Documentation Needs

### **User Documentation:**
1. **Third-Party Gizmos Guide**
   - What's included
   - How to use
   - Hotkey reference

2. **NukeSurvivalToolkit Guide**
   - Tool categories
   - Popular tools
   - Link to official docs

3. **BuddySystem Guide**
   - Node graph utilities
   - Hotkey reference
   - Panel tools

### **Technical Documentation:**
1. **Integration Architecture**
   - How packages are loaded
   - Plugin path system
   - Menu execution

2. **Adding New Packages**
   - Requirements
   - Folder structure
   - Testing

---

## 🎯 Success Criteria

- ✅ NukeSurvivalToolkit menu appears with all 200+ gizmos
- ✅ BuddySystem menu appears with all tools and scripts
- ✅ All hotkeys work correctly
- ✅ No conflicts with existing Multishot functionality
- ✅ Icons load correctly
- ✅ Python scripts execute without errors
- ✅ Documentation is complete and clear

---

**Ready to implement!** 🚀

