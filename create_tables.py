# Este script importa o nosso app e o banco de dados
from app import app, db

# Ele entra no "modo de engenharia" do nosso forte...
with app.app_context():
    # ...e dá a ordem para construir todas as prateleiras (tabelas)!
    db.create_all()

print("Decreto de construção executado: As tabelas do banco de dados foram criadas com sucesso.")
