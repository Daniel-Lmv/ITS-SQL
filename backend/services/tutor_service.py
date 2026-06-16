import sqlite3
from pathlib import Path
from backend.services.proficiency_service import ProficiencyService

DB_PATH = Path(__file__).resolve().parent.parent / "database" / "its.db"


class TutorService:

    @staticmethod
    def get_connection():
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    @staticmethod
    def get_next_question(user_id):
        """
        Analisa o nível atual do aluno no seu conceito mais fraco
        e seleciona a próxima questão ideal baseada na dificuldade.
        """
        # 1. Identifica o conceito onde o aluno tem a menor nota
        weakest = ProficiencyService.get_weakest_concept(user_id)

        # Fallback caso o aluno não tenha nenhuma proficiência no banco (ex: pulou o diagnóstico)
        if weakest is None:
            concept_id = 1
            concept_name = "SELECT"
            target_difficulty = 1  # Começa pelo fácil
        else:
            concept_id = weakest["id"]
            concept_name = weakest["nome"]
            user_level = weakest["nivel"]

            # 2. Define a dificuldade da questão com base na régua de proficiência (0 a 100)
            if user_level <= 33.33:
                target_difficulty = 1  # Nível Baixo -> Questão Fácil
            elif user_level <= 66.66:
                target_difficulty = 2  # Nível Médio -> Questão Média
            else:
                target_difficulty = 3  # Nível Alto -> Questão Difícil

        conn = TutorService.get_connection()
        cursor = conn.cursor()

        # 3. Busca uma questão que pertença a esse conceito e dificuldade
        # Usamos ORDER BY RANDOM() para que, se houver mais de uma, varie a pergunta
        cursor.execute("""
                       SELECT id,
                              conceito_id,
                              enunciado,
                              alternativa_a,
                              alternativa_b,
                              alternativa_c,
                              alternativa_d,
                              dificuldade
                       FROM questoes
                       WHERE conceito_id = ?
                         AND dificuldade = ?
                       ORDER BY RANDOM()
                       LIMIT 1
                       """, (concept_id, target_difficulty))

        question_row = cursor.fetchone()

        # 4. Fallback Pedagógico: Se o banco não tiver nenhuma questão cadastrada
        # especificamente para aquela dificuldade daquele conceito, o tutor busca
        # qualquer dificuldade disponível daquele mesmo assunto para não travar o fluxo.
        if question_row is None:
            cursor.execute("""
                           SELECT id,
                                  conceito_id,
                                  enunciado,
                                  alternativa_a,
                                  alternativa_b,
                                  alternativa_c,
                                  alternativa_d,
                                  dificuldade
                           FROM questoes
                           WHERE conceito_id = ?
                           ORDER BY RANDOM()
                           LIMIT 1
                           """, (concept_id,))
            question_row = cursor.fetchone()

        conn.close()

        # Se o banco de dados estiver totalmente sem questões para esse conceito
        if question_row is None:
            return {
                "status": "error",
                "message": f"Nenhuma questão encontrada para o conceito {concept_name}."
            }

        return {
            "status": "success",
            "concept_name": concept_name,
            "user_current_level": weakest["nivel"] if weakest else 0,
            "question": {
                "id": question_row["id"],
                "conceito_id": question_row["conceito_id"],
                "enunciado": question_row["enunciado"],
                "alternativa_a": question_row["alternativa_a"],
                "alternativa_b": question_row["alternativa_b"],
                "alternativa_c": question_row["alternativa_c"],
                "alternativa_d": question_row["alternativa_d"],
                "dificuldade": question_row["dificuldade"]
            }
        }