import sqlite3

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

DB_PATH = BASE_DIR / "its.db"

def criar_tabela_questoes():
    # Conecta ao mesmo banco de dados do seu projeto
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Cria a tabela para armazenar as perguntas do laboratório
    cursor.execute("""
    DROP TABLE IF EXISTS laboratorio_questoes;
    """)
    
    cursor.execute("""
    CREATE TABLE laboratorio_questoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        conceito_id INTEGER NOT NULL, -- 1 para SELECT, 2 para WHERE, etc.
        enunciado TEXT NOT NULL,
        gabarito_sql TEXT NOT NULL
    );
    """)

    # As 10 questões exatas extraídas do seu documento (Conceito 1 = SELECT)
    questoes = [
        (1, "Escreva a consulta SQL para visualizar todas as informações (todas as colunas) da tabela historico_copas de uma só vez.", "SELECT * FROM historico_copas;"),
        (1, "Escreva a consulta SQL para exibir apenas o ano do torneio (coluna ano) e a seleção campeã (coluna campeao).", "SELECT ano, campeao FROM historico_copas;"),
        (1, "Escreva a consulta SQL para selecionar a coluna times_participantes, renomeando-a temporariamente na saída de exibição para Total_Selecoes.", "SELECT times_participantes AS Total_Selecoes FROM historico_copas;"),
        (1, "O comando SELECT permite realizar cálculos matemáticos. Escreva a consulta SQL que calcule a média de gols por jogo de cada copa (dividindo a coluna gols_totais pela coluna jogos_disputados).", "SELECT gols_totais / jogos_disputados FROM historico_copas;"),
        (1, "Escreva a consulta SQL para exibir a lista de continentes (coluna continente_sede) que já sediaram uma Copa, garantindo que não sejam exibidos valores repetidos na resposta.", "SELECT DISTINCT continente_sede FROM historico_copas;"),
        (1, "Escreva a consulta SQL para exibir uma string literal com o texto 'A sede foi: ' ao lado da coluna do país sede (pais_sede), para cada registro retornado da tabela.", "SELECT 'A sede foi: ', pais_sede FROM historico_copas;"),
        (1, "Escreva a consulta SQL estruturalmente correta selecionando as colunas campeão e vice da tabela historico_copas, respeitando a ordem obrigatória das cláusulas fundamentais de seleção e origem.", "SELECT campeao, vice FROM historico_copas;"),
        (1, "Sabendo que solicitar uma coluna inexistente gera erro fatal na query, escreva a consulta SQL correta e válida para selecionar o ano (ano) e o nome do artilheiro (artilheiro_nome) da tabela historico_copas.", "SELECT ano, artilheiro_nome FROM historico_copas;"),
        (1, "Corrija a seguinte instrução SQL, reescrevendo-a corretamente para remover o erro de sintaxe de pontuação (vírgula): SELECT ano, campeao, FROM historico_copas;", "SELECT ano, campeao FROM historico_copas;"),
        (1, "Em vários bancos de dados é possível usar o comando SELECT de modo independente. Escreva uma instrução SQL usando apenas o comando SELECT (sem a cláusula FROM) para calcular e exibir o resultado da equação matemática 100 * 2.", "SELECT 100 * 2;")
    ]

    # Insere as perguntas no banco
    cursor.executemany("""
        INSERT INTO laboratorio_questoes (conceito_id, enunciado, gabarito_sql) 
        VALUES (?, ?, ?);
    """, questoes)

    conn.commit()
    conn.close()
    print("Sucesso: Tabela 'laboratorio_questoes' criada e populada com os dados do PDF!")

if __name__ == "__main__":
    criar_tabela_questoes()