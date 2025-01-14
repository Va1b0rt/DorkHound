from typing import Type

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

Base = declarative_base()


class DorkEntry(Base):
    __tablename__ = 'dork_entries'

    id = Column(Integer, primary_key=True)
    domain = Column(String, unique=True, nullable=False)
    dork = Column(String, nullable=False)

    def __repr__(self):
        return f"<DorkEntry({self.id=}, {self.domain=}, {self.dork=})>"


class DorkDatabase:
    def __init__(self, db_path='sqlite:///dorks.db'):
        self.engine = create_engine(db_path)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def session_connector(self, func):
        def wrapper(*args, **kwargs):
            session = self.Session()
            try:
                result = func(session, *args, **kwargs)
            finally:
                session.close()
            return result

        return wrapper

    def add_entry(self,domain: str, dork: str) -> bool:
        """
        Добавляет новую запись в базу данных.
        Возвращает True в случае успеха, False если домен уже существует.
        """
        session = self.Session()
        try:
            entry = DorkEntry(domain=domain, dork=dork)
            session.add(entry)
            session.commit()
            return True
        except IntegrityError:
            session.rollback()
            return False
        finally:
            session.close()

    def get_entry_by_domain(self, domain: str) -> Type[DorkEntry] | None:
        """Получает запись по домену"""
        session = self.Session()
        try:
            return session.query(DorkEntry).filter_by(domain=domain).first()
        finally:
            session.close()

    def get_all_entries(self) -> list[Type[DorkEntry]]:
        """Получает все записи"""
        session = self.Session()
        try:
            return session.query(DorkEntry).all()
        finally:
            session.close()

    def update_entry(self, domain: str, new_dork: str) -> bool:
        """
        Обновляет dork для указанного домена.
        Возвращает True если запись найдена и обновлена, иначе False.
        """
        session = self.Session()
        try:
            entry = session.query(DorkEntry).filter_by(domain=domain).first()
            if entry:
                entry.dork = new_dork
                session.commit()
                return True
            return False
        finally:
            session.close()

    def delete_entry(self, domain: str) -> bool:
        """
        Удаляет запись по домену.
        Возвращает True если запись найдена и удалена, иначе False.
        """
        session = self.Session()
        try:
            entry = session.query(DorkEntry).filter_by(domain=domain).first()
            if entry:
                session.delete(entry)
                session.commit()
                return True
            return False
        finally:
            session.close()