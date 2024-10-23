# rag_logger.py

import os
import json

RAG_LOG_PATH = "rag_log.json"  # Path to the RAG log file

def log_rag_item(file_info):
    try:
        # Verify write access to the RAG log path
        if not os.access(os.path.dirname(RAG_LOG_PATH) or '.', os.W_OK):
            print(f"WARNING: No write access to log directory: {os.path.dirname(RAG_LOG_PATH) or '.'}. Ensure permissions are set correctly.")
            return

        log_entry = {
            "id": file_info.get("id"),
            "user_id": file_info.get("user_id"),
            "filename": file_info.get("filename"),
            "meta": file_info.get("meta"),
            "created_at": file_info.get("created_at")
        }
        if not os.path.exists(RAG_LOG_PATH):
            with open(RAG_LOG_PATH, 'w') as log_file:
                json.dump([], log_file)

        with open(RAG_LOG_PATH, 'r') as log_file:
            rag_log = json.load(log_file)

        rag_log.append(log_entry)

        with open(RAG_LOG_PATH, 'w') as log_file:
            json.dump(rag_log, log_file, indent=4)
            print("RAG item successfully logged.")
    except Exception as e:
        print(f"Failed to log RAG item: {e}")

def view_rag_log():
    try:
        if not os.path.exists(RAG_LOG_PATH):
            print("No RAG items logged yet.")
            return

        with open(RAG_LOG_PATH, 'r') as log_file:
            rag_log = json.load(log_file)
            if not rag_log:
                print("No RAG items logged yet.")
            else:
                for idx, item in enumerate(rag_log, start=1):
                    print(f"{idx}. File Name: {item['meta']['name']}, File ID: {item['id']}, Created At: {item['created_at']}")
    except Exception as e:
        print(f"Failed to read RAG log: {e}")
