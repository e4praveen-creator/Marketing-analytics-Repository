# Marketing Analyst AI Cockpit (MVP)

Full-stack MVP implementing a deterministic marketing cockpit with a tool-first chat analyst.

## Stack
- Frontend: Next.js (TypeScript)
- Backend: FastAPI + SQLAlchemy
- Infra: Docker Compose with Postgres + Redis

## Run
```bash
docker compose up --build
```

Open:
- UI: http://localhost:3000/cockpit
- API docs: http://localhost:8000/docs

## Implemented pages
- `/cockpit`
- `/campaign/[id]`
- `/anomalies`
- `/chat`
- `/admin/metrics`
- `/audit`

## Implemented API
- Auth: `/auth/login`, `/auth/me`
- Metrics: `/metrics/query`, `/metrics/definitions`
- Campaigns: `/campaigns`, `/campaigns/{id}`, pause/resume
- Actions: `/actions/propose`, `/actions/execute`
- Anomalies: list/detail/run/ack/resolve
- Chat: `/chat/message` (structured response)
- Audit: `/audit/actions`

## Notes
- Seed data is auto-created at backend startup.
- Anomaly detection uses rolling median + MAD on CTR.
