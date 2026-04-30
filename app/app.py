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

# ─────────────────────────── HOME ────────────────────────────
@app.route('/')
def index():
    db = get_db(); cur = db.cursor()
    cur.execute("SELECT COUNT(*) FROM clientes"); c = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM pets");     p = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM atendimentos"); a = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM produtos");     pr = cur.fetchone()[0]
    cur.close(); db.close()
    return render_template('index.html', total_clientes=c, total_pets=p,
                           total_atendimentos=a, total_produtos=pr)

# ─────────────────────────── CLIENTES ────────────────────────
@app.route('/clientes')
def listar_clientes():
    db = get_db(); cur = db.cursor(dictionary=True)
    cur.execute("SELECT * FROM clientes ORDER BY nome")
    dados = cur.fetchall(); cur.close(); db.close()
    return render_template('clientes.html', clientes=dados)

@app.route('/clientes/novo', methods=['GET','POST'])
def novo_cliente():
    if request.method == 'POST':
        nome  = request.form['nome']
        tel   = request.form['telefone']
        email = request.form['email']
        db = get_db(); cur = db.cursor()
        cur.execute("INSERT INTO clientes (nome,telefone,email) VALUES (%s,%s,%s)", (nome,tel,email))
        db.commit(); cur.close(); db.close()
        flash('Cliente cadastrado com sucesso!', 'success')
        return redirect(url_for('listar_clientes'))
    return render_template('form_cliente.html')

@app.route('/clientes/editar/<int:id>', methods=['GET','POST'])
def editar_cliente(id):
    db = get_db(); cur = db.cursor(dictionary=True)
    if request.method == 'POST':
        cur.execute("UPDATE clientes SET nome=%s,telefone=%s,email=%s WHERE id=%s",
                    (request.form['nome'],request.form['telefone'],request.form['email'],id))
        db.commit(); cur.close(); db.close()
        flash('Cliente atualizado!', 'success')
        return redirect(url_for('listar_clientes'))
    cur.execute("SELECT * FROM clientes WHERE id=%s", (id,))
    cliente = cur.fetchone(); cur.close(); db.close()
    return render_template('form_cliente.html', cliente=cliente)

@app.route('/clientes/excluir/<int:id>')
def excluir_cliente(id):
    db = get_db(); cur = db.cursor()
    cur.execute("DELETE FROM clientes WHERE id=%s", (id,))
    db.commit(); cur.close(); db.close()
    flash('Cliente excluído!', 'info')
    return redirect(url_for('listar_clientes'))

# ─────────────────────────── PETS ────────────────────────────
@app.route('/pets')
def listar_pets():
    db = get_db(); cur = db.cursor(dictionary=True)
    cur.execute("""SELECT p.*, c.nome AS nome_cliente
                   FROM pets p JOIN clientes c ON p.cliente_id=c.id ORDER BY p.nome""")
    dados = cur.fetchall(); cur.close(); db.close()
    return render_template('pets.html', pets=dados)

@app.route('/pets/novo', methods=['GET','POST'])
def novo_pet():
    db = get_db(); cur = db.cursor(dictionary=True)
    if request.method == 'POST':
        cur2 = db.cursor()
        cur2.execute("INSERT INTO pets (nome,tipo,raca,idade,cliente_id) VALUES (%s,%s,%s,%s,%s)",
                     (request.form['nome'],request.form['tipo'],
                      request.form['raca'],request.form['idade'],request.form['cliente_id']))
        db.commit(); cur2.close(); cur.close(); db.close()
        flash('Pet cadastrado com sucesso!', 'success')
        return redirect(url_for('listar_pets'))
    cur.execute("SELECT id,nome FROM clientes ORDER BY nome")
    clientes = cur.fetchall(); cur.close(); db.close()
    return render_template('form_pet.html', clientes=clientes)

@app.route('/pets/editar/<int:id>', methods=['GET','POST'])
def editar_pet(id):
    db = get_db(); cur = db.cursor(dictionary=True)
    if request.method == 'POST':
        cur2 = db.cursor()
        cur2.execute("UPDATE pets SET nome=%s,tipo=%s,raca=%s,idade=%s,cliente_id=%s WHERE id=%s",
                     (request.form['nome'],request.form['tipo'],request.form['raca'],
                      request.form['idade'],request.form['cliente_id'],id))
        db.commit(); cur2.close()
    else:
        cur.execute("SELECT * FROM pets WHERE id=%s", (id,))
        pet = cur.fetchone()
        cur.execute("SELECT id,nome FROM clientes ORDER BY nome")
        clientes = cur.fetchall(); cur.close(); db.close()
        return render_template('form_pet.html', pet=pet, clientes=clientes)
    cur.close(); db.close()
    flash('Pet atualizado!', 'success')
    return redirect(url_for('listar_pets'))

@app.route('/pets/excluir/<int:id>')
def excluir_pet(id):
    db = get_db(); cur = db.cursor()
    cur.execute("DELETE FROM pets WHERE id=%s", (id,))
    db.commit(); cur.close(); db.close()
    flash('Pet excluído!', 'info')
    return redirect(url_for('listar_pets'))

# ─────────────────────────── ATENDIMENTOS ────────────────────
@app.route('/atendimentos')
def listar_atendimentos():
    db = get_db(); cur = db.cursor(dictionary=True)
    cur.execute("""SELECT a.*, p.nome AS nome_pet, c.nome AS nome_cliente
                   FROM atendimentos a
                   JOIN pets p ON a.pet_id=p.id
                   JOIN clientes c ON p.cliente_id=c.id
                   ORDER BY a.data DESC""")
    dados = cur.fetchall(); cur.close(); db.close()
    return render_template('atendimentos.html', atendimentos=dados)

@app.route('/atendimentos/novo', methods=['GET','POST'])
def novo_atendimento():
    db = get_db(); cur = db.cursor(dictionary=True)
    if request.method == 'POST':
        cur2 = db.cursor()
        cur2.execute("INSERT INTO atendimentos (pet_id,tipo_servico,data,valor) VALUES (%s,%s,%s,%s)",
                     (request.form['pet_id'],request.form['tipo_servico'],
                      request.form['data'],request.form['valor']))
        db.commit(); cur2.close(); cur.close(); db.close()
        flash('Atendimento registrado com sucesso!', 'success')
        return redirect(url_for('listar_atendimentos'))
    cur.execute("SELECT p.id, p.nome, c.nome AS nome_cliente FROM pets p JOIN clientes c ON p.cliente_id=c.id ORDER BY p.nome")
    pets = cur.fetchall(); cur.close(); db.close()
    return render_template('form_atendimento.html', pets=pets)

@app.route('/atendimentos/excluir/<int:id>')
def excluir_atendimento(id):
    db = get_db(); cur = db.cursor()
    cur.execute("DELETE FROM atendimentos WHERE id=%s", (id,))
    db.commit(); cur.close(); db.close()
    flash('Atendimento excluído!', 'info')
    return redirect(url_for('listar_atendimentos'))

# ─────────────────────────── PRODUTOS ────────────────────────
@app.route('/produtos')
def listar_produtos():
    db = get_db(); cur = db.cursor(dictionary=True)
    cur.execute("SELECT * FROM produtos ORDER BY nome")
    dados = cur.fetchall(); cur.close(); db.close()
    return render_template('produtos.html', produtos=dados)

@app.route('/produtos/novo', methods=['GET','POST'])
def novo_produto():
    if request.method == 'POST':
        db = get_db(); cur = db.cursor()
        cur.execute("INSERT INTO produtos (nome,descricao,preco,quantidade_estoque) VALUES (%s,%s,%s,%s)",
                    (request.form['nome'],request.form['descricao'],
                     request.form['preco'],request.form['quantidade_estoque']))
        db.commit(); cur.close(); db.close()
        flash('Produto cadastrado com sucesso!', 'success')
        return redirect(url_for('listar_produtos'))
    return render_template('form_produto.html')

@app.route('/produtos/editar/<int:id>', methods=['GET','POST'])
def editar_produto(id):
    db = get_db(); cur = db.cursor(dictionary=True)
    if request.method == 'POST':
        cur2 = db.cursor()
        cur2.execute("UPDATE produtos SET nome=%s,descricao=%s,preco=%s,quantidade_estoque=%s WHERE id=%s",
                     (request.form['nome'],request.form['descricao'],
                      request.form['preco'],request.form['quantidade_estoque'],id))
        db.commit(); cur2.close(); cur.close(); db.close()
        flash('Produto atualizado!', 'success')
        return redirect(url_for('listar_produtos'))
    
    cur.execute("SELECT * FROM produtos WHERE id=%s", (id,))
    produto = cur.fetchone(); cur.close(); db.close()
    return render_template('form_produto.html', produto=produto)

@app.route('/produtos/excluir/<int:id>')
def excluir_produto(id):
    db = get_db(); cur = db.cursor()
    cur.execute("DELETE FROM produtos WHERE id=%s", (id,))
    db.commit(); cur.close(); db.close()
    flash('Produto excluído!', 'info')
    return redirect(url_for('listar_produtos'))

# ─────────────────────────── FORNECEDORES ────────────────────
@app.route('/fornecedores')
def listar_fornecedores():
    db = get_db(); cur = db.cursor(dictionary=True)
    cur.execute("SELECT * FROM fornecedores ORDER BY nome")
    dados = cur.fetchall(); cur.close(); db.close()
    return render_template('fornecedores.html', fornecedores=dados)

@app.route('/fornecedores/novo', methods=['GET','POST'])
def novo_fornecedor():
    if request.method == 'POST':
        db = get_db(); cur = db.cursor()
        cur.execute("INSERT INTO fornecedores (nome,telefone,email,produtos_representados) VALUES (%s,%s,%s,%s)",
                    (request.form['nome'],request.form['telefone'],
                     request.form['email'],request.form['produtos_representados']))
        db.commit(); cur.close(); db.close()
        flash('Fornecedor cadastrado com sucesso!', 'success')
        return redirect(url_for('listar_fornecedores'))
    return render_template('form_fornecedor.html')

@app.route('/fornecedores/excluir/<int:id>')
def excluir_fornecedor(id):
    db = get_db(); cur = db.cursor()
    cur.execute("DELETE FROM fornecedores WHERE id=%s", (id,))
    db.commit(); cur.close(); db.close()
    flash('Fornecedor excluído!', 'info')
    return redirect(url_for('listar_fornecedores'))

# ─────────────────────────── VENDAS ──────────────────────────
@app.route('/vendas')
def listar_vendas():
    db = get_db(); cur = db.cursor(dictionary=True)
    cur.execute("""SELECT v.*, c.nome AS nome_cliente, p.nome AS nome_produto
                   FROM vendas v
                   JOIN clientes c ON v.cliente_id=c.id
                   JOIN produtos p ON v.produto_id=p.id
                   ORDER BY v.data DESC""")
    dados = cur.fetchall(); cur.close(); db.close()
    return render_template('vendas.html', vendas=dados)

@app.route('/vendas/nova', methods=['GET','POST'])
def nova_venda():
    db = get_db(); cur = db.cursor(dictionary=True)
    if request.method == 'POST':
        produto_id   = request.form['produto_id']
        quantidade   = int(request.form['quantidade'])
        cur2 = db.cursor(dictionary=True)
        cur2.execute("SELECT preco, quantidade_estoque FROM produtos WHERE id=%s", (produto_id,))
        prod = cur2.fetchone()
        if prod['quantidade_estoque'] < quantidade:
            flash('Estoque insuficiente!', 'danger')
            cur.execute("SELECT id,nome FROM clientes ORDER BY nome")
            clientes = cur.fetchall()
            cur.execute("SELECT id,nome,preco,quantidade_estoque FROM produtos ORDER BY nome")
            produtos = cur.fetchall(); cur.close(); cur2.close(); db.close()
            return render_template('form_venda.html', clientes=clientes, produtos=produtos)
        
        valor_total = round(prod['preco'] * quantidade, 2)
        cur2.execute("INSERT INTO vendas (cliente_id,produto_id,quantidade,data,valor_total) VALUES (%s,%s,%s,%s,%s)",
                     (request.form['cliente_id'],produto_id,quantidade,request.form['data'],valor_total))
        cur2.execute("UPDATE produtos SET quantidade_estoque=quantidade_estoque-%s WHERE id=%s", (quantidade,produto_id))
        db.commit(); cur2.close(); cur.close(); db.close()
        flash('Venda registrada com sucesso!', 'success')
        return redirect(url_for('listar_vendas'))
    
    cur.execute("SELECT id,nome FROM clientes ORDER BY nome")
    clientes = cur.fetchall()
    cur.execute("SELECT id,nome,preco,quantidade_estoque FROM produtos ORDER BY nome")
    produtos = cur.fetchall(); cur.close(); db.close()
    return render_template('form_venda.html', clientes=clientes, produtos=produtos)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
