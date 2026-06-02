FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
## No copiar archivos de entorno (.env) dentro de la imagen.
## No incluya secretos en la imagen — pase variables en runtime o mediante secretos de CI.

EXPOSE 5000

CMD ["python", "app.py"]
