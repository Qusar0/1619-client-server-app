from contextlib import asynccontextmanager, contextmanager
from functools import wraps
from fastapi import Depends
from src.config import get_async_db_url, get_sync_db_url
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from typing import Callable, AsyncGenerator, Optional, Generator


ASYNC_DATABASE_URL = get_async_db_url()
SYNC_DATABASE_URL = get_sync_db_url()

async_engine = create_async_engine(ASYNC_DATABASE_URL)
async_session_maker = async_sessionmaker(async_engine, expire_on_commit=False)

sync_engine = create_engine(SYNC_DATABASE_URL)
sync_session_maker = sessionmaker(bind=sync_engine, expire_on_commit=False)


class DatabaseSessionManager:
    def __init__(self, 
                 async_session_maker: async_sessionmaker[AsyncSession],
                 sync_session_maker: sessionmaker[Session]
    ):
        self.async_session_maker = async_session_maker
        self.sync_session_maker = sync_session_maker

    @asynccontextmanager
    async def create_async_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.async_session_maker() as session:
            try:
                yield session
            except Exception as e:
                raise
            finally:
                await session.close()

    @asynccontextmanager
    async def async_transaction(self, session: AsyncSession) -> AsyncGenerator[None, None]:
        try:
            yield
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise

    async def get_async_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.create_async_session() as session:
            yield session

    async def get_async_transaction_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.create_async_session() as session:
            async with self.async_transaction(session):
                yield session

    @contextmanager
    def create_sync_session(self) -> Generator[Session, None, None]:
        session = self.sync_session_maker()
        try:
            yield session
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    @contextmanager
    def sync_transaction(self, session: Session) -> Generator[None, None, None]:
        try:
            yield
            session.commit()
        except Exception:
            session.rollback()
            raise
    
    def get_sync_session(self) -> Generator[Session, None, None]:
        with self.create_sync_session() as session:
            yield session
        
    def get_sync_transaction_session(self) -> Generator[Session, None, None]:
        with self.create_sync_session() as session:
            with self.sync_transaction(session):
                yield session

    def connection(self, commit: bool = True, async_mode: bool = True):
        def decorator(method):
            @wraps(method)
            async def async_wrapper(*args, **kwargs):
                async with self.async_session_maker() as session:
                    try:
                        result = await method(*args, session=session, **kwargs)

                        if commit:
                            await session.commit()

                        return result
                    except Exception as e:
                        await session.rollback()
                        raise
                    finally:
                        await session.close()

            @wraps(method)
            def sync_wrapper(*args, **kwargs):
                with self.sync_session_maker() as session:
                    try:
                        result = method(*args, session=session, **kwargs)

                        if commit:
                            session.commit()

                        return result
                    except Exception:
                        session.rollback()
                        raise
                    finally:
                        session.close()

            return async_wrapper if async_mode else sync_wrapper

        return decorator

    @property
    def async_session_dependency(self) -> Callable:
        return Depends(self.get_async_session)

    @property
    def async_transaction_session_dependency(self) -> Callable:
        return Depends(self.get_async_transaction_session)
    
    @property
    def sync_session_dependency(self) -> Callable:
        return Depends(self.get_sync_session)
    
    @property
    def sync_transaction_session_dependency(self) -> Callable:
        return Depends(self.get_sync_transaction_session)


session_manager = DatabaseSessionManager(async_session_maker, sync_session_maker)

AsyncSessionDep = session_manager.async_session_dependency
AsyncTransactionSessionDep = session_manager.async_transaction_session_dependency
SyncSessionDep = session_manager.sync_session_dependency
SyncTransactionSessionDep = session_manager.sync_transaction_session_dependency
