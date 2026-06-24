import argparse
import getpass
import json
import sys

from .client import ForwardNetworksClient
from .csv_parser import parse_csv
from .exceptions import BulkIntentCreatorError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="bulk-intent-creator",
        description="Bulk create Forward Networks intent checks from a CSV file.",
    )
    parser.add_argument(
        "--api-key",
        required=True,
        metavar="KEY",
        help="Forward Networks API key (used as Basic auth username)",
    )
    parser.add_argument(
        "--host",
        default="https://fwd.app",
        metavar="URL",
        help="Forward Networks instance base URL (default: https://fwd.app)",
    )
    parser.add_argument(
        "--snapshot-id",
        required=True,
        metavar="ID",
        help="Snapshot ID to create all checks against",
    )
    parser.add_argument(
        "--csv-file",
        required=True,
        metavar="FILE",
        help="Path to the CSV file containing intent check definitions",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the API payload for each check without sending any requests",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    try:
        checks = parse_csv(args.csv_file)
    except BulkIntentCreatorError as exc:
        print(f"Error reading CSV: {exc}", file=sys.stderr)
        sys.exit(1)
    except OSError as exc:
        print(f"Error opening file: {exc}", file=sys.stderr)
        sys.exit(1)

    if not checks:
        print("No checks found in CSV file.")
        return

    if args.dry_run:
        for check in checks:
            print(json.dumps(check.to_api_payload(), indent=2))
        return

    api_secret = getpass.getpass("API secret key: ")
    client = ForwardNetworksClient(host=args.host, api_key=args.api_key, api_secret=api_secret)
    succeeded = 0
    failed = 0

    for check in checks:
        try:
            client.add_check(check, snapshot_id=args.snapshot_id)
            print(f"[OK]    {check.name}")
            succeeded += 1
        except BulkIntentCreatorError as exc:
            print(f"[ERROR] {check.name}: {exc}", file=sys.stderr)
            failed += 1

    print(f"\n{succeeded} succeeded, {failed} failed")
    if failed:
        sys.exit(1)
