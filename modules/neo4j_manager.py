# neo4j_manager.py

import subprocess
import time
import requests

class Neo4jManager:
    def __init__(self, container_name="neo4j"):
        self.container_name = container_name

    def run_initial_setup(self):
        """Run any required setup for Neo4j after it starts."""
        neo4j_url = "http://localhost:7474"
        timeout = 60  # 60 seconds timeout for health check

        # Check Neo4j health status
        for _ in range(timeout):
            try:
                response = requests.get(neo4j_url)
                if response.status_code == 200:
                    print("Neo4j is ready.")
                    break
            except requests.ConnectionError:
                time.sleep(1)
        else:
            print("Neo4j did not become ready in time.")
            return

        # Proceed with initial setup
        init_command = [
            "docker", "exec", self.container_name,
            "cypher-shell", "-u", "neo4j", "-p", "password", "CREATE CONSTRAINT ON (n:Role) ASSERT n.id IS UNIQUE"
        ]
        try:
            subprocess.run(init_command, check=True)
            print("Neo4j setup complete with initial data/constraints.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to run initialization script for Neo4j: {e}")
