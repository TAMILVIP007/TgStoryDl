from sqlalchemy import BigInteger, Column, Integer, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, unique=True, nullable=False)
    access_hash = Column(BigInteger, nullable=False)


class DownloadedFile(Base):
    __tablename__ = "downloaded_files"
    id = Column(Integer, primary_key=True, autoincrement=True)


class Database:
    def __init__(self, database_url):
        self.async_engine = create_async_engine(database_url, echo=True)
        self.async_session = sessionmaker(
            bind=self.async_engine, expire_on_commit=False, class_=AsyncSession
        )

    async def create_tables(self):
        async with self.async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def add_user(self, user_id, access_hash):
        async with self.async_session() as session:
            async with session.begin():
                user = await session.execute(select(User).filter_by(user_id=user_id))
                user = user.scalar_one_or_none()
                if user is None:
                    new_user = User(user_id=user_id, access_hash=access_hash)
                    session.add(new_user)
                    return True
                return False

    async def add_downloaded_file(self):
        async with self.async_session() as session:
            async with session.begin():
                session.add(DownloadedFile())
                await session.commit()

    async def get_status(self):
        async with self.async_session() as session:
            async with session.begin():
                total_users = await session.scalar(
                    select(func.count()).select_from(User)
                )
                downloaded_files_count = await session.scalar(
                    select(func.count()).select_from(DownloadedFile)
                )

                async with self.async_engine.connect() as conn:
                    result = await conn.scalar(
                        text(
                            "SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()"
                        )
                    )
                    db_size_bytes = result
                    db_size_kb = db_size_bytes / 1024
                    db_size_mb = db_size_kb / 1024

                return total_users, downloaded_files_count, db_size_mb, db_size_kb
