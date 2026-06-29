-- ==============================================================================
-- DEVFORGE POSTGRESQL STARTER SEED SCRIPT
-- ==============================================================================

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO users (name, email) VALUES
('Alice Smith', 'alice@devforge.local'),
('Bob Jones', 'bob@devforge.local')
ON CONFLICT (email) DO NOTHING;

-- Map tasks to existing seed users
INSERT INTO tasks (user_id, title, description, completed) VALUES
(1, 'Configure Ingress Gateway', 'Set up reverse proxies for DevForge admin UIs.', true),
(1, 'Deploy SSL certificates', 'Generate self-signed SSL certs for local secure routing.', false),
(2, 'Scaffold Spring Boot project', 'Create starter backend template for Phase 5.', true);
