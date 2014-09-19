from contextlib import contextmanager
import json

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker


@contextmanager
def scoped_session(*args, **kwargs):
    """Provide a transactional scope around a series of operations."""
    session = sessionmaker(*args, **kwargs)()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


class DBImporter(object):
    def __init__(self, config, table):
        self.url = config['url']
        self.engine = create_engine(self.url)
        self.connection = self.engine.connect()
        self.metadata = MetaData(bind=self.connection)
        self.metadata.reflect(only=[table])
        self.table = self.metadata.tables[table]

    def metadata_schema(self):
        schema = {}
        for col in self.table.columns:
            schema[col.name] = str(col.type)
        return json.dumps(schema)

    def __iter__(self):
        with scoped_session(bind=self.engine) as session:
            query = session.query(self.table)
            for row in query:
                print row
                yield row

            session.rollback()
