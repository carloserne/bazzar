from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from passlib.context import CryptContext

app = FastAPI()

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir solicitudes desde cualquier origen
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permitir todos los encabezados
)

# Lista global para almacenar los datos de los usuarios registrados
SESSION = []

# Configuración para hashing de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class LoginRequest(BaseModel):
    email: str
    contrasena: str

class User(BaseModel):
    id: int
    email: str
    nombre: str
    sexo: str
    hashed_password: str

class RegistroRequest(BaseModel):
    contrasena: str
    email: str
    nombre: str
    sexo: str

@app.post("/api/login", response_model=User)
def login(request: LoginRequest):
    # Buscar el usuario en la lista SESSION
    for user in SESSION:
        if user.email == request.email and request.contrasena == user.hashed_password:
            return user
    raise HTTPException(status_code=400, detail="Invalid credentials")

@app.post("/api/registrar", response_model=User)
def registrar(request: RegistroRequest):
    user = User(id=len(SESSION) + 1, nombre=request.nombre, email=request.email, sexo=request.sexo, hashed_password=request.contrasena)
    SESSION.append(user)
    return user

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)


