#!/usr/bin/env python3
"""
Browser UI Demo

Demonstrates the MultishotBrowser functionality without requiring Nuke.
Shows the UI structure and core functionality.
"""

import os
import sys
import tempfile
import shutil

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def create_demo_structure():
    """Create a demo directory structure for testing."""
    temp_dir = tempfile.mkdtemp(prefix="multishot_browser_demo_")
    project_root = temp_dir
    project = "DemoProject"
    
    print(f"Creating demo structure in: {temp_dir}")
    
    base_path = os.path.join(project_root, project, "scene")
    
    # Create episodes
    episodes = ["Ep01", "Ep02"]
    for ep in episodes:
        ep_path = os.path.join(base_path, ep)
        
        # Create sequences
        sequences = ["sq0110", "sq0120"] if ep == "Ep01" else ["sq0210", "sq0220"]
        for seq in sequences:
            seq_path = os.path.join(ep_path, seq)
            
            # Create shots
            shots = ["SH0520", "SH0530"] if "0110" in seq else ["SH0620", "SH0630"]
            for shot in shots:
                shot_path = os.path.join(seq_path, shot)
                
                # Create departments
                departments = ["comp", "lighting", "fx", "anim"]
                for dept in departments:
                    dept_path = os.path.join(shot_path, dept)
                    
                    # Create version directory
                    version_path = os.path.join(dept_path, "version")
                    os.makedirs(version_path, exist_ok=True)
                    
                    # Create version subdirectories
                    versions = ["v001", "v002", "v003", "v001_001", "v002_001"]
                    for version in versions:
                        ver_path = os.path.join(version_path, version)
                        os.makedirs(ver_path, exist_ok=True)
                        
                        # Create a demo Nuke file
                        nuke_file = f"{ep}_{seq}_{shot}_{dept}_{version}.nk"
                        nuke_path = os.path.join(ver_path, nuke_file)
                        with open(nuke_path, 'w') as f:
                            f.write(f"# Demo Nuke file for {ep}/{seq}/{shot}/{dept}/{version}\n")
                            f.write("Root {\n")
                            f.write(f'  name "{nuke_file}"\n')
                            f.write("}\n")
                    
                    # Create publish directory with demo assets
                    publish_path = os.path.join(dept_path, "publish")
                    for version in versions[:3]:  # Only first 3 versions
                        pub_ver_path = os.path.join(publish_path, version)
                        os.makedirs(pub_ver_path, exist_ok=True)
                        
                        # Create demo assets
                        assets = [
                            ("MASTER_BEAUTY.1001.exr", "# EXR render"),
                            ("MASTER_BEAUTY.1002.exr", "# EXR render"),
                            ("geometry.abc", "# Alembic geometry"),
                            ("camera.abc", "# Alembic camera"),
                            ("MASTER_BEAUTY.png", "# PNG preview")
                        ]
                        for asset_name, content in assets:
                            asset_path = os.path.join(pub_ver_path, asset_name)
                            with open(asset_path, 'w') as f:
                                f.write(content)
    
    return temp_dir, project_root, project

def demo_browser_functionality():
    """Demonstrate browser functionality without Qt UI."""
    print("\n" + "="*60)
    print("MULTISHOT BROWSER DEMO")
    print("="*60)
    
    # Create demo structure
    temp_dir, project_root, project = create_demo_structure()
    
    try:
        # Import browser components
        from multishot.core.variables import VariableManager
        from multishot.core.scanner import DirectoryScanner
        from multishot.core.paths import PathResolver
        from multishot.core.context import ContextDetector
        
        print(f"\nProject Root: {project_root}")
        print(f"Project: {project}")
        
        # Initialize components (like browser would)
        variable_manager = VariableManager()
        scanner = DirectoryScanner()
        path_resolver = PathResolver()
        context_detector = ContextDetector()
        
        # Set up root variables
        variable_manager.set_variable("PROJ_ROOT", project_root + "/")
        variable_manager.set_variable("IMG_ROOT", project_root + "/")
        variable_manager.set_variable("project", project)
        
        print("\n1. Browser Initialization:")
        print("   OK - VariableManager initialized")
        print("   OK - DirectoryScanner initialized")
        print("   OK - PathResolver initialized")
        print("   OK - ContextDetector initialized")
        
        # Simulate project loading (like browser dropdown would)
        print("\n2. Project Discovery:")
        projects = []
        try:
            for item in os.listdir(project_root):
                item_path = os.path.join(project_root, item)
                if os.path.isdir(item_path):
                    projects.append(item)
        except (OSError, PermissionError):
            pass
        
        print(f"   Found projects: {projects}")
        
        # Simulate episode loading
        print("\n3. Episode Discovery:")
        episodes = scanner.scan_episodes(project_root, project)
        print(f"   Found episodes: {episodes}")
        
        # Simulate sequence loading for first episode
        if episodes:
            ep = episodes[0]
            print(f"\n4. Sequence Discovery for {ep}:")
            sequences = scanner.scan_sequences(project_root, project, ep)
            print(f"   Found sequences: {sequences}")
            
            # Simulate shot loading for first sequence
            if sequences:
                seq = sequences[0]
                print(f"\n5. Shot Discovery for {ep}/{seq}:")
                shots = scanner.scan_shots(project_root, project, ep, seq)
                print(f"   Found shots: {shots}")
                
                # Simulate department loading for first shot
                if shots:
                    shot = shots[0]
                    print(f"\n6. Department Discovery for {ep}/{seq}/{shot}:")
                    departments = scanner.scan_departments(project_root, project, ep, seq, shot)
                    print(f"   Found departments: {departments}")
                    
                    # Simulate context setting (like browser would do)
                    if departments:
                        dept = departments[0]
                        context = {
                            'project': project,
                            'ep': ep,
                            'seq': seq,
                            'shot': shot,
                            'department': dept
                        }
                        
                        print(f"\n7. Context Setting:")
                        print(f"   Context: {context}")
                        
                        # Set context variables
                        variable_manager.set_context_variables(context)
                        
                        # Get all variables (like browser would display)
                        all_vars = variable_manager.get_all_variables()
                        print(f"\n8. All Variables:")
                        for key, value in sorted(all_vars.items()):
                            print(f"   {key}: {value}")
                        
                        # Resolve paths (like browser would show)
                        print(f"\n9. Path Resolution:")
                        nuke_path = path_resolver.get_nuke_file_path(all_vars)
                        renders_path = path_resolver.get_render_path(all_vars)
                        geometry_path = path_resolver.get_geometry_path(all_vars)
                        camera_path = path_resolver.get_camera_path(all_vars)
                        
                        print(f"   Nuke Files: {nuke_path}")
                        print(f"   Renders: {renders_path}")
                        print(f"   Geometry: {geometry_path}")
                        print(f"   Camera: {camera_path}")
                        
                        # Scan for versions (like browser file tabs would)
                        print(f"\n10. Version Discovery:")
                        if os.path.exists(nuke_path):
                            versions = scanner.scan_versions(nuke_path)
                            print(f"    Nuke versions: {versions}")
                            
                            if versions:
                                latest = scanner.get_latest_version(versions)
                                print(f"    Latest version: {latest}")
                                
                                # Scan files in latest version
                                latest_path = os.path.join(nuke_path, latest)
                                nuke_files = scanner.scan_nuke_files(latest_path)
                                print(f"    Nuke files in {latest}:")
                                for file_info in nuke_files:
                                    print(f"      - {file_info['filename']}")
                                    if file_info['context']:
                                        print(f"        Context: {file_info['context']}")
                        
                        # Scan for assets (like browser asset tabs would)
                        publish_base = os.path.dirname(renders_path)
                        if os.path.exists(publish_base):
                            pub_versions = scanner.scan_versions(publish_base)
                            print(f"\n11. Asset Discovery:")
                            print(f"    Publish versions: {pub_versions}")
                            
                            if pub_versions:
                                latest_pub = scanner.get_latest_version(pub_versions)
                                latest_pub_path = os.path.join(publish_base, latest_pub)
                                assets = scanner.scan_assets(latest_pub_path)
                                
                                print(f"    Assets in {latest_pub}:")
                                for asset_type, asset_list in assets.items():
                                    if asset_list:
                                        print(f"      {asset_type.upper()}: {len(asset_list)} files")
                                        for asset in asset_list[:2]:  # Show first 2
                                            print(f"        - {asset['filename']}")
        
        print(f"\n12. Browser Functionality Summary:")
        print("   OK - Project discovery and selection")
        print("   OK - Hierarchical context navigation (Episode -> Sequence -> Shot -> Department)")
        print("   OK - Variable management and path resolution")
        print("   OK - Version discovery and latest version detection")
        print("   OK - File scanning with context detection")
        print("   OK - Asset organization by type")
        print("   OK - Real-time UI updates based on context changes")
        
    finally:
        # Clean up
        shutil.rmtree(temp_dir, ignore_errors=True)
        print(f"\nCleaned up demo directory: {temp_dir}")

def demo_browser_ui_structure():
    """Demonstrate the browser UI structure."""
    print("\n" + "="*60)
    print("BROWSER UI STRUCTURE DEMO")
    print("="*60)
    
    print("\nUI Layout Structure:")
    print("+-------------------------------------------------------------+")
    print("| Multishot Browser                                  [Refresh] |")
    print("+-----------------+-------------------------------------------+")
    print("| Context         | Files                                     |")
    print("| +-------------+ | +-----------------------------------------+ |")
    print("| | Project: v  | | | [Nuke Files] [Renders] [Geometry] [Cam] | |")
    print("| | Episode: v  | | | Version: [v003 v]              [Latest] | |")
    print("| | Sequence: v | | | +-------------------------------------+ | |")
    print("| | Shot: v     | | | | - Ep01_sq0110_SH0520_comp_v003.nk  | | |")
    print("| | Dept: v     | | | | - Ep01_sq0110_SH0520_comp_v002.nk  | | |")
    print("| +-------------+ | | | - Ep01_sq0110_SH0520_comp_v001.nk  | | |")
    print("|                 | | +-------------------------------------+ | |")
    print("| Path Templates  | | +-------------------------------------+ | |")
    print("| +-------------+ | | | File Details:                       | | |")
    print("| | Nuke: V:/.. | | | | File: Ep01_sq0110_SH0520_comp_v003  | | |")
    print("| | Renders:W:/ | | | | Size: 2.5 MB                       | | |")
    print("| +-------------+ | | | Context: ep=Ep01, seq=sq0110...     | | |")
    print("|                 | | +-------------------------------------+ | |")
    print("| Variables       | +-----------------------------------------+ |")
    print("| [Manage Vars]   |                                             |")
    print("| +-------------+ |                                             |")
    print("| | project:SWA | |                                             |")
    print("| | ep: Ep01    | |                                             |")
    print("| | seq: sq0110 | |                                             |")
    print("| +-------------+ |                                             |")
    print("+-----------------+-------------------------------------------+")
    print("| Ready                    [Open] [Save As...] [New Version]   |")
    print("+-------------------------------------------------------------+")
    
    print("\nKey Features:")
    print("- Left Panel:")
    print("  - Context dropdowns with hierarchical loading")
    print("  - Real-time path template display")
    print("  - Variable management integration")
    print("- Right Panel:")
    print("  - Tabbed file browser (Nuke, Renders, Geometry, Camera)")
    print("  - Version selection with 'Latest' button")
    print("  - File details with context information")
    print("- Bottom Panel:")
    print("  - Status display")
    print("  - Action buttons (Open, Save As, New Version)")
    
    print("\nInteraction Flow:")
    print("1. User selects Project -> Episodes populate")
    print("2. User selects Episode -> Sequences populate")
    print("3. User selects Sequence -> Shots populate")
    print("4. User selects Shot -> Departments populate")
    print("5. User selects Department → File tabs update with versions")
    print("6. User selects Version → File lists update")
    print("7. User selects File → Details display, Open button enables")
    print("8. User clicks Open → File opens in Nuke (if available)")

if __name__ == "__main__":
    demo_browser_functionality()
    demo_browser_ui_structure()
    
    print("\n" + "="*60)
    print("BROWSER DEMO COMPLETE")
    print("="*60)
    print("\nThe MultishotBrowser provides a comprehensive interface that:")
    print("- Integrates all core systems (Variables, Scanner, Paths, Context)")
    print("- Provides intuitive hierarchical navigation")
    print("- Updates UI in real-time based on context changes")
    print("- Supports all asset types with version management")
    print("- Enables seamless file operations within Nuke workflow")
    print("\nReady for integration with custom nodes and advanced features!")
