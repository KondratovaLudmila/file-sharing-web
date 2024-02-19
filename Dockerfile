FROM python:3.10

WORKDIR /src

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --upgrade cryptography paramiko
RUN apt-get update && apt-get install -y postgresql-client

COPY . .

COPY entrypoint.sh /src/entrypoint.sh
RUN chmod +x entrypoint.sh
RUN chmod +x wait-for-postgres.sh

ENTRYPOINT ["/src/entrypoint.sh"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
