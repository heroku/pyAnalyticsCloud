from contextlib import contextmanager
import json

from sqlalchemy import create_engine, MetaData
from sqlalchemy.sql import sqltypes
from sqlalchemy.orm import sessionmaker

from .base import metadata_object


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
        fqname = self.table.name
        api_name = self.table.name.replace(' ', '')
        display_name = self.table.name
        schema = metadata_object(fqname, display_name, api_name, fields=[])
        for col in self.table.columns:
            fqname = '{}.{}'.format(self.table.name, col.name)
            api_name = col.name
            display_name = col.name
            schema['fields'].append(metadata_object(fqname, display_name, api_name,
                                    **self._type_kwargs(col.type)))
        return schema

    def _type_kwargs(self, dbtype):
        if str(dbtype) == 'INTEGER':
            return {
                'type': 'Numeric',
                'precision': 0,
                'scale': 0,
                'format': '0'
            }

        if str(dbtype).startswith('VARCHAR'):
            return {'type': 'String'}

        if str(dbtype) == 'TIMESTAMP WITHOUT TIME ZONE':
            return {
                'type': 'Date',
                'format': 'yyyy-mm-dd HH:MM:SS.mm'
            }

        raise TypeError('Unknown Type, {}'.format(dbtype))

    def __iter__(self):
        with scoped_session(bind=self.engine) as session:
            query = session.query(self.table)
            for row in query:
                yield row
