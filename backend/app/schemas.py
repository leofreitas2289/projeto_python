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
    class Config:
        orm_mode = True

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    created_at: datetime
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class NlpEntidade(BaseModel):
    texto: str
    tipo_entidade: str

class NlpToken(BaseModel):
    palavra: str
    lema: str

class AgentSuggestion(BaseModel):
    tipo_sugestao: str
    descricao: str
    acao_recomendada: str

class NlpAnalysisResponse(BaseModel):
    entidades_nomeadas: List[NlpEntidade]
    tokens: List[NlpToken]
    sugestoes_do_agente: Optional[List[AgentSuggestion]] = None
    class Config:
        orm_mode = True


