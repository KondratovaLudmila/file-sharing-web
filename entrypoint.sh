#!/bin/sh
## test string for check 8000 

sh -c "uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

./wait-for-postgres.sh db echo "Database is up"

alembic upgrade head

exec "$@"
