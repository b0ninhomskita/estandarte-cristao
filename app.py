import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'uma-chave-secreta-muito-segura-e-dificil-de-adivinhar'

# --- MUDANÇA PRINCIPAL AQUI ---
# Agora, ele vai procurar o mapa do tesouro em uma variável de ambiente.
# Se não achar, ele usa um site.db local para testes.
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'sqlite:///site.db'
# --- FIM DA MUDANÇA ---

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# ... (o resto do seu app.py, com as pastas de upload, modelos e rotas, continua EXATAMENTE IGUAL) ...
# (Cole o resto do seu app.py aqui, sem mudar mais nada)
