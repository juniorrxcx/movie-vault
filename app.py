import os
import uuid
from flask import Flask, render_template, request, redirect, url_for, flash# type: ignore
from werkzeug.utils import secure_filename # type: ignore
from dotenv import load_dotenv # type: ignore
from database import get_db_connection

# carrega o .env com as var de ambiente
load_dotenv()

app = Flask(__name__)


# chave secreta para segurança das sessões
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'chave-secreta-padrao-para-mudar')

# config da pasta de upload
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}


def allowed_file(filename):
    """Verifica se a extensão do arquivo é permitida."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Rota principal que exibe todos os filmes do acervo."""
    conn = None 
    filmes = [] 
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id, nome, ano, genero, sinopse, poster FROM Filmes ORDER BY id DESC")
            filmes = cursor.fetchall()
            cursor.close()
        else:
            flash("Não foi possível conectar ao banco de dados.", "error")
    except Exception as e:
        
        flash(f"Ocorreu um erro ao buscar os filmes: {e}", "error")
    finally:
        
        if conn and conn.is_connected():
            conn.close()
    
    return render_template('index.html', filmes=filmes)

@app.route('/adicionar', methods=['GET', 'POST'])
def adicionar_filme():
    """Rota para exibir o formulário e processar a adição de um novo filme."""
    if request.method == 'POST':
        # pega os dados do formulário
        nome = request.form.get('nome')
        ano = request.form.get('ano')
        genero = request.form.get('genero')
        sinopse = request.form.get('sinopse')
        poster_file = request.files.get('poster')

        # valida os dados
        if not all([nome, ano, genero, sinopse, poster_file]):
            flash('Todos os campos, incluindo o pôster, são obrigatórios!', 'warning')
            return redirect(request.url)
        
        if not allowed_file(poster_file.filename):
            flash('Tipo de arquivo de imagem inválido!', 'error')
            return redirect(request.url)

   
        conn = None
        try:
            
            filename = secure_filename(poster_file.filename)
            extension = filename.rsplit('.', 1)[1].lower()
            unique_filename = f"{uuid.uuid4()}.{extension}"
            
            # salva o arquivo na pasta de uploads
            poster_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            poster_file.save(poster_path)
            
            
            db_poster_path = f'uploads/{unique_filename}'

            
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                sql = "INSERT INTO Filmes (nome, ano, genero, sinopse, poster) VALUES (%s, %s, %s, %s, %s)"
                val = (nome, ano, genero, sinopse, db_poster_path)
                cursor.execute(sql, val)
                conn.commit()
                cursor.close()
                flash('Filme adicionado com sucesso!', 'success')
            else:
                flash('Falha na conexão com o banco de dados.', 'error')

        except Exception as e:
            flash(f'Ocorreu um erro inesperado ao salvar o filme: {e}', 'error')
        finally:
            if conn and conn.is_connected():
                conn.close()
        
        return redirect(url_for('index'))

    
    return render_template('adicionar.html')

if __name__ == '__main__':
    
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)