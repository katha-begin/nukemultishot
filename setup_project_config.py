#!/usr/bin/env python
"""
Multishot Project Configuration Setup

This script properly sets up project configuration files in the correct locations
according to the PRD specifications. Run this once per project.

Usage:
    python setup_project_config.py --project SWA --proj_root V:/ --img_root W:/
    python setup_project_config.py --project TestProject --proj_root T:/test --img_root T:/test
"""

import os
import json
import shutil
import argparse
from pathlib import Path

class ProjectConfigSetup:
    """Handles proper project configuration setup."""
    
    def __init__(self):
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
    
    def create_root_config(self, proj_root, img_root):
        """Create the ROOT configuration file (global settings)."""
        config = {
            "version": "1.0.0",
            "description": "Multishot Root Configuration - Global Settings",

            "roots": {
                "PROJ_ROOT": proj_root,
                "IMG_ROOT": img_root
            },

            "global_settings": {
                "cache_timeout": 300,
                "max_recent_projects": 10,
                "auto_refresh": True,
                "log_level": "INFO"
            }
        }
        return config

    def create_project_config(self, project_name):
        """Create a PROJECT configuration file (project-specific settings)."""
        config = {
            "version": "1.0.0",
            "project_name": project_name,
            "description": f"{project_name} Project Configuration",
            
            "defaults": {
                "project": project_name,
                "version": "v001",
                "variance": "main",
                "element": "beauty",
                "frame": "####",
                "ext": "exr"
            },

            "paths": {
                "nuke_files": "{PROJ_ROOT}{project}/all/scene/{ep}/{seq}/{shot}/{department}/version/",
                "renders": "{IMG_ROOT}{project}/all/scene/{ep}/{seq}/{shot}/{department}/publish/",
                "renders_versioned": "{IMG_ROOT}{project}/all/scene/{ep}/{seq}/{shot}/{department}/publish/{version}/",
                "geometry": "{PROJ_ROOT}{project}/all/scene/{ep}/{seq}/{shot}/{department}/publish/",
                "geometry_versioned": "{PROJ_ROOT}{project}/all/scene/{ep}/{seq}/{shot}/{department}/publish/{version}/",
                "camera": "{PROJ_ROOT}{project}/all/scene/{ep}/{seq}/{shot}/{department}/publish/",
                "camera_versioned": "{PROJ_ROOT}{project}/all/scene/{ep}/{seq}/{shot}/{department}/publish/{version}/"
            },

            "ui": {
                "default_department": "comp",
                "show_approval_status": True
            },

            "patterns": {
                "episode": "^Ep\\d{2}$",
                "sequence": "^sq\\d{4}$",
                "shot": "^SH\\d{4}$"
            },

            "farm": {
                "submit_command": "qsub",
                "queue_name": "comp",
                "priority": 50
            },

            "custom_variables": {
                "show_code": project_name,
                "season": "01",
                "client": "Production",
                "resolution": "2048x1152"
            }
        }
        
        return config
    
    def install_root_config(self, proj_root, root_config):
        """Install ROOT configuration file."""
        print(f"\n2. Installing Root Configuration:")

        # Root config goes in PROJ_ROOT (V:/root_config.json)
        root_config_path = os.path.join(proj_root, "root_config.json")
        with open(root_config_path, 'w') as f:
            json.dump(root_config, f, indent=2)
        print(f"   ✅ Root config: {root_config_path}")

        return root_config_path

    def setup_project_directories(self, project_name, proj_root):
        """Create project directory structure (only if it doesn't exist)."""
        print(f"\n3. Checking Project Directory Structure:")

        # Project directory (V:/SWA/)
        project_dir = os.path.join(proj_root, project_name)
        if not os.path.exists(project_dir):
            print(f"   ⚠️  Project directory doesn't exist: {project_dir}")
            print(f"   ⚠️  This should be created by your production pipeline")
            print(f"   ⚠️  Multishot will work when the directory exists")
        else:
            print(f"   ✅ Project directory exists: {project_dir}")

        # Multishot config directory (V:/SWA/.multishot/)
        config_dir = os.path.join(project_dir, ".multishot")
        os.makedirs(config_dir, exist_ok=True)
        print(f"   ✅ Config directory: {config_dir}")

        return config_dir
    
    def install_project_config(self, project_name, project_config, proj_root):
        """Install PROJECT configuration file."""
        print(f"\n4. Installing Project Configuration:")

        # Project config goes in {PROJ_ROOT}{project}/.multishot/config.json
        config_dir = os.path.join(proj_root, project_name, ".multishot")
        project_config_path = os.path.join(config_dir, "config.json")

        with open(project_config_path, 'w') as f:
            json.dump(project_config, f, indent=2)
        print(f"   ✅ Project config: {project_config_path}")

        return project_config_path
    
    def update_config_manager(self):
        """Update the ConfigManager to load root config properly."""
        print(f"\n5. Updating ConfigManager:")
        print(f"   ⚠️  ConfigManager needs manual update to load root_config.json")
        print(f"   ⚠️  This will be done separately to avoid breaking existing code")
    
    def validate_setup(self, project_name, proj_root):
        """Validate the configuration setup."""
        print(f"\n6. Validating Configuration:")

        # Check config files
        root_config_path = os.path.join(proj_root, "root_config.json")
        config_dir = os.path.join(proj_root, project_name, ".multishot")
        project_config_path = os.path.join(config_dir, "config.json")

        checks = [
            (root_config_path, "Root config file"),
            (config_dir, "Project config directory"),
            (project_config_path, "Project config file")
        ]

        all_good = True
        for path, description in checks:
            if os.path.exists(path):
                print(f"   ✅ {description}: {path}")
            else:
                print(f"   ❌ {description}: {path}")
                all_good = False

        return all_good
    
    def setup_project(self, project_name, proj_root, img_root):
        """Complete project setup process."""
        print("="*60)
        print(f"MULTISHOT CONFIGURATION SETUP: {project_name}")
        print("="*60)

        # Normalize paths
        proj_root = proj_root.rstrip('/\\') + '/'
        img_root = img_root.rstrip('/\\') + '/'

        print(f"Project: {project_name}")
        print(f"Project Root (PROJ_ROOT): {proj_root}")
        print(f"Image Root (IMG_ROOT): {img_root}")

        # Step 1: Create root config
        print(f"\n1. Creating Root Configuration:")
        root_config = self.create_root_config(proj_root, img_root)
        print(f"   ✅ Root configuration created")

        # Step 2: Install root config
        try:
            root_config_path = self.install_root_config(proj_root, root_config)
        except Exception as e:
            print(f"   ❌ Error installing root config: {e}")
            return False

        # Step 3: Setup project directories
        try:
            self.setup_project_directories(project_name, proj_root)
        except Exception as e:
            print(f"   ❌ Error setting up directories: {e}")
            return False

        # Step 4: Create and install project config
        print(f"\n4. Creating Project Configuration:")
        project_config = self.create_project_config(project_name)
        print(f"   ✅ Project configuration created")

        try:
            project_config_path = self.install_project_config(project_name, project_config, proj_root)
        except Exception as e:
            print(f"   ❌ Error installing project config: {e}")
            return False

        # Step 5: Update ConfigManager
        try:
            self.update_config_manager()
        except Exception as e:
            print(f"   ❌ Error updating ConfigManager: {e}")
            return False

        # Step 6: Validate
        if not self.validate_setup(project_name, proj_root):
            print(f"\n❌ Setup validation failed")
            return False

        print(f"\n" + "="*60)
        print("✅ CONFIGURATION SETUP COMPLETED")
        print("="*60)
        print(f"\nConfiguration files created:")
        print(f"• Root config: {root_config_path}")
        print(f"• Project config: {project_config_path}")
        print(f"\nPRD-Compliant Structure:")
        print(f"• Root variables in: {root_config_path}")
        print(f"• Project settings in: {project_config_path}")
        print(f"\nNext steps:")
        print(f"1. Your production pipeline should create: {proj_root}{project_name}/all/scene/")
        print(f"2. Launch Nuke and test: multishot.ui.show_browser()")
        print(f"3. Multishot will load configs in correct PRD order")

        return True

def main():
    parser = argparse.ArgumentParser(description='Setup Multishot project configuration')
    parser.add_argument('--project', required=True, help='Project name (e.g., SWA)')
    parser.add_argument('--proj_root', required=True, help='Project root path (e.g., V:/)')
    parser.add_argument('--img_root', required=True, help='Image root path (e.g., W:/)')
    
    args = parser.parse_args()
    
    setup = ProjectConfigSetup()
    success = setup.setup_project(args.project, args.proj_root, args.img_root)
    
    return 0 if success else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
