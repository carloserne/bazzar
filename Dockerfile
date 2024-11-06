# Utiliza una imagen base de Python
FROM python:3.8

# Copia el contenido del directorio "prueba" al directorio "/app" dentro del contenedor
WORKDIR /usr/src/app
COPY requirements.txt ./

# Establece el directorio de trabajo como "/app" dentro del contenedor

# Instala las dependencias
RUN pip install -r requirements.txt

COPY . .
# Expone el puerto 8000 para que el servidor FastAPI pueda escuchar
EXPOSE 8000

# Ejecuta el servidor FastAPI cuando se inicie el contenedor
CMD  ["python", "./main.py", "--host", "0.0.0.0","--port", "8000", "--reload","true"]