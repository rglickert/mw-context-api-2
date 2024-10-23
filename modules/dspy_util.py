import yaml
import importlib
import os
import sys
import logging

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

YAML_PATH = os.getenv("YAML_PATH", "./dspy_modules.yaml")


def load_dspy_modules():
    """Load the DSPy modules metadata from the YAML file."""
    try:
        with open(YAML_PATH, 'r') as file:
            dspy_data = yaml.safe_load(file)
        return dspy_data["dspy_modules"]
    except FileNotFoundError:
        logger.error(f"The YAML file at {YAML_PATH} was not found.")
        return []
    except yaml.YAMLError as e:
        logger.error(f"Failed to parse the YAML file at {YAML_PATH}. Details: {e}")
        return []
    except Exception as e:
        logger.error(f"An unexpected error occurred while loading the YAML file. Details: {e}")
        return []


def get_module_by_name(module_name, dspy_modules):
    """Dynamically import a module by name using the metadata from the YAML file."""
    for module_info in dspy_modules:
        if module_info["name"] == module_name:
            try:
                # Attempt to import using the custom DSPy path from the project directory
                module = importlib.import_module(module_info["import_path"])
                return module
            except ModuleNotFoundError as e:
                logger.warning(f"Module '{module_name}' not found in the project directory. Trying site-packages. Details: {e}")
                try:
                    # Attempt to import from the global site-packages instead
                    sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))  # Add fallback path
                    module = importlib.import_module(module_info["import_path"])
                    # Update the YAML with the correct working path if the fallback succeeds
                    update_yaml_with_working_path(module_name, module_info["import_path"])
                    return module
                except ModuleNotFoundError as e:
                    logger.error(f"Module '{module_name}' not found in site-packages either. Details: {e}")
                    return None
                except Exception as e:
                    logger.error(f"Unexpected error when importing module '{module_name}' from site-packages. Details: {e}")
                    return None
            except Exception as e:
                logger.error(f"An unexpected error occurred while importing module '{module_name}'. Details: {e}")
                return None
    logger.error(f"Module '{module_name}' not found in available DSPy modules.")
    return None


def update_yaml_with_working_path(module_name, import_path):
    """Update the YAML file with the working import path to optimize future imports."""
    try:
        with open(YAML_PATH, 'r') as file:
            dspy_data = yaml.safe_load(file)
        for module_info in dspy_data["dspy_modules"]:
            if module_info["name"] == module_name:
                module_info["import_path"] = import_path + " # Updated to working path"
                break
        with open(YAML_PATH, 'w') as file:
            yaml.safe_dump(dspy_data, file)
        logger.info(f"Updated YAML with working path for module '{module_name}'.")
    except Exception as e:
        logger.error(f"Failed to update the YAML file with the working path. Details: {e}")


def list_available_modules(dspy_modules):
    """List all available modules for user selection."""
    logger.info("Available Modules:")
    for idx, module in enumerate(dspy_modules):
        logger.info(f"{idx + 1}: {module['name']} - {module['description']}")


def list_functions(module_name, dspy_modules):
    """List all functions available in a given DSPy module."""
    module = get_module_by_name(module_name, dspy_modules)
    if not module:
        return []
    return [func for func in dir(module) if callable(getattr(module, func)) and not func.startswith("__")]


def execute_function(module_name, function_name, dspy_modules, *args, **kwargs):
    """Dynamically execute a function from a module."""
    module = get_module_by_name(module_name, dspy_modules)
    if not module:
        logger.error("Module not found.")
        return None

    func = getattr(module, function_name, None)
    if callable(func):
        try:
            logger.info(f"Executing {function_name} from {module_name} with arguments {args} and keyword arguments {kwargs}...")
            result = func(*args, **kwargs)
            logger.info(f"Execution result: {result}")
            return result
        except TypeError as e:
            logger.error(f"Error executing function '{function_name}': {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during execution of '{function_name}': {e}")
            return None
    else:
        logger.error(f"Function '{function_name}' not found in module '{module_name}'.")
        return None

# Example of loading modules and executing a function if script runs independently
if __name__ == "__main__":
    dspy_modules = load_dspy_modules()
    list_available_modules(dspy_modules)
    module_name = input("Enter the name of the module you wish to execute a function from: ")
    function_name = input("Enter the function name you wish to execute: ")
    execute_function(module_name, function_name, dspy_modules)
