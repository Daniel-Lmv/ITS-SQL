import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

DB_PATH = BASE_DIR / "its.db"

def inicializar_banco_copas():
    # Conecta ao arquivo de banco de dados do seu projeto
    # Altere o caminho se o seu arquivo 'its.db' estiver em outra pasta
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("Otimizando e criando a tabela 'historico_copas' no SQLite...")

    # 1. Criação da Tabela com tipos adequados para o SQLite
    cursor.execute("""
    DROP TABLE IF EXISTS historico_copas;
    """)
    
    cursor.execute("""
    CREATE TABLE historico_copas (
        ano INTEGER PRIMARY KEY,
        pais_sede TEXT NOT NULL,
        continente_sede TEXT,
        campeao TEXT NOT NULL,
        vice TEXT NOT NULL,
        terceiro_lugar TEXT,
        quarto_lugar TEXT,
        times_participantes INTEGER NOT NULL,
        jogos_disputados INTEGER NOT NULL,
        publico_total INTEGER, 
        gols_totais INTEGER NOT NULL,
        cartoes_amarelos INTEGER,
        cartoes_vermelhos INTEGER,
        artilheiro_nome TEXT,
        gols_artilheiro INTEGER,
        bola_de_ouro TEXT,
        luva_de_ouro TEXT,
        jovem_revelacao TEXT
    );
    """)

    # 2. Dados estruturados prontos para inserção massiva (executemany)
    dados_copas = [
        (1930, 'Uruguai', 'América do Sul', 'Uruguai', 'Argentina', 'Estados Unidos', 'Iugoslávia', 13, 18, 434500, 70, None, 1, 'Guillermo Stábile', 8, None, None, None),
        (1934, 'Itália', 'Europa', 'Itália', 'Tchecoslováquia', 'Alemanha', 'Áustria', 16, 17, 363000, 70, None, 1, 'Oldřich Nejedlý', 5, None, None, None),
        (1938, 'França', 'Europa', 'Itália', 'Hungria', 'Brasil', 'Suécia', 15, 18, 375700, 84, None, 4, 'Leônidas', 7, None, None, None),
        (1950, 'Brasil', 'América do Sul', 'Uruguai', 'Brasil', 'Suécia', 'Espanha', 13, 22, 1045246, 88, None, 0, 'Ademir', 9, None, None, None),
        (1954, 'Suíça', 'Europa', 'Alemanha Ocidental', 'Hungria', 'Áustria', 'Uruguai', 16, 26, 768600, 140, None, 3, 'Sándor Kocsis', 11, None, None, None),
        (1958, 'Suécia', 'Europa', 'Brasil', 'Suécia', 'França', 'Alemanha Ocidental', 16, 35, 819810, 126, None, 3, 'Just Fontaine', 13, None, None, 'Pelé'),
        (1962, 'Chile', 'América do Sul', 'Brasil', 'Tchecoslováquia', 'Chile', 'Iugoslávia', 16, 32, 893172, 89, None, 6, 'Garrincha, Vavá, Leonel Sánchez, Flórián Albert, Valentin Ivanov, Dražan Jerković', 4, None, None, 'Flórián Albert'),
        (1966, 'Inglaterra', 'Europa', 'Inglaterra', 'Alemanha Ocidental', 'Portugal', 'União Soviética', 16, 32, 1563135, 89, None, 5, 'Eusébio', 9, None, None, 'Franz Beckenbauer'),
        (1970, 'México', 'América do Norte', 'Brasil', 'Itália', 'Alemanha Ocidental', 'Uruguai', 16, 32, 1603975, 95, 52, 0, 'Gerd Müller', 10, None, None, 'Teófilo Cubillas'),
        (1974, 'Alemanha Ocidental', 'Europa', 'Alemanha Ocidental', 'Holanda', 'Polônia', 'Brasil', 16, 38, 1865753, 97, 86, 5, 'Grzegorz Lato', 7, None, None, 'Władysław Żmuda'),
        (1978, 'Argentina', 'América do Sul', 'Argentina', 'Holanda', 'Brasil', 'Itália', 16, 38, 1545791, 102, 59, 3, 'Mario Kempes', 6, 'Mario Kempes', None, 'Antonio Cabrini'),
        (1982, 'Espanha', 'Europa', 'Itália', 'Alemanha Ocidental', 'Polônia', 'França', 24, 52, 2109723, 146, 98, 5, 'Paolo Rossi', 6, 'Paolo Rossi', None, 'Manuel Amoros'),
        (1986, 'México', 'América do Norte', 'Argentina', 'Alemanha Ocidental', 'França', 'Bélgica', 24, 52, 2394031, 132, 137, 8, 'Gary Lineker', 6, 'Diego Maradona', None, 'Enzo Scifo'),
        (1990, 'Itália', 'Europa', 'Alemanha Ocidental', 'Argentina', 'Itália', 'Inglaterra', 24, 52, 2516215, 115, 193, 16, 'Salvatore Schillaci', 6, 'Salvatore Schillaci', None, 'Robert Prosinečki'),
        (1994, 'Estados Unidos', 'América do Norte', 'Brasil', 'Itália', 'Suécia', 'Bulgária', 24, 52, 3587538, 141, 235, 15, 'Oleg Salenko, Hristo Stoichkov', 6, 'Romário', "Michel Preud'homme", 'Marc Overmars'),
        (1998, 'França', 'Europa', 'França', 'Brasil', 'Croácia', 'Holanda', 32, 64, 2785100, 171, 258, 22, 'Davor Šuker', 6, 'Ronaldo', 'Fabien Barthez', 'Michael Owen'),
        (2002, 'Coreia do Sul / Japão', 'Ásia', 'Brasil', 'Alemanha', 'Turquia', 'Coreia do Sul', 32, 64, 2705197, 161, 272, 17, 'Ronaldo', 8, 'Oliver Kahn', 'Oliver Kahn', 'Landon Donovan'),
        (2006, 'Alemanha', 'Europa', 'Itália', 'França', 'Alemanha', 'Portugal', 32, 64, 3359439, 147, 345, 28, 'Miroslav Klose', 5, 'Zinedine Zidane', 'Gianluigi Buffon', 'Lukas Podolski'),
        (2010, 'África do Sul', 'África', 'Espanha', 'Holanda', 'Alemanha', 'Uruguai', 32, 64, 3178856, 145, 261, 17, 'Thomas Müller', 5, 'Diego Forlán', 'Iker Casillas', 'Thomas Müller'),
        (2014, 'Brasil', 'América do Sul', 'Alemanha', 'Argentina', 'Holanda', 'Brasil', 32, 64, 3429873, 171, 187, 10, 'James Rodríguez', 6, 'Lionel Messi', 'Manuel Neuer', 'Paul Pogba'),
        (2018, 'Rússia', 'Europa', 'França', 'Croácia', 'Bélgica', 'Inglaterra', 32, 64, 3031768, 169, 219, 4, 'Harry Kane', 6, 'Luka Modrić', 'Thibaut Courtois', 'Kylian Mbappé'),
        (2022, 'Catar', 'Ásia', 'Argentina', 'França', 'Croácia', 'Marrocos', 32, 64, 3404252, 172, 227, 4, 'Kylian Mbappé', 8, 'Lionel Messi', 'Emiliano Martínez', 'Enzo Fernández')
    ]

    # 3. Query parametrizada segura contra SQL Injection e problemas de caracteres
    query_insercao = """
    INSERT INTO historico_copas (
        ano, pais_sede, continente_sede, campeao, vice, terceiro_lugar, quarto_lugar, 
        times_participantes, jogos_disputados, publico_total, gols_totais, 
        cartoes_amarelos, cartoes_vermelhos, artilheiro_nome, gols_artilheiro, 
        bola_de_ouro, luva_de_ouro, jovem_revelacao
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """

    # Executa a inserção em lote de todas as linhas de uma vez
    cursor.executemany(query_insercao, dados_copas)
    
    # Salva as alterações no arquivo de forma permanente
    conn.commit()
    
    # Validação rápida no console
    cursor.execute("SELECT COUNT(*) FROM historico_copas;")
    total_linhas = cursor.fetchone()[0]
    
    conn.close()
    print(f"Sucesso! Tabela criada e {total_linhas} edições inseridas com segurança no SQLite.")

if __name__ == "__main__":
    inicializar_banco_copas()