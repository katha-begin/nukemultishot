"""
Version control system for the Multishot Workflow System.

Implements version detection, approval marking (.approved files), and UI highlighting.
"""

import os
import re
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple

from ..utils.logging import get_logger

class VersionControl:
    """
    Version control and approval system.
    
    Features:
    - Version detection and comparison
    - Approval marking with .approved files
    - Version history tracking
    - UI status highlighting
    - Batch approval operations
    """
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.logger.info("VersionControl initialized")
    
    def get_version_info(self, filepath: str) -> Dict[str, Any]:
        """
        Get comprehensive version information for a file or directory.
        
        Args:
            filepath: Path to file or directory
            
        Returns:
            Dictionary with version information
        """
        try:
            if not filepath or not os.path.exists(filepath):
                return {
                    'exists': False,
                    'approved': False,
                    'version': None,
                    'status': 'missing'
                }
            
            # Extract version from path
            version = self.extract_version_from_path(filepath)
            
            # Check approval status
            is_approved = self.is_approved(filepath)
            
            # Get file/directory info
            is_directory = os.path.isdir(filepath)
            
            # Get modification time
            mod_time = os.path.getmtime(filepath)
            mod_datetime = datetime.fromtimestamp(mod_time)
            
            # Determine status
            if is_approved:
                status = 'approved'
            elif self.is_latest_version(filepath):
                status = 'latest'
            else:
                status = 'outdated'
            
            return {
                'exists': True,
                'approved': is_approved,
                'version': version,
                'status': status,
                'is_directory': is_directory,
                'modified': mod_datetime.isoformat(),
                'filepath': filepath
            }
            
        except Exception as e:
            self.logger.error(f"Error getting version info for {filepath}: {e}")
            return {
                'exists': False,
                'approved': False,
                'version': None,
                'status': 'error',
                'error': str(e)
            }
    
    def extract_version_from_path(self, filepath: str) -> Optional[str]:
        """
        Extract version string from file path.
        
        Args:
            filepath: File path to analyze
            
        Returns:
            Version string (e.g., 'v001') or None
        """
        try:
            # Common version patterns
            patterns = [
                r'/v(\d{3,4})/',           # /v001/ in path
                r'_v(\d{3,4})(?:[_.]|$)',  # _v001_ or _v001. in filename
                r'\.v(\d{3,4})\.',         # .v001. in filename
                r'version[_/]v?(\d{3,4})', # version/v001 or version_001
            ]
            
            for pattern in patterns:
                match = re.search(pattern, filepath, re.IGNORECASE)
                if match:
                    version_num = match.group(1)
                    return f"v{version_num.zfill(3)}"
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error extracting version from path {filepath}: {e}")
            return None
    
    def is_approved(self, filepath: str) -> bool:
        """
        Check if a file or directory is approved.
        
        Args:
            filepath: Path to check
            
        Returns:
            True if approved, False otherwise
        """
        try:
            if not os.path.exists(filepath):
                return False
            
            if os.path.isdir(filepath):
                # For directories, check for .approved file inside
                approved_file = os.path.join(filepath, '.approved')
                return os.path.exists(approved_file)
            else:
                # For files, check for .approved file with same name
                approved_file = filepath + '.approved'
                return os.path.exists(approved_file)
                
        except Exception as e:
            self.logger.error(f"Error checking approval status for {filepath}: {e}")
            return False
    
    def approve(self, filepath: str, approver: str = None, notes: str = None) -> bool:
        """
        Mark a file or directory as approved.
        
        Args:
            filepath: Path to approve
            approver: Name of person approving
            notes: Optional approval notes
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not os.path.exists(filepath):
                self.logger.error(f"Cannot approve non-existent path: {filepath}")
                return False
            
            # Determine approval file path
            if os.path.isdir(filepath):
                approved_file = os.path.join(filepath, '.approved')
            else:
                approved_file = filepath + '.approved'
            
            # Create approval metadata
            approval_data = {
                'approved_by': approver or 'Unknown',
                'approved_at': datetime.now().isoformat(),
                'notes': notes or '',
                'filepath': filepath,
                'version': self.extract_version_from_path(filepath)
            }
            
            # Write approval file
            with open(approved_file, 'w') as f:
                json.dump(approval_data, f, indent=2)
            
            self.logger.info(f"Approved: {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error approving {filepath}: {e}")
            return False
    
    def unapprove(self, filepath: str) -> bool:
        """
        Remove approval from a file or directory.
        
        Args:
            filepath: Path to unapprove
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Determine approval file path
            if os.path.isdir(filepath):
                approved_file = os.path.join(filepath, '.approved')
            else:
                approved_file = filepath + '.approved'
            
            if os.path.exists(approved_file):
                os.remove(approved_file)
                self.logger.info(f"Unapproved: {filepath}")
                return True
            else:
                self.logger.warning(f"No approval file found for: {filepath}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error unapproving {filepath}: {e}")
            return False

    def get_approval_info(self, filepath: str) -> Optional[Dict[str, Any]]:
        """
        Get approval information for a file or directory.

        Args:
            filepath: Path to check

        Returns:
            Approval information dictionary or None
        """
        try:
            # Determine approval file path
            if os.path.isdir(filepath):
                approved_file = os.path.join(filepath, '.approved')
            else:
                approved_file = filepath + '.approved'

            if not os.path.exists(approved_file):
                return None

            # Read approval data
            with open(approved_file, 'r') as f:
                approval_data = json.load(f)

            return approval_data

        except Exception as e:
            self.logger.error(f"Error getting approval info for {filepath}: {e}")
            return None

    def is_latest_version(self, filepath: str) -> bool:
        """
        Check if the given path represents the latest version.

        Args:
            filepath: Path to check

        Returns:
            True if this is the latest version, False otherwise
        """
        try:
            current_version = self.extract_version_from_path(filepath)
            if not current_version:
                return True  # No version info, assume latest

            # Get all versions in the same directory structure
            all_versions = self.get_all_versions(filepath)

            if not all_versions:
                return True

            # Sort versions and check if current is the highest
            sorted_versions = self.sort_versions(all_versions)
            latest_version = sorted_versions[-1] if sorted_versions else current_version

            return current_version == latest_version

        except Exception as e:
            self.logger.error(f"Error checking if latest version for {filepath}: {e}")
            return False

    def get_all_versions(self, filepath: str) -> List[str]:
        """
        Get all available versions for a given file path.

        Args:
            filepath: Path to analyze

        Returns:
            List of version strings
        """
        try:
            versions = []

            # Get the base directory (parent of version directory)
            current_version = self.extract_version_from_path(filepath)
            if not current_version:
                return []

            # Find the version directory in the path
            version_pattern = rf'/{current_version}/'
            if version_pattern not in filepath:
                return []

            # Get the base path (everything before the version)
            base_path = filepath.split(version_pattern)[0]

            if not os.path.exists(base_path):
                return []

            # Scan for version directories
            for item in os.listdir(base_path):
                item_path = os.path.join(base_path, item)
                if os.path.isdir(item_path):
                    # Check if this looks like a version directory
                    if re.match(r'v\d{3,4}$', item, re.IGNORECASE):
                        versions.append(item.lower())

            return versions

        except Exception as e:
            self.logger.error(f"Error getting all versions for {filepath}: {e}")
            return []

    def sort_versions(self, versions: List[str]) -> List[str]:
        """
        Sort version strings in ascending order.

        Args:
            versions: List of version strings (e.g., ['v001', 'v002', 'v010'])

        Returns:
            Sorted list of versions
        """
        try:
            def version_key(version_str):
                # Extract numeric part for sorting
                match = re.search(r'v(\d+)', version_str, re.IGNORECASE)
                if match:
                    return int(match.group(1))
                return 0

            return sorted(versions, key=version_key)

        except Exception as e:
            self.logger.error(f"Error sorting versions: {e}")
            return versions

    def get_status_color(self, status: str) -> str:
        """
        Get color code for status display.

        Args:
            status: Status string ('approved', 'latest', 'outdated', 'missing', 'error')

        Returns:
            Color code for UI display
        """
        color_map = {
            'approved': '#90EE90',    # Light green
            'latest': '#87CEEB',      # Sky blue
            'outdated': '#FFD700',    # Gold
            'missing': '#FF6B6B',     # Light red
            'error': '#FF4444'        # Red
        }

        return color_map.get(status, '#FFFFFF')  # White default

    def batch_approve(self, filepaths: List[str], approver: str = None, notes: str = None) -> Dict[str, bool]:
        """
        Approve multiple files/directories in batch.

        Args:
            filepaths: List of paths to approve
            approver: Name of person approving
            notes: Optional approval notes

        Returns:
            Dictionary mapping filepath to success status
        """
        results = {}

        for filepath in filepaths:
            try:
                success = self.approve(filepath, approver, notes)
                results[filepath] = success
            except Exception as e:
                self.logger.error(f"Error in batch approve for {filepath}: {e}")
                results[filepath] = False

        successful = sum(1 for success in results.values() if success)
        self.logger.info(f"Batch approve: {successful}/{len(filepaths)} successful")

        return results

    def batch_unapprove(self, filepaths: List[str]) -> Dict[str, bool]:
        """
        Unapprove multiple files/directories in batch.

        Args:
            filepaths: List of paths to unapprove

        Returns:
            Dictionary mapping filepath to success status
        """
        results = {}

        for filepath in filepaths:
            try:
                success = self.unapprove(filepath)
                results[filepath] = success
            except Exception as e:
                self.logger.error(f"Error in batch unapprove for {filepath}: {e}")
                results[filepath] = False

        successful = sum(1 for success in results.values() if success)
        self.logger.info(f"Batch unapprove: {successful}/{len(filepaths)} successful")

        return results
