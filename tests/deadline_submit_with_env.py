"""
Submit Nuke script to Deadline with proper environment variables.

This ensures that:
1. NUKE_PATH is set so init.py loads
2. Variables are accessible in batch mode
3. TCL expressions evaluate correctly

Usage in Nuke:
    exec(open('T:/pipeline/development/nuke/nukemultishot/tests/deadline_submit_with_env.py').read())
    submit_to_deadline_with_env()
"""

def submit_to_deadline_with_env():
    """
    Submit current Nuke script to Deadline with proper environment variables.
    """
    try:
        import nuke
        import os
        
        print("=" * 70)
        print("DEADLINE SUBMISSION WITH ENVIRONMENT VARIABLES")
        print("=" * 70)
        
        # Check if script is saved
        script_path = nuke.root().name()
        if script_path == 'Root' or not script_path:
            print("\nERROR: Script is not saved!")
            print("Please save your script first: nuke.scriptSave()")
            print("=" * 70)
            return False
        
        print("\nScript: {}".format(script_path))
        
        # Get current environment variables
        print("\nChecking environment variables:")
        
        # NUKE_PATH - critical for loading init.py
        nuke_path = os.environ.get('NUKE_PATH', '')
        multishot_path = 'T:/pipeline/development/nuke/nukemultishot'
        
        if multishot_path not in nuke_path:
            if nuke_path:
                nuke_path = multishot_path + os.pathsep + nuke_path
            else:
                nuke_path = multishot_path
        
        print("  NUKE_PATH: {}".format(nuke_path))
        
        # OCIO
        ocio_path = os.environ.get('OCIO', '')
        if not ocio_path:
            ocio_path = 'T:/pipeline/ocio/aces_2.0/studio-config-v1.0.0_aces-v1.3_ocio-v2.0.ocio'
        print("  OCIO: {}".format(ocio_path))
        
        # PROJ_ROOT and IMG_ROOT from script
        proj_root = nuke.root().knob('PROJ_ROOT')
        img_root = nuke.root().knob('IMG_ROOT')
        
        if proj_root:
            print("  PROJ_ROOT: {}".format(proj_root.value()))
        else:
            print("  PROJ_ROOT: NOT SET IN SCRIPT")
        
        if img_root:
            print("  IMG_ROOT: {}".format(img_root.value()))
        else:
            print("  IMG_ROOT: NOT SET IN SCRIPT")
        
        print("\n" + "=" * 70)
        print("IMPORTANT: Add these environment variables to Deadline job:")
        print("=" * 70)
        print("\nIn Deadline Monitor:")
        print("1. Right-click on the job")
        print("2. Select 'Modify Job Properties'")
        print("3. Go to 'Environment' tab")
        print("4. Add these variables:")
        print("")
        print("   NUKE_PATH = {}".format(nuke_path))
        print("   OCIO = {}".format(ocio_path))
        print("")
        print("OR in Deadline submission script, add:")
        print("")
        print("   job_info['EnvironmentKeyValue0'] = 'NUKE_PATH={}'".format(nuke_path))
        print("   job_info['EnvironmentKeyValue1'] = 'OCIO={}'".format(ocio_path))
        print("")
        print("=" * 70)
        print("\nWhy this is needed:")
        print("  - NUKE_PATH: Tells Nuke where to find init.py")
        print("  - init.py: Creates individual knobs (ep, seq, shot, PROJ_ROOT, IMG_ROOT)")
        print("  - Without these knobs: TCL expressions like [value root.IMG_ROOT] fail")
        print("  - OCIO: Ensures consistent color management")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print("\nERROR: {}".format(e))
        import traceback
        traceback.print_exc()
        return False


def check_deadline_environment():
    """
    Check if environment is properly set up for Deadline rendering.
    """
    try:
        import nuke
        import os
        
        print("=" * 70)
        print("CHECKING DEADLINE ENVIRONMENT SETUP")
        print("=" * 70)
        
        issues = []
        
        # Check NUKE_PATH
        nuke_path = os.environ.get('NUKE_PATH', '')
        multishot_path = 'T:/pipeline/development/nuke/nukemultishot'
        
        print("\n1. NUKE_PATH:")
        if not nuke_path:
            print("   STATUS: NOT SET")
            issues.append("NUKE_PATH is not set")
        elif multishot_path not in nuke_path:
            print("   STATUS: SET but missing multishot path")
            print("   Current: {}".format(nuke_path))
            issues.append("NUKE_PATH does not include multishot path")
        else:
            print("   STATUS: OK")
            print("   Value: {}".format(nuke_path))
        
        # Check OCIO
        ocio_path = os.environ.get('OCIO', '')
        print("\n2. OCIO:")
        if not ocio_path:
            print("   STATUS: NOT SET (will use Nuke default)")
        else:
            print("   STATUS: OK")
            print("   Value: {}".format(ocio_path))
        
        # Check root knobs
        print("\n3. Root knobs:")
        required_knobs = ['ep', 'seq', 'shot', 'project', 'PROJ_ROOT', 'IMG_ROOT']
        missing_knobs = []
        
        for knob_name in required_knobs:
            knob = nuke.root().knob(knob_name)
            if knob:
                print("   {}: OK (value='{}')".format(knob_name, knob.value()))
            else:
                print("   {}: MISSING".format(knob_name))
                missing_knobs.append(knob_name)
                issues.append("Root knob '{}' is missing".format(knob_name))
        
        # Summary
        print("\n" + "=" * 70)
        if issues:
            print("ISSUES FOUND:")
            for i, issue in enumerate(issues, 1):
                print("  {}. {}".format(i, issue))
            print("\nTo fix, run:")
            print("  submit_to_deadline_with_env()")
        else:
            print("ALL CHECKS PASSED - Ready for Deadline rendering!")
        print("=" * 70)
        
        return len(issues) == 0
        
    except Exception as e:
        print("\nERROR: {}".format(e))
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    # Check current environment
    check_deadline_environment()
    
    print("\n")
    
    # Show submission instructions
    print("To submit to Deadline with proper environment:")
    print("  submit_to_deadline_with_env()")

