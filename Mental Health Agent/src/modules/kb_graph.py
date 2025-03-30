import json
import hashlib
import mysql.connector
from pathlib import Path
from typing import Dict, Any, List, Tuple, Union, Optional
from collections import Counter
import re
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

DB_HOST = os.getenv("host")
DB_USER = os.getenv("user")
DB_PASSWORD = os.getenv("password")
DB_NAME = os.getenv("database") 

def get_db_connection():
    conn = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    return conn

def create_edge(source_id: str, target_id: str, relationship_type: str, strength: float):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO edges (source_id, target_id, relationship_type, strength)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE strength = VALUES(strength)
        ''', (source_id, target_id, relationship_type, strength))
        conn.commit()

def update_knowledge_graph(new_information: Union[Dict[str, Any], List[Any], str]):
    info_id = hashlib.md5(json.dumps(new_information, sort_keys=True).encode()).hexdigest()

    key_concepts = extract_key_concepts(new_information)

    for concept in key_concepts:
        create_edge(info_id, concept, "RELATED_TO", 1.0)

    related_info = find_related_information(new_information)

    for related_id, similarity in related_info:
        create_edge(info_id, related_id, "SIMILAR_TO", similarity)

    print(f"Updated knowledge graph with new information (ID: {info_id})")

def extract_key_concepts(information: Union[Dict[str, Any], List[Any], str]) -> List[str]:
    if isinstance(information, dict):
        return list(information.keys())
    elif isinstance(information, list):
        return [str(i) for i in range(len(information))]  # Use indices as keys for lists
    elif isinstance(information, str):
        return [information]
    else:
        return []  # Return an empty list for unsupported types

def find_related_information(information: Union[Dict[str, Any], List[Any], str]) -> List[Tuple[str, float]]:
    return []

def get_related_nodes(node_id: str, relationship_type: str = None) -> List[Tuple[str, str, float]]:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        if relationship_type:
            cursor.execute('''
                SELECT target_id, relationship_type, strength
                FROM edges
                WHERE source_id = %s AND relationship_type = %s
                UNION
                SELECT source_id, relationship_type, strength
                FROM edges
                WHERE target_id = %s AND relationship_type = %s
            ''', (node_id, relationship_type, node_id, relationship_type))
        else:
            cursor.execute('''
                SELECT target_id, relationship_type, strength
                FROM edges
                WHERE source_id = %s
                UNION
                SELECT source_id, relationship_type, strength
                FROM edges
                WHERE target_id = %s
            ''', (node_id, node_id))
        return cursor.fetchall()

def analyze_file_pair(file1: Dict[str, Any], file2: Dict[str, Any]) -> List[Tuple[str, float]]:
    edge_categories = []

    if 'content' in file1 and 'content' in file2:
        content_similarity = compare_content(file1['content'], file2['content'])
        if content_similarity > 0.3:
            edge_categories.append(("SIMILAR_CONTENT", content_similarity))

    if 'tags' in file1 and 'tags' in file2:
        tag_similarity = compare_tags(file1['tags'], file2['tags'])
        if tag_similarity > 0:
            edge_categories.append(("SHARED_TAGS", tag_similarity))

    if 'title' in file1 and 'title' in file2:
        title_similarity = compare_titles(file1['title'], file2['title'])
        if title_similarity > 0.5:
            edge_categories.append(("RELATED_TOPIC", title_similarity))

    if 'timestamp' in file1 and 'timestamp' in file2:
        time_relation = compare_timestamps(file1['timestamp'], file2['timestamp'])
        if time_relation:
            edge_categories.append(time_relation)

    return edge_categories

def compare_content(content1: Union[str, Dict, List], content2: Union[str, Dict, List]) -> float:
    def extract_text(content: Union[str, Dict, List]) -> str:
        if isinstance(content, str):
            return content
        elif isinstance(content, dict):
            return ' '.join(str(v) for v in content.values() if isinstance(v, str))
        elif isinstance(content, list):
            return ' '.join(str(item) for item in content if isinstance(item, str))
        else:
            return ''

    text1 = extract_text(content1)
    text2 = extract_text(content2)

    words1 = set(re.findall(r'\w+', text1.lower()))
    words2 = set(re.findall(r'\w+', text2.lower()))
    common_words = words1.intersection(words2)
    return len(common_words) / (len(words1) + len(words2) - len(common_words)) if (words1 or words2) else 0

def compare_tags(tags1: List[str], tags2: List[str]) -> float:
    common_tags = set(tags1).intersection(set(tags2))
    return len(common_tags) / len(set(tags1).union(set(tags2))) if (tags1 or tags2) else 0

def compare_titles(title1: str, title2: str) -> float:
    words1 = set(re.findall(r'\w+', title1.lower()))
    words2 = set(re.findall(r'\w+', title2.lower()))
    common_words = words1.intersection(words2)
    return len(common_words) / (len(words1) + len(words2) - len(common_words)) if (words1 or words2) else 0

def compare_timestamps(timestamp1: str, timestamp2: str) -> Optional[Tuple[str, float]]:
    t1 = parse_timestamp(timestamp1)
    t2 = parse_timestamp(timestamp2)
    time_diff = abs((t2 - t1).total_seconds())

    if time_diff < 3600:  # Within an hour
        return ("TEMPORALLY_CLOSE", 0.9)
    elif time_diff < 86400:  # Within a day
        return ("SAME_DAY", 0.7)
    elif time_diff < 604800:  # Within a week
        return ("SAME_WEEK", 0.5)
    else:
        return None

def parse_timestamp(timestamp: str) -> datetime:
    return datetime.fromisoformat(timestamp.replace('Z', '+00:00'))

if __name__ == "__main__":
    file1 = {
        "title": "Introduction to Python",
        "content": "Python is a high-level programming language...",
        "tags": ["programming", "beginner", "python"],
        "timestamp": "2023-05-01T10:00:00Z"
    }
    file2 = {
        "title": "Python for Data Science",
        "content": "Python is widely used in data science for its simplicity...",
        "tags": ["programming", "data science", "python"],
        "timestamp": "2023-05-01T11:30:00Z"
    }

    edge_categories = analyze_file_pair(file1, file2)
    print("Edge categories:", edge_categories)

    update_knowledge_graph(file1)
    update_knowledge_graph(file2)

    file1_id = hashlib.md5(json.dumps(file1, sort_keys=True).encode()).hexdigest()
    file2_id = hashlib.md5(json.dumps(file2, sort_keys=True).encode()).hexdigest()
    for category, strength in edge_categories:
        create_edge(file1_id, file2_id, category, strength)

    related_nodes = get_related_nodes(file1_id)
    print("Related nodes:", related_nodes)
