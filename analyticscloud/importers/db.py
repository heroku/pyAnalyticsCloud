from contextlib import contextmanager
import inspect
import json

from sqlalchemy import create_engine, MetaData
from sqlalchemy import types as sqltypes
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects import postgresql

from analyticscloud.importers.utils import new_field, metadata_factory, exclude_columns


SQL_TEXT_TYPES = (
    sqltypes.BOOLEAN, sqltypes.CHAR, sqltypes.BINARY,
    sqltypes._Binary, sqltypes.VARBINARY, sqltypes.VARCHAR,
    sqltypes.NCHAR, sqltypes.NVARCHAR, sqltypes.STRINGTYPE, sqltypes.TEXT,
    postgresql.UUID, postgresql.ENUM
)

SQL_NUMERIC_TYPES = (
    sqltypes.BIGINT, sqltypes.DECIMAL, sqltypes.FLOAT,
    sqltypes.INT, sqltypes.INTEGER, sqltypes.NUMERIC,
    sqltypes.REAL, sqltypes.SMALLINT
)

SQL_FLOAT_TYPES = (sqltypes.NUMERIC, sqltypes.DECIMAL, sqltypes.FLOAT,)

SQL_DATE_TYPES = (sqltypes.DATETIME, sqltypes.TIMESTAMP, sqltypes.DATE)

SQL_SUPPORTED_TYPES = SQL_NUMERIC_TYPES + SQL_DATE_TYPES


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
        meta = {
            'type': 'Numeric',
            'precision': 18,
            'scale': 0,
            'defaultValue': 0
        }
        if base_type in SQL_FLOAT_TYPES:
            if dbtype.precision is not None:
                meta['precision'] = min([dbtype.precision, 18])
            if dbtype.scale is not None:
                meta['scale'] = min([dbtype.scale, meta['precision'] - 1])
        return meta

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

    return {'type': 'Text'}


def metadata_dict(dburl, table, extended=None, excludes=None, schema='public'):
    if extended is None:
        extended = {}

    _, table = db_connect_table(dburl, table, schema=schema)

    metadata, fields = metadata_factory(table.name)
    metadata['objects'][0].update(extended)

    columns = exclude_columns(table.columns, excludes)

    for col in columns:
        fqname = '{}.{}'.format(table.name, col.name)
        field_meta = new_field(fqname, col.name)
        field_meta.update(metadata_for_dbtype(col.type))

        if 'fields' in extended and col.name in extended['fields']:
            field_meta.update(extended['fields'][col.name])
        fields.append(field_meta)

    return metadata


def data_generator(dburl, table, excludes=None, schema='public'):
    engine, table = db_connect_table(dburl, table, schema=schema)

    columns = exclude_columns(table.columns, excludes)

    yield [c.name for c in columns]
    with scoped_session(engine) as session:
        query = session.query(*columns).yield_per(1000)
        for row in query:
            yield row
