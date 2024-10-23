import subprocess
import os
from neo4j import GraphDatabase  # Neo4j Python Driver
from modules.role_db_operations import role_exists, list_roles, update_role, add_or_update_role
from modules.role_file_operations import read_role_data_from_yaml
from modules.role_input_operations import get_role_details_from_user, validate_role_details

class Neo4jRoleManager:

    def __init__(self, uri, user, password):
        """Initialize Neo4j connection."""
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        """Close the connection."""
        self.driver.close()

    def add_role(self, role_name, role_type, description, skills, expertise_level):
        """Add a role to the Neo4j database."""
        with self.driver.session() as session:
            session.write_transaction(self._create_and_return_role, role_name, role_type, description, skills, expertise_level)

    @staticmethod
    def _create_and_return_role(tx, role_name, role_type, description, skills, expertise_level):
        query = (
            "CREATE (r:Role {name: $role_name, type: $role_type, description: $description, "
            "skills: $skills, expertise_level: $expertise_level}) "
            "RETURN r"
        )
        tx.run(query, role_name=role_name, role_type=role_type, description=description, skills=skills, expertise_level=expertise_level)

    def update_role(self, role_name, updates):
        """Update a role's properties in Neo4j."""
        with self.driver.session() as session:
            session.write_transaction(self._update_role_properties, role_name, updates)

    @staticmethod
    def _update_role_properties(tx, role_name, updates):
        query = "MATCH (r:Role {name: $role_name}) SET "
        query += ', '.join([f"r.{key} = ${key}" for key in updates.keys()])
        query += " RETURN r"
        tx.run(query, role_name=role_name, **updates)

    def delete_role(self, role_name):
        """Delete a role from Neo4j."""
        with self.driver.session() as session:
            session.write_transaction(self._delete_role, role_name)

    @staticmethod
    def _delete_role(tx, role_name):
        query = "MATCH (r:Role {name: $role_name}) DELETE r"
        tx.run(query, role_name=role_name)

    def list_roles(self):
        """List all roles in the Neo4j database."""
        with self.driver.session() as session:
            roles = session.read_transaction(self._get_all_roles)
            for role in roles:
                print(role)

    @staticmethod
    def _get_all_roles(tx):
        query = "MATCH (r:Role) RETURN r.name AS name, r.type AS type, r.description AS description"
        result = tx.run(query)
        return [{"name": record["name"], "type": record["type"], "description": record["description"]} for record in result]

# In modules/role_manager.py
def role_management_menu():
    # Establish Neo4j connection (URI, User, and Password can be environment variables)
    uri = "bolt://localhost:7687"  # Adjust as per the Neo4j container configuration
    user = "neo4j"
    password = os.getenv("NEO4J_PASSWORD", "default_password")  # Use environment variable for password

    neo4j_manager = Neo4jRoleManager(uri, user, password)

    try:
        while True:
            print("\nRole Management Menu:")
            print("1. Get Role Details")
            print("2. Validate Role Details")
            print("3. Add Role to Neo4j")
            print("4. Update Role in Neo4j")
            print("5. Delete Role in Neo4j")
            print("6. List All Roles in Neo4j")
            print("7. Back to Main Menu")

            choice = input("Enter your choice: ")

            if choice == '1':
                get_role_details_from_user()
            elif choice == '2':
                validate_role_details()
            elif choice == '3':
                role_name = input("Enter role name: ").strip()
                role_type = input("Enter role type: ").strip()
                description = input("Enter role description: ").strip()
                skills = input("Enter skills (comma separated): ").strip()
                expertise_level = input("Enter expertise level: ").strip()

                # Add role to Neo4j
                neo4j_manager.add_role(role_name, role_type, description, skills, expertise_level)

            elif choice == '4':
                role_name = input("Enter role name to update: ").strip()
                updates = {}
                new_type = input("Enter new role type (leave blank to keep current): ").strip()
                if new_type:
                    updates['type'] = new_type
                new_description = input("Enter new description (leave blank to keep current): ").strip()
                if new_description:
                    updates['description'] = new_description
                new_skills = input("Enter new skills (leave blank to keep current): ").strip()
                if new_skills:
                    updates['skills'] = new_skills
                new_expertise = input("Enter new expertise level (leave blank to keep current): ").strip()
                if new_expertise:
                    updates['expertise_level'] = new_expertise

                # Update role in Neo4j
                if updates:
                    neo4j_manager.update_role(role_name, updates)

            elif choice == '5':
                role_name = input("Enter role name to delete: ").strip()
                neo4j_manager.delete_role(role_name)

            elif choice == '6':
                neo4j_manager.list_roles()

            elif choice == '7':
                break
            else:
                print("Invalid choice. Please try again.")
    finally:
        neo4j_manager.close()

