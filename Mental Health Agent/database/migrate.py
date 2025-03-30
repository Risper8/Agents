import os
import json
from pathlib import Path
from typing import List, Dict, Any
import hashlib
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# Adjust the import path as necessary
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.modules.kb_graph import analyze_file_pair, update_knowledge_graph, create_edge, get_related_nodes

DATA_DIR = Path('data')

load_dotenv()

DB_HOST = os.getenv("host")
DB_USER = os.getenv("user")
DB_PASSWORD = os.getenv("password")
DB_NAME = os.getenv("database")

def load_json_files(directory: Path) -> List[Dict[str, Any]]:
    json_files = []
    for file_path in directory.glob('**/*.json'):
        print(file_path)
        with open(file_path, 'r', encoding='utf-8') as file:
            try:
                data = json.load(file)
                json_files.append(data)
            except json.JSONDecodeError:
                print(f"Error decoding JSON from file: {file_path}")
    return json_files

def process_files(files: List[Dict[str, Any]]):
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        if not conn.is_connected():
            print("Failed to connect to the database.")
            return
        
        cursor = conn.cursor()

        for i, file1 in enumerate(files):
            try:
                update_knowledge_graph(file1)
                file1_id = hashlib.md5(json.dumps(file1, sort_keys=True).encode()).hexdigest()

                for file2 in files[i+1:]:
                    try:
                        file2_id = hashlib.md5(json.dumps(file2, sort_keys=True).encode()).hexdigest()
                        edge_categories = analyze_file_pair(file1, file2)

                        for category, strength in edge_categories:
                            try:
                                create_edge(file1_id, file2_id, category, strength)
                            except Error as e:
                                print(f"Error inserting edge into database: {e}")
                    except Exception as e:
                        print(f"Error processing file pair: {e}")
            except Exception as e:
                print(f"Error processing file: {e}")

        conn.commit()
        cursor.close()
        conn.close()
        print("Migration complete and data committed to the database.")

    except Error as e:
        print(f"Error connecting to the database: {e}")

def main():
    print("Starting migration process...")
    files = load_json_files(DATA_DIR)
    print(f"Loaded {len(files)} JSON files.")

    process_files(files)

if __name__ == "__main__":
    main()
