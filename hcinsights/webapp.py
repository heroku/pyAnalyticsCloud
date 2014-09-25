import os
import json

from flask import Flask, request, send_from_directory, render_template
from flask import jsonify

from flask.ext.sqlalchemy import SQLAlchemy

from hcinsights.importers.db import metadata_dict, data_generator
from hcinsights.uploader import SFSoapConnection, InsightsUploader


PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
STATIC_FILES_DIR = os.path.join(PROJECT_ROOT, 'assets', 'public')


app = Flask('hcinsights', static_folder=None)

app.config.update(DEBUG=True, static_folder=None)

app.config.setdefault('SQLALCHEMY_DATABASE_URI', os.environ.get('DATABASE_URL'))
db = SQLAlchemy(app)

# a job is table: { jobid, table, status}
JOBS = {}


@app.route('/api/tables')
def api_tables():
    result = db.engine.execute("""SELECT table_schema as schema, table_name as name
        FROM information_schema.tables
        WHERE  table_schema NOT IN ('pg_catalog', 'information_schema')
            and table_type = 'BASE TABLE'
            and table_name NOT IN ('_trigger_log', 'c5_versions', '_trigger_last_id')
        """)
    tables = result.fetchall()[1:]

    data = [{'name': '{}.{}'.format(*table), 'fields': []} for table in tables]
    return jsonify(tables=data)


@app.route('/api/uploads', methods=['GET', 'POST'])
def uploads():
    # handle get, return list of uploads and their status.
    # could also just be dict with tablename:status unless we wanted
    # to provide more meta, like failure messages
    if request.method == 'GET':
        return jsonify(jobs=JOBS)

    if request.method == 'POST':
        args = request.json  # username, password, table
        table = args['table']

        dburl = app.config['SQLALCHEMY_DATABASE_URI']
        metadata = metadata_dict(dburl, table)
        data = data_generator(dburl, table)

        connection = SFSoapConnection(args['username'], args['password'])
        uploader = InsightsUploader(connection, metadata, data)
        uploader.upload(table)

        job = {'jobid': hash(uploader), 'table': table, status: 'inprogress'}
        JOBS[table] = job

        # XXX error handling on job setup
        return jsonify(status=job['status'])


@app.route('/api/uploads/<table>', methods=['GET'])
def uploads_detail(table):
    if request.method == 'GET':
        job = JOBS[table]

        return jsonify(status=job['status'])


# static files
@app.route('/static/<path:filename>')
def download_file(filename):
    return send_from_directory(STATIC_FILES_DIR, filename)


# need catch all for React, or have to mirror endpoints
@app.route('/')
@app.route('/<path:path>')
def index(*args, **kwargs):
    return render_template('index.html')


if __name__ == '__main__':
    app.run()
