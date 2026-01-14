import dataclasses

from datetime import datetime

from fastapi import Response

from backend.common.enums import StatusType

@dataclasses.dataclass
class SnowflakeInfo:
    timestamp: int
    datetime: str
    datacenter_id: int
    worker_id: int
    sequence: int