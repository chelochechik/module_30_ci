from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite+aiosqlite:///./recipe_book.db"

engine = create_async_engine(DATABASE_URL, future=True, echo=True)

async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

Base = declarative_base()
