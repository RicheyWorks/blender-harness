# Blender team <-> Unreal team bus: we use the Unreal team's team link

**Superseded:** our earlier proposal (v1 envelope, /v1/* endpoints) is withdrawn. The bus is the Unreal team's team link
(ADR-053, Daedalus2/docs/TEAMLINK.md, `asset_pipeline.teamlink serve`) on **127.0.0.1:9890**, log bot-team\link\log.jsonl.
- Blender team name: `blender-team`. Unreal team name: `unreal-team`.
- We send: `note {text}`, `ping`, `asset.ready {asset}`.
- We receive: `pong`, `ack`, `asset.added`, `asset.shipping`, `asset.shipped`, `asset.rejected`, `asset.blocked`,
  `asset.waiting`, `note`.
- Endpoints: POST /send · GET /wait?me=blender-team&after=ID&timeout<=55 · POST /ack · POST /heartbeat · GET /pending
  · /presence · /log · /health.
- Our client is blender-harness `bharness/bus.py` (`python -m bharness.bus health|ping|note|ready <Asset>|wait`). It keeps
  a cursor in art\bus\blender-client.json and acks everything it reads. If the broker is down, outgoing messages queue
  and replay when it's back, and incoming falls back to feed.jsonl.

Load balancer: RicheyWorks/LoadBalancerPro (C:\Users\730ri\projects\LoadBalancerPro_RicheyWorks) is a Java 17 Spring
Boot reverse proxy. It isn't running on this PC right now; its demo profiles use :8080, with an API key required and
proxying off by default. If Richey wants the link behind it, that's one `/proxy/teamlink/**` route to 127.0.0.1:9890,
with a /health check and a long read timeout (above 60 s, so /wait long-polls survive). Clients then point
DAEDALUS_BUS (or art\BUS.json) at the proxy URL, with no code change.
