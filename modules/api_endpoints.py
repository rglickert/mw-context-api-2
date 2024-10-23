from flask import request, jsonify
from flask_expects_json import expects_json
from modules.container_manager import ContainerManager
from modules.dspy_manager import DSPyManager

# Initialize the container and DSPy managers
container_manager = ContainerManager()
dspy_manager = DSPyManager()  # Removed LLM reference; aligned with modular management

# JSON Schema for Docker management endpoint input validation
docker_manage_schema = {
    "type": "object",
    "properties": {
        "action": {"type": "string", "enum": ["start", "stop"]},
        "use_compose": {"type": "boolean"}
    },
    "required": ["action"]
}

# Endpoint to manage Docker containers
@expects_json(docker_manage_schema)
def docker_manage():
    """API to manage Docker containers."""
    data = request.get_json()
    action = data.get('action')
    use_compose = data.get('use_compose', True)  # Default to using Docker Compose

    try:
        if action == 'start':
            container_manager.start_docker_containers(use_compose=use_compose)
        elif action == 'stop':
            container_manager.stop_docker_containers()
        else:
            return jsonify({"error": "Invalid action."}), 400
        return jsonify({"message": f"Containers {action}ed successfully."})
    except Exception as e:
        return jsonify({"error": f"Failed to {action} containers. Details: {str(e)}"}), 500

# Endpoint to list all available DSPy modules
def list_modules():
    """List all available DSPy modules."""
    try:
        modules = dspy_manager.dspy_modules
        return jsonify({"modules": modules})
    except Exception as e:
        return jsonify({"error": f"Failed to list modules. Details: {str(e)}"}), 500

# Endpoint to get functions for a given DSPy module
def get_functions():
    """List all available functions for a given DSPy module."""
    module_name = request.args.get('module_name')
    module = dspy_manager.get_module_by_name(module_name)

    if not module:
        return jsonify({"error": f"Module '{module_name}' not found."}), 404

    # Extract the list of functions
    functions = dspy_manager.list_functions(module_name)

    return jsonify({"functions": functions})

# Endpoint to execute a selected function from a module
def execute_function():
    """Execute a selected function from a module."""
    module_name = request.json.get('module_name')
    function_name = request.json.get('function_name')
    args = request.json.get('args', [])
    kwargs = request.json.get('kwargs', {})

    try:
        result = dspy_manager.execute_function(module_name, function_name, *args, **kwargs)
        if result is not None:
            return jsonify({"result": result})
        else:
            return jsonify({"error": "Execution failed."}), 400
    except Exception as e:
        return jsonify({"error": f"Execution error. Details: {str(e)}"}), 500

# Endpoint to add knowledge to Neo4j
def add_knowledge():
    """API to add knowledge to Neo4j."""
    data = request.get_json()
    subject, relationship, obj = data.get('subject'), data.get('relationship'), data.get('object')
    if subject and relationship and obj:
        try:
            dspy_manager.add_knowledge_entry(subject.title(), relationship.upper(), obj.title())
            return jsonify({"message": f"Added knowledge entry: ({subject.title()})-[:{relationship.upper()}]->({obj.title()})"})
        except Exception as e:
            return jsonify({"error": f"Failed to add knowledge entry. Details: {str(e)}"}), 500
    else:
        return jsonify({"error": "All fields (subject, relationship, object) are required."}), 400
