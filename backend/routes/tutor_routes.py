# backend/routes/tutor_routes.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.tutor_service import TutorService
from services.ia_service import ExplanationService # Ajustado o nome do arquivo se necessário
from typing import List, Dict

router = APIRouter(prefix="/tutor", tags=["Tutor Inteligente & Treino"])

class StartLessonRequest(BaseModel):
    user_id: int
    conceito_id: int

class VerifyAnswerRequest(BaseModel):
    user_id: int
    questao_id: int
    resposta_aluno: str

class ChatMessage(BaseModel):
    role: str # "user" ou "assistant"
    content: str

class ProfessorChatRequest(BaseModel):
    dados_questao: Dict[str, str] # enunciado, resposta_correta, resposta_aluno, conceito_nome
    historico_mensagens: List[ChatMessage]

@router.post("/lesson/start")
def iniciar_licao(data: StartLessonRequest):
    resultado = TutorService.gerar_licao(data.user_id, data.conceito_id)
    if resultado["status"] == "error":
        raise HTTPException(status_code=404, detail=resultado["message"])
    return resultado

@router.post("/lesson/verify")
def verificar_resposta(data: VerifyAnswerRequest):
    # Dica: dentro do seu TutorService.verificar_resposta_treino, quando o aluno errar,
    # você deve chamar o ExplanationService.gerar_feedback_worked_example para alimentar o retorno!
    resultado = TutorService.verificar_resposta_treino(data.user_id, data.questao_id, data.resposta_aluno)
    if resultado["status"] == "error":
        raise HTTPException(status_code=404, detail=resultado["message"])
    return resultado

@router.post("/chat/professor-virtual")
def conversar_tutor(data: ProfessorChatRequest):
    """
    Rota oficial do chat lateral contínuo com o Professor Virtual baseada em Skills.
    """
    historico_convertido = [{"role": msg.role, "content": msg.content} for msg in data.historico_mensagens]
    
    resposta_ia = ExplanationService.conversar_professor_virtual(data.dados_questao, historico_convertido)
    return {"status": "success", "response": resposta_ia}