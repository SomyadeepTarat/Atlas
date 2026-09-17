#!/bin/sh

set -eu

echo "Running Atlas database migrations..."

alembic upgrade head

echo "Starting Atlas API..."

exec "$@"
