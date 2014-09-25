from contextlib import contextmanager
import json

from sqlalchemy import create_engine, MetaData
from sqlalchemy.sql import sqltypes
from sqlalchemy.orm import sessionmaker

from hcinsights.importers.utils import new_field, metadata_factory


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


def db_connect_table(dburl, table):
    engine = create_engine(dburl)
    connection = engine.connect()
    dbmetadata = MetaData(bind=connection)
    dbmetadata.reflect(only=[table])
    table = dbmetadata.tables[table]

    return engine, table


def metadata_for_dbtype(dbtype):
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

    if str(dbtype) == 'TIMESTAMP WITH TIME ZONE':
        return {
            'type': 'Date',
            'format': 'yyyy-MM-dd HH:mm:ss'
        }

    if str(dbtype) == 'BOOLEAN':
        # XXX better to use numeric?
        return {'type': 'Text'}

    raise TypeError('Unknown Type, {}'.format(dbtype))


def metadata_dict(dburl, table, extended=None):
    if extended is None:
        extended = {}

    _, table = db_connect_table(dburl, table)

    metadata, fields = metadata_factory(table.name)
    metadata['objects'][0].update(extended)
    for col in table.columns:
        api_name = col.name
        display_name = col.name
        fqname = '{}.{}'.format(table.name, col.name)
        field_meta = new_field(fqname, col.name)
        field_meta.update(metadata_for_dbtype(col.type))

        if 'fields' in extended and col.name in extended['fields']:
            field_meta.update(extended['fields'][col.name])
        fields.append(field_meta)

    return metadata


def data_generator(dburl, table):
    engine, table = db_connect_table(dburl, table)

    yield [c.name for c in table.columns]
    with scoped_session(engine) as session:
        query = session.query(table)
        for row in query:
            yield row
