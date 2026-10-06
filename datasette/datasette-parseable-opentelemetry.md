# Using Parseable with Datasette for OpenTelemetry traces

[Parseable](https://www.parseable.com) is a brand new observability tool, compatible with [OpenTelemetry](https://opentelemetry.io), for storing and querying observability data.

[Datasette 1.0a41](https://docs.datasette.io/en/latest/changelog.html#a41-2026-09-24) added support for OpenTelemetry tracing, contributed by [Alex Garcia](https://alexgarcia.xyz).

Here's how I ran the two together, giving me neat local visualizations of traces of Datasette responses.

## Installing Parseable

I used the open source release of Parseable from their GitHub releases - I tried [v3.2.4](https://github.com/parseablehq/parseable/releases/tag/v3.2.4). They have a macOS Apple Silicon release (a 171MB download) which I downloaded and ran like so:
```bash
curl -fL https://github.com/parseablehq/parseable/releases/download/v3.2.4/Parseable_OSS_aarch64-apple-darwin -o parseable
chmod +x parseable
./parseable local-store
```
Running `./parseable local-store` starts Parseable with all of the default settings, and stores data in `./data` and `./staging` directories. It uses ports 8000, 8001, and 8002.

Then visit http://localhost:8000/ and sign in with the default `admin/admin` username and password.

## Running Datasette

I fetched a test database for Datasette to use:
```bash
wget https://latest.datasette.io/fixtures.db
```
Then I started Datasette like this:
```
OTEL_SERVICE_NAME=datasette-local \
OTEL_EXPORTER_OTLP_ENDPOINT=http://127.0.0.1:8000 \
OTEL_EXPORTER_OTLP_TRACES_HEADERS='Authorization=Basic%20YWRtaW46YWRtaW4%3D,X-P-Stream=datasette_traces' \
OTEL_TRACES_EXPORTER=otlp_json_http \
OTEL_METRICS_EXPORTER=none \
OTEL_LOGS_EXPORTER=none \
uvx --from 'opentelemetry-instrumentation==0.66b1' \
  --with 'opentelemetry-distro==0.66b1' \
  --with 'datasette==1.0a41' \
  --with 'opentelemetry-exporter-otlp-json-http==0.66b1' \
  opentelemetry-instrument datasette fixtures.db -p 8004
```
Note that we are *not* starting `datasette` directly - we are instead starting `opentelemetry-instrument datasette ...` to properly initialize the tracing.

## Viewing a trace

Load up http://localhost:8004/ and click around a bit, then wait a few seconds for the traces to be sent to Parseable. Then navigate to "traces" in the Parseable web interface and you should be able to find things like this:

![Screenshot of a trace detail view in an observability web app, with a span waterfall overlaid on a dimmed navigation sidebar and filter column. Dimmed sidebar: breadcrumb "Community > Traces > datas" (cut off), search box "Search... ⌘K", nav items "Home", "Ingest telemetry", section "ANALYZE": "Keystone", "Dashboards", "SQL Editor", section "OBSERVE": "Logs", "Metrics", "Traces" (selected), "APM", "Agents", section "MONITOR": "Alerts", "Errors", section "DATA": "Datasets", and at the bottom "Settings", "Book a call", "Support". Dimmed filter column, cut off at the right edge: "Search fi", "Core", "Log format", "User agent", "Source IPs", "Error", "Service", "service.ins", "service.na", "datasett" (checked), "Span", "Database", "HTTP", "http.reque", "NULL" (unchecked), "GET" (checked), "http.respo", "http.route", "Server", "server.add", "Telemetry", "URL", "All fields". Trace panel header: "Trace detail > 6f819a2170bcd1e91c6ea3ae236ec60b" with a copy icon, a "Related logs" button and a close X. Summary: "Start time 6:56 PM, Oct 6, 2026 UTC", "Duration 40.9 ms", "Spans 247". A minimap with axis "0ns 10.2ms 20.5ms 30.7ms 40.9ms" shows many short span bars cascading diagonally from top left toward the lower middle, with a few longer bars. Below is a span table with a "Span name" header, a "Search spans..." box, collapse and expand buttons, and a timeline axis "0ns 10.2ms 20.5ms 30.7ms 40.9ms". Rows (name, service, duration): root span with collapse toggle "123", "GET /..." "datasette..." 40.9ms spanning the full timeline; then alternating rows where each "db.query" has a collapse toggle "1": db.query datasette-local 679µs, db.query.execute datasette-local 278µs, db.query datasette-local 341µs, db.query.execute datasette-local 55µs, db.query datasette-local 357µs, db.query.execute datasette-local 197µs, db.query datasette-local 330µs, db.query.execute datasette-local 73µs, db.query datasette-local 2.26ms, db.query.execute datasette-local 2.02ms, db.query datasette-local 232µs, db.query.execute datasette-local 64µs, db.query datasette-local 207µs, db.query.execute datasette-local 71µs, db.query datasette-local 6.11ms. The child span bars start progressively later across the early part of the timeline.](https://raw.githubusercontent.com/simonw/til/refs/heads/main/datasette/datasette-parsable.webp)

Each request now has a trace which shows the details of every subsequent SQL query. Consult [the Datasette OpenTelemetry docs](https://docs.datasette.io/en/latest/internals.html#internals-telemetry) for more details.
## Alternative ports

To run Parseable on ports other than 8000, 8001, and 8002:

```bash
P_ADDR=127.0.0.1:18000 ./parseable local-store \
  --grpc-port 18001 \
  --flight-port 18002
```

You'll need to also update Datasette's environment variable to point at the new port:
```bash
OTEL_EXPORTER_OTLP_ENDPOINT=http://127.0.0.1:18000
```
