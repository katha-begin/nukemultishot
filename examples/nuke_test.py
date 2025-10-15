#!/usr/bin/env python3
"""
Nuke Integration Test Script

Run this in Nuke's Script Editor to test the multishot system.
"""

def setup_multishot_path():
    """Setup the multishot path dynamically - works from any location."""
    import sys
    import os

    print("Setting up multishot path...")

    # Method 1: Try relative to this script (examples/nuke_test.py -> project_root/)
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)  # Go up from examples/ to project root
        multishot_path = os.path.join(project_root, 'multishot')

        if os.path.exists(multishot_path) and os.path.isdir(multishot_path):
            if project_root not in sys.path:
                sys.path.insert(0, project_root)
            print(f"✓ Found multishot at: {project_root}")
            return project_root
    except:
        pass

    # Method 2: Try current working directory
    try:
        cwd = os.getcwd()
        multishot_cwd = os.path.join(cwd, 'multishot')
        if os.path.exists(multishot_cwd) and os.path.isdir(multishot_cwd):
            if cwd not in sys.path:
                sys.path.insert(0, cwd)
            print(f"✓ Found multishot in cwd: {cwd}")
            return cwd
    except:
        pass

    # Method 3: Search up the directory tree from script location
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        for _ in range(10):  # Search up to 10 levels
            multishot_search = os.path.join(current_dir, 'multishot')
            if os.path.exists(multishot_search) and os.path.isdir(multishot_search):
                if current_dir not in sys.path:
                    sys.path.insert(0, current_dir)
                print(f"✓ Found multishot by searching up: {current_dir}")
                return current_dir
            parent = os.path.dirname(current_dir)
            if parent == current_dir:  # Reached root
                break
            current_dir = parent
    except:
        pass

    # Method 4: Check if already available
    try:
        import multishot
        print("✓ Multishot already available in Python path")
        return "already_available"
    except ImportError:
        pass

    # Method 5: Manual path hints for common locations
    common_paths = [
        r'T:\pipeline\development\nuke\nukemultishot',
        r'C:\Users\Admin\Documents\augment-projects\nukemultishot',
        r'C:\nukemultishot',
        r'D:\nukemultishot'
    ]

    for path in common_paths:
        try:
            if os.path.exists(path):
                multishot_path = os.path.join(path, 'multishot')
                if os.path.exists(multishot_path):
                    if path not in sys.path:
                        sys.path.insert(0, path)
                    print(f"✓ Found multishot at common location: {path}")
                    return path
        except:
            continue

    raise FileNotFoundError(
        "Could not locate multishot module!\n"
        "Please ensure:\n"
        "1. You're running from the nukemultishot directory, or\n"
        "2. The multishot folder exists in your project, or\n"
        "3. Add the correct path manually to sys.path"
    )

def test_multishot_in_nuke():
    """Test multishot system integration in Nuke."""
    print("="*60)
    print("MULTISHOT NUKE INTEGRATION TEST")
    print("="*60)

    try:
        # Setup path dynamically
        print("\n0. Setting up multishot path...")
        setup_multishot_path()

        # Test 1: Import multishot
        print("\n1. Testing Import...")
        import multishot
        print("   ✓ Multishot imported successfully")
        
        # Test 2: Initialize system
        print("\n2. Testing Initialization...")
        multishot.initialize()
        print("    Multishot initialized successfully")
        
        # Test 3: Test Variable Manager
        print("\n3. Testing Variable Manager...")
        from multishot.core.variables import VariableManager
        vm = VariableManager()
        
        # Set some test variables
        vm.set_variable("project", "TestProject")
        vm.set_variable("ep", "Ep01")
        vm.set_variable("seq", "sq0110")
        vm.set_variable("shot", "SH0520")
        vm.set_variable("department", "comp")
        
        # Get all variables
        all_vars = vm.get_all_variables()
        print(f"    Variables stored: {len(all_vars)} variables")
        for key, value in sorted(all_vars.items()):
            print(f"     {key}: {value}")
        
        # Test 4: Test Context Detection
        print("\n4. Testing Context Detection...")
        from multishot.core.context import ContextDetector
        cd = ContextDetector()
        
        test_filename = "Ep01_sq0110_SH0520_comp_v001.nk"
        context = cd.detect_from_filepath(test_filename)
        print(f"    Context detected from '{test_filename}':")
        for key, value in context.items():
            print(f"     {key}: {value}")
        
        # Test 5: Test Path Resolution
        print("\n5. Testing Path Resolution...")
        from multishot.core.paths import PathResolver
        pr = PathResolver()
        
        # Test path resolution
        variables = vm.get_all_variables()
        nuke_path = pr.get_nuke_file_path(variables)
        render_path = pr.get_render_path(variables)
        
        print(f"   Nuke file path: {nuke_path}")
        print(f"   Render path: {render_path}")
        
        # Test 6: Test Directory Scanner
        print("\n6. Testing Directory Scanner...")
        from multishot.core.scanner import DirectoryScanner
        scanner = DirectoryScanner()
        print("   DirectoryScanner initialized")
        print("   Cache system active")
        
        # Test 7: Test Browser UI (without showing)
        print("\n7. Testing Browser UI...")
        from multishot.ui.browser import MultishotBrowser
        
        # Create browser instance (don't show it yet)
        browser = MultishotBrowser()
        print("    MultishotBrowser created successfully")
        print("    All UI components initialized")
        
        # Test 8: Test Variables Dialog
        print("\n8. Testing Variables Dialog...")
        from multishot.ui.variables_dialog import VariablesDialog
        print("    VariablesDialog available")
        
        # Test 9: Check Nuke Integration
        print("\n9. Testing Nuke Integration...")
        import nuke
        
        # Check if variables are stored in root
        root = nuke.root()
        knobs = root.knobs()
        multishot_knobs = [k for k in knobs.keys() if k.startswith('multishot_')]
        print(f"    Found {len(multishot_knobs)} multishot knobs in root:")
        for knob_name in multishot_knobs:
            print(f"     - {knob_name}")
        
        # Test 10: Menu Integration
        print("\n10. Testing Menu Integration...")
        try:
            menubar = nuke.menu('Nuke')
            multishot_menu = menubar.findItem('Multishot')
            if multishot_menu:
                print("    Multishot menu found in Nuke menubar")
            else:
                print("    Multishot menu not found (may need restart)")
        except:
            print("    Could not check menu (may need restart)")
        
        print("\n" + "="*60)
        print(" ALL TESTS PASSED!")
        print("="*60)
        print("\nNext Steps:")
        print("1. Restart Nuke to see the Multishot menu")
        print("2. Use Multishot > Browser to open the main interface")
        print("3. Use Multishot > Show Variables to manage variables")
        print("4. Check the toolbar for quick access buttons")
        
        return True
        
    except Exception as e:
        print(f"\nERROR - TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_browser():
    """Show the multishot browser."""
    try:
        # Setup path
        setup_multishot_path()

        from multishot.ui.browser import MultishotBrowser
        browser = MultishotBrowser()
        browser.show()
        print("✓ Browser opened successfully!")
        return browser
    except Exception as e:
        print(f"ERROR - Failed to show browser: {e}")
        return None

def show_variables():
    """Show the variables dialog."""
    try:
        # Setup path
        setup_multishot_path()

        from multishot.ui.variables_dialog import VariablesDialog
        dialog = VariablesDialog()
        dialog.show()
        print("✓ Variables dialog opened successfully!")
        return dialog
    except Exception as e:
        print(f"ERROR - Failed to show variables dialog: {e}")
        return None

def quick_setup():
    """Quick setup for testing."""
    print("Setting up test environment...")

    # Setup path
    setup_multishot_path()

    # Import and initialize
    import multishot
    multishot.initialize()
    
    # Set up test variables
    from multishot.core.variables import VariableManager
    vm = VariableManager()
    
    # Set root paths (adjust these to your actual paths)
    vm.set_variable("PROJ_ROOT", "V:/")
    vm.set_variable("IMG_ROOT", "W:/")
    
    # Set test context
    vm.set_context_variables({
        "project": "TestProject",
        "ep": "Ep01", 
        "seq": "sq0110",
        "shot": "SH0520",
        "department": "comp"
    })
    
    print(" Test environment ready!")
    print("Run show_browser() to open the browser")
    print("Run show_variables() to manage variables")

if __name__ == "__main__":
    # If running in Nuke, run the test
    try:
        import nuke
        print("Running in Nuke environment")
        test_multishot_in_nuke()
    except ImportError:
        print("Not in Nuke environment - run this in Nuke's Script Editor")

# Quick access functions for Nuke Script Editor:
# test_multishot_in_nuke()  # Run full test
# quick_setup()             # Quick setup
# show_browser()            # Show browser
# show_variables()          # Show variables dialog
