"""Example of using bulk_intent_creator as a library rather than a CLI tool."""

from bulk_intent_creator import ForwardNetworksClient, parse_csv

HOST = "https://your-instance.fwd.app"
API_KEY = "your-api-key"
API_SECRET = "your-api-secret"
SNAPSHOT_ID = "snap_abc123"
CSV_FILE = "sample_checks.csv"

checks = parse_csv(CSV_FILE)
print(f"Loaded {len(checks)} checks from {CSV_FILE}")

client = ForwardNetworksClient(host=HOST, api_key=API_KEY, api_secret=API_SECRET)

for check in checks:
    result = client.add_check(check, snapshot_id=SNAPSHOT_ID)
    print(f"Created: {check.name} -> {result}")
