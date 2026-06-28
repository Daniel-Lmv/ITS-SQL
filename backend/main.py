# backend/main.py
import sys
from pathlib import Path

# Garante que o Python enxergue a pasta backend para imports relativos funcionarem
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import auth_routes, diagnostic_routes, tutor_routes, laboratorio_routes

app = FastAPI(
    title="ITS-SQL API",
    description="Backend do Sistema de Tutoria Inteligente para Aprendizado de SQL com IA Local",
    version="1.0.0"
)

# Configuração do CORS - Essencial para conectar com o Frontend depois
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Permite requisições de qualquer origem (ideal para desenvolvimento)
    allow_credentials=True,
    allow_methods=["*"], # Permite todos os métodos (GET, POST, etc)
    allow_headers=["*"], # Permite todos os cabeçalhos HTTP
)

# Registrando as rotas no ecossistema do FastAPI
app.include_router(auth_routes.router)
app.include_router(diagnostic_routes.router)
app.include_router(tutor_routes.router)
app.include_router(laboratorio_routes.router)

@app.get("/")
def raiz():
    return {"status": "online", "message": "API do ITS-SQL rodando perfeitamente!"}

if __name__ == "__main__":
    import uvicorn
    # Inicializa o servidor local na porta 8000 com reload automático ao salvar arquivos
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)