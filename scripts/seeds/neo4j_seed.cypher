// ==============================================================================
// DEVFORGE NEO4J STARTER SEED CYPHER QUERY
// ==============================================================================

// Clean existing graph
MATCH (n) DETACH DELETE n;

// Create Platform and Database Node structures
CREATE (df:Platform {name: 'DevForge', version: '1.0.0'})
CREATE (pg:Database {name: 'PostgreSQL', type: 'Relational'})
CREATE (mg:Database {name: 'MongoDB', type: 'Document'})
CREATE (rd:Database {name: 'Redis', type: 'Key-Value'})
CREATE (n4:Database {name: 'Neo4j', type: 'Graph'})
CREATE (qd:Database {name: 'Qdrant', type: 'Vector'})
CREATE (ch:Database {name: 'ChromaDB', type: 'Vector'})

// Establish integration relations
CREATE (df)-[:INTEGRATES]->(pg)
CREATE (df)-[:INTEGRATES]->(mg)
CREATE (df)-[:INTEGRATES]->(rd)
CREATE (df)-[:INTEGRATES]->(n4)
CREATE (df)-[:INTEGRATES]->(qd)
CREATE (df)-[:INTEGRATES]->(ch);
