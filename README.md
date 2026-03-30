# Product Decision Advisor

An AI agent that answers PM and founder product decisions — pricing, roadmap, growth, retention, hiring, and PMF — by searching Lenny's Podcast transcripts and synthesizing opinionated, evidence-grounded recommendations.

Built with [Google ADK](https://google.github.io/adk-docs/) and deployed on Cloud Run.

## Requirements

- [uv](https://docs.astral.sh/uv/getting-started/installation/) — Python package manager
- [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
- `make`

## Quick Start

```bash
cp .env.example .env   # fill in your GCP project
make install && make playground
```

## Commands

| Command | Description |
|---------|-------------|
| `make install` | Install dependencies |
| `make playground` | Local dev environment at http://localhost:8501 |
| `make test` | Run unit and integration tests |
| `make eval` | Run evaluation against eval cases |
| `make lint` | Code quality checks |
| `make deploy` | Deploy to Cloud Run |

## Deployment

```bash
gcloud config set project <your-project-id>
make deploy
```

## Credits

- Skill frameworks derived from [RefoundAI/lenny-skills](https://github.com/RefoundAI/lenny-skills) (MIT)
- Transcript search powered by [akshayvkt/lenny-mcp](https://github.com/akshayvkt/lenny-mcp) (MIT)
- Podcast transcripts are the property of [Lenny Rachitsky](https://www.lennysnewsletter.com), used with his public permission
