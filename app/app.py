from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import mysql.connector
import time
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'petvida-secret')

DB_HOST = os.environ.get('DB_HOST', 'mysql-service')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'petvida')
DB_USER = os.environ.get('DB_USER', 'petvida')
DB_NAME = os.environ.get('DB_NAME', 'petvida_db')


def conectar_db():
    tentativas = 10
    while tentativas > 0:
        try:
            conexao = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                database=DB_NAME,
                password=DB_PASSWORD
            )
            return conexao
        except mysql.connector.Error:
            tentativas -= 1
            time.sleep(3)
    return None


# ─────────────────────────── DASHBOARD ───────────────────────────

@app.route("/")
def dashboard():
    conexao = conectar_db()
    stats = {"clientes": 0, "pets": 0, "atendimentos": 0, "produtos": 0}
    if conexao:
        cursor = conexao.cursor()
        cursor.execute("SELECT COUNT(*) FROM cliente")
        stats["clientes"] = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM pet")
        stats["pets"] = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM atendimento")
        stats["atendimentos"] = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM produto")
        stats["produtos"] = cursor.fetchone()[0]
        cursor.close()
        conexao.close()
    return render_template("dashboard.html", stats=stats)


# ─────────────────────────── CLIENTES ───────────────────────────

@app.route("/clientes")
def listar_clientes():
    conexao = conectar_db()
    clientes = []
    if conexao:
        cursor = conexao.cursor(dictionary=True)
        cursor.execute("SELECT * FROM cliente ORDER BY id DESC")
        clientes = cursor.fetchall()
        cursor.close()
        conexao.close()
    return render_template("clientes.html", clientes=clientes)


@app.route("/clientes/novo", methods=["GET", "POST"])
def novo_cliente():
    if request.method == "POST":
        nome = request.form["nome"]
        email = request.form["email"]
        telefone = request.form["telefone"]
        conexao = conectar_db()
        if conexao:
            try:
                cursor = conexao.cursor()
                cursor.execute(
                    "INSERT INTO cliente (nome, telefone, email) VALUES (%s, %s, %s)",
                    (nome, telefone, email)
                )
                conexao.commit()
                cursor.close()
                conexao.close()
                flash("Cliente cadastrado com sucesso!", "success")
            except mysql.connector.IntegrityError:
                flash("E-mail já cadastrado.", "error")
        return redirect(url_for("listar_clientes"))
    return render_template("form_cliente.html")


@app.route("/clientes/editar/<int:id>", methods=["GET", "POST"])
def editar_cliente(id):
    conexao = conectar_db()
    if request.method == "POST":
        nome = request.form["nome"]
        email = request.form["email"]
        telefone = request.form["telefone"]
        if conexao:
            cursor = conexao.cursor()
            cursor.execute(
                "UPDATE cliente SET nome=%s, telefone=%s, email=%s WHERE id=%s",
                (nome, telefone, email, id)
            )
            conexao.commit()
            cursor.close()
            conexao.close()
            flash("Cliente atualizado!", "success")
        return redirect(url_for("listar_clientes"))
    cliente = None
    if conexao:
        cursor = conexao.cursor(dictionary=True)
        cursor.execute("SELECT * FROM cliente WHERE id=%s", (id,))
        cliente = cursor.fetchone()
        cursor.close()
        conexao.close()
    return render_template("form_cliente.html", cliente=cliente)


@app.route("/clientes/excluir/<int:id>", methods=["POST"])
def excluir_cliente(id):
    conexao = conectar_db()
    if conexao:
        cursor = conexao.cursor()
        # 1. pega todos os pets do cliente
        cursor.execute("SELECT id FROM pet WHERE id_cliente=%s", (id,))
        pet_ids = [row[0] for row in cursor.fetchall()]
        # 2. deleta atendimentos de cada pet
        for pet_id in pet_ids:
            cursor.execute("DELETE FROM atendimento WHERE id_pet=%s", (pet_id,))
        # 3. deleta os pets
        cursor.execute("DELETE FROM pet WHERE id_cliente=%s", (id,))
        # 4. deleta o cliente
        cursor.execute("DELETE FROM cliente WHERE id=%s", (id,))
        conexao.commit()
        cursor.close()
        conexao.close()
        flash("Cliente removido.", "success")
    return redirect(url_for("listar_clientes"))


# ─────────────────────────── PETS ───────────────────────────

@app.route("/pets")
def listar_pets():
    conexao = conectar_db()
    pets = []
    if conexao:
        cursor = conexao.cursor(dictionary=True)
        cursor.execute("""
            SELECT p.*, c.nome AS nome_cliente
            FROM pet p
            JOIN cliente c ON p.id_cliente = c.id
            ORDER BY p.id DESC
        """)
        pets = cursor.fetchall()
        cursor.close()
        conexao.close()
    return render_template("pets.html", pets=pets)


@app.route("/pets/novo", methods=["GET", "POST"])
def novo_pet():
    conexao = conectar_db()
    clientes = []
    if conexao:
        cursor = conexao.cursor(dictionary=True)
        cursor.execute("SELECT id, nome FROM cliente ORDER BY nome")
        clientes = cursor.fetchall()
        cursor.close()
        conexao.close()

    if request.method == "POST":
        nome = request.form["nome"]
        tipo = request.form["tipo"]
        raca = request.form["raca"]
        idade = request.form["idade"]
        id_cliente = request.form["id_cliente"]
        conexao = conectar_db()
        if conexao:
            cursor = conexao.cursor()
            cursor.execute(
                "INSERT INTO pet (nome, tipo, raca, idade, id_cliente) VALUES (%s, %s, %s, %s, %s)",
                (nome, tipo, raca, idade, id_cliente)
            )
            conexao.commit()
            cursor.close()
            conexao.close()
            flash("Pet cadastrado com sucesso!", "success")
        return redirect(url_for("listar_pets"))
    return render_template("form_pet.html", clientes=clientes)


@app.route("/pets/editar/<int:id>", methods=["GET", "POST"])
def editar_pet(id):
    conexao = conectar_db()
    clientes = []
    pet = None
    if conexao:
        cursor = conexao.cursor(dictionary=True)
        cursor.execute("SELECT id, nome FROM cliente ORDER BY nome")
        clientes = cursor.fetchall()
        cursor.execute("SELECT * FROM pet WHERE id=%s", (id,))
        pet = cursor.fetchone()
        cursor.close()
        conexao.close()

    if request.method == "POST":
        nome = request.form["nome"]
        tipo = request.form["tipo"]
        raca = request.form["raca"]
        idade = request.form["idade"]
        id_cliente = request.form["id_cliente"]
        conexao = conectar_db()
        if conexao:
            cursor = conexao.cursor()
            cursor.execute(
                "UPDATE pet SET nome=%s, tipo=%s, raca=%s, idade=%s, id_cliente=%s WHERE id=%s",
                (nome, tipo, raca, idade, id_cliente, id)
            )
            conexao.commit()
            cursor.close()
            conexao.close()
            flash("Pet atualizado!", "success")
        return redirect(url_for("listar_pets"))
    return render_template("form_pet.html", clientes=clientes, pet=pet)


@app.route("/pets/excluir/<int:id>", methods=["POST"])
def excluir_pet(id):
    conexao = conectar_db()
    if conexao:
        cursor = conexao.cursor()
        # 1. deleta atendimentos do pet
        cursor.execute("DELETE FROM atendimento WHERE id_pet=%s", (id,))
        # 2. deleta o pet
        cursor.execute("DELETE FROM pet WHERE id=%s", (id,))
        conexao.commit()
        cursor.close()
        conexao.close()
        flash("Pet removido.", "success")
    return redirect(url_for("listar_pets"))


# ─────────────────────────── ATENDIMENTOS ───────────────────────────

@app.route("/atendimentos")
def listar_atendimentos():
    conexao = conectar_db()
    atendimentos = []
    if conexao:
        cursor = conexao.cursor(dictionary=True)
        cursor.execute("""
            SELECT a.*, p.nome AS nome_pet, c.nome AS nome_cliente
            FROM atendimento a
            JOIN pet p ON a.id_pet = p.id
            JOIN cliente c ON p.id_cliente = c.id
            ORDER BY a.data_atendimento DESC
        """)
        atendimentos = cursor.fetchall()
        cursor.close()
        conexao.close()
    return render_template("atendimentos.html", atendimentos=atendimentos)


@app.route("/atendimentos/novo", methods=["GET", "POST"])
def novo_atendimento():
    conexao = conectar_db()
    pets = []
    if conexao:
        cursor = conexao.cursor(dictionary=True)
        cursor.execute("""
            SELECT p.id, p.nome, c.nome AS nome_cliente
            FROM pet p JOIN cliente c ON p.id_cliente = c.id
            ORDER BY p.nome
        """)
        pets = cursor.fetchall()
        cursor.close()
        conexao.close()

    if request.method == "POST":
        tipo = request.form["tipo"]
        data_atendimento = request.form["data_atendimento"]
        valor = request.form["valor"]
        id_pet = request.form["id_pet"]
        conexao = conectar_db()
        if conexao:
            cursor = conexao.cursor()
            cursor.execute(
                "INSERT INTO atendimento (tipo, data_atendimento, valor, id_pet) VALUES (%s, %s, %s, %s)",
                (tipo, data_atendimento, valor, id_pet)
            )
            conexao.commit()
            cursor.close()
            conexao.close()
            flash("Atendimento registrado!", "success")
        return redirect(url_for("listar_atendimentos"))
    return render_template("form_atendimento.html", pets=pets)


@app.route("/atendimentos/excluir/<int:id>", methods=["POST"])
def excluir_atendimento(id):
    conexao = conectar_db()
    if conexao:
        cursor = conexao.cursor()
        cursor.execute("DELETE FROM atendimento WHERE id=%s", (id,))
        conexao.commit()
        cursor.close()
        conexao.close()
        flash("Atendimento removido.", "success")
    return redirect(url_for("listar_atendimentos"))


# ─────────────────────────── PRODUTOS ───────────────────────────

@app.route("/produtos")
def listar_produtos():
    conexao = conectar_db()
    produtos = []
    if conexao:
        cursor = conexao.cursor(dictionary=True)
        cursor.execute("SELECT * FROM produto ORDER BY id DESC")
        produtos = cursor.fetchall()
        cursor.close()
        conexao.close()
    return render_template("produtos.html", produtos=produtos)


@app.route("/produtos/novo", methods=["GET", "POST"])
def novo_produto():
    if request.method == "POST":
        descricao = request.form["descricao"]
        preco = request.form["preco"]
        quantidade = request.form["quantidade"]
        conexao = conectar_db()
        if conexao:
            cursor = conexao.cursor()
            cursor.execute(
                "INSERT INTO produto (descricao, preco, quantidade) VALUES (%s, %s, %s)",
                (descricao, preco, quantidade)
            )
            conexao.commit()
            cursor.close()
            conexao.close()
            flash("Produto cadastrado!", "success")
        return redirect(url_for("listar_produtos"))
    return render_template("form_produto.html")


@app.route("/produtos/editar/<int:id>", methods=["GET", "POST"])
def editar_produto(id):
    conexao = conectar_db()
    produto = None
    if conexao:
        cursor = conexao.cursor(dictionary=True)
        cursor.execute("SELECT * FROM produto WHERE id=%s", (id,))
        produto = cursor.fetchone()
        cursor.close()
        conexao.close()

    if request.method == "POST":
        descricao = request.form["descricao"]
        preco = request.form["preco"]
        quantidade = request.form["quantidade"]
        conexao = conectar_db()
        if conexao:
            cursor = conexao.cursor()
            cursor.execute(
                "UPDATE produto SET descricao=%s, preco=%s, quantidade=%s WHERE id=%s",
                (descricao, preco, quantidade, id)
            )
            conexao.commit()
            cursor.close()
            conexao.close()
            flash("Produto atualizado!", "success")
        return redirect(url_for("listar_produtos"))
    return render_template("form_produto.html", produto=produto)


@app.route("/produtos/excluir/<int:id>", methods=["POST"])
def excluir_produto(id):
    conexao = conectar_db()
    if conexao:
        cursor = conexao.cursor()
        cursor.execute("DELETE FROM produto WHERE id=%s", (id,))
        conexao.commit()
        cursor.close()
        conexao.close()
        flash("Produto removido.", "success")
    return redirect(url_for("listar_produtos"))


# ─────────────────────────── API JSON (compatibilidade) ───────────────────────────

@app.route("/api/clientes", methods=["GET", "POST"])
def api_clientes():
    if request.method == "POST":
        data = request.get_json() or request.form
        nome = data.get("nome")
        email = data.get("email")
        telefone = data.get("telefone")
        conexao = conectar_db()
        if conexao:
            try:
                cursor = conexao.cursor()
                cursor.execute(
                    "INSERT INTO cliente (nome, telefone, email) VALUES (%s, %s, %s)",
                    (nome, telefone, email)
                )
                conexao.commit()
                cursor.close()
                conexao.close()
                return jsonify({"mensagem": "Cliente cadastrado"}), 201
            except mysql.connector.IntegrityError:
                return jsonify({"erro": "E-mail já cadastrado"}), 409
        return jsonify({"erro": "Erro ao conectar ao banco"}), 500

    quantidade = int(request.args.get("quantidade", 10))
    pagina = int(request.args.get("pagina", 1))
    limite = quantidade
    offset = (pagina - 1) * limite
    conexao = conectar_db()
    if conexao:
        cursor = conexao.cursor(dictionary=True)
        cursor.execute("SELECT * FROM cliente ORDER BY id LIMIT %s OFFSET %s", (limite, offset))
        clientes = cursor.fetchall()
        cursor.close()
        conexao.close()
        return jsonify(clientes)
    return jsonify({"erro": "Erro ao conectar ao banco"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)