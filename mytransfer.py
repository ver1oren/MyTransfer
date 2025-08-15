###TODO###
# Load files into temp dir
# zip files
# add multi file upload
# add drag and drop
# persistent lookup table (pickling?)
# modify lookup to work with zip files
# zipfile lookup table
# modify downloaded filename

# optional:
# input for zip file name on download
#   - implement zip file name lookup table


import os
import xxhash
import random, string
from flask import Flask, flash, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = os.getcwd()
#UPLOAD_FOLDER = '/var/mytransfer'
#ALLOWED_EXTENSIONS = {}

checksums     = {}
download_urls = {}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def hash_file_xxh64(filepath, chunk_size=4096):
    """
    Calculates the XXH64 hash of a file.

    Args:
        filepath (str): The path to the file.
        chunk_size (int): The size of chunks to read from the file.

    Returns:
        str: The hexadecimal representation of the XXH64 hash.
    """
    hasher = xxhash.xxh64()
    with open(filepath, 'rb') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()

def gen_url() -> str:
  x = ''
  for i in range(50):
      x = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
      if x not in download_urls:
          return x

  return x

# We're not going to use this at first
def allowed_file(filename):
    return True
    #return '.' in filename and \
    #       filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/',methods=['GET','POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            full_path = os.path.join(UPLOAD_FOLDER,filename)
            file.save(full_path)
            h = hash_file_xxh64(full_path)

            if h in checksums and filename == checksums[h][0]:
                link = checksums[h][1]
            else:
                link = gen_url()
                checksums[h] = (filename, link)
                download_urls[link] = filename

            url = f"{request.url}{link}"
            return f'''
            <!doctype html>
            <title>File link</title>
            <a href="{url}">{url}</a>
            '''
            #return redirect(url_for('download_file', name=filename))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''

@app.route('/<h>')
def download_file(h):
    if h in download_urls:
        return send_from_directory(UPLOAD_FOLDER,download_urls[h])
    return "NAH DUDE"

if __name__ == "__main__":

    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.debug = True
    app.run()
