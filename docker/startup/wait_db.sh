#!/bin/sh

cmd="$@"
>&2 echo "--------------"
>&2 echo "$cmd"
>&2 echo "--------------"

until PGPASSWORD="$POSTGRESQL_PASSWORD" psql \
	-h "$POSTGRESQL_HOST" \
	-p "$POSTGRESQL_PORT" \
	-U "$POSTGRESQL_USERNAME" \
	-d "$POSTGRESQL_DATABASE" \
	-c '\q'; \
do
	>&2 echo "Postgres is unavailable - sleeping"
	sleep 1
done
>&2 echo "Postgres is up, continuing"

sh -c "$cmd"
