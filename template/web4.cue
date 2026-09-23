package web4

import "./template.cue"

config: project & {
  name: "Aura Dashboard"
  id: "aura-dashboard"

  repository: {
    owner: "auraecosystem"
    repo: "aura-dashboard"
  }
}

backend: {
  database: {
    url: "postgres://localhost/aura"
  }
}

ai: {
  models: [{
    name: "LMLM-7B"
    size: "7B"
    local: true
  }]
}
