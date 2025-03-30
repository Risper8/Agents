# src/utils/schema.py

SCHEMA = """
CREATE TABLE IF NOT EXISTS edges (
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
);

CREATE TABLE IF NOT EXISTS node_attributes (
    node_id VARCHAR(255) NOT NULL,
    attribute_name VARCHAR(255) NOT NULL,
    attribute_value TEXT NOT NULL,
    confidence FLOAT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (node_id, attribute_name)
);

CREATE TABLE IF NOT EXISTS hierarchies (
    parent_id VARCHAR(255) NOT NULL,
    child_id VARCHAR(255) NOT NULL,
    hierarchy_type VARCHAR(255) NOT NULL,
    confidence FLOAT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (parent_id, child_id, hierarchy_type)
);

CREATE INDEX idx_edges_source_id ON edges(source_id);
CREATE INDEX idx_edges_target_id ON edges(target_id);
CREATE INDEX idx_edges_relationship_type ON edges(relationship_type);
CREATE INDEX idx_edges_start_time ON edges(start_time);
CREATE INDEX idx_edges_end_time ON edges(end_time);
CREATE INDEX idx_node_attributes_node_id ON node_attributes(node_id);
CREATE INDEX idx_hierarchies_parent_id ON hierarchies(parent_id);
CREATE INDEX idx_hierarchies_child_id ON hierarchies(child_id);

DELIMITER $$
CREATE TRIGGER update_edges_timestamp
BEFORE UPDATE ON edges
FOR EACH ROW
BEGIN
    SET NEW.updated_at = CURRENT_TIMESTAMP;
END$$
DELIMITER ;

DELIMITER $$
CREATE TRIGGER update_node_attributes_timestamp
BEFORE UPDATE ON node_attributes
FOR EACH ROW
BEGIN
    SET NEW.updated_at = CURRENT_TIMESTAMP;
END$$
DELIMITER ;

DELIMITER $$
CREATE TRIGGER update_hierarchies_timestamp
BEFORE UPDATE ON hierarchies
FOR EACH ROW
BEGIN
    SET NEW.updated_at = CURRENT_TIMESTAMP;
END$$
DELIMITER ;
"""
