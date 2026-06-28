# backend/services/diagnostic_service.py
import sqlite3
from pathlib import Path
from services.proficiency_service import ProficiencyService

DB_PATH = Path(__file__).resolve().parent.parent / "database" / "its.db"

class DiagnosticService:

    @staticmethod
    def get_connection():
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    @staticmethod
    def obter_questoes_diagnostico():
        """
        Retorna todas as questões da tabela 'questoes_diagnostico' ordenadas.
        """
        conn = ProficiencyService.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, ordem, conceito_id, enunciado, 
                   alternativa_a, alternativa_b, alternativa_c, alternativa_d,
                   dificuldade
            FROM questoes_diagnostico 
            ORDER BY ordem ASC
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        questoes = []
        for row in rows:
            questoes.append({
                "id": row["id"],
                "ordem": row["ordem"],
                "conceito_id": row["conceito_id"],
                "enunciado": row["enunciado"],
                "alternativas": {
                    "A": row["alternativa_a"],
                    "B": row["alternativa_b"],
                    "C": row["alternativa_c"],
                    "D": row["alternativa_d"]
                },
                "dificuldade": row["dificuldade"]
            })
            
        return questoes
    
    @staticmethod
    def processar_respostas_diagnostico(user_id: int, answers: dict):
        """
        Recebe as respostas do aluno no formato de dicionário:
        answers = { "1": "A", "2": "C", ... }
        
        Calcula a proficiência inicial por conceito de forma híbrida/multitópico,
        aplicando travas de dependência hierárquica e teto de nivelamento.
        """
        conn = DiagnosticService.get_connection()
        cursor = conn.cursor()

        # Puxa o gabarito estruturado
        cursor.execute("""
            SELECT id, conceito_id, resposta_correta 
            FROM questoes_diagnostico
        """)
        questions_gabarito = cursor.fetchall()
        conn.close()

        # MATRIZ DE CORRELAÇÃO: Mapeia cada Questão ID aos conceitos que ela impacta
        MATRIZ_CONCEITOS = {
            1: [1],          # Q1 (SELECT/WHERE) afeta Conceito 1
            2: [1, 2],       # Q2 (BETWEEN/NULL) afeta Conceito 1 e 2
            3: [1, 3, 4],    # Q3 (Agregação/Ordenação) afeta Conceito 1, 3 e 4
            4: [1, 6],       # Q4 (INNER JOIN) afeta Conceito 1 e 6
            5: [1, 3, 4, 5], # Q5 (HAVING) afeta Conceito 1, 3, 4 e 5
            6: [1, 6, 7],    # Q6 (LEFT JOIN) afeta Conceito 1, 6 e 7
            7: [1, 8],       # Q7 (Subqueries) afeta Conceito 1 e 8
            8: [1, 2]        # Q8 (DISTINCT/LIMIT) afeta Conceito 1 e 2
        }

        # REGRAS DO GRAFO (Pré-requisitos): Mapeia qual conceito depende de qual
        # Formato: conceito_id: conceito_pai_id
        PRE_REQUISITOS = {
            2: 1,  # WHERE depende de SELECT
            3: 1,  # ORDER BY depende de SELECT
            4: 1,  # AGREGAÇÕES depende de SELECT
            5: 4,  # HAVING depende de AGREGAÇÕES (Conceito 4)
            6: 2,  # INNER JOIN depende de WHERE (Conceito 2)
            7: 6,  # LEFT JOIN depende de INNER JOIN (Conceito 6)
            8: 6   # SUBQUERIES depende de INNER JOIN (Conceito 6)
        }

        TETO_DIAGNOSTICO = 75.0  # Nenhum aluno sai do diagnóstico com mais de 75%

        # Inicializa os contadores para TODOS os 8 conceitos do sistema
        concept_stats = {i: {"correct": 0, "total": 0} for i in range(1, 9)}

        for question in questions_gabarito:
            question_id = question["id"]
            correct_answer = question["resposta_correta"]

            conceitos_afetados = MATRIZ_CONCEITOS.get(question_id, [question["conceito_id"]])
            student_answer = answers.get(str(question_id)) or answers.get(question_id)

            if student_answer is not None:
                is_correct = student_answer.strip().upper() == correct_answer.strip().upper()
                
                for c_id in conceitos_afetados:
                    concept_stats[c_id]["total"] += 1
                    if is_correct:
                        concept_stats[c_id]["correct"] += 1

        # 1º Passo: Calcular as proficiências brutas limitadas ao TETO
        proficiency = {}
        for concept_id, stats in concept_stats.items():
            total = stats["total"]
            if total == 0:
                proficiency[concept_id] = 0.0
                continue

            score = (stats["correct"] / total) * 100
            # Aplica o teto para garantir que ninguém domine o assunto de primeira
            proficiency[concept_id] = min(round(score, 2), TETO_DIAGNOSTICO)

        # 2º Passo: Cascata de Dependência (Ancoragem por Pré-requisito)
        # Passamos pelos conceitos de forma ordenada para que as travas se propaguem corretamente
        for concept_id in range(1, 9):
            pai_id = PRE_REQUISITOS.get(concept_id)
            if pai_id in proficiency:
                # A nota do filho não pode ser maior que a nota do pai
                nota_pai = proficiency[pai_id]
                if proficiency[concept_id] > nota_pai:
                    proficiency[concept_id] = nota_pai

        # Invoca o salvamento
        ProficiencyService.save_initial_proficiency(user_id, proficiency)

        return {
            "status": "success",
            "message": "Diagnóstico adaptativo processado com sucesso aplicando regras de Grafo!",
            "proficiencia_calculada": proficiency
        }