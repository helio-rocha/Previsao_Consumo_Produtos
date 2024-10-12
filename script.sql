CREATE DATABASE supermercado;

USE supermercado;

CREATE TABLE consumo_produtos (ID INT AUTO_INCREMENT,
									horario DATETIME NOT NULL,
                                    id_produto INT NOT NULL,
									quantidade_comprada INT NOT NULL,
                                    quantidade_estoque INT NOT NULL,
                                    PRIMARY KEY (ID),
                                    FOREIGN KEY (id_produto) REFERENCES produtos (ID));
                                    
CREATE TABLE produtos (ID INT AUTO_INCREMENT,
						nome_produto VARCHAR(50) NOT NULL,
						PRIMARY KEY (ID));
                                    
DROP TABLE consumo_produtos;
                                    
SELECT nome_produto FROM produtos;

SELECT * FROM produtos;

SELECT * FROM consumo_produtos;
SELECT * FROM consumo_produtos WHERE id_produto = 18;

SELECT id_produto, horario, quantidade_estoque FROM consumo_produtos ORDER BY id_produto, ID ASC;

UPDATE produtos SET nome_produto = "Suco" WHERE ID = 3;



SELECT * FROM produtos;

INSERT INTO consumo_produtos (horario, quantidade_comprada, quantidade_estoque) VALUES ("2024-09-11 21:29:48.109890", 2, 998);

INSERT INTO produtos (nome_produto) VALUES ("Camarão");
INSERT INTO produtos (nome_produto) VALUES ("Energético");
INSERT INTO produtos (nome_produto) VALUES ("Picanha");
INSERT INTO produtos (nome_produto) VALUES ("Suco");

DELETE FROM consumo_produtos WHERE ID>=1


