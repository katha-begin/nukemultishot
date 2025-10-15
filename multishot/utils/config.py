"""
Configuration management for the Multishot Workflow System.

Handles project-specific configuration, default settings, and user preferences.
"""

import os
import json
from typing import Dict, Any, Optional
from .logging import get_logger

class ConfigManager:
    """Manages configuration files and settings for multishot workflows."""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self._project_config = None
        self._user_prefs = None
        self._default_config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get the default configuration settings."""
        return {
            "version": "1.0.0",
            "roots": {
                "PROJ_ROOT": "V:/",
                "IMG_ROOT": "W:/"
            },
            "project": "SWA",

            "asset_types": {
                "image": [".exr", ".png", ".jpg", ".jpeg", ".tiff", ".tif", ".dpx"],
                "geometry": [".abc", ".obj", ".fbx", ".usd", ".usda", ".usdc"],
                "camera": [".abc", ".fbx", ".ma", ".mb"]
            },
            "version_formats": ["v###", "v###_###"],
            "naming_convention": {
                "nuke_file": "{ep}_{seq}_{shot}_{department}_{variance}_{version}.nk",
                "render": "{element}.{frame}.{ext}",
                "geometry": "{element}.{ext}",
                "camera": "{element}.{ext}"
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
                "cache_timeout": 300,  # 5 minutes
                "max_recent_projects": 10,
                "auto_refresh": True,
                "show_approval_status": True
            }
        }
    
    def get_project_config_path(self, project_root: str, project: str) -> str:
        """Get the path to the project configuration file."""
        # Method 1: Project root (V:/SWA_config.json) - Primary location
        if project_root:
            project_config = os.path.join(project_root, f"{project}_config.json")
            if os.path.exists(project_config):
                return project_config

        # Method 2: Project .multishot directory (V:/SWA/.multishot/config.json) - Secondary
        if project_root:
            config_dir = os.path.join(project_root, project, ".multishot")
            secondary_config = os.path.join(config_dir, "config.json")
            if os.path.exists(secondary_config):
                return secondary_config

        # Method 3: Nukemultishot directory (development fallback)
        script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        nukemultishot_config = os.path.join(script_dir, f"{project}_config.json")
        if os.path.exists(nukemultishot_config):
            return nukemultishot_config

        # Method 4: Default fallback
        if project_root:
            config_dir = os.path.join(project_root, project, ".multishot")
            return os.path.join(config_dir, "config.json")
        else:
            return os.path.join(script_dir, f"{project}_config.json")
    
    def get_user_prefs_path(self, project_root: str, project: str) -> str:
        """Get the path to the user preferences file."""
        config_dir = os.path.join(project_root, project, ".multishot")
        return os.path.join(config_dir, "user_prefs.json")
    
    def load_project_config(self, project_root: str, project: str) -> Dict[str, Any]:
        """Load project-specific configuration."""
        config_path = self.get_project_config_path(project_root, project)

        try:
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)

                self.logger.info(f"Loaded project config from {config_path}")

                # Merge with defaults
                merged_config = self._default_config.copy()
                self._deep_merge(merged_config, config)
                self._project_config = merged_config
                return merged_config
            else:
                self.logger.info(f"No project config found at {config_path}, using defaults")
                self._project_config = self._default_config.copy()
                return self._project_config

        except Exception as e:
            self.logger.error(f"Error loading project config: {e}")
            self._project_config = self._default_config.copy()
            return self._project_config

    def _deep_merge(self, base: Dict[str, Any], update: Dict[str, Any]) -> None:
        """Deep merge update dict into base dict."""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value
    
    def save_project_config(self, project_root: str, project: str, config: Dict[str, Any]) -> bool:
        """Save project-specific configuration."""
        config_path = self.get_project_config_path(project_root, project)
        
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            self.logger.info(f"Saved project config to {config_path}")
            self._project_config = config
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving project config: {e}")
            return False
    
    def load_user_prefs(self, project_root: str, project: str) -> Dict[str, Any]:
        """Load user preferences."""
        prefs_path = self.get_user_prefs_path(project_root, project)
        
        try:
            if os.path.exists(prefs_path):
                with open(prefs_path, 'r') as f:
                    prefs = json.load(f)
                self.logger.info(f"Loaded user preferences from {prefs_path}")
                self._user_prefs = prefs
                return prefs
            else:
                self.logger.info("No user preferences found, using defaults")
                self._user_prefs = {}
                return {}
                
        except Exception as e:
            self.logger.error(f"Error loading user preferences: {e}")
            self._user_prefs = {}
            return {}
    
    def save_user_prefs(self, project_root: str, project: str, prefs: Dict[str, Any]) -> bool:
        """Save user preferences."""
        prefs_path = self.get_user_prefs_path(project_root, project)
        
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(prefs_path), exist_ok=True)
            
            with open(prefs_path, 'w') as f:
                json.dump(prefs, f, indent=2)
            
            self.logger.info(f"Saved user preferences to {prefs_path}")
            self._user_prefs = prefs
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving user preferences: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        if self._project_config and key in self._project_config:
            return self._project_config[key]
        return self._default_config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set a configuration value."""
        if self._project_config is None:
            self._project_config = self._default_config.copy()
        self._project_config[key] = value
    
    def get_user_pref(self, key: str, default: Any = None) -> Any:
        """Get a user preference value."""
        if self._user_prefs and key in self._user_prefs:
            return self._user_prefs[key]
        return default
    
    def set_user_pref(self, key: str, value: Any) -> None:
        """Set a user preference value."""
        if self._user_prefs is None:
            self._user_prefs = {}
        self._user_prefs[key] = value
    
    def get_path_template(self, path_type: str) -> Optional[str]:
        """Get a path template for the specified type."""
        paths = self.get("paths", {})
        return paths.get(path_type)
    
    def get_departments(self) -> list:
        """
        DEPRECATED: Get the list of available departments.

        This method is deprecated. Departments should be discovered dynamically
        from the filesystem using DirectoryScanner.scan_departments().

        Returns empty list to force dynamic discovery.
        """
        # Always return empty list to force dynamic discovery
        return []
    
    def get_asset_extensions(self, asset_type: str) -> list:
        """Get file extensions for the specified asset type."""
        asset_types = self.get("asset_types", {})
        return asset_types.get(asset_type, [])
    
    def is_valid_extension(self, filepath: str, asset_type: str) -> bool:
        """Check if a file extension is valid for the asset type."""
        _, ext = os.path.splitext(filepath.lower())
        valid_extensions = self.get_asset_extensions(asset_type)
        return ext in valid_extensions
