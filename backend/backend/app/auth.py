'''# backend/app/auth.py

from passlib.context import CryptContext

# Configura o algoritmo de hashing de senha (bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    """Verifica se a senha fornecida corresponde ao hash salvo."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """Gera o hash de uma senha."""
    return pwd_context.hash(password)
 '''

# backend/app/auth.py

from passlib.context import CryptContext
# NOVAS IMPORTAÇÕES
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
# Adicione estas importações no topo do auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from . import models, schemas, database # Precisaremos acessar o banco de dados

# ... (depois das importações)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# --- CONFIGURAÇÃO DO TOKEN ---
# Chave secreta para assinar o token. Em produção, isso DEVE ser um segredo complexo
# e guardado de forma segura (ex: em variáveis de ambiente).
SECRET_KEY = "uma-chave-secreta-muito-segura-e-dificil-de-adivinhar"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# --- CÓDIGO EXISTENTE ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)


# --- NOVAS FUNÇÕES PARA O TOKEN ---

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Cria um novo token de acesso JWT."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        # Define um tempo de expiração padrão de 15 minutos se não for fornecido
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Adicionaremos a função para verificar o token (get_current_user) no próximo passo.
# Por enquanto, isso é o suficiente para a rota de login.
# ... (depois das outras funções em auth.py)

def get_user(db: Session, username: str):
    """Função auxiliar para buscar um usuário no banco de dados."""
    return db.query(models.User).filter(models.User.username == username).first()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    """
    Dependência para obter o usuário atual a partir de um token JWT.
    Valida o token e retorna os dados do usuário.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decodifica o token para extrair o payload (os dados)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # O 'subject' do nosso token é o username
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        # Se o token for inválido ou expirado, levanta uma exceção
        raise credentials_exception
    
    # Busca o usuário no banco de dados a partir do username no token
    user = get_user(db, username=token_data.username)
    if user is None:
        # Se o usuário não for encontrado no banco, o token é inválido
        raise credentials_exception
    
    # Retorna o objeto do usuário do banco de dados
    return user
