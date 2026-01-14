from typing import Any, TypeVar

from msgspec import json
from starlette.responses import JSONResponse


class MsgSpecJSONResponse(JSONResponse):
    """
    使用高性能的 msgspec 库将数据序列化为 JSON 的响应类
    """

    def render(self, content: Any) -> bytes:
        return json.encode(content)


