# Hosted deployment

An optional way to run the real engine on a server (the GitHub Pages build runs it in the browser instead). Two containers:

- **web**: nginx with the built interface; proxies `/engine` (WebSocket) to the engine.
- **engine**: `python -m qlp_engine --public`, on an internal network with no internet access.

```bash
# from the repository root
SITE_ORIGIN=https://quantum.example.org docker compose -f deploy/docker-compose.yml up --build
```

Put a TLS terminator (Caddy, a cloud load balancer, or nginx with certificates) in front of port 8080. `SITE_ORIGIN` must be the exact origin learners use (scheme + host), because the engine only accepts WebSocket connections from it.

## Public mode (`--public`)

| Local mode (`npm run dev`) | Public mode |
|---|---|
| Listens on 127.0.0.1 | Listens on `--host` (0.0.0.0 in the container) |
| Session token required | No token; the `Origin` header must be one of `--allow-origin` (required) |
| Progress in SQLite on the engine | Progress in each learner's browser (localStorage), with export/import on the hub |
| One worker process | `--workers N` processes run code in parallel |
| No connection limit | `--max-connections` (engine) and 4 connections per IP (nginx) |

To try public mode without Docker: `npm --prefix app run e2e:hosted` runs the engine with `--public` behind the Vite dev proxy (`VITE_ENGINE_URL=/engine`, `VITE_ENGINE_PROXY=…`), the same path nginx uses.

## Security

Learner code is arbitrary Python. In public mode the **container is the security boundary**: the AST check in `engine/qlp_engine/guard.py` gives clear errors but can be bypassed.

Applied in `docker-compose.yml`:

- non-root user, read-only filesystem, `/tmp` as a small tmpfs;
- all Linux capabilities dropped, `no-new-privileges`, PID limit, memory and CPU limits;
- no internet access for the engine (internal network);
- per-job timeout and memory limit inside the engine (`RLIMIT_AS` on Linux); a runaway job kills only its worker.

Required before opening to the public (not done, and not testable on the development machine):

1. **Kernel isolation:** install gVisor on the host and enable `runtime: runsc` in the compose file. Without it, a container escape exposes the host.
2. **Per-session isolation:** today all learners share the engine container (each job runs in a worker process, but workers are reused). For untrusted public traffic, run one short-lived sandbox per session or per job (gVisor or Firecracker), created by a small orchestrator.
3. **Security review** of the sandbox and a **load test** sized for the expected number of learners.
4. **Abuse limits** per IP beyond connections (requests per minute), and monitoring.

For yourself or a small group you trust, the compose setup as it is (ideally with gVisor) is a reasonable start.
