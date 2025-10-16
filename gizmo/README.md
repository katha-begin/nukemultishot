# Gizmo Directory (Tier 1 - Repository Level)

This directory contains **repository-level gizmos** that are shared across all projects.

## 📁 Directory Structure

```
gizmo/
├── README.md (this file)
├── Compositing/          # Compositing-related gizmos
├── Color/                # Color correction gizmos
├── Keying/               # Keying and matte tools
├── Utilities/            # Utility gizmos
└── [YourCategory]/       # Custom categories
```

## 🎯 Purpose

**Tier 1 gizmos** are:
- Shared across ALL projects
- Version-controlled in the repository
- Available to all artists immediately after pulling the repo
- Registered automatically to: `Nuke → Multishot → Gizmos → Repository`

## 📝 How to Add a Gizmo

### Method 1: Export from Nuke

1. Create your custom Group node in Nuke
2. Select the Group node
3. Go to: `Edit → Node → Export as Gizmo...`
4. Save to this directory (or a subdirectory)
5. Restart Nuke or reload menu

### Method 2: Copy Existing .gizmo File

1. Copy your `.gizmo` file to this directory
2. Optionally organize into subdirectories by category
3. Restart Nuke or reload menu

## 📂 Organizing Gizmos

Create subdirectories to organize gizmos by category:

```
gizmo/
├── Compositing/
│   ├── EdgeExtend.gizmo
│   └── SmartMerge.gizmo
├── Color/
│   ├── ColorMatch.gizmo
│   └── LUTLoader.gizmo
└── Keying/
    ├── AdvancedKeyer.gizmo
    └── DespillPro.gizmo
```

These will appear in Nuke menu as:
```
Nuke → Multishot → Gizmos → Repository
    ├── Compositing
    │   ├── EdgeExtend
    │   └── SmartMerge
    ├── Color
    │   ├── ColorMatch
    │   └── LUTLoader
    └── Keying
        ├── AdvancedKeyer
        └── DespillPro
```

## 🔄 Auto-Registration

Gizmos in this directory are automatically registered when Nuke starts.

The registration happens in `init.py`:
```python
from multishot.utils.gizmo_loader import load_gizmos_and_toolsets
load_gizmos_and_toolsets()
```

## 🆚 Tier 1 vs Tier 2

| Feature | Tier 1 (This Directory) | Tier 2 (Project Library) |
|---------|-------------------------|--------------------------|
| **Location** | `/gizmo` (repo root) | `{root}/{project}/all/library/gizmo` |
| **Scope** | All projects | Specific project only |
| **Version Control** | Git repository | Project-specific |
| **Menu Path** | `Multishot/Gizmos/Repository` | `Multishot/Gizmos/Project` |
| **Use Case** | Studio-wide tools | Project-specific tools |

## 💡 Best Practices

1. **Naming Convention:**
   - Use descriptive names: `EdgeExtend.gizmo` not `tool1.gizmo`
   - Use PascalCase: `SmartMerge.gizmo`

2. **Documentation:**
   - Add tooltips to knobs in your gizmo
   - Include a description in the gizmo properties

3. **Testing:**
   - Test gizmo thoroughly before committing
   - Ensure it works in Nuke 14, 15, and 16

4. **Categories:**
   - Use standard categories when possible
   - Create new categories only when necessary

## 🚀 Example: Creating a Custom Gizmo

```python
# In Nuke Script Editor:

# 1. Create a Group node
group = nuke.nodes.Group()
group.begin()

# 2. Add internal nodes
input_node = nuke.nodes.Input()
blur = nuke.nodes.Blur()
blur.setInput(0, input_node)
output_node = nuke.nodes.Output()
output_node.setInput(0, blur)

group.end()

# 3. Add custom knobs
blur_knob = nuke.Double_Knob('blur_size', 'Blur Size')
blur_knob.setValue(10)
group.addKnob(blur_knob)

# 4. Export as gizmo
# Select the group, then:
# Edit → Node → Export as Gizmo...
# Save to: /path/to/repo/gizmo/Utilities/MyBlur.gizmo
```

## 📚 Additional Resources

- [Nuke Documentation - Creating Gizmos](https://learn.foundry.com/nuke/content/comp_environment/configuring_nuke/creating_gizmos.html)
- See `toolset/README.md` for toolset information
- See project library: `{root}/{project}/all/library/gizmo` for project-specific gizmos

