FROM python:3.12-slim

WORKDIR /app
RUN mkdir /app/db

COPY requirements.txt /app
RUN pip install --no-cache -r /app/requirements.txt

COPY *.py /app

ENTRYPOINT ["uvicorn", "--host", "0.0.0.0", "server:app"]
