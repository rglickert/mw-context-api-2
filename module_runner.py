# module_runner.py  
import io
import sys
import os
import importlib.util

# Get the root directory of the current script to ensure dynamic pathing
repo_root = os.path.dirname(os.path.abspath(__file__))
MODULES_FOLDER = os.path.join(repo_root, 'modules')

# Ensure necessary folders exist
def ensure_modules_folder(MODULES_FOLDER):
    if not os.path.exists(MODULES_FOLDER):
        os.makedirs(MODULES_FOLDER)

# Function to run a module from the subfolder
def run_module_from_subfolder(subfolder, module, function, MODULES_FOLDER=MODULES_FOLDER):
    ensure_modules_folder(MODULES_FOLDER)  # Ensure the modules folder exists

    subfolder_path = os.path.join(MODULES_FOLDER, subfolder)

    if not os.path.exists(subfolder_path):
        print(f"Subfolder '{subfolder_path}' not found. Please check the folder name and try again.")
        return

    module_path = os.path.join(subfolder_path, f"{module}.py")

    if not os.path.exists(module_path):
        print(f"Module '{module}' not found in subfolder '{subfolder}'. Please check the module name and try again.")
        return

    print(f"Attempting to load and run function: '{function}' from module: '{module}'")

    try:
        captured_output = io.StringIO()
        original_stdout = sys.stdout
        sys.stdout = captured_output

        # Load the module dynamically
        spec = importlib.util.spec_from_file_location(module, module_path)
        loaded_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(loaded_module)

        # Check for and execute the specified function if present
        if hasattr(loaded_module, function):
            print(f"Executing '{function}' function in module '{module}'")
            getattr(loaded_module, function)()
        else:
            print(f"Module '{module}' does not have a function named '{function}' to execute.")

        sys.stdout = original_stdout
        output = captured_output.getvalue()
        if output:
            print(f"Module Output:\n{output}")  # Print captured output
        else:
            print(f"Module '{module}' executed successfully, no output.")

    except Exception as e:
        sys.stdout = original_stdout
        print(f"Error running function '{function}' in module '{module}': {e}\n"
            "Ensure that the module is correctly implemented and has no syntax errors.")
