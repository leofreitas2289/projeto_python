from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm

from . import models, schemas, auth, nlp, agent
from .database import engine, get_db
from .base import Base

# Cria as tabelas no banco de dados (para desenvolvimento)
Base.metadata.create_all(bind=engine)

app = FastAPI()

# --- Funções de CRUD (Lógica de Banco de Dados) ---

def get_user_by_username(db: Session, username: str):
    """Busca um usuário pelo seu nome de usuário."""
    return db.query(models.User).filter(models.User.username == username).first()

def create_db_user(db: Session, user: schemas.UserCreate):
    """Cria um novo usuário no banco de dados."""
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(
        username=user.username, 
        email=user.email, 
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# --- Rotas de Usuário ---

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Verifica se a API está funcionando."""
    return {"status": "ok", "message": "API is healthy"}

@app.post("/users/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Cria um novo usuário.
    """
    db_user = get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    return create_db_user(db=db, user=user)

@app.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retorna uma lista de usuários.
    """
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users

@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    """
    Retorna um usuário específico pelo seu ID.
    """
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# --- Rota de Login (Autenticação) ---

@app.post("/token", response_model=schemas.Token)
def login_for_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Recebe username e password, verifica as credenciais e retorna um token de acesso.
    """
    user = get_user_by_username(db, username=form_data.username)
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me/", response_model=schemas.User)
def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
    """
    Retorna os dados do usuário atualmente autenticado.
    """
    return current_user

# --- Rotas de Processos ---

@app.post("/processes/", response_model=schemas.Process, status_code=status.HTTP_201_CREATED)
def create_process(
    process: schemas.ProcessCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Cria um novo processo para o usuário autenticado.
    """
    db_process = models.Process(**process.model_dump(), owner_id=current_user.id)
    db.add(db_process)
    db.commit()
    db.refresh(db_process)
    return db_process
   
@app.get("/processes/", response_model=List[schemas.Process])
def read_processes(
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Retorna uma lista de processos pertencentes ao usuário atualmente autenticado.
    """
    return current_user.processes

@app.put("/processes/{process_id}", response_model=schemas.Process)
def update_process(
    process_id: int,
    process_update: schemas.ProcessCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Atualiza um processo existente pertencente ao usuário autenticado.
    """
    db_process = db.query(models.Process).filter(models.Process.id == process_id).first()
    if db_process is None:
        raise HTTPException(status_code=404, detail="Process not found")

    if db_process.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this process")

    db_process.title = process_update.title
    db_process.description = process_update.description
    
    db.commit()
    db.refresh(db_process)
    
    return db_process

@app.delete("/processes/{process_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_process(
    process_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Deleta um processo existente pertencente ao usuário autenticado.
    """
    db_process = db.query(models.Process).filter(models.Process.id == process_id).first()

    if db_process is None:
        raise HTTPException(status_code=404, detail="Process not found")

    if db_process.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this process")

    db.delete(db_process)
    db.commit()
    
    return

@app.post("/processes/{process_id}/analyze", response_model=schemas.NlpAnalysisResponse)
def analyze_process_description(
    process_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Executa uma análise de NLP na descrição de um processo existente
    pertencente ao usuário autenticado.
    """
    db_process = db.query(models.Process).filter(models.Process.id == process_id).first()

    if db_process is None:
        raise HTTPException(status_code=404, detail="Process not found")

    if db_process.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to analyze this process")

    analysis_result = nlp.analisar_descricao_processo(db_process.description)
    sugestoes = agent.gerar_sugestoes_de_padronizacao(analysis_result)

    resposta_completa = {
        "entidades_nomeadas": analysis_result.get("entidades_nomeadas", []),
        "tokens": analysis_result.get("tokens", []),
        "sugestoes_do_agente": sugestoes
    }

    return resposta_completa


