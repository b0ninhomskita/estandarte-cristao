# Importando as ferramentas necessárias do nosso arsenal
import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

# --- CONFIGURAÇÃO INICIAL ---
app = Flask(__name__)
app.config['SECRET_KEY'] = 'uma-chave-secreta-muito-segura-e-dificil-de-adivinhar'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# --- PASTAS DE UPLOAD ---
# Garante que as pastas para upload existam
app.config['EBOOKS_FOLDER'] = os.path.join(app.root_path, 'static', 'ebooks')
app.config['COVERS_FOLDER'] = os.path.join(app.root_path, 'static', 'covers')
app.config['ARTICLE_COVERS_FOLDER'] = os.path.join(app.root_path, 'static', 'article_covers')
os.makedirs(app.config['EBOOKS_FOLDER'], exist_ok=True)
os.makedirs(app.config['COVERS_FOLDER'], exist_ok=True)
os.makedirs(app.config['ARTICLE_COVERS_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)

# --- MODELOS DO BANCO DE DADOS ATUALIZADOS ---
class Artigo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(150), nullable=False)
    conteudo = db.Column(db.Text, nullable=False)
    resumo = db.Column(db.String(300), nullable=False)
    # Novo campo para a capa do artigo
    nome_arquivo_capa = db.Column(db.String(100), nullable=False, default='default_article.jpg')

class Ebook(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(150), nullable=False)
    categoria = db.Column(db.String(50), nullable=False)
    nome_arquivo_pdf = db.Column(db.String(100), nullable=False)
    nome_arquivo_capa = db.Column(db.String(100), nullable=False, default='default_ebook.jpg')

# --- ROTAS PÚBLICAS (sem alterações) ---
@app.route("/")
def home():
    artigos_recentes = Artigo.query.order_by(Artigo.id.desc()).limit(3).all()
    return render_template('index.html', artigos=artigos_recentes)

@app.route("/conteudo")
def conteudo():
    ebooks = Ebook.query.all()
    artigos = Artigo.query.all()
    return render_template('conteudo.html', ebooks=ebooks, artigos=artigos)

@app.route("/artigo/<int:artigo_id>")
def pagina_artigo(artigo_id):
    artigo = Artigo.query.get_or_404(artigo_id)
    return render_template('artigo.html', artigo=artigo)

@app.route("/sobre")
def sobre():
    return render_template('sobre.html')

# --- ROTAS ADMINISTRATIVAS ---
@app.route("/admin")
def admin():
    artigos = Artigo.query.all()
    ebooks = Ebook.query.all()
    return render_template('admin.html', artigos=artigos, ebooks=ebooks)

# --- ROTAS DE ARTIGOS ATUALIZADAS ---
@app.route("/admin/adicionar_artigo", methods=['GET', 'POST'])
def adicionar_artigo():
    if request.method == 'POST':
        if 'arquivo_capa' not in request.files or request.files['arquivo_capa'].filename == '':
            flash('Por favor, selecione uma imagem de capa para o artigo.', 'danger')
            return redirect(request.url)

        arquivo_capa = request.files['arquivo_capa']
        nome_capa = arquivo_capa.filename
        arquivo_capa.save(os.path.join(app.config['ARTICLE_COVERS_FOLDER'], nome_capa))

        novo_artigo = Artigo(
            titulo=request.form['titulo'], 
            resumo=request.form['resumo'], 
            conteudo=request.form['conteudo'],
            nome_arquivo_capa=nome_capa
        )
        db.session.add(novo_artigo)
        db.session.commit()
        flash('Artigo adicionado com sucesso!', 'success')
        return redirect(url_for('admin'))
    return render_template('adicionar_artigo.html')


@app.route("/admin/editar_artigo/<int:artigo_id>", methods=['GET', 'POST'])
def editar_artigo(artigo_id):
    artigo = Artigo.query.get_or_404(artigo_id)
    if request.method == 'POST':
        artigo.titulo = request.form['titulo']
        artigo.resumo = request.form['resumo']
        artigo.conteudo = request.form['conteudo']
        
        # Lógica para atualizar a capa, se uma nova for enviada
        if 'arquivo_capa' in request.files and request.files['arquivo_capa'].filename != '':
            arquivo_capa = request.files['arquivo_capa']
            nome_capa = arquivo_capa.filename
            arquivo_capa.save(os.path.join(app.config['ARTICLE_COVERS_FOLDER'], nome_capa))
            artigo.nome_arquivo_capa = nome_capa

        db.session.commit()
        flash('Artigo atualizado com sucesso!', 'success')
        return redirect(url_for('admin'))
    return render_template('editar_artigo.html', artigo=artigo)


@app.route('/admin/deletar_artigo/<int:artigo_id>', methods=['POST'])
def deletar_artigo(artigo_id):
    artigo = Artigo.query.get_or_404(artigo_id)
    try:
        os.remove(os.path.join(app.config['ARTICLE_COVERS_FOLDER'], artigo.nome_arquivo_capa))
    except FileNotFoundError:
        flash('Arquivo de capa não encontrado no servidor, mas registro removido.', 'warning')
    
    db.session.delete(artigo)
    db.session.commit()
    flash('Artigo deletado com sucesso!', 'success')
    return redirect(url_for('admin'))

# --- ROTAS DE E-BOOKS (sem alterações) ---
@app.route("/admin/adicionar_ebook", methods=['GET', 'POST'])
def adicionar_ebook():
    if request.method == 'POST':
        if 'arquivo_pdf' not in request.files or request.files['arquivo_pdf'].filename == '' or \
           'arquivo_capa' not in request.files or request.files['arquivo_capa'].filename == '':
            flash('Por favor, selecione o arquivo PDF e a imagem da capa.', 'danger')
            return redirect(request.url)
        arquivo_pdf = request.files['arquivo_pdf']
        arquivo_capa = request.files['arquivo_capa']
        nome_pdf = arquivo_pdf.filename
        nome_capa = arquivo_capa.filename
        arquivo_pdf.save(os.path.join(app.config['EBOOKS_FOLDER'], nome_pdf))
        arquivo_capa.save(os.path.join(app.config['COVERS_FOLDER'], nome_capa))
        novo_ebook = Ebook(titulo=request.form['titulo'], categoria=request.form['categoria'], nome_arquivo_pdf=nome_pdf, nome_arquivo_capa=nome_capa)
        db.session.add(novo_ebook)
        db.session.commit()
        flash('E-book adicionado com sucesso!', 'success')
        return redirect(url_for('admin'))
    return render_template('adicionar_ebook.html')

@app.route('/admin/deletar_ebook/<int:ebook_id>', methods=['POST'])
def deletar_ebook(ebook_id):
    ebook_para_deletar = Ebook.query.get_or_404(ebook_id)
    try:
        os.remove(os.path.join(app.config['EBOOKS_FOLDER'], ebook_para_deletar.nome_arquivo_pdf))
        os.remove(os.path.join(app.config['COVERS_FOLDER'], ebook_para_deletar.nome_arquivo_capa))
    except FileNotFoundError:
        flash('Arquivos do e-book não encontrados no servidor, mas o registro foi removido.', 'warning')
    db.session.delete(ebook_para_deletar)
    db.session.commit()
    flash('E-book deletado com sucesso!', 'success')
    return redirect(url_for('admin'))

# --- Bloco de Inicialização ---
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
