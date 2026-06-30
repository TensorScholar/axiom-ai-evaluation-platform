# AXIOM Global Constraints v0.5

## Product

AXIOM is a spec-driven, trace-aware, regression-focused evaluation platform for:

- LLM applications,
- RAG systems,
- tool-using agents,
- coding agents,
- loop-based AI workflows.

## Architecture

MVP architecture: modular monolith.

Allowed:

- FastAPI
- Pydantic
- pytest
- SQLAlchemy only when persistence spec requires it
- simple typed provider adapters
- local/SQL-backed persistence later
- CLI later when specified

Forbidden:

- Kafka
- Kubernetes
- Terraform
- Helm
- service mesh
- microservices
- event sourcing
- CQRS framework
- chaos engineering
- RL adversarial generation

## Engineering Style

Prefer:

- explicit domain models,
- deterministic tests,
- clear status transitions,
- boring code,
- typed interfaces,
- simple modules.

Avoid:

- clever abstractions,
- broad refactors,
- premature async complexity,
- distributed architecture,
- future feature scaffolding.
