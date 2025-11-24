# DevOps Agent — Happy Path (excerpt)

- Destructive operations require `--execute`. Shell helpers enforce a best‑effort mutation guard.
- Telegram notifications are off by default (token‑in‑URL). Use Slack/ntfy/Webhook instead, or set `telegram.allow_url_token=true` if you accept the risk.

Scheduler one-shot (optional)
```python
from devops_agent.scheduler import run_scheduler

# Build or load your jobs iterable
jobs = []  # TODO: load your Job objects
results = run_scheduler(jobs)
print({k: v.ok for k, v in results.items()})
```

Notifications via environment (optional)
- `DEVOPS_NOTIFY_DESKTOP=1`
- `DEVOPS_NOTIFY_NTFY_URL=https://ntfy.sh/your_topic` (+ `DEVOPS_NOTIFY_NTFY_TOKEN=...`)
- `DEVOPS_NOTIFY_WEBHOOK_URL=https://example/hooks/abc` (+ `DEVOPS_NOTIFY_WEBHOOK_FORMAT=slack|generic`, headers via `DEVOPS_NOTIFY_WEBHOOK_HEADER_X-Api-Key=...`)
- `DEVOPS_NOTIFY_TELEGRAM_URL=https://api.telegram.org/bot<token>/sendMessage?...`

Tokens are redacted in error paths.

Metrics (optional)
- Set `DEVOPS_METRICS_DIR=/var/lib/node_exporter/textfile_collector` (or any directory) to emit a Prometheus-compatible `devops_agent.prom` on each scheduler tick.

Memory-First Shorthands (conversation)
- Use `memory-first: …` to force the agent to consult agent-memory (ArangoDB) before any external tools.
- `mf: …` is a synonym for `memory-first:`.
- `mf-only: …` consults memory only; no external tools. If memory is unreachable, the agent should respond with locally available cache and note the gap.
