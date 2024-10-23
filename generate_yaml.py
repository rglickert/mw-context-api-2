import os
import inspect
import yaml
import importlib.util

MODULES_DIR = "modules/dspy"
OUTPUT_YAML_PATH = r"C:\MWW\mw-Github\mw-context-api\dspy_modules.yaml"

def get_module_info(module_path, module_name):
    """Extract information about a module including name, import path, functions, and description."""
    try:
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Get module docstring if available
        description = inspect.getdoc(module) if module.__doc__ else "No description available."
        
        # Get functions from the module, filtering out duplicates to avoid redundancy
        functions = list(set(func for func, obj in inspect.getmembers(module, inspect.isfunction)))
        
        return {
            "name": module_name,
            "import_path": f"modules.dspy.{module_name}",
            "description": description,
            "functions": functions
        }
    except Exception as e:
        print(f"Failed to import {module_name}: {e}")
        return None

def generate_yaml_for_dspy_modules():
    modules_info = []

    # Walk through the MODULES_DIR and get all Python files
    for root, _, files in os.walk(MODULES_DIR):
        for file in files:
            if file.endswith(".py"):
                module_path = os.path.join(root, file)
                module_name = os.path.splitext(file)[0]
                module_info = get_module_info(module_path, module_name)
                if module_info:
                    modules_info.append(module_info)

    # Write the gathered information into the YAML file
    with open(OUTPUT_YAML_PATH, "w") as yaml_file:
        yaml.dump({"dspy_modules": modules_info}, yaml_file, default_flow_style=False)

    print(f"YAML file generated at: {OUTPUT_YAML_PATH}")

if __name__ == "__main__":
    generate_yaml_for_dspy_modules()
