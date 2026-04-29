from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'petvida-secret')

def get_db():
    return mysql.connector.connect(
        host=os.environ.get('DB_HOST', 'mysql-service'),
        user=os.environ.get('DB_USER', 'petvida'),
        password=os.environ.get('DB_PASSWORD', 'petvida123'),
        database=os.environ.get('DB_NAME', 'petvida_db')
    )

#--------------------------- Aqui é a parte dos pet -------------------------------

@app.route('/pets')
def listar_pets():
    db = get_db(); cur = db.cursor(dictionary=True)
    cur.execute("""SELECT p.*, c.nome AS nome_cliente
                   FROM pets p JOIN clientes c ON p.cliente_id=c.id ORDER BY p.nome""")
    dados = cur.fetchall(); cur.close(); db.close()
    return render_template('pets.html', pets=dados)
