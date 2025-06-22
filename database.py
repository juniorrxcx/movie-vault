import mysql.connector # type: ignore
import os

def get_db_connection():
    """Cria e retorna uma conexão com o banco de dados."""
    try:
        conn = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_DATABASE')
        )
        print("Conexão com o MySQL bem-sucedida!")
        return conn
    except mysql.connector.Error as e:
        print(f"Erro ao conectar ao MySQL: {e}")
        return None