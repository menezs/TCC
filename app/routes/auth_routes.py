from flask import render_template, redirect, url_for, request, flash
from flask_login import login_user, login_required, logout_user
from app import app, login_manager
from ..database.db_mongo import Mongo
from app.models.user import User

@login_manager.user_loader
def load_user(user_id):
    collectionUser = Mongo('users').collection
    user_data = collectionUser.find_one({'_id': user_id})
    if user_data:
        return User(user_data['_id'], user_data['name'], user_data['email'])
    return None

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'GET':
        return render_template('login.html')
    
    elif request.method == 'POST':

        logemail = request.form['logemail']
        logpass = request.form['logpass']

        collectionUser = Mongo('users').collection
        user_data = collectionUser.find_one({'_id': logemail})

        if user_data:

            if logpass == user_data['password']:
                userLogado = User(user_data['_id'], user_data['name'], user_data['email'])
                login_user(userLogado)
                print("usuário logado")

                next_route = request.form['next']
                if next_route == None:
                    next_route = '2F'

                return redirect(next_route)
            else:
                flash("E-mail e/ou Senha incorreta", "error")
        else:
            flash("Usuário não cadastrado", "error")

        return redirect('/')


    
@app.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':

        logemail = request.form['logemail']
        logpass = request.form['logpass']
        logname = request.form['logname']

        collectionUser = Mongo('users').collection
        user_data = collectionUser.find_one({'_id': logemail})

        if user_data == None:

            dataDB = {
                "_id": logemail,
                "name": logname,
                "email": logemail,
                "password": logpass
            }

            collectionUser.insert_one(dataDB)

            flash("Entre com E-mail e Senha cadastrados", "success")

            return redirect('/login')
        else:
            flash("E-mail já cadastrado, tente novamente", "error")

            return redirect('/login')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    print('Você foi desconectado')
    return redirect('/login')

