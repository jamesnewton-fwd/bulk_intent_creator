from dataclasses import dataclass, field
from typing import Optional


@dataclass
class IntentCheck:
    """Represents a single Forward Networks intent check.

    Flat representation of the nested API body — to_api_payload() builds the
    full JSON structure. snapshot_id is NOT stored here; it is supplied at
    call time via the --snapshot-id CLI argument.
    """

    # --- required ---
    name: str
    check_type: str               # e.g. "Existential"
    from_location_type: str       # e.g. "HostFilter", "DeviceFilter", "NetworkFilter"
    from_location_value: str      # e.g. "10.10.10.10"
    to_location_type: str
    to_location_value: str

    # --- top-level optional ---
    note: Optional[str] = None
    enabled: bool = True
    priority: str = "NOT_SET"
    perf_monitoring_enabled: bool = False
    tags: list[str] = field(default_factory=list)

    # --- definition optional ---
    return_path: str = "ANY"
    mode: str = "PERMIT_ALL"
    flow_types: list[str] = field(default_factory=list)
    forwarding_types: list[str] = field(default_factory=list)
    noise_types: list[str] = field(default_factory=list)
    header_fields_with_defaults: list[str] = field(default_factory=list)

    # --- endpoint optional ---
    from_logical_network: Optional[str] = None
    to_logical_network: Optional[str] = None

    # --- packet header filters (creates a PacketFilter entry in headers[]) ---
    from_ipv4_dst: list[str] = field(default_factory=list)
    to_ipv4_dst: list[str] = field(default_factory=list)

    # --- bypass: comma-separated device names, each becomes a DeviceFilter ---
    bypass_devices: list[str] = field(default_factory=list)

    def to_api_payload(self) -> dict:
        from_ep: dict = {
            "location": {
                "type": self.from_location_type,
                "value": self.from_location_value,
            }
        }
        if self.from_ipv4_dst:
            from_ep["headers"] = [
                {"type": "PacketFilter", "values": {"ipv4_dst": self.from_ipv4_dst}}
            ]
        if self.from_logical_network:
            from_ep["logicalNetwork"] = self.from_logical_network

        to_ep: dict = {
            "location": {
                "type": self.to_location_type,
                "value": self.to_location_value,
            }
        }
        if self.to_ipv4_dst:
            to_ep["headers"] = [
                {"type": "PacketFilter", "values": {"ipv4_dst": self.to_ipv4_dst}}
            ]
        if self.to_logical_network:
            to_ep["logicalNetwork"] = self.to_logical_network

        filters: dict = {
            "from": from_ep,
            "to": to_ep,
            "mode": self.mode,
        }
        if self.flow_types:
            filters["flowTypes"] = self.flow_types
        if self.forwarding_types:
            filters["forwardingTypes"] = self.forwarding_types
        if self.bypass_devices:
            filters["bypass"] = [
                {"type": "DeviceFilter", "value": d} for d in self.bypass_devices
            ]

        definition: dict = {
            "checkType": self.check_type,
            "filters": filters,
            "returnPath": self.return_path,
        }
        if self.noise_types:
            definition["noiseTypes"] = self.noise_types
        if self.header_fields_with_defaults:
            definition["headerFieldsWithDefaults"] = self.header_fields_with_defaults

        payload: dict = {
            "definition": definition,
            "enabled": self.enabled,
            "name": self.name,
            "priority": self.priority,
            "perfMonitoringEnabled": self.perf_monitoring_enabled,
        }
        if self.note:
            payload["note"] = self.note
        if self.tags:
            payload["tags"] = self.tags

        return payload
