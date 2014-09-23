import os
from flask import Flask, send_from_directory, render_template


PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
STATIC_FILES_DIR = os.path.join(PROJECT_ROOT, 'assets', 'public')


app = Flask(__name__, static_folder=None)
app.config.update(DEBUG=True, static_folder=None)


@app.route('/')
def index():
    return render_template('index.html')


# static files
@app.route('/static/<path:filename>')
def download_file(filename):
    print filename
    return send_from_directory(STATIC_FILES_DIR, filename)


if __name__=='__main__':
  app.run()