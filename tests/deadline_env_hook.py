"""
Deadline Environment Hook for Multishot

This script modifies the Deadline job submission to include required environment variables.
It should be integrated into the Deadline submission workflow.

Usage:
    1. Copy this file to your Deadline repository custom scripts folder
    2. Or integrate the add_multishot_env_vars() function into your existing submission script

Environment Variables Added:
    - NUKE_PATH: Path to multishot installation
    - OCIO: Path to OCIO config file
"""

from __future__ import print_function
from __future__ import absolute_import
import os
import sys
import platform


def get_multishot_path():
    """
    Get the path to the multishot installation.
    
    Returns:
        str: Path to multishot directory
    """
    # Try to get from environment first
    if 'NUKE_PATH' in os.environ:
        nuke_paths = os.environ['NUKE_PATH'].split(os.pathsep)
        for path in nuke_paths:
            if 'multishot' in path.lower() or 'nukemultishot' in path.lower():
                return path
    
    # Default paths based on platform
    if platform.system() == 'Windows':
        # Windows path
        default_path = 'T:/pipeline/development/nuke/nukemultishot'
    else:
        # Linux path (for render farm)
        default_path = '/mnt/ppr_dev_t/pipeline/development/nuke/nukemultishot'
    
    return default_path


def get_ocio_path():
    """
    Get the path to the OCIO config file.
    
    Returns:
        str: Path to OCIO config file
    """
    # Try to get from environment first
    if 'OCIO' in os.environ:
        return os.environ['OCIO']
    
    # Default paths based on platform
    if platform.system() == 'Windows':
        # Windows path
        default_path = 'T:/pipeline/ocio/aces_2.0/studio-config-v1.0.0_aces-v1.3_ocio-v2.0.ocio'
    else:
        # Linux path (for render farm)
        default_path = '/mnt/ppr_dev_t/pipeline/ocio/aces_2.0/studio-config-v1.0.0_aces-v1.3_ocio-v2.0.ocio'
    
    return default_path


def fix_ocio_in_current_script():
    """
    Fix OCIO display device names in the current Nuke script before submission.

    This function scans all Read and Write nodes and replaces display device names
    with proper colorspaces to prevent "Bad value for display" errors on render farm.

    Returns:
        int: Number of fixes applied
    """
    try:
        import nuke

        print("Checking for OCIO display device names in script...")

        # Map of display device names to proper colorspaces
        display_to_colorspace_map = {
            'sRGB - Display': 'sRGB - Texture',
            'Rec.1886 Rec.709 - Display': 'Rec.709 - Display',
            'Rec.1886 Rec.2020 - Display': 'Rec.2020 - Display',
        }

        fixed_count = 0

        # Fix Read nodes
        for node in nuke.allNodes('Read'):
            try:
                if node.knob('colorspace'):
                    current_cs = node.knob('colorspace').value()
                    if current_cs in display_to_colorspace_map:
                        new_cs = display_to_colorspace_map[current_cs]
                        node.knob('colorspace').setValue(new_cs)
                        print("  Read '{}': changed colorspace '{}' -> '{}'".format(
                            node.name(), current_cs, new_cs))
                        fixed_count += 1
            except Exception as e:
                print("  Warning: Could not check Read node '{}': {}".format(node.name(), e))

        # Fix Write nodes
        for node in nuke.allNodes('Write'):
            try:
                if node.knob('colorspace'):
                    current_cs = node.knob('colorspace').value()
                    if current_cs in display_to_colorspace_map:
                        new_cs = display_to_colorspace_map[current_cs]
                        node.knob('colorspace').setValue(new_cs)
                        print("  Write '{}': changed colorspace '{}' -> '{}'".format(
                            node.name(), current_cs, new_cs))
                        fixed_count += 1
            except Exception as e:
                print("  Warning: Could not check Write node '{}': {}".format(node.name(), e))

        if fixed_count > 0:
            print("Fixed {} OCIO display device names before submission".format(fixed_count))
            # Save the script with fixes
            try:
                nuke.scriptSave()
                print("Script saved with OCIO fixes")
            except:
                print("Warning: Could not auto-save script. Please save manually.")
        else:
            print("No OCIO fixes needed")

        return fixed_count

    except Exception as e:
        print("Error fixing OCIO settings: {}".format(e))
        import traceback
        traceback.print_exc()
        return 0


def add_multishot_env_vars(job_info_file_handle, start_index=0):
    """
    Add multishot environment variables to the Deadline job info file.
    
    This function should be called after opening the job info file and before closing it.
    
    Args:
        job_info_file_handle: File handle for the job info file (opened in write mode)
        start_index (int): Starting index for EnvironmentKeyValue entries (default: 0)
    
    Returns:
        int: Next available index for additional environment variables
    
    Example:
        fileHandle = open(jobInfoFile, "wb")
        fileHandle.write(EncodeAsUTF16String("Plugin=Nuke\\n"))
        
        # Add multishot environment variables
        next_index = add_multishot_env_vars(fileHandle, start_index=0)
        
        # Add more environment variables if needed
        fileHandle.write(EncodeAsUTF16String(f"EnvironmentKeyValue{next_index}=MY_VAR=my_value\\n"))
        
        fileHandle.close()
    """
    try:
        # Import encoding function (this should be available in Deadline submission scripts)
        try:
            from SubmitNukeToDeadline import EncodeAsUTF16String
        except ImportError:
            # Fallback encoding function
            def EncodeAsUTF16String(text):
                if sys.version_info[0] > 2:
                    return text.encode('utf-16-le')
                else:
                    return text.encode('utf-16-le')
        
        env_index = start_index
        
        # Add NUKE_PATH
        nuke_path = get_multishot_path()
        if nuke_path and os.path.exists(nuke_path):
            job_info_file_handle.write(
                EncodeAsUTF16String(f"EnvironmentKeyValue{env_index}=NUKE_PATH={nuke_path}\n")
            )
            print(f"Added NUKE_PATH={nuke_path} to Deadline job")
            env_index += 1
        else:
            print(f"Warning: NUKE_PATH not found: {nuke_path}")
        
        # Add OCIO
        ocio_path = get_ocio_path()
        if ocio_path and os.path.exists(ocio_path):
            job_info_file_handle.write(
                EncodeAsUTF16String(f"EnvironmentKeyValue{env_index}=OCIO={ocio_path}\n")
            )
            print(f"Added OCIO={ocio_path} to Deadline job")
            env_index += 1
        else:
            print(f"Warning: OCIO config not found: {ocio_path}")
        
        return env_index
        
    except Exception as e:
        print(f"Error adding multishot environment variables: {e}")
        import traceback
        traceback.print_exc()
        return start_index

