# Security Policy

## Reporting a Vulnerability

**Please do not open a public GitHub issue for security vulnerabilities.**

If you discover a security issue in this project, please disclose it responsibly:

1. Email the maintainer directly (check the GitHub profile of the repo owner)
2. Include a clear description of the vulnerability and steps to reproduce
3. Allow reasonable time (72 hours) for acknowledgement before public disclosure

## Supported Versions

Only the latest commit on the `main` branch is actively maintained.

## Credentials & Secrets

- **Never commit `.env`** — it is listed in `.gitignore`
- Use `.env.example` as the template for required environment variables
- For Cloud Run deployments, use **Vertex AI with a dedicated service account** instead of API keys
- API keys (Google AI Studio) are for local development only

## Cloud Run Deployment Security

This project is designed to deploy on Google Cloud Run with the following security posture:

- `--no-allow-unauthenticated` is set by default — the service requires GCP credentials to access
- The container runs as a non-root user (`appuser`)
- CORS origins must be explicitly set via `ALLOW_ORIGINS` env var in production
- Service account should follow the principle of least privilege:
  - `roles/aiplatform.user` — Vertex AI inference
  - `roles/logging.logWriter` — Cloud Logging
  - `roles/storage.objectAdmin` — GCS artifact bucket (if used)

## External Dependencies

This agent calls an external MCP server at `https://lenny-mcp.onrender.com/mcp`.
- No auth is required for this endpoint (it is public)
- User queries are sent to this server for transcript search — do not send PII
- The endpoint is hosted on Render's free tier and may have cold-start latency
