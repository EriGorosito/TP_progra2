# 1. Imagen base
# Usamos una imagen oficial de Python. Tus archivos __pycache__ [cite: 1, 2, 3, 4]
# indican que usas Python 3.12.
FROM python:3.12-slim

# 2. Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# 3. Instalar dependencias
# Copiamos solo el archivo de requisitos primero para aprovechar el caché de Docker.
# Asumo que tu archivo de requisitos se llama requerimientos.txt [cite: 5]
COPY requerimientos.txt .
RUN pip install --no-cache-dir -r requerimientos.txt

# 4. Copiar el código del proyecto
# Copiamos el directorio 'petcare' [cite: 1] y el script init_db.py [cite: 5]
COPY ./petcare ./petcare
COPY ./init_db.py .

# 5. Exponer el puerto
# El puerto estándar que usa Uvicorn/FastAPI
EXPOSE 8000

# 6. Comando para correr la app
# Asumo que en petcare/api/main.py [cite: 1] tienes una variable llamada "app"
# El host 0.0.0.0 es necesario para que sea accesible desde fuera del contenedor
CMD ["uvicorn", "petcare.api.main:app", "--host", "0.0.0.0", "--port", "8000"]