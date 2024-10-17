import sqlalchemy
import pandas as pd
import mysql.connector

# Credenciais de acesso ao banco de dados
host = "localhost"
user = "root"
password = "root"
database = "supermercado"

def select():
    # connection = mysql.connector.connect(host=host, user=user, password=password, database=database)
    engine = sqlalchemy.create_engine('mysql+pymysql://root:root@localhost:3306/supermercado')
    query = "SELECT horario AS data, quantidade_estoque AS quant, id_produto FROM consumo_produtos ORDER BY ID ASC"
    df = pd.read_sql(query, con = engine)
    return df

def obterProdutos():
    engine = sqlalchemy.create_engine('mysql+pymysql://root:root@localhost:3306/supermercado')
    query = "SELECT ID AS id_produto, nome_produto FROM produtos ORDER BY ID ASC"
    df = pd.read_sql(query, con = engine)
    return df

def obterVendas():
    engine = sqlalchemy.create_engine('mysql+pymysql://root:root@localhost:3306/supermercado')
    query = "SELECT A.ID AS id_produto, IFNULL(SUM(B.quantidade_comprada), 0) AS quant_total FROM produtos AS A LEFT JOIN consumo_produtos AS B ON A.ID = B.id_produto GROUP BY A.ID ORDER BY A.ID ASC;"
    df_bar = pd.read_sql(query, con = engine)
    return df_bar

def saveDB(quant, date, quant_estoque, id_produto):
    try:
        connection = mysql.connector.connect(host=host, user=user, password=password, database=database)
        # print("Conectado ao banco de dados MySQL!")
        
        # Criando um cursor para executar consultas
        cursor = connection.cursor()
        
        consulta = f"INSERT INTO consumo_produtos (horario, id_produto, quantidade_comprada, quantidade_estoque) VALUES ('{date}', {id_produto}, {quant}, {quant_estoque});"
        cursor.execute(consulta)
        
        connection.commit()
            
    except mysql.connector.Error as err:
        print("Erro na conexão: {}".format(err))
    finally:
        try:
            if connection:
                connection.close()
                # print("Conexão fechada")
        except:
            pass

def criar_produto(nome):
    try:
        connection = mysql.connector.connect(host=host, user=user, password=password, database=database)
        # print("Conectado ao banco de dados MySQL!")
        
        # Criando um cursor para executar consultas
        cursor = connection.cursor()
        
        consulta = f"INSERT INTO produtos (nome_produto) VALUES ('{nome}');"
        cursor.execute(consulta)
        
        connection.commit()
            
    except mysql.connector.Error as err:
        print("Erro na conexão: {}".format(err))
    finally:
        try:
            if connection:
                connection.close()
                # print("Conexão fechada")
        except:
            pass
        
def get_options_from_db():
    try:
        connection = mysql.connector.connect(host=host, user=user, password=password, database=database)
        # print("Conectado ao banco de dados MySQL!")
        
        # Criando um cursor para executar consultas
        cursor = connection.cursor()
        
        # Consulta SQL
        cursor.execute("SELECT ID, nome_produto FROM produtos ORDER BY nome_produto ASC")
        results = cursor.fetchall()

        # Fechando a conexão
        cursor.close()
        connection.close()

        # Convertendo resultados para o formato esperado pelo Dropdown
        options = [{"label": row[1], "value": row[0]} for row in results]
        return options

    except Exception as e:
        print(f"Erro ao consultar o banco de dados: {e}")
        return []