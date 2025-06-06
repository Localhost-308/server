FROM python:3.11-slim

WORKDIR /api-6-semestre

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["flask", "run", "--host=0.0.0.0", "--port=5000", "--debug"]