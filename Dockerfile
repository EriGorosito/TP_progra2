# 1. Imagen base

FROM python:3.12-slim

# 2. Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# 3. Instalar dependencias

COPY requerimientos.txt .
RUN pip install --no-cache-dir -r requerimientos.txt

# 4. Copiar el código del proyecto
# Copiamos el directorio 'petcare' y el script init_db.py
COPY ./petcare ./petcare
COPY ./init_db.py .

# 5. Exponer el puerto

EXPOSE 8000

# 6. Comando para correr la app

CMD ["uvicorn", "petcare.api.main:app", "--host", "0.0.0.0", "--port", "8000"]