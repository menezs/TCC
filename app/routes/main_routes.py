from flask import render_template
from flask_login import login_required,current_user
from app import app

@app.route('/')
@login_required
def home():
    return render_template('home.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return f'Bem-vindo ao painel, {current_user.username}!<br><a href="/logout"><button name="logout">logout</button></a>'