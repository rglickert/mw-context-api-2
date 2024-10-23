# main.py - Flask Web Version
from flask import Flask, render_template
from modules.api_endpoints import docker_manage, add_knowledge, list_modules, execute_function, get_functions
from modules.container_manager import ContainerManager
from modules.dspy_manager import DSPyManager

app = Flask(__name__)

# Register API routes using imported functions from api_endpoints
app.add_url_rule('/docker_manage', view_func=docker_manage, methods=['POST'])
app.add_url_rule('/add_knowledge', view_func=add_knowledge, methods=['POST'])
app.add_url_rule('/list_modules', view_func=list_modules, methods=['GET'])
app.add_url_rule('/execute_function', view_func=execute_function, methods=['POST'])
app.add_url_rule('/get_functions', view_func=get_functions, methods=['GET'])

@app.route('/')
def home():
    """Render home page with available options."""
    return render_template("index.html")  # Make sure 'index.html' is located in the templates directory

# Initialize managers only once
container_manager = ContainerManager()
dspy_manager = DSPyManager

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
