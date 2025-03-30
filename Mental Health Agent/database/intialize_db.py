import mysql.connector
from mysql.connector import Error
from pathlib import Path
from schema import SCHEMA
from dotenv import load_dotenv
import os

load_dotenv()

DB_HOST = os.getenv("host")
DB_USER = os.getenv("user")
DB_PASSWORD = os.getenv("password")
DB_NAME = os.getenv("database")

# MySQL Configuration
def create_database():
    """Create the database if it doesn't exist."""
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            # database=DB_NAME
        )
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        print(f"Database '{DB_NAME}' ensured to exist.")
        conn.close()
    except Error as e:
        print(f"Error creating database: {e}")


def initialize_database():
    """Initialize the database by creating tables and setting up schema."""
    # Connect to the MySQL server and select the database
    conn = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME  # Make sure to select the database here
    )
    create_database()

    if conn.is_connected():
        cursor = conn.cursor()

        # Execute full schema
        cursor.execute("SET sql_mode = ''")  # Avoid strict mode issues
        for stmt in SCHEMA.split(";"):
            if stmt.strip():
                try:
                    cursor.execute(stmt)
                except Error as e:
                    print(f"Error executing statement: {stmt}\n{e}")

        conn.commit()
        conn.close()
    print("Database initialized with schema.")


def update_existing_database():
    """Update existing database with new tables and columns."""
    conn = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME  
    )
    cursor = conn.cursor()

    cursor.execute("SHOW TABLES LIKE 'edges'")
    if cursor.fetchone():
        # Add missing columns if they don't exist
        columns_to_add = [
            ("confidence", "FLOAT NOT NULL DEFAULT 1.0"),
            ("bidirectional", "BOOLEAN DEFAULT FALSE"),
            ("start_time", "TIMESTAMP NULL"),
            ("end_time", "TIMESTAMP NULL"),
            ("metadata", "JSON NULL")
        ]
        for column_name, column_type in columns_to_add:
            try:
                cursor.execute(f"ALTER TABLE edges ADD COLUMN {column_name} {column_type}")
                print(f"Added column {column_name} to edges table")
            except Error:
                print(f"Column {column_name} already exists in edges table")
    else:
        # Create edges table if it doesn't exist
        cursor.execute("""
        CREATE TABLE edges (
            id INT AUTO_INCREMENT PRIMARY KEY,
            source_id VARCHAR(255) NOT NULL,
            target_id VARCHAR(255) NOT NULL,
            relationship_type VARCHAR(255) NOT NULL,
            strength FLOAT NOT NULL,
            confidence FLOAT NOT NULL DEFAULT 1.0,
            bidirectional TINYINT(1) DEFAULT 0,
            start_time DATETIME,
            end_time DATETIME,
            metadata JSON,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            UNIQUE(source_id, target_id, relationship_type)
        )
        """)
        print("Created edges table.")

    # Create node_attributes table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS node_attributes (
        node_id VARCHAR(255) NOT NULL,
        attribute_name VARCHAR(255) NOT NULL,
        attribute_value TEXT NOT NULL,
        confidence FLOAT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        PRIMARY KEY (node_id, attribute_name)
    )
    """)

    # Create hierarchies table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS hierarchies (
        parent_id VARCHAR(255) NOT NULL,
        child_id VARCHAR(255) NOT NULL,
        hierarchy_type VARCHAR(255) NOT NULL,
        confidence FLOAT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        PRIMARY KEY (parent_id, child_id, hierarchy_type)
    )
    """)

    # Create indexes (ensure they don't already exist)
    cursor.execute("SHOW INDEXES FROM edges WHERE Key_name = 'idx_edges_source_id'")
    if not cursor.fetchone():
        cursor.execute("CREATE INDEX idx_edges_source_id ON edges(source_id)")

    cursor.execute("SHOW INDEXES FROM edges WHERE Key_name = 'idx_edges_target_id'")
    if not cursor.fetchone():
        cursor.execute("CREATE INDEX idx_edges_target_id ON edges(target_id)")

    cursor.execute("SHOW INDEXES FROM edges WHERE Key_name = 'idx_edges_relationship_type'")
    if not cursor.fetchone():
        cursor.execute("CREATE INDEX idx_edges_relationship_type ON edges(relationship_type)")

    cursor.execute("SHOW INDEXES FROM node_attributes WHERE Key_name = 'idx_node_attributes_node_id'")
    if not cursor.fetchone():
        cursor.execute("CREATE INDEX idx_node_attributes_node_id ON node_attributes(node_id)")

    cursor.execute("SHOW INDEXES FROM hierarchies WHERE Key_name = 'idx_hierarchies_parent_id'")
    if not cursor.fetchone():
        cursor.execute("CREATE INDEX idx_hierarchies_parent_id ON hierarchies(parent_id)")

    cursor.execute("SHOW INDEXES FROM hierarchies WHERE Key_name = 'idx_hierarchies_child_id'")
    if not cursor.fetchone():
        cursor.execute("CREATE INDEX idx_hierarchies_child_id ON hierarchies(child_id)")

    conn.commit()
    conn.close()
    print("Existing database updated with new schema elements.")


def check_database_status():
    """Check the database status and print table information."""
    conn = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME  # Ensure the database is selected
    )
    cursor = conn.cursor()

    # Get tables
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    print("\nDatabase Status:")
    print(f"Tables found: {len(tables)}")

    for table in tables:
        table_name = table[0]
        cursor.execute(f"DESCRIBE {table_name}")
        columns = cursor.fetchall()
        print(f"\nTable: {table_name}")
        print("Columns:")
        for column in columns:
            print(f"  - {column[0]} ({column[1]})")

        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        row_count = cursor.fetchone()[0]
        print(f"Row count: {row_count}")

    conn.close()


def main():
    create_database()  
    initialize_database()  
    check_database_status()  

    print("\nDatabase setup completed successfully.")


if __name__ == "__main__":
    main()
