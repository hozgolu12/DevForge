// ==============================================================================
// DEVFORGE MONGODB STARTER SEED SCRIPT
// ==============================================================================

db = db.getSiblingDB('devforge');

// Clean up existing collection
db.projects.drop();

// Seed workspace configurations
db.projects.insertMany([
  {
    name: "DevForge Ingress Gateway",
    type: "infrastructure",
    status: "active",
    details: {
      port: 8080,
      protocol: "HTTPS"
    },
    updated_at: new Date()
  },
  {
    name: "Sample React Counter App",
    type: "frontend",
    status: "pending",
    details: {
      port: 5173,
      framework: "Vite"
    },
    updated_at: new Date()
  },
  {
    name: "AI LangChain Service API",
    type: "ai_ml",
    status: "active",
    details: {
      port: 8083,
      models: ["llama3", "mistral"]
    },
    updated_at: new Date()
  }
]);

print("MongoDB: Seeded projects collection successfully.");
