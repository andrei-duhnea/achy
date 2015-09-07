import os
import bottle
from bottle import Bottle, run, route, static_file, template, request, redirect

from parser import Pain8Doc
from achy import build_pain2
from helpers import timestamp_string

BUILD_DIR = 'build'
UPLOAD_DIR = 'uploads'

bottle.TEMPLATE_PATH.append('templates')

def save_upload(upload):
    upload_path = os.path.join(UPLOAD_DIR, upload.filename)
    with open(upload_path, 'w') as f:
            f.write(upload.file.read())
    return upload_path

def make_pain2(pain2_file, pain8_file, mappings_file, default_reason):
    pain8_data = Pain8Doc(pain8_file)
    if default_reason == '':
        default_reason = None
    pain2 = build_pain2(pain8_data, mappings_file, default_reason)
    pain2_path = os.path.join(BUILD_DIR, pain2_file)
    with open(pain2_path, 'w') as f:
        f.write(pain2)

    return pain2_path

@route('/')
def index():
    redirect('/upload')

@route('/upload', method='GET')
def upload_form():
    return template('upload')

@route('/upload', method='POST')
def do_upload():
    pain8_file = request.files.get('pain8-upload')
    pain8_name, pain8_ext = os.path.splitext(pain8_file.filename)
    print(pain8_name)
    if pain8_ext not in ('.xml','.XML'):
        return 'Pain.008 file extension not allowed ({}).'.format(pain8_ext)

    pain8_path = save_upload(pain8_file)

    mappings_path = None
    mappings_file = request.files.get('mappings-upload')
    if mappings_file:
        mappings_path = save_upload(mappings_file)

    default_reason = request.forms.get('default-reason')
    pain2_filename = 'pain.002_{}.xml'.format(timestamp_string())
    make_pain2(pain2_filename, pain8_path, mappings_path, default_reason)
    redirect('/download/{}'.format(pain2_filename))

@route('/download/<pain2_file>', method='GET')
def download(pain2_file):
    return template('download.html', pain2_file=pain2_file)

@route('/direct-download/<pain2_file>', method='GET')
def direct_download(pain2_file):
    return static_file(pain2_file, root=BUILD_DIR, download=pain2_file)

run(host='localhost', port=12345, debug=True, reloader=True)
