from contextlib import contextmanager
import json

from sqlalchemy import create_engine, MetaData
from sqlalchemy.sql import sqltypes
from sqlalchemy.orm import sessionmaker

from .base import new_field


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
    def __init__(self, config):
        self.config = config
        self.engine = create_engine(config['url'])
        self.connection = self.engine.connect()

        table = self.config['table']
        metadata = MetaData(bind=self.connection)
        metadata.reflect(only=[table])
        self.table = metadata.tables[table]

    def object_metadata(self):

        obj_meta = {
            'fullyQualifiedName': self.table.name,
            'name': self.table.name,
            'label': self.table.name,
            'fields': []
        }

        metadata = self.config.get('metadata', {})
        obj_meta.update(metadata)

        for col in self.table.columns:
            api_name = col.name
            display_name = col.name
            fqname = '{}.{}'.format(self.table.name, col.name)
            field_meta = new_field(fqname, col.name)
            field_meta.update(self._type_kwargs(col.type))
            if 'fields' in metadata and col.name in metadata['fields']:
                field_meta.update(metadata['fields'][col.name])
            obj_meta['fields'].append(field_meta)

        return obj_meta

    def _type_kwargs(self, dbtype):
        if str(dbtype) in ('SMALLINT', 'INTEGER'):
            return {
                'type': 'Numeric',
                'precision': 19,
                'scale': 0,
                'defaultValue': 0
            }

        if str(dbtype).startswith('VARCHAR'):
            return {'type': 'Text'}

        if str(dbtype) in ('TIMESTAMP WITHOUT TIME ZONE', 'DATE'):
            return {
                'type': 'Date',
                'format': 'yyyy-MM-dd HH:mm:ss'
            }

        if str(dbtype) == 'BOOLEAN':
            # XXX better to use numeric?
            return {'type': 'Text'}

        raise TypeError('Unknown Type, {}'.format(dbtype))

    def __iter__(self):
        with scoped_session(bind=self.engine) as session:
            query = session.query(self.table)
            for row in query:
                yield row
