#!/usr/bin/env python3
"""
Directory Scanner Demo

Demonstrates the DirectoryScanner functionality for discovering
project structure and populating UI dropdowns.
"""

import os
import sys
import tempfile
import shutil

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from multishot.core.scanner import DirectoryScanner
from multishot.core.variables import VariableManager
from multishot.core.paths import PathResolver

def create_demo_structure():
    """Create a demo directory structure for testing."""
    temp_dir = tempfile.mkdtemp(prefix="multishot_demo_")
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

def demo_basic_scanning():
    """Demonstrate basic directory scanning functionality."""
    print("\n" + "="*60)
    print("DIRECTORY SCANNER DEMO")
    print("="*60)
    
    # Create demo structure
    temp_dir, project_root, project = create_demo_structure()
    
    try:
        # Initialize scanner
        scanner = DirectoryScanner(cache_timeout=60)  # 1 minute cache
        
        print(f"\nProject Root: {project_root}")
        print(f"Project: {project}")
        
        # Scan episodes
        print("\n1. Scanning Episodes:")
        episodes = scanner.scan_episodes(project_root, project)
        for ep in episodes:
            print(f"   - {ep}")
        
        # Scan sequences for first episode
        if episodes:
            ep = episodes[0]
            print(f"\n2. Scanning Sequences in {ep}:")
            sequences = scanner.scan_sequences(project_root, project, ep)
            for seq in sequences:
                print(f"   - {seq}")
            
            # Scan shots for first sequence
            if sequences:
                seq = sequences[0]
                print(f"\n3. Scanning Shots in {ep}/{seq}:")
                shots = scanner.scan_shots(project_root, project, ep, seq)
                for shot in shots:
                    print(f"   - {shot}")
                
                # Scan departments for first shot
                if shots:
                    shot = shots[0]
                    print(f"\n4. Scanning Departments in {ep}/{seq}/{shot}:")
                    departments = scanner.scan_departments(project_root, project, ep, seq, shot)
                    for dept in departments:
                        print(f"   - {dept}")
                    
                    # Scan versions for first department
                    if departments:
                        dept = departments[0]
                        version_path = os.path.join(project_root, project, "scene", ep, seq, shot, dept, "version")
                        print(f"\n5. Scanning Versions in {ep}/{seq}/{shot}/{dept}:")
                        versions = scanner.scan_versions(version_path)
                        for version in versions:
                            print(f"   - {version}")
                        
                        # Get latest version
                        latest = scanner.get_latest_version(versions)
                        print(f"\n   Latest version: {latest}")
                        
                        # Scan Nuke files in latest version
                        if latest:
                            nuke_path = os.path.join(version_path, latest)
                            print(f"\n6. Scanning Nuke Files in {latest}:")
                            nuke_files = scanner.scan_nuke_files(nuke_path)
                            for file_info in nuke_files:
                                print(f"   - {file_info['filename']}")
                                if file_info['context']:
                                    print(f"     Context: {file_info['context']}")
                        
                        # Scan assets in publish directory
                        publish_path = os.path.join(project_root, project, "scene", ep, seq, shot, dept, "publish", "v001")
                        print(f"\n7. Scanning Assets in publish/v001:")
                        assets = scanner.scan_assets(publish_path)
                        for asset_type, asset_list in assets.items():
                            if asset_list:
                                print(f"   {asset_type.upper()}:")
                                for asset in asset_list:
                                    print(f"     - {asset['filename']}")
        
        # Demonstrate caching
        print(f"\n8. Cache Statistics:")
        cache_stats = scanner.get_cache_stats()
        print(f"   Total entries: {cache_stats['total_entries']}")
        print(f"   Valid entries: {cache_stats['valid_entries']}")
        print(f"   Cache timeout: {cache_stats['cache_timeout']}s")
        
    finally:
        # Clean up
        shutil.rmtree(temp_dir, ignore_errors=True)
        print(f"\nCleaned up demo directory: {temp_dir}")

def demo_project_structure():
    """Demonstrate complete project structure scanning."""
    print("\n" + "="*60)
    print("COMPLETE PROJECT STRUCTURE DEMO")
    print("="*60)
    
    # Create demo structure
    temp_dir, project_root, project = create_demo_structure()
    
    try:
        # Initialize scanner
        scanner = DirectoryScanner()
        
        print(f"\nScanning complete project structure...")
        structure = scanner.scan_project_structure(project_root, project)
        
        print(f"\nProject: {structure['project']}")
        print(f"Episodes: {len(structure['episodes'])}")
        
        for ep_name, ep_data in structure['episodes'].items():
            print(f"\n{ep_name}:")
            for seq_name, seq_data in ep_data['sequences'].items():
                print(f"  {seq_name}:")
                for shot_name, shot_data in seq_data['shots'].items():
                    print(f"    {shot_name}:")
                    for dept_name, dept_data in shot_data['departments'].items():
                        versions = dept_data['versions']
                        latest = dept_data['latest_version']
                        print(f"      {dept_name}: {len(versions)} versions (latest: {latest})")
        
    finally:
        # Clean up
        shutil.rmtree(temp_dir, ignore_errors=True)
        print(f"\nCleaned up demo directory: {temp_dir}")

def demo_integration_with_variables():
    """Demonstrate integration with variable management system."""
    print("\n" + "="*60)
    print("INTEGRATION WITH VARIABLE SYSTEM DEMO")
    print("="*60)
    
    # Create demo structure
    temp_dir, project_root, project = create_demo_structure()
    
    try:
        # Initialize components
        scanner = DirectoryScanner()
        
        # Mock variable manager for demo (since we don't have Nuke)
        print(f"\nDemo Context: Ep01/sq0110/SH0520/comp")
        
        context = {
            'project': project,
            'ep': 'Ep01',
            'seq': 'sq0110', 
            'shot': 'SH0520',
            'department': 'comp'
        }
        
        # Find files matching this context
        print(f"\nFinding files for context: {context}")
        
        # Manually build paths for demo
        nuke_path = os.path.join(project_root, project, "scene", "Ep01", "sq0110", "SH0520", "comp", "version")
        publish_path = os.path.join(project_root, project, "scene", "Ep01", "sq0110", "SH0520", "comp", "publish")
        
        print(f"\nNuke files in version directory:")
        versions = scanner.scan_versions(nuke_path)
        for version in versions:
            ver_path = os.path.join(nuke_path, version)
            nuke_files = scanner.scan_nuke_files(ver_path)
            for file_info in nuke_files:
                print(f"  {version}: {file_info['filename']}")
        
        print(f"\nAssets in publish directory:")
        for version in versions[:2]:  # Show first 2 versions
            ver_path = os.path.join(publish_path, version)
            if os.path.exists(ver_path):
                assets = scanner.scan_assets(ver_path)
                print(f"  {version}:")
                for asset_type, asset_list in assets.items():
                    if asset_list:
                        print(f"    {asset_type}: {len(asset_list)} files")
        
    finally:
        # Clean up
        shutil.rmtree(temp_dir, ignore_errors=True)
        print(f"\nCleaned up demo directory: {temp_dir}")

if __name__ == "__main__":
    demo_basic_scanning()
    demo_project_structure()
    demo_integration_with_variables()
    
    print("\n" + "="*60)
    print("DEMO COMPLETE")
    print("="*60)
