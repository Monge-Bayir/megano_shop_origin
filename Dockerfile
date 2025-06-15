FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

COPY diploma-frontend/dist/diploma-frontend-0.6.tar.gz /app/diploma-frontend/dist/
RUN pip install /app/diploma-frontend/dist/diploma-frontend-0.6.tar.gz

COPY . .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
