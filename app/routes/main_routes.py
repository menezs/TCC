from flask import render_template, request, redirect
from flask_login import login_required,current_user
from werkzeug.utils import secure_filename
from ..database.db_mongo import Mongo
from app import app
import os

ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/upload", methods=['POST'])
@login_required
def upload():
    if request.method == 'GET':
        return render_template("index.html")
    
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'Nenhum arquivo enviado'

        file = request.files['file']

        if file.filename == '':
            return 'Nome do arquivo vazio'

        if 'filename' not in request.form:
            return 'Nome do arquivo não fornecido'

        filename = request.form['filename']

        if not allowed_file(file.filename):
            return 'Extensão de arquivo não permitida. Apenas arquivos .csv são permitidos.'

        new_filename = secure_filename(filename + '.csv')
        
        file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'], new_filename))

        collectionUpload = Mongo('uploads').collection
        collectionUpload.insert_one({'userID': current_user.id, 'fileName': filename+'.csv'})

        return redirect('/')

@app.route('/')
@login_required
def home():

    fileNames = []

    collectionUpload = Mongo('uploads').collection
    dataUserDB = collectionUpload.find({'userID': current_user.id})

    if dataUserDB:
        for index, item in enumerate(dataUserDB):
            item.update({"index": index+1})
            fileNames.append(item)

    return render_template('index.html', fileNames=fileNames)

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')