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
    def __init__(self, dburl, config):
        self.config = config
        self.fields = self.config.pop('fields', {})


        table = config['table']
        self.engine = create_engine(dburl)
        self.connection = self.engine.connect()
        self.metadata = MetaData(bind=self.connection)
        self.metadata.reflect(only=[table])
        self.table = self.metadata.tables[table]

    def object_metadata(self):
        obj_meta = {
            'fullyQualifiedName': self.table.name,
            'name': self.table.name,
            'label': self.table.name,
            'fields': []
        }
        obj_meta.update(self.config)

        for col in self.table.columns:
            api_name = col.name
            display_name = col.name
            field_meta = {
                'fullyQualifiedName': '{}.{}'.format(self.table.name, col.name),
                'name': col.name,
                'label': col.name,
            }
            field_meta.update(self._type_kwargs(col.type))
            if col.name in self.fields:
                field_meta.update(self.fields[col.name])
            obj_meta['fields'].append(field_meta)

        return obj_meta

    def _type_kwargs(self, dbtype):
        if str(dbtype) in ('SMALLINT', 'INTEGER'):
            return {
                'type': 'Numeric',
                'precision': 0,
                'scale': 0,
                'format': '0'
            }

        if str(dbtype).startswith('VARCHAR'):
            return {'type': 'Text'}

        if str(dbtype) == 'TIMESTAMP WITHOUT TIME ZONE':
            return {
                'type': 'Date',
                'format': 'yyyy-MM-dd HH:mm:ss.SSSZ'
            }

        raise TypeError('Unknown Type, {}'.format(dbtype))

    def __iter__(self):
        with scoped_session(bind=self.engine) as session:
            query = session.query(self.table)
            for row in query:
                yield row
