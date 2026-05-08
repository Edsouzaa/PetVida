from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import mysql.connector
import time
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'petvida-secret')

# Variaveis de Ambiente para a conexão do banco.
DB_HOST = os.environ.get('DB_HOST', 'mysql-service')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'petvida')
DB_USER = os.environ.get('DB_USER', 'petvida')
DB_NAME = os.environ.get('DB_NAME', 'petvida_db')
    

def conectar_db():
    tentativas = 10
    while tentativas > 0:
        try:
            conexao = mysql.connector.connect(
                host = DB_HOST,
                user = DB_USER,
                database = DB_NAME,
                password = DB_PASSWORD
            )
            return conexao
        except mysql.connector.Error:
            tentativas -= 1
            time.sleep(3)
    return None

# Casdastrar e puxar clientes.
@app.route("/cliente", methods=["POST","GET"])
def index():
    if request.method == "POST":
        nome = request.form["nome"]
        email = request.form["email"]
        telefone = request.form["telefone"]
        conexao = conectar_db()
        if conexao:
            cursor = conexao.cursor()
            cursor.execute(
                "INSERT INTO cliente (nome, telefone, email) VALUES (%s, %s, %s)",
                (nome, telefone, email)
            )
            conexao.commit()
            cursor.close()
            conexao.close()
    quantidade_clientes = int(request.form["quantidade"])
    pagina = int(request.form["pagina"])
    
    limite = quantidade_clientes
    offset = (pagina - 1) * limite
    
    conexao = conectar_db()
    if conexao:
        cursor = conexao.cursor()
        cursor.execute(
            "SELECT * FROM cliente ORDER BY id LIMIT %s OFFSET %s",
            (limite, offset)
        )
        clientes = cursor.fetchall()
        cursor.close()
        conexao.close()
        return jsonify(clientes)
    return jsonify({
        "erro":"Erro ao conectar ao banco"
    }), 500
    
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
