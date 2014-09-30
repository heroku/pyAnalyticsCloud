from contextlib import contextmanager
import inspect
import json

from sqlalchemy import create_engine, MetaData
from sqlalchemy import types as sqltypes
from sqlalchemy.orm import sessionmaker

from analyticscloud.importers.utils import new_field, metadata_factory


SQL_TEXT_TYPES = (
    sqltypes.BOOLEAN, sqltypes.CHAR, sqltypes.BINARY,
    sqltypes._Binary, sqltypes.VARBINARY, sqltypes.VARCHAR,
    sqltypes.NCHAR, sqltypes.NVARCHAR, sqltypes.STRINGTYPE, sqltypes.TEXT
)

SQL_NUMERIC_TYPES = (
    sqltypes.BIGINT, sqltypes.DECIMAL, sqltypes.FLOAT,
    sqltypes.INT, sqltypes.INTEGER, sqltypes.NUMERIC, sqltypes.Numeric,
    sqltypes.REAL, sqltypes.SMALLINT
)

SQL_DATE_TYPES = (sqltypes.DATETIME, sqltypes.TIMESTAMP, sqltypes.DATE)

SQL_SUPPORTED_TYPES = SQL_TEXT_TYPES + SQL_NUMERIC_TYPES + SQL_DATE_TYPES


def get_base_sqlclass(cls):
    for c in inspect.getmro(cls):
        if c in SQL_SUPPORTED_TYPES:
            return c
    return None


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


def db_connect_table(dburl, table, schema='public'):
    engine = create_engine(dburl)
    connection = engine.connect()
    dbmetadata = MetaData(bind=connection, schema=schema)
    dbmetadata.reflect(only=[table])
    table = dbmetadata.tables['{}.{}'.format(schema, table)]

    return engine, table


def metadata_for_dbtype(dbtype):
    base_type = get_base_sqlclass(dbtype.__class__)

    if base_type in SQL_NUMERIC_TYPES:
        return {
            'type': 'Numeric',
            'precision': 19,
            'scale': 0,
            'defaultValue': 0
        }

    if base_type in SQL_TEXT_TYPES:
        return {'type': 'Text'}

    if base_type in SQL_DATE_TYPES:
        # Treat timezones differently?
        if str(dbtype) == 'TIMESTAMP WITH TIME ZONE':
            return {
                'type': 'Date',
                'format': 'yyyy-MM-dd HH:mm:ss'
            }
        return {
            'type': 'Date',
            'format': 'yyyy-MM-dd HH:mm:ss'
        }

    raise TypeError('Unknown Type, {}'.format(dbtype))


def metadata_dict(dburl, table, extended=None, schema='public'):
    if extended is None:
        extended = {}

    _, table = db_connect_table(dburl, table, schema=schema)

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


def data_generator(dburl, table, schema='public'):
    engine, table = db_connect_table(dburl, table, schema=schema)

    yield [c.name for c in table.columns]
    with scoped_session(engine) as session:
        query = session.query(table)
        for row in query:
            yield row
