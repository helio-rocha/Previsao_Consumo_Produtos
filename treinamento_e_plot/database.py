import sqlalchemy
import pandas as pd
import mysql.connector

# Credenciais de acesso ao banco de dados
host = "localhost"
user = "root"
password = "root"
database = "supermercado"

def select():
    engine = sqlalchemy.create_engine('mysql+pymysql://root:root@localhost:3306/supermercado')
    query = "SELECT horario AS data, quantidade_estoque AS quant, id_produto FROM consumo ORDER BY ID ASC"
    df = pd.read_sql(query, con = engine)
    return df

def obter_config():
    engine = sqlalchemy.create_engine('mysql+pymysql://root:root@localhost:3306/supermercado')
    query = "SELECT intervalo_padrao, grafico_barras, previsao_home, estoque_minimo FROM configuracao WHERE ID = 1"
    df = pd.read_sql(query, con = engine)
    return df

def obterProdutos():
    engine = sqlalchemy.create_engine('mysql+pymysql://root:root@localhost:3306/supermercado')
    query = "SELECT ID AS id_produto, nome_produto, quant_max_prateleira FROM produto ORDER BY ID ASC"
    df = pd.read_sql(query, con = engine)
    return df

def obterVendas():
    engine = sqlalchemy.create_engine('mysql+pymysql://root:root@localhost:3306/supermercado')
    query = "SELECT A.ID AS id_produto, IFNULL(SUM(B.quantidade_comprada), 0) AS quant_total FROM produto AS A LEFT JOIN consumo AS B ON A.ID = B.id_produto GROUP BY A.ID ORDER BY A.ID ASC;"
    df_bar = pd.read_sql(query, con = engine)
    return df_bar

def historico(id_produto):
    engine = sqlalchemy.create_engine('mysql+pymysql://root:root@localhost:3306/supermercado')
    query = f"SELECT horario AS data, quantidade_comprada AS quant, id_produto FROM consumo WHERE id_produto = {id_produto} ORDER BY ID ASC"
    df = pd.read_sql(query, con = engine)
    return df

def historico_estoque(id_produto):
    engine = sqlalchemy.create_engine('mysql+pymysql://root:root@localhost:3306/supermercado')
    query = f"SELECT horario AS data, quantidade_estoque AS quant, id_produto FROM consumo WHERE id_produto = {id_produto} ORDER BY ID ASC"
    df = pd.read_sql(query, con = engine)
    return df

def historico_personalizado(id_produto):
    engine = sqlalchemy.create_engine('mysql+pymysql://root:root@localhost:3306/supermercado')
    query = f""" SELECT 
            data,
            quant,
            id_produto
        FROM (
            SELECT 
                horario AS data, 
                quantidade_estoque AS quant, 
                id_produto,
                ROW_NUMBER() OVER (PARTITION BY id_produto ORDER BY horario DESC) AS row_num
            FROM 
                consumo
            WHERE id_produto = {id_produto}
        ) subquery
        WHERE 
            row_num <= 1000
        ORDER BY 
            id_produto ASC, data ASC"""
    # query = f"SELECT horario AS data, quantidade_estoque AS quant, id_produto FROM consumo WHERE id_produto = {id_produto} AND ID > 53526 ORDER BY ID ASC LIMIT 990"
    # query = f"SELECT horario AS data, quantidade_estoque AS quant, id_produto FROM consumo WHERE id_produto = {id_produto} AND ID BETWEEN 68757 AND 69257 ORDER BY ID ASC"
    # query = f"SELECT horario AS data, quantidade_estoque AS quant, id_produto FROM consumo WHERE id_produto = {id_produto} AND ID BETWEEN 69553 AND 69586 ORDER BY ID ASC"
    df = pd.read_sql(query, con = engine)
    return df

def saveDB(quant, date, quant_estoque, id_produto):
    if quant_estoque == 0: quant_estoque = 1
    try:
        connection = mysql.connector.connect(host=host, user=user, password=password, database=database)
        
        cursor = connection.cursor()
        
        consulta = f"INSERT INTO consumo (horario, id_produto, quantidade_comprada, quantidade_estoque) VALUES ('{date}', {id_produto}, {quant}, {quant_estoque});"
        cursor.execute(consulta)
        
        connection.commit()
            
    except mysql.connector.Error as err:
        print("Erro na conexão: {}".format(err))
    finally:
        try:
            if connection:
                connection.close()
        except:
            pass

def saveConfig(intervalo_padrao, grafico_barras, previsao_home, estoque_minimo):
    try:
        connection = mysql.connector.connect(host=host, user=user, password=password, database=database)
        
        cursor = connection.cursor()
        
        query = f"UPDATE configuracao SET intervalo_padrao = {intervalo_padrao}, grafico_barras = {grafico_barras}, previsao_home = {previsao_home}, estoque_minimo = {estoque_minimo}"
        cursor.execute(query)
        
        connection.commit()
            
    except mysql.connector.Error as err:
        print("Erro na conexão: {}".format(err))
    finally:
        try:
            if connection:
                connection.close()
        except:
            pass

def criar_produto(nome):
    try:
        connection = mysql.connector.connect(host=host, user=user, password=password, database=database)
        
        cursor = connection.cursor()
        
        consulta = f"INSERT INTO produto (nome_produto) VALUES ('{nome}');"
        cursor.execute(consulta)
        
        connection.commit()
            
    except mysql.connector.Error as err:
        print("Erro na conexão: {}".format(err))
    finally:
        try:
            if connection:
                connection.close()
        except:
            pass
        
def get_options_from_db():
    try:
        connection = mysql.connector.connect(host=host, user=user, password=password, database=database)
        
        cursor = connection.cursor()
        
        cursor.execute("SELECT ID, nome_produto FROM produto ORDER BY nome_produto ASC")
        results = cursor.fetchall()

        cursor.close()
        connection.close()

        options = [{"label": row[1], "value": row[0]} for row in results]
        return options

    except Exception as e:
        print(f"Erro ao consultar o banco de dados: {e}")
        return []