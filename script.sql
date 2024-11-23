CREATE DATABASE supermercado;

USE supermercado;

CREATE TABLE consumo (ID INT AUTO_INCREMENT,
									horario DATETIME NOT NULL,
                                    id_produto INT NOT NULL,
									quantidade_comprada INT NOT NULL,
                                    quantidade_estoque INT NOT NULL,
                                    PRIMARY KEY (ID),
                                    FOREIGN KEY (id_produto) REFERENCES produto (ID));
                                    
CREATE TABLE produto (ID INT AUTO_INCREMENT,
						nome_produto VARCHAR(50) NOT NULL,
                        quant_max_prateleira INT NOT NULL,
						PRIMARY KEY (ID));
                        
CREATE TABLE configuracao (ID INT AUTO_INCREMENT,
						intervalo_padrao INT NULL,
						grafico_barras BOOLEAN NOT NULL DEFAULT TRUE,
                        previsao_home BOOLEAN NOT NULL DEFAULT TRUE,
                        estoque_minimo FLOAT NULL,
						PRIMARY KEY (ID));
                        
INSERT INTO configuracao (intervalo_padrao, estoque_minimo) VALUES (30, 30);

SELECT * FROM configuracao;
                                    
DROP TABLE produto;

RENAME TABLE produtos TO produto;
RENAME TABLE consumo_produtos TO consumo;
                                    
SELECT nome_produto FROM produto;

SELECT * FROM produto;

SELECT * FROM consumo ORDER BY ID DESC LIMIT 9999999;
SELECT * FROM consumo WHERE id_produto = 18;

SELECT id_produto, horario, quantidade_estoque FROM consumo ORDER BY id_produto, ID ASC;

UPDATE produto SET nome_produto = "Suco" WHERE ID = 3;

SELECT * FROM produto;

INSERT INTO consumo (horario, quantidade_comprada, quantidade_estoque) VALUES ("2024-09-11 21:29:48.109890", 2, 998);

INSERT INTO produto (nome_produto, quant_max_prateleira) VALUES ("Café", 500);
INSERT INTO produto (nome_produto, quant_max_prateleira) VALUES ("Suco", 1000);
INSERT INTO produto (nome_produto, quant_max_prateleira) VALUES ("Leite", 2000);
INSERT INTO produto (nome_produto, quant_max_prateleira) VALUES ("Energético", 300);

DELETE FROM consumo WHERE ID>=1;

SELECT id_produto,
		SUM(quantidade_comprada) AS quant_total
FROM consumo
GROUP BY id_produto
ORDER BY id_produto ASC;

SELECT A.ID AS id_produto, IFNULL(SUM(B.quantidade_comprada), 0) AS quant_total FROM produto AS A LEFT JOIN consumo AS B ON A.ID = B.id_produto GROUP BY A.ID ORDER BY A.ID ASC;

SELECT A.ID, IFNULL(SUM(B.quantidade_comprada), 0) AS quant_total FROM produto AS A LEFT JOIN consumo AS B ON A.ID = B.id_produto GROUP BY A.ID ORDER BY A.ID ASC;

SELECT * FROM consumo WHERE id_produto = 1 LIMIT 0, 999999;

SELECT 39495 - 39653;

SELECT * FROM consumo WHERE id_produto = 1 AND ID >= (SELECT MIN(LIMITE.ID) FROM (SELECT ID FROM consumo WHERE id_produto = 1 AND quantidade_estoque = 1 ORDER BY ID DESC LIMIT 5) AS LIMITE) ORDER BY ID DESC;

SELECT ID FROM consumo WHERE id_produto = 1 AND quantidade_estoque = 1 ORDER BY ID DESC LIMIT 5;

SELECT MIN(LIMITE.ID) FROM (SELECT ID FROM consumo WHERE id_produto = 1 AND quantidade_estoque = 1 ORDER BY ID DESC LIMIT 5) AS LIMITE;

SELECT 69706 - 69553;

SELECT 68757 - 68928;
SELECT 68928 - 69090;
SELECT 69090 - 69257;

48834  47993;

69586 69553;

SELECT ID, horario AS data, quantidade_estoque AS quant, id_produto FROM consumo WHERE id_produto = 1 AND ID BETWEEN 68757 AND 69257 ORDER BY ID ASC;

SELECT ID FROM consumo WHERE id_produto = 1 AND quantidade_estoque = 0 ORDER BY ID DESC LIMIT 5;

SELECT 
    ID AS atual,
    LAG(quantidade_estoque, 1, NULL) OVER (ORDER BY ID DESC) AS anterior,
    quantidade_estoque - LAG(quantidade_estoque, 1, NULL) OVER (ORDER BY ID DESC) AS diferenca
FROM 
    consumo
ORDER BY 
    ID DESC
LIMIT 5;
WITH CTE AS
(
SELECT ID, ID - LAG(ID) OVER (ORDER BY ID DESC) AS DIFF FROM consumo WHERE id_produto = 1 AND quantidade_estoque = 0 ORDER BY ID DESC LIMIT 9999
)
SELECT AVG(DIFF) FROM CTE;

SELECT * FROM consumo WHERE id_produto = 1 ORDER BY ID DESC LIMIT 990;

SELECT horario AS data, quantidade_estoque AS quant, id_produto FROM consumo WHERE id_produto = 1 AND ID > 53526 ORDER BY ID ASC LIMIT 990;

SELECT 
  sales_employee, 
  fiscal_year, 
  sale, 
  LAG(sale, 1 , 0) OVER (
    PARTITION BY sales_employee 
    ORDER BY fiscal_year
  ) 'previous year sale' 
FROM 
  sales;
  
SELECT 
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
) subquery
WHERE 
    row_num <= 1000
ORDER BY 
    id_produto ASC, data ASC;

WITH CTE AS(
SELECT 
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
	WHERE id_produto = 1
) subquery
WHERE 
	row_num <= 1000
ORDER BY 
	id_produto ASC, data ASC)
SELECT 	data,
		quant,
		id_produto,
        LAG(quant) OVER (ORDER BY data) AS quantidade_anterior
FROM CTE 
ORDER BY data DESC LIMIT 1;
    
WITH CTE AS(
SELECT
	ID,
	data,
	quant,
	id_produto,
    LAG(quant) OVER (ORDER BY data) AS quantidade_anterior
FROM (
	SELECT
		ID,
		horario AS data, 
		quantidade_estoque AS quant, 
		id_produto,
		ROW_NUMBER() OVER (PARTITION BY id_produto ORDER BY horario DESC) AS row_num
	FROM 
		consumo
	WHERE id_produto = 1
) subquery
WHERE 
	row_num <= 1000
ORDER BY 
	id_produto ASC, data ASC)
SELECT 	ID,
		data,
		quant,
		id_produto,
        quantidade_anterior
FROM CTE
WHERE quantidade_anterior = 0
ORDER BY data DESC LIMIT 1;

SELECT ID, quantidade_comprada FROM consumo WHERE id_produto = 1 ORDER BY ID DESC LIMIT 9999999;

SELECT 
    ID,
    SUM(quantidade_comprada) OVER (ORDER BY ID ) AS quantidade_vendida
FROM (SELECT ID, quantidade_comprada FROM consumo WHERE id_produto = 1 ORDER BY ID DESC LIMIT 990) A
ORDER BY ID DESC LIMIT 990;


SELECT 
    data,
    quantidade_estoque,
    SUM(quantidade_comprada) OVER (ORDER BY ID ) AS quant,
    id_produto
FROM (SELECT ID, horario AS data, quantidade_comprada, id_produto, quantidade_estoque FROM consumo WHERE id_produto = 1 ORDER BY ID DESC LIMIT 1000) A
ORDER BY ID DESC LIMIT 1000;