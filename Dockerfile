FROM python:3.10-slim
LABEL authors="Ata Can"

WORKDIR /app

COPY requirements.txt .
COPY forexFactoryScrapper.py .
COPY main.py .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["python", "main.py"]
