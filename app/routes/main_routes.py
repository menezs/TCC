from flask import render_template, request, redirect, jsonify
from flask_login import login_required,current_user
from werkzeug.utils import secure_filename
from app.models.analyzer import Analyzer
from ..database.db_mongo import Mongo
from bson.objectid import ObjectId
from app.models.plot import Plot
from app import app
import os
import matplotlib
matplotlib.use('Agg')  

ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/ranking-apriori", methods=['GET'])
@login_required
def rankingApriori():

    idParam = request.args.get('id')
    country = request.args.get('country')
    collection = Mongo('uploads').collection

    fileName = collection.find_one({"_id": ObjectId(idParam)})

    filePath = os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'], fileName['fileName'])

    if os.path.exists(filePath):

        if country == 'Null':
            country = 'France'

        plot = Plot(filePath)   

        years, plot_data1, listRankItens1, plot_data2, listRankItens2 = plot.generate_plot(country)

        analyzer = Analyzer(filePath, idParam)

        countries = analyzer.getCountries(country)

        analyzerResultsFirstYear = analyzer.firstRanking(listRankItens1, country, years[0])
        analyzerResultsSecondYear = analyzer.firstRanking(listRankItens2, country, years[1])

        response = jsonify({
            "success": True,
            "data": {
            "plot1": plot_data1,
            "ranking1": analyzerResultsFirstYear,
            "plot2": plot_data2,
            "ranking2": analyzerResultsSecondYear,
            "countries": countries}
        }), 200

    else:
        print("Arquivo Não encontrado")

        response = jsonify({"success": False}), 200

    return response

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

        uploadPath = os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'])
        if not os.path.exists(uploadPath):
            os.makedirs(uploadPath)
        
        file.save(os.path.join(uploadPath, new_filename))

        collectionUpload = Mongo('uploads').collection
        collectionUpload.insert_one({'userID': current_user.id, 'fileName': filename+'.csv'})

        return redirect('/')

@app.route('/delete', methods=['POST'])
@login_required
def delete():
    if request.method == 'POST':

        idDB = request.args.get('id')

        collection = Mongo('uploads').collection

        itemCollection = collection.find_one_and_delete({'_id': ObjectId(idDB)})

        if itemCollection:

            uploadPath = os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'], itemCollection['fileName'])

            if os.path.exists(uploadPath):

                try:
                    os.remove(uploadPath)

                except Exception as e:

                    print(f"Ocorreu um erro ao tentar deletar o arquivo: {e}")
                    
                    return jsonify({"error": e}), 400

    return jsonify({"success": True}), 200


@app.route('/')
@login_required
def home():

    fileNames = []

    collectionUpload = Mongo('uploads').collection
    dataUserDB = collectionUpload.find({'userID': current_user.id})

    defaultFileDB = collectionUpload.find({'userID': 'all'})
    
    index = 1
    if defaultFileDB:
        for item in defaultFileDB:
            item.update({"index": index})
            fileNames.append(item)
            index += 1

    if dataUserDB:
        for item in dataUserDB:
            item.update({"index": index})
            fileNames.append(item)
            index += 1

    return render_template('index.html', fileNames=fileNames)

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')