# bulk-intent-creator

Bulk create [Forward Networks](https://www.forwardnetworks.com/) intent checks from a CSV file.

## Installation

```bash
pip install .
```

For development (includes `pytest`):

```bash
pip install ".[dev]"
```

Requires Python 3.10+.

## Quick start

```bash
bulk-intent-creator \
  --api-key <YOUR_API_KEY> \
  --snapshot-id <SNAPSHOT_ID> \
  --csv-file checks.csv
```

You will be prompted for your API secret key at runtime. The tool uses HTTP Basic auth with `api-key` as the username and the secret as the password.

## CLI reference

| Flag | Required | Default | Description |
|---|---|---|---|
| `--api-key KEY` | Yes | — | Forward Networks API key (Basic auth username) |
| `--snapshot-id ID` | Yes | — | Snapshot ID to create all checks against |
| `--csv-file FILE` | Yes | — | Path to the CSV file |
| `--host URL` | No | `https://fwd.app` | Base URL of your Forward Networks instance |
| `--dry-run` | No | off | Print the API payload for each check without sending any requests |

### Dry run

Use `--dry-run` to preview the JSON payload that would be sent for each check without making any API calls (no API key prompt):

```bash
bulk-intent-creator --api-key dummy --snapshot-id dummy --csv-file checks.csv --dry-run
```

## CSV format

The CSV must have a header row. Column names must match exactly (case-sensitive).

### Required columns

| Column | Description |
|---|---|
| `name` | Display name for the intent check |
| `check_type` | e.g. `Existential` |
| `from_location_type` | e.g. `HostFilter`, `DeviceFilter`, `NetworkFilter` |
| `from_location_value` | e.g. `10.0.0.10` or `10.0.0.0/24` |
| `to_location_type` | Same type options as `from_location_type` |
| `to_location_value` | Destination location value |

### Optional columns

| Column | Default | Description |
|---|---|---|
| `note` | — | Free-text note attached to the check |
| `enabled` | `true` | `true`/`false` (also accepts `yes`/`no`/`1`/`0`) |
| `priority` | `NOT_SET` | e.g. `HIGH`, `MEDIUM`, `LOW`, `NOT_SET` |
| `perf_monitoring_enabled` | `false` | Enable performance monitoring |
| `tags` | — | Comma-separated list of tags |
| `return_path` | `ANY` | e.g. `ANY`, `SAME`, `SYMMETRIC` |
| `mode` | `PERMIT_ALL` | e.g. `PERMIT_ALL`, `DENY_ALL` |
| `flow_types` | — | Comma-separated list, e.g. `VALID,DELIVERED` |
| `forwarding_types` | — | Comma-separated list, e.g. `L3` |
| `noise_types` | — | Comma-separated list |
| `header_fields_with_defaults` | — | Comma-separated list |
| `from_logical_network` | — | Logical network for the source endpoint |
| `to_logical_network` | — | Logical network for the destination endpoint |
| `from_ipv4_dst` | — | Comma-separated IPv4 destination filter(s) for source |
| `to_ipv4_dst` | — | Comma-separated IPv4 destination filter(s) for destination |
| `bypass_devices` | — | Comma-separated device names to bypass |

### Example CSV

```csv
name,check_type,from_location_type,from_location_value,to_location_type,to_location_value,mode,flow_types,forwarding_types,from_ipv4_dst,to_ipv4_dst,bypass_devices,tags,note,priority,enabled,perf_monitoring_enabled,return_path
Web to app reachability,Existential,HostFilter,10.0.0.10,HostFilter,10.1.0.20,PERMIT_ALL,VALID,L3,,,,web-checks,Verify web tier can reach app server,NOT_SET,true,false,ANY
DNS reachability,Existential,NetworkFilter,10.0.0.0/24,HostFilter,10.2.0.53,PERMIT_ALL,VALID,,10.2.0.53,,,dns-checks,All hosts can reach internal DNS,NOT_SET,true,false,ANY
Firewall bypass check,Existential,HostFilter,10.3.0.5,HostFilter,10.1.0.20,PERMIT_ALL,VALID,L3,,,nyc-dc01-fw01,security,Check path bypassing edge firewall,HIGH,true,false,ANY
```

A full example file is at [examples/sample_checks.csv](examples/sample_checks.csv).

## Python API

You can also use the package as a library:

```python
from bulk_intent_creator import ForwardNetworksClient, parse_csv

checks = parse_csv("checks.csv")

client = ForwardNetworksClient(
    host="https://your-instance.fwd.app",
    api_key="your-api-key",
    api_secret="your-api-secret",
)

for check in checks:
    result = client.add_check(check, snapshot_id="snap_abc123")
    print(f"Created: {check.name}")
```

See [examples/bulk_create_example.py](examples/bulk_create_example.py) for a complete script.

## Running tests

```bash
pytest
```

## License

See [LICENSE](LICENSE).
