import mysql.connector
from mysql.connector import Error
from pathlib import Path
import os
from dotenv import load_dotenv


load_dotenv()

DB_HOST = os.getenv("host")
DB_USER = os.getenv("user")
DB_PASSWORD = os.getenv("password")
DB_NAME = os.getenv("database")

def verify_setup():
    try:
        # Connect to the MySQL database
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )

        if conn.is_connected():
            print("Successfully connected to the database.")
            cursor = conn.cursor()

            print("Verifying database setup...")

            # Check indexes
            cursor.execute("SHOW INDEXES FROM edges;")
            indexes = cursor.fetchall()
            print("\nIndexes on 'edges' table:")
            for index in indexes:
                print(f"  - {index[2]}")  

            # Test creating an edge
            try:
                cursor.execute("""
                INSERT INTO edges (source_id, target_id, relationship_type, strength)
                VALUES ('test_source', 'test_target', 'test_relation', 0.5)
                """)
                conn.commit()
                print("\nTest edge inserted successfully.")
            except Error as e:
                print(f"\nError inserting test edge: {e}")

            # Verify the insertion
            cursor.execute("SELECT * FROM edges WHERE source_id = 'test_source'")
            result = cursor.fetchone()
            if result:
                print(f"Retrieved test edge: {result}")
            else:
                print("Failed to retrieve test edge.")

            # Test updating the edge
            try:
                cursor.execute("""
                UPDATE edges
                SET strength = 0.7
                WHERE source_id = 'test_source' AND target_id = 'test_target'
                """)
                conn.commit()
                print("\nTest edge updated successfully.")
            except Error as e:
                print(f"\nError updating test edge: {e}")

            # Verify the update
            cursor.execute("SELECT * FROM edges WHERE source_id = 'test_source'")
            result = cursor.fetchone()
            if result:
                print(f"Retrieved updated test edge: {result}")
                print("Check if 'updated_at' timestamp has changed.")
            else:
                print("Failed to retrieve updated test edge.")

            # Clean up test data
            cursor.execute("DELETE FROM edges WHERE source_id = 'test_source'")
            conn.commit()
            print("\nTest data cleaned up.")

            cursor.close()
            conn.close()
            print("Connection closed.")
        else:
            print("Failed to connect to the database.")

    except Error as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify_setup()
