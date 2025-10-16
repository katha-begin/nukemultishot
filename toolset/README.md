# Toolset Directory (Tier 1 - Repository Level)

This directory contains **repository-level toolsets** that are shared across all projects.

## 📁 Directory Structure

```
toolset/
├── README.md (this file)
├── Compositing/          # Compositing node setups
├── Color/                # Color grading setups
├── Keying/               # Keying setups
├── Templates/            # Template node trees
└── [YourCategory]/       # Custom categories
```

## 🎯 Purpose

**Tier 1 toolsets** are:
- Shared across ALL projects
- Version-controlled in the repository
- Available to all artists immediately after pulling the repo
- Registered automatically to: `Nuke → Multishot → Toolsets → Repository`

## 📝 What is a Toolset?

A **toolset** is a saved collection of nodes (`.nk` file) that can be imported into any Nuke script.

**Differences from Gizmos:**
- **Gizmo:** Single node (Group) with custom interface
- **Toolset:** Multiple nodes with connections preserved

## 📝 How to Create a Toolset

### Method 1: Export from Nuke

1. Select the nodes you want to save as a toolset
2. Go to: `Edit → Node → Copy`
3. Create a new `.nk` file in this directory
4. Paste the nodes into the file
5. Save the file

### Method 2: Using Nuke's Export Feature

1. Select the nodes you want to save
2. Go to: `File → Export Nodes as Script...`
3. Save to this directory (or a subdirectory)
4. Restart Nuke or reload menu

### Method 3: Script Editor

```python
# Select nodes in Node Graph, then run:
import nuke

# Get selected nodes
selected = nuke.selectedNodes()

if selected:
    # Copy to clipboard
    nuke.nodeCopy('/path/to/repo/toolset/MyToolset.nk')
    print(f"Saved {len(selected)} nodes to toolset")
else:
    print("No nodes selected")
```

## 📂 Organizing Toolsets

Create subdirectories to organize toolsets by category:

```
toolset/
├── Compositing/
│   ├── BasicComp.nk
│   └── AdvancedComp.nk
├── Color/
│   ├── ColorGrade.nk
│   └── LookDev.nk
└── Keying/
    ├── GreenScreenSetup.nk
    └── BlueScreenSetup.nk
```

These will appear in Nuke menu as:
```
Nuke → Multishot → Toolsets → Repository
    ├── Compositing
    │   ├── BasicComp
    │   └── AdvancedComp
    ├── Color
    │   ├── ColorGrade
    │   └── LookDev
    └── Keying
        ├── GreenScreenSetup
        └── BlueScreenSetup
```

## 🔄 Auto-Registration

Toolsets in this directory are automatically registered when Nuke starts.

The registration happens in `init.py`:
```python
from multishot.utils.gizmo_loader import load_gizmos_and_toolsets
load_gizmos_and_toolsets()
```

## 🆚 Tier 1 vs Tier 2

| Feature | Tier 1 (This Directory) | Tier 2 (Project Library) |
|---------|-------------------------|--------------------------|
| **Location** | `/toolset` (repo root) | `{root}/{project}/all/library/toolset` |
| **Scope** | All projects | Specific project only |
| **Version Control** | Git repository | Project-specific |
| **Menu Path** | `Multishot/Toolsets/Repository` | `Multishot/Toolsets/Project` |
| **Use Case** | Studio-wide setups | Project-specific setups |

## 💡 Best Practices

1. **Naming Convention:**
   - Use descriptive names: `GreenScreenSetup.nk` not `setup1.nk`
   - Use PascalCase: `BasicComp.nk`

2. **Documentation:**
   - Add a Sticky note at the top explaining the toolset
   - Document any required inputs/outputs

3. **Relative Paths:**
   - Use expressions for file paths when possible
   - Avoid hardcoded absolute paths

4. **Testing:**
   - Test toolset in a clean script before committing
   - Ensure it works in Nuke 14, 15, and 16

5. **Dependencies:**
   - Document any required plugins or gizmos
   - Keep toolsets self-contained when possible

## 🚀 Example: Creating a Basic Comp Toolset

```python
# In Nuke Script Editor:

# 1. Create a basic comp setup
read = nuke.nodes.Read()
read['file'].setValue('[value root.IMG_ROOT]/[value root.project]/plate.%04d.exr')

grade = nuke.nodes.Grade()
grade.setInput(0, read)

blur = nuke.nodes.Blur()
blur.setInput(0, grade)

write = nuke.nodes.Write()
write.setInput(0, blur)
write['file'].setValue('[value root.IMG_ROOT]/[value root.project]/output.%04d.exr')

# 2. Select all nodes
for node in [read, grade, blur, write]:
    node.setSelected(True)

# 3. Export
nuke.nodeCopy('/path/to/repo/toolset/Compositing/BasicComp.nk')
```

## 📝 Example Toolset Content

Here's what a simple toolset `.nk` file looks like:

```tcl
# BasicComp.nk
set cut_paste_input [stack 0]
version 14.0 v5
Read {
 inputs 0
 file "\[value root.IMG_ROOT]/\[value root.project]/plate.%04d.exr"
 name Read1
}
Grade {
 name Grade1
}
Blur {
 size 10
 name Blur1
}
Write {
 file "\[value root.IMG_ROOT]/\[value root.project]/output.%04d.exr"
 name Write1
}
```

## 🎯 Common Toolset Examples

### 1. Green Screen Keying Setup
```
toolset/Keying/GreenScreenSetup.nk
- Read (plate)
- Keylight
- Despill
- EdgeBlur
- Premult
- Merge (over background)
```

### 2. Color Grading Setup
```
toolset/Color/ColorGrade.nk
- Read (input)
- ColorCorrect (shadows)
- ColorCorrect (midtones)
- ColorCorrect (highlights)
- Saturation
- Write (output)
```

### 3. Basic Comp Template
```
toolset/Templates/BasicComp.nk
- Read (background)
- Read (foreground)
- Grade (foreground)
- Merge
- Write (output)
```

## 📚 Additional Resources

- [Nuke Documentation - Node Presets](https://learn.foundry.com/nuke/content/comp_environment/configuring_nuke/creating_node_presets.html)
- See `gizmo/README.md` for gizmo information
- See project library: `{root}/{project}/all/library/toolset` for project-specific toolsets

## 🔧 Troubleshooting

**Toolset not appearing in menu?**
1. Check file extension is `.nk`
2. Restart Nuke
3. Check console for errors

**Toolset has broken paths?**
1. Use expressions instead of absolute paths
2. Use `[value root.variable]` syntax
3. Test in a clean script before saving

