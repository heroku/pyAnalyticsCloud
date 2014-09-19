from contextlib import contextmanager

from sqlalchemy import create_engine, MetaData, sessionmaker


@contextmanager
def scoped_session(*args, **kwargs):
    """Provide a transactional scope around a series of operations."""
    session = sessionmaker(*args, **kwargs)
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


class DBImporter(object):
    def __init__(self, url, table):
        self.url = url

        self.engine = create_engine(options.url)
        self.connection = sefl.engine.connect()
        self.metadata = MetaData(bind=self.connection)
        self.metadata.reflect(only=[table])
        self.table = self.metadata.tables[table]

    def __iter__(self):
        with scoped_session(bind=engine) as session
            query = session.query(self.table)
            for row in query:
                print row
                yield row

            session.rollback()
