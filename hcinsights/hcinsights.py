import os
import json
from flask import (Flask, request, send_from_directory, render_template,
    make_response)


PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
STATIC_FILES_DIR = os.path.join(PROJECT_ROOT, 'assets', 'public')


app = Flask(__name__, static_folder=None)
app.config.update(DEBUG=True, static_folder=None)


@app.route('/')
def index():
    return render_template('index.html')


# api
@app.route('/api/tables')
def tables():
    data = [
        {'name': 'tablename', 'fields': []},
    ]
    resp = make_json_response(data, status=200)
    return resp


@app.route('/api/uploads', methods=['GET', 'POST'])
def uploads():
    # handle get, return list of uploads and their status.
    # could also just be dict with tablename:status unless we wanted
    # to provide more meta, like failure messages
    if request.method == 'GET':
        data = [
            {'table': 'tablename', 'status': 'WAITING'},
            {'table': 'tablename', 'status': 'PROCESSING'},
            {'table': 'tablename', 'status': 'COMPLETE'},
            {'table': 'tablename', 'status': 'FAILED'}
        ]
        resp = make_json_response(data, status=200)
        return resp
    elif request.method == 'POST':
        data = request.json
        data = {'table': 'tablename', 'username': '', 'password': ''}
        # Start subprocess ... keep hash of them somewhere
        # for status updates per-table. Don't need response data, just 200 if good?
        resp = make_json_response({}, status=200)
        return resp


@app.route('/api/uploads/<table>', methods=['GET', 'DELETE'])
def uploads_detail():
    if request.method == 'GET':
        data = {
            'status': 'COMPLETE'
        }
        resp = make_json_response(data, status=200)
        return resp
    elif request.method == 'POST':
        # cancel/remove from in-memory queue?
        resp = make_json_response({}, status=200)
        return resp


# static files
@app.route('/static/<path:filename>')
def download_file(filename):
    return send_from_directory(STATIC_FILES_DIR, filename)


def make_json_response(data, *args, **kwargs):
    kwargs['content_type'] = 'application/json'
    resp = make_response(json.dumps(data), *args, **kwargs)
    return resp


if __name__=='__main__':
  app.run()