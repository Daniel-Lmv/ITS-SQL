# backend/services/tutor_service.py
import sqlite3
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))
    
from services.proficiency_service import ProficiencyService

DB_PATH = Path(__file__).resolve().parent.parent / "database" / "its.db"

class TutorService:

    @staticmethod
    def get_connection():
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    @staticmethod
    def gerar_licao(user_id: int, conceito_id: int):
        """
        Gera um bloco fixo de 10 questões mistas para o tópico selecionado.
        Padrão ideal: 4 fáceis (1), 3 médias (2) e 3 difíceis (3).
        """
        conn = TutorService.get_connection()
        cursor = conn.cursor()

        # 1. Tenta buscar o mix balanceado de dificuldades (trazendo resposta_correta)
        mix_config = [(1, 4), (2, 3), (3, 3)] # (dificuldade, quantidade)
        questoes_sorteadas = []

        for diff, qtd in mix_config:
            cursor.execute("""
                SELECT id, conceito_id, enunciado, alternativa_a, alternativa_b, alternativa_c, alternativa_d, resposta_correta, dificuldade
                FROM questoes
                WHERE conceito_id = ? AND dificuldade = ?
                ORDER BY RANDOM()
                LIMIT ?
            """, (conceito_id, diff, qtd))
            questoes_sorteadas.extend([dict(row) for row in cursor.fetchall()])

        # 2. Fallback: Se o mix não completou 10 questões
        if len(questoes_sorteadas) < 10:
            ids_ja_escolhidos = [q["id"] for q in questoes_sorteadas]
            falta = 10 - len(questoes_sorteadas)
            
            placeholders = ",".join("?" for _ in ids_ja_escolhidos)
            query_fallback = f"""
                SELECT id, conceito_id, enunciado, alternativa_a, alternativa_b, alternativa_c, alternativa_d, resposta_correta, dificuldade
                FROM questoes
                WHERE conceito_id = ?
                {"AND id NOT IN (" + placeholders + ")" if ids_ja_escolhidos else ""}
                ORDER BY RANDOM()
                LIMIT ?
            """
            params = [conceito_id] + ids_ja_escolhidos + [falta]
            cursor.execute(query_fallback, params)
            questoes_sorteadas.extend([dict(row) for row in cursor.fetchall()])

        # 3. Busca o nome do conceito para personificar o Header da página
        cursor.execute("SELECT nome FROM conceitos WHERE id = ?", (conceito_id,))
        conceito_row = cursor.fetchone()
        conceito_nome = conceito_row["nome"] if conceito_row else "Exercícios de SQL"

        conn.close()

        if not questoes_sorteadas:
            return {
                "status": "error",
                "message": "Nenhuma questão encontrada para este conceito."
            }

        return {
            "status": "success",
            "conceito_id": conceito_id,
            "conceito_nome": conceito_nome,
            "total_questoes": len(questoes_sorteadas),
            "questoes": questoes_sorteadas 
        }

    @staticmethod
    def verificar_resposta_treino(user_id: int, questao_id: int, resposta_aluno: str):
        """
        Verifica a resposta enviada pelo aluno, atualiza a proficiência
        e retorna se ele acertou ou errou (sinalizando a necessidade de IA).
        """
        conn = TutorService.get_connection()
        cursor = conn.cursor()

        # Busca o gabarito e o conceito da questão
        cursor.execute("""
            SELECT conceito_id, resposta_correta, enunciado
            FROM questoes
            WHERE id = ?
        """, (questao_id,))
        questao = cursor.fetchone()
        conn.close()

        if questao is None:
            return {"status": "error", "message": "Questão não encontrada."}

        conceito_id = questao["conceito_id"]
        resposta_correta = questao["resposta_correta"].strip().upper()
        resposta_aluno_formatada = resposta_aluno.strip().upper()

        acertou = (resposta_aluno_formatada == resposta_correta)

        # Atualiza a nota do aluno usando a sua regra de negócio (+10 ou -5)
        # Passamos também o conceito_id para atualizar a proficiência certa
        novo_nivel = ProficiencyService.update_proficiency(
            user_id=user_id,
            concept_id=conceito_id,
            correct=acertou
        )

        return {
            "status": "success",
            "acertou": acertou,
            "resposta_correta": resposta_correta, # O frontend usará para mostrar a certa caso ele mude de questão
            "novo_nivel_conceito": novo_nivel,
            "sugerir_ajuda_ia": not acertou, # Se errou, ativa o popup de ajuda socrática
            "dados_questao": {
                "enunciado": questao["enunciado"],
                "resposta_aluno": resposta_aluno_formatada,
                "resposta_correta": resposta_correta
            }
        }