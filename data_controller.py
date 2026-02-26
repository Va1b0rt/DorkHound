from sqlalchemy import create_engine, Column, Integer, String, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.sqlite import insert

Base = declarative_base()


class DorkEntry(Base):
    __tablename__ = 'dork_entries'

    id = Column(Integer, primary_key=True)
    domain = Column(String, unique=True, nullable=False)
    dork = Column(String, nullable=False)

    def __repr__(self):
        return f"<DorkEntry(id={self.id}, domain={self.domain}, dork={self.dork})>"

class ProcessedDork(Base):
    __tablename__ = 'processed_dorks'

    id = Column(Integer, primary_key=True)
    dork = Column(String, unique=True, nullable=False)

class DorkDatabase:
    def __init__(self, db_path='sqlite:///dorks.db'):
        self.engine = create_engine(db_path)

        @event.listens_for(self.engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.close()

        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def add_entry(self, domain: str, dork: str) -> bool:
        session = self.Session()
        try:
            stmt = insert(DorkEntry).values(domain=domain, dork=dork)
            stmt = stmt.on_conflict_do_nothing(index_elements=['domain'])
            result = session.execute(stmt)
            session.commit()
            return result.rowcount > 0
        except Exception:
            session.rollback()
            return False
        finally:
            session.close()

    def get_entry_by_domain(self, domain: str):
        session = self.Session()
        try:
            return session.query(DorkEntry).filter_by(domain=domain).first()
        finally:
            session.close()

    def get_entry_by_dork(self, dork: str):
        session = self.Session()
        try:
            return session.query(DorkEntry).filter_by(dork=dork).first()
        finally:
            session.close()

    def get_all_entries(self):
        session = self.Session()
        try:
            return session.query(DorkEntry).all()
        finally:
            session.close()

    def add_processed_dork(self, dork: str) -> bool:
        session = self.Session()
        try:
            stmt = insert(ProcessedDork).values(dork=dork)
            stmt = stmt.on_conflict_do_nothing(index_elements=['dork'])
            session.execute(stmt)
            session.commit()
            return True
        except Exception:
            session.rollback()
            return False
        finally:
            session.close()

    def is_dork_processed(self, dork: str) -> bool:
        session = self.Session()
        try:
            return session.query(ProcessedDork.id).filter_by(dork=dork).first() is not None
        finally:
            session.close()