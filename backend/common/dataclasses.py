import dataclasses

from datetime import datetime

from fastapi import Response

from backend.common.enums import StatusType


@dataclasses.dataclass
class AccessToken:
    access_token: str
    access_token_expire_time: datetime
    session_uuid: str


@dataclasses.dataclass
class RefreshToken:
    refresh_token: str
    refresh_token_expire_time: datetime


@dataclasses.dataclass
class NewToken:
    new_access_token: str
    new_access_token_expire_time: datetime
    new_refresh_token: str
    new_refresh_token_expire_time: datetime
    session_uuid: str



@dataclasses.dataclass
class SnowflakeInfo:
    timestamp: int
    datetime: str
    datacenter_id: int
    worker_id: int
    sequence: int