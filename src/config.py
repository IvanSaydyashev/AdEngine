import enum
import os
from dotenv import load_dotenv

from pydantic_settings import BaseSettings
from typing import ClassVar

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

import redis.asyncio as redis

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))


#=====================================================================================

class Settings(BaseSettings):
    username: ClassVar[str] = os.getenv("POSTGRES_USERNAME", "postgres")
    password: ClassVar[str] = os.getenv("POSTGRES_PASSWORD", "admin")
    host: ClassVar[str] = os.getenv("POSTGRES_HOST", "localhost")
    port: ClassVar[str] = os.getenv("POSTGRES_PORT", "5432")
    dbname: ClassVar[str] = os.getenv("POSTGRES_DATABASE", "postgres")

    redis_host: ClassVar[str] = os.getenv("REDIS_HOST", "localhost")
    redis_port: ClassVar[int] = os.getenv("REDIS_PORT", "6379")

    LLM_API_KEY: ClassVar[str] = os.getenv("LLM_API_KEY", "Undefined")

    API_URL: ClassVar[str] = os.getenv("API_URL", "http://localhost:8000")

    SERVER_HOST: ClassVar[str] = os.getenv("SERVER_HOST", "localhost")
    SERVER_PORT: ClassVar[str] = os.getenv("SERVER_PORT", "8000")

    @property
    def DATABASE_URL(self) -> str:
        return f'postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.dbname}'

    @property
    def REDIS_URL(self) -> str:
        return f'redis://{self.redis_host}:{self.redis_port}'


settings = Settings()


# =====================================================================================

class Gender(str, enum.Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    ALL = "ALL"


#=====================================================================================


Base = declarative_base()

engine = create_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


async def init_db():
    Base.metadata.drop_all(bind=engine)
    redis_db = redis.Redis.from_url(settings.REDIS_URL)  # pragma: no cover
    await redis_db.set("current_date", 0)  # pragma: no cover
    Base.metadata.create_all(bind=engine)  #pragma: no cover


def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def reset_db():
    Base.metadata.drop_all(bind=engine)  # pragma: no cover
    Base.metadata.create_all(bind=engine)  # pragma: no cover


#=====================================================================================

async def get_redis():
    r = redis.Redis.from_url(settings.REDIS_URL)
    try:
        yield r
    finally:
        await r.aclose()


# =====================================================================================

class Gender(str, enum.Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    ALL = "ALL"

#=====================================================================================
