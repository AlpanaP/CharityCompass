# Charity Compass

Foundational scaffolding for the Charity Compass platform. This repository mixes a Next.js frontend, FastAPI backend, shared tooling, and workflow automation exports.

## Structure

```
charity-compass/
  app/                 # Next.js app router entry point
  api/                 # Client wrappers and shared API helpers
  infra/
    env/.env.demo.example
  server/
    main.py            # FastAPI service entrypoint
    requirements.txt   # Python dependencies for the API service
    sql/schema.sql     # Database schema baseline
  tools/
    sync_env.py        # Environment variable sync utility
  n8n/                 # Automation workflows exported from n8n
```

## Next Steps

- Populate `app/` and `api/` with the actual Next.js application code.
- Flesh out the FastAPI service and align the schema with production requirements.
- Wire up `tools/sync_env.py` to your deployment provider APIs.
- Place n8n workflow exports inside `n8n/` as JSON files.
