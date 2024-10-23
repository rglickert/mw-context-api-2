import subprocess
import os
import yaml
import logging

# Set the compose file path based on your specific directory structure.
# You can use an environment variable to override this if needed.
COMPOSE_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'docker-compose.yml')
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContainerManager:
    def __init__(self):
        self.containers = self.load_containers_from_compose()
        # Lazy import to avoid circular dependencies
        from modules.neo4j_manager import Neo4jManager
        self.neo4j_manager = Neo4jManager()

    def load_containers_from_compose(self):
        """Load container configurations from docker-compose.yml to manage dynamically."""
        if not os.path.exists(COMPOSE_FILE_PATH):
            logger.error(f"Compose file not found at path: {COMPOSE_FILE_PATH}")
            raise FileNotFoundError(f"Compose file not found at path: {COMPOSE_FILE_PATH}")
        
        with open(COMPOSE_FILE_PATH, 'r') as file:
            compose_data = yaml.safe_load(file)
        
        containers = []
        for service_name, config in compose_data.get('services', {}).items():
            container_info = {
                "name": service_name,
                "image": config.get("image"),
                "ports": config.get("ports", []),
                "env": config.get("environment", {})
            }
            containers.append(container_info)
        
        return containers

    def start_docker_containers(self, use_compose=True):
        """Start containers using Docker Compose or individually."""
        if use_compose:
            self._start_all_containers_with_compose()
        else:
            # Use the Docker API to start individual containers as needed
            for container in self.containers:
                self.start_container(container["name"])

    def stop_docker_containers(self):
        """Stop containers using Docker Compose."""
        try:
            subprocess.run(["docker-compose", "-f", COMPOSE_FILE_PATH, "down"], check=True)
            logger.info("All containers stopped successfully.")
        except subprocess.CalledProcessError as e:
            logger.error(f"Error stopping containers via Docker Compose: {e}")

    def _start_all_containers_with_compose(self):
        """Starts all containers using Docker Compose."""
        try:
            subprocess.run(["docker-compose", "-f", COMPOSE_FILE_PATH, "up", "-d"], check=True)
            logger.info("All containers started successfully.")

            # Perform initial setup for Neo4j after start
            self.neo4j_manager.run_initial_setup()

        except subprocess.CalledProcessError as e:
            logger.error(f"Error starting containers via Docker Compose: {e}")