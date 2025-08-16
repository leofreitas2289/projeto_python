# backend/app/schemas.py
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List

class ProcessBase(BaseModel):
    title: str
    description: Optional[str] = None

class ProcessCreate(ProcessBase):
    pass

class Process(ProcessBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime
    # Adicione esta classe Config aninhada
    class Config:
        orm_mode = True # <-- USE ESTA SINTAXE ANTIGA

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    created_at: datetime
    # Adicione esta classe Config aninhada
    class Config:
         orm_mode = True # <-- USE ESTA SINTAXE ANTIGA

    # backend/app/schemas.py

# ... (schemas existentes de User e Process) ...

# --- NOVOS ESQUEMAS PARA AUTENTICAÇÃO ---

class Token(BaseModel):
    """Esquema para a resposta do token."""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """Esquema para os dados contidos dentro do token."""
    username: Optional[str] = None

# backend/app/schemas.py

# ... (schemas existentes de User, Process, Token, etc.) ...

# --- NOVOS ESQUEMAS PARA A ANÁLISE DE NLP ---

class NlpEntidade(BaseModel):
    """Esquema para uma única entidade nomeada."""
    texto: str
    tipo_entidade: str

class NlpToken(BaseModel):
    """Esquema para um único token/lema."""
    palavra: str
    lema: str
    # --- NOVO ESQUEMA PARA AS SUGESTÕES DO AGENTE ---
class AgentSuggestion(BaseModel):
    """Esquema para uma única sugestão do agente."""
    tipo_sugestao: str
    descricao: str
    acao_recomendada: str

class NlpAnalysisResponse(BaseModel):
    """Esquema para a resposta completa da análise."""
    entidades_nomeadas: List[NlpEntidade]
    tokens: List[NlpToken]
    # A correção está aqui:
    sugestoes_do_agente: Optional[List[AgentSuggestion]] = None

    # Adicione a configuração de compatibilidade aqui também, por segurança.
    class Config:
        orm_mode = True


