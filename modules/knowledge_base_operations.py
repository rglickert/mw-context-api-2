import subprocess
import json
from modules.add_context_folder import add_context_folder  # Import the function from add_context_folder.py

# Main entry point for Knowledge Management
def knowledge_management_menu():
    """Interactive menu to manage the knowledge base."""
    
    while True:
        print("\n--- Knowledge Base Management Menu ---")
        print("1. Add Knowledge Entry")
        print("2. View Knowledge Base Entries")
        print("3. Update Knowledge Entry")
        print("4. Delete Knowledge Entry")
        print("5. Add File to Knowledge Collection")
        print("6. Add Context Folder to Knowledge Base")
        print("7. Back to Main Menu")
        
        choice = input("Enter your choice (1-7): ")

        if choice == '1':
            title = input("Enter title for the knowledge entry: ")
            content = input("Enter content for the knowledge entry: ")
            entry = {"title": title, "content": content}
            add_knowledge_entry(entry)

        elif choice == '2':
            view_knowledge_base()

        elif choice == '3':
            entry_id = input("Enter the ID of the entry to update: ")
            new_content = input("Enter the new content for the entry: ")
            update_knowledge_entry(entry_id, new_content)

        elif choice == '4':
            entry_id = input("Enter the ID of the entry to delete: ")
            delete_knowledge_entry(entry_id)

        elif choice == '5':
            file_path = input("Enter the file path to add to the knowledge collection: ")
            add_file_to_knowledge_collection(file_path)

        elif choice == '6':
            repo_url = input("Enter the GitHub URL or Local Path for the Context Folder: ").strip()
            add_context_folder(repo_url)

        elif choice == '7':
            print("Returning to Main Menu.")
            break

        else:
            print("Invalid choice. Please try again.")

# Supporting Functions
def execute_query(query):
    """Helper function to execute PostgreSQL commands."""
    try:
        command = [
            "docker", "exec", "mw-postgres",
            "psql", "-U", "myuser", "-d", "animals",
            "-c", query
        ]
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error executing query: {e}")
        return None

def add_knowledge_entry(entry):
    """Add a new entry to the knowledge base."""
    title = entry.get('title')
    content = entry.get('content')

    if not title or not content:
        print("Both title and content are required to add a knowledge entry.")
        return

    query = f"INSERT INTO knowledge_base (title, content) VALUES ('{title}', '{content}');"
    execute_query(query)
    print(f"Successfully added knowledge entry: {title}")

def view_knowledge_base():
    """View all entries in the knowledge base."""
    query = "SELECT * FROM knowledge_base;"
    result = execute_query(query)
    if result:
        print("Knowledge Base Entries:")
        print(result)
    else:
        print("No entries found in the knowledge base.")

def update_knowledge_entry(entry_id, new_content):
    """Update an existing entry in the knowledge base."""
    query = f"UPDATE knowledge_base SET content = '{new_content}' WHERE id = {entry_id};"
    result = execute_query(query)
    if result:
        print(f"Successfully updated entry with ID: {entry_id}")
    else:
        print("Error updating entry. Please check the ID and try again.")

def delete_knowledge_entry(entry_id):
    """Delete an entry from the knowledge base by ID."""
    query = f"DELETE FROM knowledge_base WHERE id = {entry_id};"
    result = execute_query(query)
    if result:
        print(f"Successfully deleted entry with ID: {entry_id}")
    else:
        print("Error deleting entry. Please check the ID and try again.")

# Placeholder functions for adding and using uploaded files
def add_file_to_knowledge_collection(file_path):
    print(f"File '{file_path}' has been added to the knowledge collection.")

