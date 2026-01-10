
from typing import Any, Literal
from pydantic import model_validator

from pydantic_settings import BaseSettings, SettingsConfigDict

from backend.core.path_conf import ENV_EXAMPLE_FILE_PATH, ENV_FILE_PATH


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH,
        env_file_encoding='utf-8',
        extra='ignore',
        case_sensitive=True,
    )

    # .env 当前环境
    ENVIRONMENT: Literal['dev', 'prod']

    DATABASE_TYPE: Literal['mysql', 'postgresql']
    DATABASE_HOST: str
    DATABASE_PORT: int
    DATABASE_USER: str
    DATABASE_PASSWORD: str

    @model_validator(mode='before')
    @classmethod
    def check_env(cls, values: Any) -> Any:
        """检查环境变量"""
        if values.get('ENVIRONMENT') == 'prod':
            # FastAPI
            values['FASTAPI_OPENAPI_URL'] = None
            values['FASTAPI_STATIC_FILES'] = False

            # task
            values['CELERY_BROKER'] = 'rabbitmq'

        return values

# @lru_cache
# def get_settings() -> Settings:
#     """获取全局配置单例"""
#     if not ENV_FILE_PATH.exists():
#         shutil.copy(ENV_EXAMPLE_FILE_PATH, ENV_FILE_PATH)
#     return Settings()

setting = Settings()
print(setting)