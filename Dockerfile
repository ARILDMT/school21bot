FROM python:3.11-slim
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# В продакшене мы запускаем через webhook, поэтому сразу main.py
CMD ["python", "main.py"]
