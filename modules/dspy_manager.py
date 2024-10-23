import yaml
import importlib
import os

YAML_PATH = os.getenv("YAML_PATH", "dspy_modules.yaml")

class DSPyManager:
    def __init__(self):
        """Initialize DSPy Manager with modules loaded from a YAML file."""
        self.dspy_modules = self.load_dspy_modules()

    def load_dspy_modules(self):
        """Load the DSPy modules metadata from the YAML file."""
        try:
            with open(YAML_PATH, 'r') as file:
                dspy_data = yaml.safe_load(file)
            return dspy_data.get("dspy_modules", [])
        except FileNotFoundError:
            print(f"Error: YAML file not found at {YAML_PATH}")
            return []
        except yaml.YAMLError as e:
            print(f"Error: Failed to parse YAML file at {YAML_PATH}. Details: {e}")
            return []

    def get_module_by_name(self, module_name):
        """Dynamically import a module by name using the metadata from the YAML file."""
        for module_info in self.dspy_modules:
            if module_info["name"] == module_name:
                try:
                    # Import module dynamically using import path from YAML
                    module = importlib.import_module(module_info["import_path"])
                    return module
                except ModuleNotFoundError as e:
                    print(f"Error: Module '{module_name}' not found. Details: {e}")
                    return None
                except Exception as e:
                    print(f"Error: An unexpected error occurred while importing module '{module_name}'. Details: {e}")
                    return None
        return None

    def execute_function(self, module_name, function_name, *args, **kwargs):
        """Execute a selected function from a given module."""
        module = self.get_module_by_name(module_name)
        if not module:
            print("Module not found.")
            return None

        func = getattr(module, function_name, None)
        if callable(func):
            try:
                print(f"Executing {function_name} from {module_name} with arguments {args} and keyword arguments {kwargs}...")
                result = func(*args, **kwargs)
                return result
            except TypeError as e:
                print(f"Error executing function '{function_name}': {e}")
                return None
            except Exception as e:
                print(f"Error executing function '{function_name}': {e}")
                return None
        else:
            print(f"Function {function_name} not found in {module_name}.")
            return None

    def list_functions(self, module_name):
        """List all available functions for a given module."""
        module = self.get_module_by_name(module_name)
        if not module:
            print(f"Module '{module_name}' not found.")
            return []

        functions = [func for func in dir(module) if callable(getattr(module, func)) and not func.startswith("__")]
        for idx, func in enumerate(functions):
            print(f"{idx + 1}: {func}")
        return functions
