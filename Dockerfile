FROM python:3.13-slim

WORKDIR /app

COPY requirements-docker.txt .
RUN pip install -r requirements-docker.txt

COPY /src/ /app/

ENTRYPOINT ["python", "-u", "app.py"]