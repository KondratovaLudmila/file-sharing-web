#!/bin/sh

./wait-for-postgres.sh db echo "Database is up"

alembic upgrade head

exec "$@"
