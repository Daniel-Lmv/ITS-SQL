import sqlite3
import random
import re
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

DB_PATH = BASE_DIR.parent / "database" / "its.db"

router = APIRouter(prefix="/laboratorio", tags=["Laboratório"])

# Modelos do Pydantic para os dados de entrada e saída
class RespostaLabSchema(BaseModel):
    questao_id: int
    query_usuario: str

class QuestaoLabResponse(BaseModel):
    id: int
    enunciado: str

# 1. ROTA PARA BUSCAR E SORTEAR 3 QUESTÕES ALEATÓRIAS
@router.get("/questoes/{conceito_id}")
def obter_questoes_laboratorio(conceito_id: int):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Procura todas as questões cadastradas para o conceito (Ex: 1 = SELECT)
        cursor.execute("""
            SELECT id, enunciado FROM laboratorio_questoes 
            WHERE conceito_id = ?;
        """, (conceito_id,))
        
        todas_questoes = cursor.fetchall()
        conn.close()
        
        if not todas_questoes:
            raise HTTPException(status_code=404, detail="Nenhuma questão encontrada para este conceito.")
            
        # Se houver menos de 3 questões, ajusta o limite para não quebrar o random.sample
        qtd_a_sortear = min(3, len(todas_questoes))
        
        # Sorteia aleatoriamente as questões sem repetição
        questoes_sorteadas = random.sample(todas_questoes, qtd_a_sortear)
        
        # Formata o retorno para o frontend
        return [{"id": q[0], "enunciado": q[1]} for q in questoes_sorteadas]
        
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Erro no banco de dados: {str(e)}")

# 2. ROTA PARA VALIDAR A QUERY SQL ENVIADA PELO ALUNO
@router.post("/verificar")
def verificar_resposta_laboratorio(dados: RespostaLabSchema):
    # Proteção simples contra comandos que alteram o banco de dados
    query_limpa = dados.query_usuario.strip().upper()
    if any(cmd in query_limpa for cmd in ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER"]):
        return {
            "correto": False,
            "mensagem": "Operação não permitida. Use apenas comandos de consulta (SELECT)."
        }
        
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Busca o gabarito oficial da questão selecionada
        cursor.execute("SELECT gabarito_sql FROM laboratorio_questoes WHERE id = ?;", (dados.questao_id,))
        questao = cursor.fetchone()
        
        if not questao:
            conn.close()
            raise HTTPException(status_code=404, detail="Questão não encontrada.")
            
        gabarito_sql = questao[0]
        
        # Executa a query oficial do gabarito para ver o resultado esperado
        cursor.execute(gabarito_sql)
        resultado_gabarito = cursor.fetchall()
        
        # Executa a query que o aluno escreveu
        cursor.execute(dados.query_usuario)
        resultado_usuario = cursor.fetchall()
        
        conn.close()
        
        # Compara as duas matrizes de resultados estruturais
        if resultado_gabarito == resultado_usuario:
            return {
                "correto": True,
                "mensagem": "Excelente! A sua consulta retornou exatamente os dados esperados pelo gabarito."
            }
        else:
            return {
                "correto": False,
                "mensagem": "A estrutura ou os dados retornados não correspondem ao objetivo do exercício. Verifique as colunas solicitadas."
            }
            
    except sqlite3.Error as e:
        # Se o aluno digitar algo com erro de sintaxe, captura o erro e envia de volta sem quebrar a API
        return {
            "correto": False,
            "mensagem": f"Erro de Sintaxe SQL: {str(e)}"
        }
    
@router.get("/referencia/copas")
def obter_tabela_referencia():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        # Busca toda a tabela de referência
        cursor.execute("SELECT * FROM historico_copas;")
        
        colunas = [description[0] for description in cursor.description]
        dados = [dict(zip(colunas, linha)) for linha in cursor.fetchall()]
        
        conn.close()
        return dados
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=str(e))