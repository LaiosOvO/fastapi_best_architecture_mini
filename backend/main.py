import uvicorn
from rich.text import Text

from backend.utils.console import console
from backend.utils.timezone import timezone
from backend.core.registrar import register_app


_log_prefix = f'{timezone.to_str(timezone.now(), "%Y-%m-%d %H:%M:%S.%M0")} | {"INFO": <8} | - | '
console.print(Text(f'{_log_prefix}检测插件依赖...', style='bold cyan'))

app = register_app()


if __name__ == '__main__':
    uvicorn.run(
        app='backend.main:app',
        host='0.0.0.0',
        port=8000,
        reload=True,
    )
