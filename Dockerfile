FROM python:3.11-slim

WORKDIR /app
COPY . /app

LABEL authors="sachok_42"
RUN pip install -r requirements.txt
CMD ["flask", "--app", "server.py", "run", "-h", "0.0.0.0", "-p", "8080"]