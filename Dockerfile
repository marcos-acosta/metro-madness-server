FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY /src/ /app/

ENTRYPOINT ["python", "-u", "app.py"]