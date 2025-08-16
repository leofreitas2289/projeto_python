# backend/app/main.py
from fastapi import FastAPI, Depends, status
from sqlalchemy.orm import Session
from . import models
#from .database import SessionLocal, engine
from .database import SessionLocal, engine, get_db

from typing import List
from . import auth      # Para usar as funções de hash de senha
from . import schemas   # Para usar os modelos Pydantic (a correção do erro)
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
# Adicione estas importações no topo do main.py
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
# ... (outras importações)
from .auth import get_current_user
# No topo do main.py
from . import models
from .base import Base # Importa a Base
from .database import engine # Importa o engine
# Em main.py, adicione esta importação
from . import nlp
from . import agent # --- ADICIONE ESTA IMPORTAÇÃO ---


# ...

# A linha abaixo agora funcionará
Base.metadata.create_all(bind=engine) 



# Cria as tabelas no banco de dados (para desenvolvimento)
models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# --- Funções de CRUD (Lógica de Banco de Dados) ---

def get_user_by_username(db: Session, username: str):
    """Busca um usuário pelo seu nome de usuário."""
    return db.query(models.User).filter(models.User.username == username).first()

def create_db_user(db: Session, user: schemas.UserCreate):
    """Cria um novo usuário no banco de dados."""
    # Gera o hash da senha antes de salvar
    hashed_password = auth.get_password_hash(user.password)
    # Cria o objeto do modelo SQLAlchemy
    db_user = models.User(
        username=user.username, 
        email=user.email, 
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

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
# ... (rotas de CRUD de usuários existentes) ...

# --- ROTA DE LOGIN (AUTENTICAÇÃO) ---

@app.post("/token", response_model=schemas.Token)
def login_for_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Recebe username e password, verifica as credenciais e retorna um token de acesso.
    """
    # 1. Busca o usuário no banco de dados
    user = get_user_by_username(db, username=form_data.username)

    # 2. Verifica se o usuário existe e se a senha está correta
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. Se as credenciais estiverem corretas, cria o token de acesso
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    # 4. Retorna o token
    return {"access_token": access_token, "token_type": "bearer"}
# ... (depois da rota /token)

# --- ROTA PROTEGIDA DE EXEMPLO ---

@app.get("/users/me/", response_model=schemas.User)
def read_users_me(current_user: models.User = Depends(get_current_user)):
    """
    Retorna os dados do usuário atualmente autenticado.
    A autenticação é gerenciada pela dependência get_current_user.
    """
    return current_user

# Em main.py, adicione esta função

def create_user_process(db: Session, process: schemas.ProcessCreate, user_id: int):
    """Cria um novo processo no banco de dados associado a um usuário."""
    db_process = models.Process(**process.dict(), owner_id=user_id)
    db.add(db_process)
    db.commit()
    db.refresh(db_process)
    return db_process
# Em main.py, adicione esta nova rota

@app.post("/processes/", response_model=schemas.Process, status_code=status.HTTP_201_CREATED)
def create_process(
    process: schemas.ProcessCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Cria um novo processo para o usuário autenticado.
    """
    # 1. Cria um objeto do modelo SQLAlchemy a partir dos dados recebidos
    #    e associa ao usuário logado.
    db_process = models.Process(**process.model_dump(), owner_id=current_user.id)
    
    # 2. Adiciona o novo objeto à sessão do banco de dados.
    db.add(db_process)
    
    # 3. Confirma (salva) a transação no banco.
    db.commit()
    
    # 4. Atualiza o objeto 'db_process' com os dados do banco (como o ID e timestamps).
    db.refresh(db_process)
    
    # 5. Retorna o objeto completo que foi salvo. Este é o passo crucial.
    return db_process
   

@app.get("/processes/", response_model=List[schemas.Process])
def read_processes(
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    """
    Retorna uma lista de processos pertencentes ao usuário atualmente autenticado.
    """
    return current_user.processes

# Em main.py, adicione esta nova rota 15_=08_2025 ATUALIZAR

@app.put("/processes/{process_id}", response_model=schemas.Process)
def update_process(
    process_id: int,
    process_update: schemas.ProcessCreate, # Reutilizamos o schema de criação para a atualização
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Atualiza um processo existente pertencente ao usuário autenticado.
    """
    # 1. Busca o processo no banco de dados
    db_process = db.query(models.Process).filter(models.Process.id == process_id).first()

    # 2. Verifica se o processo existe
    if db_process is None:
        raise HTTPException(status_code=404, detail="Process not found")

    # 3. VERIFICAÇÃO DE SEGURANÇA: Garante que o usuário é o dono do processo
    if db_process.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this process")

    # 4. Atualiza os campos do processo com os novos dados
    db_process.title = process_update.title
    db_process.description = process_update.description
    
    db.commit()
    db.refresh(db_process)
    
    return db_process

# Em main.py, adicione esta rota também

@app.delete("/processes/{process_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_process(
    process_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Deleta um processo existente pertencente ao usuário autenticado.
    """
    # 1. Busca o processo no banco de dados
    db_process = db.query(models.Process).filter(models.Process.id == process_id).first()

    # 2. Verifica se o processo existe
    if db_process is None:
        raise HTTPException(status_code=404, detail="Process not found")

    # 3. VERIFICAÇÃO DE SEGURANÇA: Garante que o usuário é o dono do processo
    if db_process.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this process")

    # 4. Deleta o processo
    db.delete(db_process)
    db.commit()
    
    # Retorna uma resposta vazia com o código 204
    return
# Em main.py, adicione esta nova rota

@app.post("/processes/{process_id}/analyze", response_model=schemas.NlpAnalysisResponse)
def analyze_process_description(
    process_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Executa uma análise de NLP na descrição de um processo existente
    pertencente ao usuário autenticado.
    """
    # 1. Busca o processo no banco de dados
    db_process = db.query(models.Process).filter(models.Process.id == process_id).first()

    # 2. Verifica se o processo existe
    if db_process is None:
        raise HTTPException(status_code=404, detail="Process not found")

    # 3. VERIFICAÇÃO DE SEGURANÇA: Garante que o usuário é o dono do processo
    if db_process.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to analyze this process")

    # 4. Executa a análise de NLP na descrição do processo
    analysis_result = nlp.analisar_descricao_processo(db_process.description)

    # 5. Retorna o resultado da análise
    return analysis_result

