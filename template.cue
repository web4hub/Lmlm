package web4

// ===============================
// Aura Ecosystem Project Template
// ===============================

project: {
  name:        string | *"Web4 Application"
  id:          string | *"web4app"
  version:     string | *"1.0.0"
  description: string | *"Web4 + AI + Blockchain application"

  author: {
    name:  string | *"Seriki Yakub (KUBU LEE)"
    org:   string | *"Aura Ecosystem"
    email?: string
  }

  repository: {
    provider: *"github" | "gitlab" | "bitbucket"
    owner:    string
    repo:     string
    branch:   *"main" | string
  }

  license: *"MIT" | "Apache-2.0" | "GPL-3.0"

  homepage?: string
}

// ===============================
// Frontend
// ===============================

frontend: {
  framework: *"vue3" | "react" | "svelte" | "solid"
  bundler:   *"vite" | "webpack"

  router:    bool | *true
  typescript: bool | *true

  styling: {
    css:         bool | *true
    tailwind:    bool | *true
    glassmorphism: bool | *true
    darkMode:    bool | *true
  }

  assets: {
    logo: *"/assets/logo.png" | string
    icons: [...string]
  }
}

// ===============================
// Backend
// ===============================

backend: {
  runtime: *"bun" | "node" | "deno"
  api:     *"express" | "elysia" | "fastify"

  port: int | *3000

  cors: bool | *true

  database: {
    provider: *"postgres" | "sqlite" | "mongodb"
    url: string
  }
}

// ===============================
// AI Services
// ===============================

ai: {
  enabled: bool | *true

  provider: *"LMLM" | "GPT-5-mini" | "KIBS" | "Local"

  models: [...{
    name: string
    size: string
    local: bool
  }]

  memory: {
    enabled: bool | *true
    vectorDB: *"sqlite" | "postgres" | "qdrant"
  }
}

// ===============================
// Blockchain
// ===============================

blockchain: {
  enabled: bool | *true

  network: *"Fadaka" | "Ethereum" | "Solana"

  wallet: {
    enabled: bool | *true
    login: *"Web4ID" | "WalletConnect"
  }
}

// ===============================
// Environment Variables
// ===============================

env: {
  APP_NAME: project.name
  PORT: backend.port

  DATABASE_URL: backend.database.url

  AI_PROVIDER: ai.provider

  CHAIN: blockchain.network
}

// ===============================
// Validation Rules
// ===============================

if backend.runtime == "bun" {
  backend.api: "elysia"
}

if frontend.framework == "vue3" {
  frontend.router: true
}

if ai.enabled == false {
  ai.models: []
}
