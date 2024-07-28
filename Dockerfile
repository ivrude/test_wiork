FROM python:3.8-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY settings.py settings.py
COPY main.py main.py

CMD ["python", "main.py"]
